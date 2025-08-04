import numpy as np
import scanpy as sc
import anndata as ad
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import f1_score



def mclust_R(adata, num_cluster, modelNames='EEE', used_obsm='embedding', random_seed=666):
    """\
    Clustering using the mclust algorithm.
    The parameters are the same as those in the R package mclust.
    """

    np.random.seed(random_seed)
    import rpy2
    import rpy2.robjects as robjects
    robjects.r.library("mclust")

    import rpy2.robjects.numpy2ri
    rpy2.robjects.numpy2ri.activate()
    r_random_seed = robjects.r['set.seed']
    r_random_seed(random_seed)
    rmclust = robjects.r['Mclust']

    res = rmclust(adata.obsm[used_obsm], num_cluster, modelNames)
    mclust_res = np.array(res[-2])

    adata.obs['mclust'] = mclust_res
    adata.obs['mclust'] = adata.obs['mclust'].astype('int')
    adata.obs['mclust'] = adata.obs['mclust'].astype('category')
    return adata

def mclust_init(emb, num_clusters, modelNames='EEE', random_seed=2024):
    """\
    Clustering using the mclust algorithm.
    The parameters are the same as those in the R package mclust.
    """

    np.random.seed(random_seed)
    import rpy2
    import rpy2.robjects as robjects
    robjects.r.library("mclust")

    import rpy2.robjects.numpy2ri
    rpy2.robjects.numpy2ri.activate()
    r_random_seed = robjects.r['set.seed']
    r_random_seed(random_seed)
    rmclust = robjects.r['Mclust']

    res = rmclust(emb, num_clusters, modelNames)
    #res = mclustpy(emb, G=num_clusters)
    
    mclust_res = np.array(res[-2])

    return mclust_res


def plot_boxplot(nmi_data):
    plt.figure(dpi=500)
    plt.rcParams['figure.figsize'] = (8, 5)

    figure, axes = plt.subplots()
    colors = ['#FFB6C1', '#e07b54', '#87CEFA', '#51b1b7', '#e0bb00']

    for i in range(0, 5):
        plt.scatter((i+1) * np.ones_like(nmi_data[i]), nmi_data[i], alpha=0.8, color=colors[i],
                s=70, zorder=3, marker='p')

    legend_elements = []

    mean_values = [np.mean(data) for data in nmi_data]

    # 添加平均数线
    # 添加短线段表示平均值
    for i, mean_value in enumerate(mean_values):
        plt.plot([i+0.85, i+1.15], [mean_value, mean_value], color=colors[i], linewidth=6)

    for i in range(len(ami_data)-1):
        for j in range(len(ami_data[0])):
            plt.plot([i+1, i+2], [nmi_data[i][j], nmi_data[i+1][j]], linestyle='--', color='#c4c4c4',linewidth=2)

    # 添加点作为图例
    legend_elements.append(plt.scatter([], [], color=colors[0], s=50, label='method'))
    
    plt.show()



 def communication_direction(
    adata,
    database_name = None,
    pathway_name = None,
    lr_pair = None,
    k = 5,
    pos_idx = None,
    copy = False):
    """
    Construct spatial vector fields for inferred communication.

    Parameters
    ----------
    adata
        The data matrix of shape ``n_obs`` × ``n_var``.
        Rows correspond to cells or spots and columns to genes.
    database_name
        Name of the ligand-receptor database.
        If both pathway_name and lr_pair are None, the signaling direction of all ligand-receptor pairs is computed.
    pathway_name
        Name of the signaling pathway.
        If given, only the signaling direction of this signaling pathway is computed.
    lr_pair
        A tuple of ligand-receptor pair. 
        If given, only the signaling direction of this pair is computed.
    k
        Top k senders or receivers to consider when determining the direction.
    pos_idx
        The columns in ``.obsm['spatial']`` to use. If None, all columns are used.
        For example, to use just the first and third columns, set pos_idx to ``numpy.array([0,2],int)``.
    copy
        Whether to return a copy of the :class:`anndata.AnnData`.
    Returns
    -------
    adata : anndata.AnnData
        Vector fields describing signaling directions are added to ``.obsm``, 
        e.g., for a database named "databaseX", 
        ``.obsm['commot_sender_vf-databaseX-ligA-recA']`` and ``.obsm['commot_receiver_vf-databaseX-ligA-recA']``
        describe the signaling directions of the cells as, respectively, senders and receivers through the 
        ligand-receptor pair ligA and recA.
        If copy=True, return the AnnData object and return None otherwise.

    """
    obsp_names = []
    if not lr_pair is None:
        obsp_names.append(lr_pair[0]+'_'+lr_pair[1])
    elif not pathway_name is None:
        obsp_names.append(pathway_name)

    ncell = adata.shape[0]
    pts = np.array( adata.obsm['spatial'], float )
    if not pos_idx is None:
        pts = pts[:,pos_idx]

    for i in range(len(obsp_names)):
        S = adata.obsp[obsp_names[i]]
        S_sum_sender = np.array( S.sum(axis=1) ).reshape(-1)
        S_sum_receiver = np.array( S.sum(axis=0) ).reshape(-1)
        sender_vf = np.zeros_like(pts)
        receiver_vf = np.zeros_like(pts)

        S_lil = S.tolil()
        for j in range(S.shape[0]):
            if len(S_lil.rows[j]) <= k:
                tmp_idx = np.array( S_lil.rows[j], int )
                tmp_data = np.array( S_lil.data[j], float )
            else:
                row_np = np.array( S_lil.rows[j], int )
                data_np = np.array( S_lil.data[j], float )
                sorted_idx = np.argsort( -data_np )[:k]
                tmp_idx = row_np[ sorted_idx ]
                tmp_data = data_np[ sorted_idx ]
            if len(tmp_idx) == 0:
                continue
            elif len(tmp_idx) == 1:
                avg_v = pts[tmp_idx[0],:] - pts[j,:]
            else:
                tmp_v = pts[tmp_idx,:] - pts[j,:]
                tmp_v = normalize(tmp_v, norm='l2')
                avg_v = tmp_v * tmp_data.reshape(-1,1)
                avg_v = np.sum( avg_v, axis=0 )
            avg_v = normalize( avg_v.reshape(1,-1) )
            sender_vf[j,:] = avg_v[0,:] * S_sum_sender[j]
            
        S_lil = S.T.tolil()
        for j in range(S.shape[0]):
            if len(S_lil.rows[j]) <= k:
                tmp_idx = np.array( S_lil.rows[j], int )
                tmp_data = np.array( S_lil.data[j], float )
            else:
                row_np = np.array( S_lil.rows[j], int )
                data_np = np.array( S_lil.data[j], float )
                sorted_idx = np.argsort( -data_np )[:k]
                tmp_idx = row_np[ sorted_idx ]
                tmp_data = data_np[ sorted_idx ]
            if len(tmp_idx) == 0:
                continue
            elif len(tmp_idx) == 1:
                avg_v = -pts[tmp_idx,:] + pts[j,:]
            else:
                tmp_v = -pts[tmp_idx,:] + pts[j,:]
                tmp_v = normalize(tmp_v, norm='l2')
                avg_v = tmp_v * tmp_data.reshape(-1,1)
                avg_v = np.sum( avg_v, axis=0 )
            avg_v = normalize( avg_v.reshape(1,-1) )
            receiver_vf[j,:] = avg_v[0,:] * S_sum_receiver[j]

        adata.obsm["sender_vf-"+obsp_names[i]] = sender_vf
        adata.obsm["receiver_vf-"+obsp_names[i]] = receiver_vf

    return adata if copy else None

# select the top sender for each node, then plot the arow from the sender to the target
# obtain a dataframe with the columns with: spots, LR pair, score, p_val
def get_signifcant_node(result_LR, nei_adj,coord,p_val_cutoff,topk = 2):
    LRs = list(result_LR.keys())
    sample_lst = []# node
    interccc_lst = []#scores
    pscore_lst = []#pvalue
    sender_lst = []# sender
    sender_x_lst = []
    sender_y_lst = []
    receiver_x_lst = []# the central node
    receiver_y_lst = []
    for i in range(len(LRs)):
        p_i = result_LR[LRs[i]]['score_strength'].iloc[:,1]
        s_i = result_LR[LRs[i]]['score_strength'].iloc[:,0]
        index_i = np.where(p_i < p_val_cutoff)[0].tolist() # the significant central nodes
        if len(index_i) > 0 :
            att = result_LR[LRs[i]]['inter_att']
            # return the top k positions for each significant cells
            for j in range(len(index_i)):
                row_np = nei_adj[index_i[j],:]
                data_np = att.iloc[index_i[j],:]
                sorted_idj = np.argsort( -data_np )[:k]# from large to small
                tmp_idj = row_np[ sorted_idj ]# top k senders
                sample_name = p_i.index.tolist()[index_i[j]]
                pscore = p_i[index_i[j]]
                interccc = s_i[index_i[j]]
                sender = tmp_idj
                sample_lst.append(sample_name)
                interccc_lst.append(interccc)
                pscore_lst.append(pscore)
                sender_lst.append(sender)
                sender_x_lst.append(coord.iloc[sender]['x'])
                sender_y_lst.append(coord.iloc[sender]['y'])
                receiver_x_lst.append(coord.iloc[index_i[j]]['x'])
                receiver_y_lst.append(coord.iloc[index_i[j]]['y'])
    res_df = pd.DataFrame({
        'Sample_Name': sample_lst,
        'Inter_Score': interccc_lst,
        'P_Score': pscore_lst,
        'Sender': sender_lst,
        'Sender_x': sender_x_lst,
        'Sender_y': sender_y_lst,
        'Receiver_x': receiver_x_lst,
        'Receiver_y': receiver_y_lst
    })
    return res_df
