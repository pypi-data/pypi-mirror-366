import scipy
import torch
import gudhi
import itertools
import hnswlib
import torch.linalg
import random
import copy
import scipy.sparse
import anndata as ad
import numpy as np
import pandas as pd
import scanpy as sc
import networkx as nx
import torch.optim as optim

from scipy import sparse
from scipy import stats
from typing import Optional
from annoy import AnnoyIndex
from scipy.spatial import distance
from collections import Counter
from sklearn.neighbors import kneighbors_graph
from sklearn.neighbors import NearestNeighbors
from scipy.optimize import linear_sum_assignment
from torch_geometric.nn import GCNConv

from torch.nn.parameter import Parameter
from torch.nn.modules.module import Module
from typing import List, Optional, Union, Any
from torch_geometric.nn.conv import MessagePassing


from torch_scatter import scatter_add
from torch_geometric.utils import add_remaining_self_loops
from sklearn.metrics.pairwise import pairwise_distances_argmin_min
from sklearn.metrics import adjusted_rand_score as ari_score

from sklearn.metrics import pairwise_distances
from collections import OrderedDict

def get_targets_index(gene_cell_mat, signaling_pathway, lrp):
    """
    Get the TFs and TGs from database for each ligand-receptor pair.
    
    Parameters:
    - gene_cell_mat: DataFrame containing gene expression data for cells.
    - signaling_pathway: DataFrame containing signaling pathway information.
    - lrp: string, the ligand-receptor pair.

    """
    # combine the first two columns
    signaling_pathway['Ligand_Receptor'] = signaling_pathway['Ligand_Symbol'] + '-' + signaling_pathway['Receptor_Symbol']
    # take out the indexes of focused lrp
    indexes = [i for i, x in enumerate(signaling_pathway['Ligand_Receptor']) if x == lrp]
    # take out the TFs and TGs
    TFs = signaling_pathway['TF_Symbol'].iloc[indexes].tolist()
    TGs = signaling_pathway['TG_Symbol'].iloc[indexes].tolist()
    TFGs = TFs+TGs
    tfg_indexes = [gene_cell_mat.index.get_loc(name) for name in TFGs if name in gene_cell_mat.index]
    return tfg_indexes, TFGs


def label_to_int(adata, label_name):
    adata_label_o = np.array(adata.obs[label_name].copy())
    label_list = list(set(adata.obs[label_name].tolist()))
    adata_label = adata_label_o.copy()
    for i in range(len(label_list)):
        need_index = np.where(adata.obs[label_name]==label_list[i])[0]
        if len(need_index):
            adata_label[need_index] = i
    adata.obs['pre_label'] = adata_label
    return adata, label_list,adata_label_o



def sparse_mx_to_torch_edge_list(sparse_mx):
    sparse_mx = sparse_mx.tocoo().astype(np.float32)
    edge_list = torch.from_numpy(np.vstack((sparse_mx.row, sparse_mx.col)).astype(np.int64))
    return edge_list


## Covert a sparse matrix into a dense matrix
to_dense_array = lambda X: np.array(X.todense()) if isinstance(X,sparse.csr.spmatrix) else X


def get_lr_data_no_tfg(links_database, gene_cell_pd):
    # take out ligand and receptor
    links_database['LRP'] = links_database['Ligand_Symbol']+'-'+links_database['Receptor_Symbol']
    
    # Group by Key and apply merge operations

    lr_f = list(set(links_database['LRP']))
    lr_l = [lr.split('-')[0] for lr in lr_f]
    lr_r = [lr.split('-')[1] for lr in lr_f] # may has multiple 
    lr_l_new = [s.split('_') for s in lr_l]
    lr_r_new = [s.split('_') for s in lr_r]
    lr_l_len = [len(x) for x in lr_l_new]
    lr_r_len = [len(x) for x in lr_r_new]
    # detect the number of two 
    lr_l_len_arr = np.array(lr_l_len)
    ix_l1 = np.where(lr_l_len_arr == 1)[0].tolist()
    lr_l1 = [lr_l[i] for i in ix_l1]
    ix_l2 = np.where(lr_l_len_arr > 1)[0].tolist()
    lr_l_data = np.zeros([len(lr_l_new), gene_cell_pd.shape[1]])
    lr_l_data[ix_l1,:] = gene_cell_pd.loc[lr_l1].values
    if len(ix_l2) > 0:
        for j in range(len(ix_l2)):
            lr_l_data[ix_l2[j],:] = np.mean(gene_cell_pd.loc[lr_l_new[ix_l2[j]]].values, axis=0)
    spots_ligand_pd = pd.DataFrame(data = lr_l_data.T, index = gene_cell_pd.columns, columns = lr_l)
    
    # detect the number of two 
    lr_r_len_arr = np.array(lr_r_len)
    ix_r1 = np.where(lr_r_len_arr == 1)[0].tolist()
    lr_r1 = [lr_r[i] for i in ix_r1]
    ix_r2 = np.where(lr_r_len_arr > 1)[0].tolist()
    lr_r_data = np.zeros([len(lr_r_new), gene_cell_pd.shape[1]])
    lr_r_data[ix_r1,:] = gene_cell_pd.loc[lr_r1].values
    if len(ix_r2) > 0:
        for j in range(len(ix_r2)):
            lr_r_data[ix_r2[j],:] = np.mean(gene_cell_pd.loc[lr_r_new[ix_r2[j]]].values, axis=0)
    spots_receptor_pd = pd.DataFrame(data = lr_r_data.T, index = gene_cell_pd.columns, columns = lr_r)


    spots_ligand_pd.columns = lr_l
    spots_receptor_pd.columns = lr_r
    return spots_ligand_pd, spots_receptor_pd, lr_f


def get_lr_data(links_database, gene_cell_pd):
    # take out ligand and receptor
    # record downstream tf and tgs for each ligand receptor pair
    links_database['LRP'] = links_database['Ligand_Symbol']+'-'+links_database['Receptor_Symbol']
    #pathway_dict = dict(zip(links_database['LRP'], zip(links_database['TF_Symbol'], links_database['TG_Symbol'])))
    merge_operations = {'TF_Symbol': lambda x: list(x),  # Combine as list
    'TG_Symbol': lambda x: list(x)  # Combine as pipe-separated string
    }
    # Group by Key and apply merge operations
    pathway_dict = links_database.groupby('LRP').agg(merge_operations).to_dict('index')
    lrp_keys = list(pathway_dict.keys())
    for i in range(len(lrp_keys)):
        tfg_i = pathway_dict[lrp_keys[i]]['TF_Symbol']+pathway_dict[lrp_keys[i]]['TG_Symbol']
        pathway_dict[lrp_keys[i]] = list(set(tfg_i))

    lr_f = list(pathway_dict.keys())
    lr_l = [lr.split('-')[0] for lr in lr_f]
    lr_r = [lr.split('-')[1] for lr in lr_f] # may has multiple 
    lr_l_new = [s.split('_') for s in lr_l]
    lr_r_new = [s.split('_') for s in lr_r]
    lr_l_len = [len(x) for x in lr_l_new]
    lr_r_len = [len(x) for x in lr_r_new]
    # detect the number of two 
    lr_l_len_arr = np.array(lr_l_len)
    ix_l1 = np.where(lr_l_len_arr == 1)[0].tolist()
    lr_l1 = [lr_l[i] for i in ix_l1]
    ix_l2 = np.where(lr_l_len_arr > 1)[0].tolist()
    lr_l_data = np.zeros([len(lr_l_new), gene_cell_pd.shape[1]])
    lr_l_data[ix_l1,:] = gene_cell_pd.loc[lr_l1].values
    if len(ix_l2) > 0:
        for j in range(len(ix_l2)):
            lr_l_data[ix_l2[j],:] = np.mean(gene_cell_pd.loc[lr_l_new[ix_l2[j]]].values, axis=0)
    spots_ligand_pd = pd.DataFrame(data = lr_l_data.T, index = gene_cell_pd.columns, columns = lr_l)
    
    # detect the number of two 
    lr_r_len_arr = np.array(lr_r_len)
    ix_r1 = np.where(lr_r_len_arr == 1)[0].tolist()
    lr_r1 = [lr_r[i] for i in ix_r1]
    ix_r2 = np.where(lr_r_len_arr > 1)[0].tolist()
    lr_r_data = np.zeros([len(lr_r_new), gene_cell_pd.shape[1]])
    lr_r_data[ix_r1,:] = gene_cell_pd.loc[lr_r1].values
    if len(ix_r2) > 0:
        for j in range(len(ix_r2)):
            lr_r_data[ix_r2[j],:] = np.mean(gene_cell_pd.loc[lr_r_new[ix_r2[j]]].values, axis=0)
    spots_receptor_pd = pd.DataFrame(data = lr_r_data.T, index = gene_cell_pd.columns, columns = lr_r)

    # take out downstream analysis
    tfg_pd_l = []
    for i in range(len(lr_f)):
        pd_g = gene_cell_pd.loc[list(pathway_dict[lr_f[i]]),:].T
        tfg_pd_l.append(pd_g)

    # change the columnnames for these two data
    spots_ligand_pd.columns = lr_l
    spots_receptor_pd.columns = lr_r
    return spots_ligand_pd, spots_receptor_pd, tfg_pd_l, lr_f



def get_neig_index(spot_loc, locMeasure, neig_number):
    # import data used for inferring CCC
    print("spot location for adjancy")
    #spot_loc = pd.read_table(spatialLocation, header = 0, index_col = 0)
    dist_loc = pairwise_distances(spot_loc.values, metric = locMeasure)

    sorted_knn = dist_loc.argsort(axis=1) # return the ordered index
    selected_node = []
    for index in list(range(np.shape(dist_loc)[0])):
        selected_node.append(sorted_knn[index, 1:(neig_number+1)]) # top 10 index

    selected_node = torch.LongTensor(selected_node)  # restore the top 10 indexes for each node

    return selected_node


def get_cell_positive_pairs(adata_rna,spot_loc,neig_number,nei_adj,no_spatial):
    if no_spatial:
        cell_cell_adj = np.zeros((len(adata_rna), len(adata_rna)), dtype = np.int32)
        for index in list(range(len(adata_rna))):
            cell_cell_adj[index, nei_adj[index,:]] = 1
    else:
        cell_clus = adata_rna.obs['cell_type'].values.astype('str')
        #cell_loc = np.column_stack((adata_rna.obs['imagerow'].values.tolist(), adata_rna.obs['imagecol'].values.tolist()))
        dist_out = pairwise_distances(spot_loc)
        cell_cell_adj = np.zeros((len(adata_rna), len(adata_rna)), dtype = np.int32)

        for index in list(range(np.shape(dist_out)[0] )):
            match_int  = np.where(cell_clus[index]==cell_clus)[0]
            sorted_knn = dist_out[index, match_int].argsort()
            cell_cell_adj[index, match_int[sorted_knn[:neig_number]]] = 1
    pos = pd.DataFrame(cell_cell_adj)
    return pos


def get_average_lr(nei_adj, spots_ligand_pd, spots_recep_pd):
    # average ligand and receptor around the neighbors
    spots_ligand_a = np.zeros(spots_ligand_pd.shape)
    spots_recep_a = np.zeros(spots_recep_pd.shape)
    for i in range(nei_adj.shape[0]):
        spots_ligand_a[i,:] = np.mean(spots_ligand_pd.values[nei_adj[i,:],:],axis = 0)+spots_ligand_pd.values[i,:]
        spots_recep_a[i,:] = np.mean(spots_recep_pd.values[nei_adj[i,:],:],axis = 0)+spots_recep_pd.values[i,:]
    spots_ligand_ave_pd = pd.DataFrame(spots_ligand_a, index = spots_ligand_pd.index, columns = spots_ligand_pd.columns)
    spots_recep_ave_pd = pd.DataFrame(spots_recep_a, index = spots_recep_pd.index, columns = spots_recep_pd.columns)
    return spots_ligand_ave_pd, spots_recep_ave_pd

# result structure: dictionary: key is L-R pair, value is a dictionary with many keys: Score, Significat p-value, attentions_inter, attentions_intra
def get_regchat_result(CCI_activity_pd, CCI_strength_pd, atten_inter_list, atten_intra_list,tfg_l):
    key_name = CCI_activity_pd.columns.tolist()
    result = {}
    for i in range(len(key_name)):
        # score and strength
        Scores_strength = pd.concat([CCI_activity_pd[key_name[i]],CCI_strength_pd[key_name[i]]], axis=1)
        # inter attention
        inter_att = pd.DataFrame(atten_inter_list[i].detach().numpy(), index = CCI_activity_pd.index)
        # intra attention
        intra_att = pd.DataFrame(atten_intra_list[i].detach().numpy(), index = CCI_activity_pd.index, columns = tfg_l[i])
        dic_inner = {'score_strength': Scores_strength, 'inter_att':inter_att, 'intra_att': intra_att}
        result[key_name[i]] = dic_inner
    return result

# compute the cell_type pair information
from collections import OrderedDict
def get_cell_type_pairs(adata_rna, nei_adj, label):
    # randomly select neighbors
    ids = np.arange(nei_adj.shape[0])
    cell_type_l = adata_rna.obs['cell_type'].tolist()
    if label is None:
        cell_type_uniq = list(OrderedDict.fromkeys(cell_type_l))
    else:
        cell_type_uniq = label
    n_type = len(cell_type_uniq)
    cell_type_num = np.zeros((nei_adj.shape[0],n_type*n_type))
    # name pair
    type_name = []
    for i in range(n_type):
        for j in range(n_type):
            type_name.append(cell_type_uniq[i]+'_'+cell_type_uniq[j])
    type_record = list()
    for i in range(nei_adj.shape[0]):
        index_i = nei_adj[i,:].tolist()
        type_matrix = np.zeros((len(index_i),n_type*n_type))
        for j in range(len(index_i)):
            type_ij = cell_type_l[index_i[j]]+'_'+cell_type_l[i]
            id_ij = type_name.index(type_ij)
            type_matrix[j,id_ij] = 1
        type_record.append(type_matrix)
    return type_record, type_name


def get_cell_type_LRs(result,type_record, type_name, p_value_cutoff):
    LRPs = list(result.keys())
    type_score = np.zeros((len(LRPs),len(type_name))) # type_name across each lr, record the average value
    type_num = np.zeros((len(LRPs),len(type_name))) # check the number count
    type_num_total = np.zeros((1,len(type_name)))
    for i in range(len(LRPs)):
        result_i_score = result[LRPs[i]]['score_strength'].iloc[:,0]# score
        result_i_strength = result[LRPs[i]]['score_strength'].iloc[:,1]# strength       
        for j in range(len(type_record)):
            index_j = type_record[j] # 10*type_name
            for t in range(index_j.shape[0]):
                # detect nonzero index
                index_t = np.where(index_j[t,:] == 1)[0][0]
                type_num_total[0,index_t] = type_num_total[0,index_t] + 1
                type_score[i,index_t] = type_score[i,index_t] + result_i_score[j] # the j-th central code
                if result_i_strength[j] < p_value_cutoff: # obtain the siginificant number.
                    type_num[i,index_t] = type_num[i,index_t] + 1
    type_num_total[type_num_total == 0] = 1# replace 0 to 1.
    #type_num_total = type_num_total/np.mean(type_num_total) 
    type_score = type_score/type_num_total
    type_num = type_num
    type_score_pd = pd.DataFrame(type_score, index = LRPs, columns = type_name)
    type_num_pd = pd.DataFrame(type_num, index = LRPs, columns = type_name)
    return type_score_pd, type_num_pd,type_num_total



def get_cell_type_LRFGs(result,type_record, type_name, p_value_cutoff):
    LRFGs = list(result.keys())
    type_score = np.zeros((len(LRFGs),len(type_name))) # type_name across each lr, record the average value
    type_num = np.zeros((len(LRFGs),len(type_name))) # check the number count
    type_num_total = np.zeros((1,len(type_name)))
    for i in range(len(LRFGs)):
        result_i_score = result[LRFGs[i]]['score_strength'].iloc[:,0]# score
        result_i_strength = result[LRFGs[i]]['score_strength'].iloc[:,1]# strength       
        for j in range(len(type_record)):
            index_j = type_record[j] # 10*type_name
            for t in range(index_j.shape[0]):
                # detect nonzero index
                index_t = np.where(index_j[t,:] == 1)[0][0]
                type_num_total[0,index_t] = type_num_total[0,index_t] + 1
                type_score[i,index_t] = type_score[i,index_t] + result_i_score[j] # the j-th central code
                if result_i_strength[j] < p_value_cutoff:
                    type_num[i,index_t] = type_num[i,index_t] + 1
    type_num_total[type_num_total == 0] = 1# replace 0 to 1.
    type_num_total = type_num_total/np.mean(type_num_total) 
    type_score = type_score/type_num_total
    type_num = type_num
    type_score_pd = pd.DataFrame(type_score, index = LRFGs, columns = type_name)
    type_num_pd = pd.DataFrame(type_num, index = LRFGs, columns = type_name)
    return type_score_pd, type_num_pd,type_num_total


# obtain the nich information of each node based on neighbors
def get_nich_score(type_record):
    # compute entropy of each node
    scores = np.zeros((1,len(type_record)))
    for i in range(len(type_record)):
        data_i = type_record[i]
        k_neig = data_i.shape[0]
        # compute the ratio
        col_means_i = np.mean(data_i, axis=0)
        col_means_i = col_means_i[col_means_i > 0]  # Filter out zeros
        s_i = -np.sum(col_means_i * np.log2(col_means_i))
        if s_i != 0:
            scores[0,i] = s_i
    return scores

# result structure: dictionary: key is L-R pair, value is a dictionary with many keys: Score, Significat p-value, attentions_inter, attentions_intra
def get_regchat_result_LR(CCI_activity_pd, CCI_strength_pd, atten_inter_list, atten_intra_list,tfg_l):
    key_name = CCI_activity_pd.columns.tolist()
    result = {}
    for i in range(len(key_name)):
        # score and strength
        Scores_strength = pd.concat([CCI_activity_pd[key_name[i]],CCI_strength_pd[key_name[i]]], axis=1)
        # inter attention
        inter_att = pd.DataFrame(atten_inter_list[i].detach().numpy(), index = CCI_activity_pd.index)
        # intra attention
        intra_att = pd.DataFrame(atten_intra_list[i].detach().numpy(), index = CCI_activity_pd.index, columns = tfg_l[i])
        dic_inner = {'score_strength': Scores_strength, 'inter_att':inter_att, 'intra_att': intra_att}
        result[key_name[i]] = dic_inner
    return result


# result structure: dictionary: key is L-R pair, value is a dictionary with many keys: Score, Significat p-value, attentions_inter, attentions_intra
def get_regchat_result_LR_inter(CCI_activity_pd, CCI_strength_pd, atten_inter_list):
    key_name = CCI_activity_pd.columns.tolist()
    result = {}
    for i in range(len(key_name)):
        # score and strength
        Scores_strength = pd.concat([CCI_activity_pd[key_name[i]],CCI_strength_pd[key_name[i]]], axis=1)
        # inter attention
        inter_att = pd.DataFrame(atten_inter_list[i].detach().numpy(), index = CCI_activity_pd.index)
        dic_inner = {'score_strength': Scores_strength, 'inter_att':inter_att}
        result[key_name[i]] = dic_inner
    return result



def get_regchat_result_LRFG(LRFG_activity_pd, LRFG_strength_pd):
    key_name = LRFG_activity_pd.columns.tolist()
    result = {}
    for i in range(len(key_name)):
        # score and strength
        Scores_strength = pd.concat([LRFG_activity_pd[key_name[i]],LRFG_strength_pd[key_name[i]]], axis=1)
        dic_inner = {'score_strength': Scores_strength}
        result[key_name[i]] = dic_inner
    return result


def get_regchat_result_LG(LG_activity_pd, LG_strength_pd):
    key_name = LG_activity_pd.columns.tolist()
    result = {}
    for i in range(len(key_name)):
        # score and strength
        Scores_strength = pd.concat([LG_activity_pd[key_name[i]],LG_strength_pd[key_name[i]]], axis=1)
        dic_inner = {'score_strength': Scores_strength}
        result[key_name[i]] = dic_inner
    return result


def compute_C(A, B):
    N = B.size  # Total number of elements in B
    # Reshape B into a 1D array for correct broadcasting
    B_flat = B.ravel()  # shape: (N,)
    # Compare every element of B with every element of A
    # Using broadcasting: (N,) vs (n, m) -> (N, n, m)
    comparison = B_flat[:, np.newaxis, np.newaxis] < A
    # Sum along the first axis (N) to get counts, then normalize
    C = 1 - np.sum(comparison, axis=0) / N
    return C

def compute_C_fast(A, B):
    N = B.size
    B_sorted = np.sort(B.ravel())  # Sort B once for efficient comparisons
    # Find insertion positions (how many B elements are < A[s,t])
    counts = np.searchsorted(B_sorted, A.ravel()).reshape(A.shape)
    C = 1 - counts / N
    return C

def compute_C_low_mem(A, B):
    N = B.size
    B_flat = B.ravel()  # Flatten B to 1D (shape N,)
    C = np.empty_like(A)  # Preallocate output
    
    # Compute in a memory-efficient way
    counts = np.zeros_like(A, dtype=np.int32)  # Use int32 to save memory
    for b in B_flat:  # Loop over B (but still fast due to NumPy's internals)
        counts += (b < A)  # Accumulate counts without storing full (N,n,m) array
    C = 1 - counts / N
    return C

# define a function about get LG_score
def get_LGs(signaling_pathway, LRFG_score_pd):
    signaling_pathway['Ligand_TG'] = signaling_pathway['Ligand_Symbol']+'-'+signaling_pathway['TG_Symbol']
    LGs = list(set(signaling_pathway['Ligand_TG'].tolist()))
    signaling_pathway['LRFG'] = signaling_pathway['Ligand_Symbol']+'-'+signaling_pathway['Receptor_Symbol']+'-'+signaling_pathway['TF_Symbol']+'-'+signaling_pathway['TG_Symbol']
    # return a dataframe with row are spots, columns are ligand-gene
    lg_score = np.zeros([LRFG_score_pd.shape[0],len(LGs)])
    for i in range(len(LGs)):
        index_i = np.where(signaling_pathway['Ligand_TG'] == LGs[i])[0] # the rows related to LG,
        lrfg_i = signaling_pathway['LRFG'][index_i]
        score_i = LRFG_score_pd[lrfg_i]
        if len(lrfg_i) > 1:
            lg_score[:,i] = score_i.mean(axis=1)
        else:
            lg_score[:,i] = score_i.to_numpy().reshape(LRFG_score_pd.shape[0],)
    LG_score_pd = pd.DataFrame(data = lg_score, index = LRFG_score_pd.index, columns = LGs)
    return LG_score_pd
 
def neg_log10_transform(array, replace_zero=None, handle_negatives='nan'):
    """
    Apply -log10(x) transformation to a 2D array with proper handling of edge cases.
    
    Parameters:
    - array: Input 2D numpy array
    - replace_zero: Value to replace zeros with before log transform (default: None skips zeros)
    - handle_negatives: How to handle negative values ('nan', 'abs', 'zero', or 'remove')
    
    Returns:
    Transformed array with same shape as input
    """
    # Create copy to avoid modifying original array
    arr = array.copy().astype(float)
    
    # Handle zeros if specified
    if replace_zero is not None:
        arr[arr == 0] = replace_zero
    
    # Handle negative values
    if handle_negatives == 'nan':
        arr[arr < 0] = np.nan
    elif handle_negatives == 'abs':
        arr = np.abs(arr)
    elif handle_negatives == 'zero':
        arr[arr < 0] = 0
    elif handle_negatives == 'remove':
        arr[arr < 0] = np.nan  # Will propagate through log transform
    
    # Apply -log10 transform (will produce nan for zeros/negatives if not handled)
    with np.errstate(divide='ignore', invalid='ignore'):
        transformed = -np.log10(arr)
    
    return transformed

def z_score_2d(array):
    """
    Perform Z-score normalization on all values in a 2D NumPy array.
    
    Parameters:
        array (np.ndarray): Input 2D array
        
    Returns:
        np.ndarray: Z-score normalized array with same shape as input
        float: Global mean of original array
        float: Global standard deviation of original array
    """
    global_mean = np.mean(array)
    global_std = np.std(array)
    
    # Handle division by zero (replace std=0 with 1 to avoid NaN)
    safe_std = global_std if global_std != 0 else 1.0
    
    normalized_array = (array - global_mean) / safe_std
    return normalized_array, global_mean, global_std

def permutation_adj(nei_adj):
    # fix central node, but change neighbors from other central node, change its adjs
    ids = np.arange(nei_adj.shape[0])
    ids = np.random.permutation(ids)
    nei_adj_per = nei_adj[ids,:]
    
    return nei_adj_per

def permutation_adj_full(nei_adj):
    # randomly selected neighbors
    idx = torch.randperm(nei_adj.numel())
    nei_adj_per = nei_adj.view(-1)[idx].view(nei_adj.size())
    return nei_adj_per

# select the top sender for each node, then plot the arow from the sender to the target
# obtain a dataframe with the columns with: spots, LR pair, score, p_val
def get_signifcant_node(adata,result_LR, nei_adj,coord,p_val_cutoff,type = 'weight',topk = 2):
    LRs = list(result_LR.keys())
    gene_cell_pd = pd.DataFrame(data = adata.X.T, index = adata.var.index, columns = adata.obs.index)
    sample_lst = []# node
    interccc_lst = []#scores
    pscore_lst = []#pvalue
    sender_lst = []# sender
    sender_x_lst = []
    sender_y_lst = []
    receiver_x_lst = []# the central node
    receiver_y_lst = []
    lrp_lst = []
    for i in range(len(LRs)):
        p_i = result_LR[LRs[i]]['score_strength'].iloc[:,1]# strength
        s_i = result_LR[LRs[i]]['score_strength'].iloc[:,0]# score
        index_i = np.where(p_i < p_val_cutoff)[0].tolist() # the significant central nodes
        if len(index_i) > 0 :
            if type == 'weight':
                att = result_LR[LRs[i]]['inter_att'] # use attention
                #or attention*ligands?
            else:
                att0 = result_LR[LRs[i]]['inter_att']
                # associated with ligands, multiply the expression of ligands
                lr_l = LRs[i].split('-')[0]
                data_l_all = gene_cell_pd.loc[lr_l].values
                data_l = np.zeros(att0.shape)
                for k in range(att0.shape[0]):
                    data_l[k,:] = data_l_all[nei_adj[k,:]]
                att = att0*data_l
            
            # return the top k positions for each significant cells
            for j in range(len(index_i)):
                row_np = nei_adj[index_i[j],:]
                data_np = att.iloc[index_i[j],:]
                sorted_idj = np.argsort( -data_np )[:topk]# from large to small
                tmp_idj = row_np[ sorted_idj ]# top k senders
                sample_name = p_i.index.tolist()[index_i[j]]
                pscore = p_i[index_i[j]]
                interccc = s_i[index_i[j]]
                sender = tmp_idj
                sender_x = coord.iloc[sender]['x']
                sender_y = coord.iloc[sender]['y']
                receiver_x = coord.iloc[index_i[j]]['x']
                receiver_y = coord.iloc[index_i[j]]['y']
                LR_name = LRs[i]
                
                if topk > 1:
                    sample_name = [sample_name] * topk
                    interccc = [interccc]* topk
                    pscore = [pscore]* topk
                    receiver_x = [receiver_x]* topk
                    receiver_y = [receiver_y]* topk
                    LR_name = [LR_name]* topk
                sample_lst.extend(sample_name)
                interccc_lst.extend(interccc)
                pscore_lst.extend(pscore)
                sender_lst.extend(sender.tolist())
                sender_x_lst.extend(sender_x)
                sender_y_lst.extend(sender_y)
                receiver_x_lst.extend(receiver_x)
                receiver_y_lst.extend(receiver_y)
                lrp_lst.extend(LR_name)
                
    res_df = pd.DataFrame({
        'Sample_Name': sample_lst,
        'LR_Name': lrp_lst,
        'Comm_Score': interccc_lst,
        'P_Score': pscore_lst,
        'Sender': sender_lst,
        'Sender_x': sender_x_lst,
        'Sender_y': sender_y_lst,
        'Receiver_x': receiver_x_lst,
        'Receiver_y': receiver_y_lst
    })
    return res_df

