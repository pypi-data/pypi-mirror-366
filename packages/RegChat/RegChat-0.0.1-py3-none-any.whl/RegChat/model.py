import math
import torch
import itertools
import random
import scipy.sparse
import anndata as ad
import numpy as np
import scanpy as sc
import pandas as pd
import torch.nn as nn
from scipy import sparse
import torch.optim as optim
import torch.nn.functional as F
from torch_geometric.nn import GATConv
from torch.nn.parameter import Parameter
from torch.nn.modules.module import Module
from typing import List, Optional, Union, Any
from collections import OrderedDict

from .utils import get_lr_data, get_average_lr,get_cell_type_pairs,get_nich_score,get_neig_index,get_cell_positive_pairs,get_regchat_result_LR,get_regchat_result_LRFG,get_regchat_result_LG, get_regchat_result_LR_inter, get_LGs,compute_C,compute_C_fast, z_score_2d,permutation_adj,permutation_adj_full


class Discriminator_inter(nn.Module):
    def __init__(self, n_h):
        super(Discriminator_inter, self).__init__()
        self.f_k = nn.Bilinear(n_h, n_h, 1)

        for m in self.modules():
            self.weights_init(m)

    def weights_init(self, m):
        if isinstance(m, nn.Bilinear):
            torch.nn.init.xavier_uniform_(m.weight.data)
            if m.bias is not None:
                m.bias.data.fill_(0.0)

    def forward(self, c, h_pl, h_mi, s_bias1=None, s_bias2=None):
        c_x = c.expand_as(h_pl)  

        sc_1 = self.f_k(h_pl, c_x)
        sc_2 = self.f_k(h_mi, c_x)

        if s_bias1 is not None:
            sc_1 += s_bias1
        if s_bias2 is not None:
            sc_2 += s_bias2

        logits = torch.cat((sc_1, sc_2), 1)

        return logits


class Discriminator_intra(nn.Module):
    def __init__(self, n_h):
        super(Discriminator_intra, self).__init__()
        self.f_k = nn.Bilinear(n_h, n_h, 1)

        for m in self.modules():
            self.weights_init(m)

    def weights_init(self, m):
        if isinstance(m, nn.Bilinear):
            torch.nn.init.xavier_uniform_(m.weight.data)
            if m.bias is not None:
                m.bias.data.fill_(0.0)

    def forward(self, c, h_pl, h_mi, s_bias1=None, s_bias2=None):
        c_x = c.expand_as(h_pl)  

        sc_1 = self.f_k(h_pl, c_x)
        sc_2 = self.f_k(h_mi, c_x)

        if s_bias1 is not None:
            sc_1 += s_bias1
        if s_bias2 is not None:
            sc_2 += s_bias2

        logits = torch.cat((sc_1, sc_2), 1)

        return logits


class Discriminator(nn.Module):
    def __init__(self, n_h):
        super(Discriminator, self).__init__()
        self.f_k = nn.Bilinear(n_h, n_h, 1)

        for m in self.modules():
            self.weights_init(m)

    def weights_init(self, m):
        if isinstance(m, nn.Bilinear):
            torch.nn.init.xavier_uniform_(m.weight.data)
            if m.bias is not None:
                m.bias.data.fill_(0.0)

    def forward(self,c, h_pl, h_mi, s_bias1=None, s_bias2=None):
        c_x = c.expand_as(h_pl)  

        sc_1 = self.f_k(h_pl, c_x)
        sc_2 = self.f_k(h_mi, c_x)

        if s_bias1 is not None:
            sc_1 += s_bias1
        if s_bias2 is not None:
            sc_2 += s_bias2

        logits = torch.cat((sc_1, sc_2), 1)

        return logits
    

class Contrast_single(nn.Module):
	def __init__(self, hidden_dim, tau):
		super(Contrast_single, self).__init__()
		
		self.tau = tau

	def sim(self, z):
		z_norm = torch.norm(z, dim=-1, keepdim=True)
		dot_numerator   = torch.mm(z, z.t())
		dot_denominator = torch.mm(z_norm, z_norm.t())
		sim_matrix = torch.exp(dot_numerator / dot_denominator / self.tau)
		return sim_matrix

	def forward(self, z, pos):
		matrix  = self.sim(z)
		matrix  = matrix/(torch.sum(matrix, dim=1).view(-1, 1) + 1e-8)
		lori = -torch.log(matrix.mul(pos).sum(dim=-1)).mean()

		return lori    

def label_to_int(adata):
    adata_label_o = np.array(adata.obs['cell_type'].copy())
    label_list = list(set(adata.obs['cell_type'].tolist()))
    adata_label = adata_label_o.copy()
    for i in range(len(label_list)):
        need_index = np.where(adata.obs['cell_type']==label_list[i])[0]
        if len(need_index):
            adata_label[need_index] = i
    adata.obs['ref'] = adata_label
    return adata

    
class LabelPredictor(nn.Module):
    def __init__(self, hidden_features, class_features):
        super(LabelPredictor, self).__init__()

        self.layer = nn.Sequential(
            nn.Linear(hidden_features, hidden_features),
            nn.ReLU(),
            
            #nn.Linear(hidden_features, hidden_features),
            #nn.ReLU(),

            nn.Linear(hidden_features, class_features)
        )

    def forward(self, h):
        c = self.layer(h)
        return c



class intra_att_LR(nn.Module):
    def __init__(self, hidden_dim, attn_drop):
        super(intra_att_LR, self).__init__()
        self.att_inter = nn.Parameter(torch.empty(size=(1, 2*hidden_dim)), requires_grad=True)
        self.att_intra = nn.Parameter(torch.empty(size=(1, 2*hidden_dim)), requires_grad=True)
        nn.init.xavier_normal_(self.att_inter.data, gain=1.414)# Initialization
        nn.init.xavier_normal_(self.att_intra.data, gain=1.414)# Initialization
        if attn_drop:
            self.attn_drop = nn.Dropout(attn_drop)
        else:
            self.attn_drop = lambda x: x
			
        self.softmax = nn.Softmax(dim=1)
        self.leakyrelu = nn.LeakyReLU()

        self.map_l = nn.Linear(1, hidden_dim, bias=True)# transform ligand
        nn.init.uniform_(self.map_l.weight, a=0, b=1)
        nn.init.uniform_(self.map_l.bias, a=0, b=0.01)

        self.map_r = nn.Linear(1, hidden_dim, bias=True)# transform receptor
        nn.init.uniform_(self.map_r.weight, a=0, b=1)
        nn.init.uniform_(self.map_r.bias, a=0, b=0.01)


        self.hidden_dim = hidden_dim


    def forward(self, nei, h, h_refer):
        h = F.relu(self.map_l(h)) # ligand 
        h_refer = F.relu(self.map_r(h_refer)) # receptor
        
        
        nei_emb = F.embedding(nei, h)# Broadcast central node features to neighbor feature dimensions from ligand to receptor
        h_refer_n = torch.unsqueeze(h_refer, 1)# 
        h_refer_n = h_refer_n.expand_as(nei_emb)# 
        all_emb = torch.cat([h_refer_n, nei_emb], dim=-1)

        
        attn_inter_curr = self.attn_drop(self.att_inter)
        att_inter = self.leakyrelu(all_emb.matmul(attn_inter_curr.t()))
        att_inter = self.softmax(att_inter)
        att_inter_e = torch.squeeze(att_inter, dim=-1)
        
        lr_inner = torch.einsum('mnk,mk->mn', nei_emb, h_refer)# each element is the inner product between ligand and receptor
        nei_emb_l = F.relu((att_inter_e * lr_inner).sum(dim=1, keepdim=True))

        return nei_emb_l, att_inter_e

    def get_score_each_lr(self, nei, h, h_refer):
        h = F.relu(self.map_l(h)) # ligand 
        h_refer = F.relu(self.map_r(h_refer)) # receptor
        
        
        nei_emb = F.embedding(nei, h)# Broadcast central node features to neighbor feature dimensions from ligand to receptor
        h_refer_n = torch.unsqueeze(h_refer, 1)# 
        h_refer_n = h_refer_n.expand_as(nei_emb)# 
        all_emb = torch.cat([h_refer_n, nei_emb], dim=-1)

        
        attn_inter_curr = self.attn_drop(self.att_inter)
        att_inter = self.leakyrelu(all_emb.matmul(attn_inter_curr.t()))
        att_inter = self.softmax(att_inter)
        att_inter_e = torch.squeeze(att_inter, dim=-1)       
        lr_inner = torch.einsum('mnk,mk->mn', nei_emb, h_refer)# each element is the inner product between ligand and receptor
        score_l = F.relu(att_inter_e * lr_inner)
        nei_emb_l = F.relu((att_inter_e * lr_inner).sum(dim=1, keepdim=True)) # each node has 1
        
        return nei_emb_l.detach().cpu().numpy(), score_l.detach().cpu().numpy()



class intra_att_LRFG(nn.Module):
    def __init__(self, hidden_dim, attn_drop):
        super(intra_att_LRFG, self).__init__()
        self.att_inter = nn.Parameter(torch.empty(size=(1, 2*hidden_dim)), requires_grad=True)
        self.att_intra = nn.Parameter(torch.empty(size=(1, 2*hidden_dim)), requires_grad=True)
        nn.init.xavier_normal_(self.att_inter.data, gain=1.414)# Initialization
        nn.init.xavier_normal_(self.att_intra.data, gain=1.414)# Initialization
        if attn_drop:
            self.attn_drop = nn.Dropout(attn_drop)
        else:
            self.attn_drop = lambda x: x
			
        self.softmax = nn.Softmax(dim=1)
        self.leakyrelu = nn.LeakyReLU()

        self.map_l = nn.Linear(1, hidden_dim, bias=True)# transform ligand
        nn.init.uniform_(self.map_l.weight, a=0, b=1)
        nn.init.uniform_(self.map_l.bias, a=0, b=0.01)

        self.map_r = nn.Linear(1, hidden_dim, bias=True)# transform receptor
        nn.init.uniform_(self.map_r.weight, a=0, b=1)
        nn.init.uniform_(self.map_r.bias, a=0, b=0.01)


        self.map_g = nn.Linear(1, hidden_dim, bias=True)# transform genes
        nn.init.uniform_(self.map_g.weight, a=0, b=1)
        nn.init.uniform_(self.map_g.bias, a=0, b=0.01)
        self.hidden_dim = hidden_dim


    def forward(self, nei, h, h_refer, h_g):
        h = F.relu(self.map_l(h)) # ligand 
        h_refer = F.relu(self.map_r(h_refer)) # receptor
        # genes need to do one by one
        h_g_t = []
        for s in range(h_g.shape[1]):
            h_s = h_g[:,s].view(-1, 1)
            h_g_s = F.relu(self.map_g(h_s)) # gene
            h_g_s_n = torch.unsqueeze(h_g_s, 1)# 
            h_g_t.append(h_g_s_n)
        # combine
        h_emb_g = torch.cat(h_g_t, dim=1)
        
        
        nei_emb = F.embedding(nei, h)# Broadcast central node features to neighbor feature dimensions from ligand to receptor
        h_refer_n = torch.unsqueeze(h_refer, 1)# 
        h_refer_n = h_refer_n.expand_as(nei_emb)# 
        all_emb = torch.cat([h_refer_n, nei_emb], dim=-1)


        # Broadcast central node features to neighbor feature dimensions from receptor to genes
        h_refer_g = torch.unsqueeze(h_refer, 1)# 
        h_refer_g = h_refer_g.expand_as(h_emb_g)# 
        all_emb_g = torch.cat([h_refer_g, h_emb_g], dim=-1)

        
        attn_inter_curr = self.attn_drop(self.att_inter)
        att_inter = self.leakyrelu(all_emb.matmul(attn_inter_curr.t()))
        att_inter = self.softmax(att_inter)
        att_inter_e = torch.squeeze(att_inter, dim=-1)
        #if self.hidden_dim == 1:
        #    nei_emb = (att_inter*nei_emb).sum(dim=1)
        #    nei_emb_l = F.relu(nei_emb*h_refer)
        #else:
            #nei_emb = (nei_emb*h_refer).sum(dim=1).unsqueeze(1)
        lr_inner = torch.einsum('mnk,mk->mn', nei_emb, h_refer)# each element is the inner product between ligand and receptor
        nei_emb_l = F.relu((att_inter_e * lr_inner).sum(dim=1, keepdim=True))
    

        attn_intra_curr = self.attn_drop(self.att_intra)
        att_intra = self.leakyrelu(all_emb_g.matmul(attn_intra_curr.t()))
        att_intra = self.softmax(att_intra)
        att_intra_e = torch.squeeze(att_intra, dim=-1)
        #if self.hidden_dim == 1:
        #    nei_emb_s = att_intra*h_emb_g # dot plot to obtain each meta-path
        #    h_refer_1 = torch.unsqueeze(h_refer, 1)
        #    nei_emb_s = F.relu(nei_emb_s*h_refer_1)
        #else:
        rg_inner = torch.einsum('mnk,mk->mn', h_emb_g, h_refer)
        nei_emb_s = F.relu((att_intra_e * rg_inner).sum(dim=1, keepdim=True))

        score =  nei_emb_l * nei_emb_s
        return score, nei_emb_l, nei_emb_s, att_inter_e, att_intra_e

    def get_metapath_score_each_lr(self, nei, h, h_refer, h_g):
        h = F.relu(self.map_l(h)) # ligand 
        h_refer = F.relu(self.map_r(h_refer)) # receptor
        # genes need to do one by one
        h_g_t = []
        for s in range(h_g.shape[1]):
            h_s = h_g[:,s].view(-1, 1)
            h_g_s = F.relu(self.map_g(h_s)) # gene
            h_g_s_n = torch.unsqueeze(h_g_s, 1)# 
            h_g_t.append(h_g_s_n)
        # combine
        h_emb_g = torch.cat(h_g_t, dim=1)
        
        
        nei_emb = F.embedding(nei, h)# Broadcast central node features to neighbor feature dimensions from ligand to receptor
        h_refer_n = torch.unsqueeze(h_refer, 1)# 
        h_refer_n = h_refer_n.expand_as(nei_emb)# 
        all_emb = torch.cat([h_refer_n, nei_emb], dim=-1)


        h_refer_g = torch.unsqueeze(h_refer, 1)# 
        h_refer_g = h_refer_g.expand_as(h_emb_g)# 
        all_emb_g = torch.cat([h_refer_g, h_emb_g], dim=-1)

        
        attn_inter_curr = self.attn_drop(self.att_inter)
        att_inter = self.leakyrelu(all_emb.matmul(attn_inter_curr.t()))
        att_inter = self.softmax(att_inter)
        att_inter_e = torch.squeeze(att_inter, dim=-1)       
        lr_inner = torch.einsum('mnk,mk->mn', nei_emb, h_refer)# each element is the inner product between ligand and receptor
        score_l = F.relu(att_inter_e * lr_inner)# dotproduct
        nei_emb_l = F.relu((att_inter_e * lr_inner).sum(dim=1, keepdim=True)) # each node has 1

        attn_intra_curr = self.attn_drop(self.att_intra)
        att_intra = self.leakyrelu(all_emb_g.matmul(attn_intra_curr.t()))
        att_intra = self.softmax(att_intra)
        att_intra_e = torch.squeeze(att_intra, dim=-1)

        
        rg_inner = torch.einsum('mnk,mk->mn', h_emb_g, h_refer)
        score_g = F.relu(att_intra_e * rg_inner)#dotproduct between tf or tg with receptor        
        
        return nei_emb_l.detach().cpu().numpy(), score_l.detach().cpu().numpy(), score_g.detach().cpu().numpy()
        

class LRP_attention(nn.Module):
    def __init__(self, cci_pairs, hidden_dim, attn_drop):
        super(LRP_attention, self).__init__()
        self.intra_cci  = nn.ModuleList([intra_att_LRFG(hidden_dim, attn_drop) for _ in range(cci_pairs)]) # each lr pair has a module
        self.cci_pairs  = cci_pairs

    def forward(self, sele_nei, ligand_exp, receptor_exp, tfg_exp_l):
        
        LR_inter_embeds = []
        atten_inter_list = []
        LR_intra_embeds = []
        atten_intra_list = []
        LR_all_embeds = []
        for z in range(self.cci_pairs):
            lrs, emb_inter, emb_intra, atten_inter, atten_intra  = self.intra_cci[z](sele_nei, ligand_exp[:,z].view(-1,1), receptor_exp[:,z].view(-1,1), tfg_exp_l[z]) # for each lr pair                     
            
            LR_inter_embeds.append(emb_inter.view(1,-1))
            atten_inter_list.append(atten_inter)
            LR_intra_embeds.append(emb_intra.view(1,-1))
            atten_intra_list.append(atten_intra)
            LR_all_embeds.append(lrs.view(1,-1))
            
        
        LR_inter_embeds = torch.cat(LR_inter_embeds, dim=0)
        #LR_embeds = LR_embeds.t().cuda()
        LR_inter_embeds = LR_inter_embeds.t()
        #atten_inter_list = torch.cat(atten_inter_list, dim=1)

        LR_intra_embeds = torch.cat(LR_intra_embeds, dim=0)
        #LR_embeds = LR_embeds.t().cuda()
        LR_intra_embeds = LR_intra_embeds.t()
        #atten_intra_list = torch.cat(atten_intra_list, dim=1)

        LR_all_embeds= torch.cat(LR_all_embeds, dim=0)
        LR_all_embeds = LR_all_embeds.t()

        return LR_all_embeds, LR_inter_embeds, LR_intra_embeds, atten_inter_list, atten_intra_list

    def get_LRFG_score(self, sele_nei, ligand_exp, receptor_exp, tfg_exp_l, LRP_name, tfg_l, links_database):
        links_database['LRP'] = links_database['Ligand_Symbol']+'-'+links_database['Receptor_Symbol']
        LRFG_l = []
        LRF_l = []
        score_l_record = []
        score_g_record = []
        for z in range(self.cci_pairs):
            score_l_total_z, score_l_z, score_g_z  = self.intra_cci[z].get_metapath_score_each_lr(sele_nei, ligand_exp[:,z].view(-1,1), receptor_exp[:,z].view(-1,1), tfg_exp_l[z]) # for each lr pair           
            # build meta_path data_frame, rows are spots, columns are meta_path
            # take out focused lr pair
            index_z = links_database.index[links_database['LRP'] == LRP_name[z]].tolist()
            tf_z = links_database.iloc[index_z, links_database.columns.get_loc('TF_Symbol')].tolist()
            tg_z = links_database.iloc[index_z, links_database.columns.get_loc('TG_Symbol')].tolist()
            # take out values
            tfg_z = tfg_l[z].tolist()
            index_f = [tfg_z.index(item) if item in tfg_z else None for item in tf_z]
            index_g = [tfg_z.index(item) if item in tfg_z else None for item in tg_z]
            lrfg_score_z = score_l_total_z*(score_g_z[:,index_f]*score_g_z[:,index_g])
            lrf_score_z = score_l_total_z*score_g_z[:,index_f]
            lrfg_name_z = [f"{LRP_name[z]}-{tf_z[g]}-{tg_z[g]}" for g in range(len(tf_z))]
            lrfg_pd_z = pd.DataFrame(lrfg_score_z, columns = lrfg_name_z)
            lrf_pd_z = pd.DataFrame(lrf_score_z, columns = lrfg_name_z)
            LRFG_l.append(lrfg_pd_z)
            LRF_l.append(lrf_pd_z)
            score_l_record.append(score_l_z)
            score_g_record.append(score_g_z)
        LRFG_score = pd.concat(LRFG_l, axis=1)
        LRF_score = pd.concat(LRF_l, axis=1)
        return LRFG_score, LRF_score, score_l_record, score_g_record            


class CCI_model(nn.Module):
    def __init__(self, cci_pairs, hidden_dim, attn_drop, layer_hidden, class_layer, tau): # by default: hidden_dim = 1
        super(CCI_model, self).__init__()
        self.LRP_attention = LRP_attention(cci_pairs, hidden_dim, attn_drop)
        self.enco_latent = nn.Linear(cci_pairs, layer_hidden, bias=False) # LRP embedding
        self.contrast_inter = Discriminator_inter(layer_hidden)
        self.contrast_intra = Discriminator_intra(layer_hidden)
        self.contrast = Discriminator(layer_hidden)
        self.contrast_s = Contrast_single(hidden_dim, tau)
        self.sigm = nn.Sigmoid()
        self.clasf = LabelPredictor(layer_hidden, class_layer)     
        
    def forward(self, nei_adj,label,ligand_exp, receptor_exp, tfg_exp_l, nei_adj_permut, ligand_exp_permut, receptor_exp_permut, tfg_exp_l_permut,indices,lamb_1,lamb_2,lamb_3,pos,mode,no_label, no_spatial):

        embeds_all,embeds_inter,embeds_intra,atten_inter_list,atten_intra_list = self.LRP_attention(nei_adj, ligand_exp, receptor_exp, tfg_exp_l)
        h = self.enco_latent(embeds_all)
        
        if not no_label:
            # classification
            h_con = h[indices,:]
            label_con = label[indices]
            class_criterion = nn.CrossEntropyLoss()
            class_logits = self.clasf(h_con)
            loss_c = class_criterion(class_logits, label_con.long())
        else:
            loss_c = 0
        
        if mode == 'fast':
            loss_con = self.contrast_s(h, pos)
            return loss_c, loss_con, h, embeds_all, atten_inter_list, atten_intra_list
            
        else:
            # run on permutated inter samples
            embeds_all_1,embeds_inter_1,embeds_intra_1,_,_ = self.LRP_attention(nei_adj_permut, ligand_exp, receptor_exp, tfg_exp_l)
            # run on permutated intra samples, fix receptors, but change tfg_exp_l
            embeds_all_2,embeds_inter_2,embeds_intra_2,_,_ = self.LRP_attention(nei_adj, ligand_exp, receptor_exp, tfg_exp_l_permut)
            # negative sample
            embeds_all_3,embeds_inter_3,embeds_intra_3,_,_ = self.LRP_attention(nei_adj, ligand_exp_permut, receptor_exp_permut, tfg_exp_l_permut)
        
        
            h1 = self.enco_latent(embeds_all_1)
            h2 = self.enco_latent(embeds_all_2)
            h3 = self.enco_latent(embeds_all_3)

        

            # build local summary vectors
            nei_emb_h = F.embedding(nei_adj, h)
            g = torch.mean(nei_emb_h, dim=1)
            g = self.sigm(g)  

            ret_1 = self.contrast_inter(g, h, h1)  
            ret_2 = self.contrast_intra(g, h, h2)
            ret_3 = self.contrast(g, h, h3)


            ret_CSL = torch.from_numpy(np.concatenate([np.ones([ligand_exp.shape[0], 1]), np.zeros([ligand_exp.shape[0], 1])], axis=1))
            loss_CSL = nn.BCEWithLogitsLoss()               
            loss_1 = loss_CSL(ret_1, ret_CSL)
            loss_2 = loss_CSL(ret_2, ret_CSL)
            loss_3 = loss_CSL(ret_3, ret_CSL)
            loss_con = lamb_1*loss_1+lamb_2*loss_2+lamb_3*loss_3
            
            return loss_c, loss_con,h,embeds_all, embeds_all_3,atten_inter_list, atten_intra_list
    
    def get_metapath_score(self, nei_adj, ligand_exp, receptor_exp, tfg_exp_l, LRP_name, tfg_l,links_database):
        LRFG_score,LRF_score, score_l_record, score_g_record = self.LRP_attention.get_LRFG_score(nei_adj, ligand_exp, receptor_exp, tfg_exp_l, LRP_name, tfg_l, links_database)
        return LRFG_score,LRF_score,score_l_record, score_g_record



class LRP_attention_no_intra(nn.Module):
    def __init__(self, cci_pairs, hidden_dim, attn_drop):
        super(LRP_attention_no_intra, self).__init__()
        self.intra_cci  = nn.ModuleList([intra_att_LR(hidden_dim, attn_drop) for _ in range(cci_pairs)]) # each lr pair has a module
        self.cci_pairs  = cci_pairs

    def forward(self, sele_nei, ligand_exp, receptor_exp):
        LR_inter_embeds = []
        atten_inter_list = []
        
        for z in range(self.cci_pairs):
            emb_inter, atten_inter  = self.intra_cci[z](sele_nei, ligand_exp[:,z].view(-1,1), receptor_exp[:,z].view(-1,1)) # for each lr pair                     
            LR_inter_embeds.append(emb_inter.view(1,-1))
            atten_inter_list.append(atten_inter)
            
        LR_inter_embeds = torch.cat(LR_inter_embeds, dim=0)
        #LR_embeds = LR_embeds.t().cuda()
        LR_inter_embeds = LR_inter_embeds.t()
        #atten_inter_list = torch.cat(atten_inter_list, dim=1)

        return LR_inter_embeds, atten_inter_list


class CCI_model_no_intra(nn.Module):
    def __init__(self, cci_pairs, hidden_dim, attn_drop, layer_hidden, class_layer, tau): # by default: hidden_dim = 1
        super(CCI_model_no_intra, self).__init__()
        self.LRP_attention = LRP_attention_no_intra(cci_pairs, hidden_dim, attn_drop)
        self.enco_latent = nn.Linear(cci_pairs, layer_hidden, bias=False) # LRP embedding
        self.contrast_inter = Discriminator_inter(layer_hidden)
        self.contrast_intra = Discriminator_intra(layer_hidden)
        self.contrast = Discriminator(layer_hidden)
        self.contrast_s = Contrast_single(hidden_dim, tau)
        self.sigm = nn.Sigmoid()
        self.clasf = LabelPredictor(layer_hidden, class_layer)     
        
    def forward(self, nei_adj,label,ligand_exp, receptor_exp, nei_adj_permut, ligand_exp_permut, receptor_exp_permut, indices,lamb_1,lamb_2,pos,mode,no_label, no_spatial):

        embeds_inter,atten_inter_list = self.LRP_attention(nei_adj, ligand_exp, receptor_exp)
        h = self.enco_latent(embeds_inter)
        if not no_label:
            # classification
            h_con = h[indices,:]
            label_con = label[indices]
            class_criterion = nn.CrossEntropyLoss()
            class_logits = self.clasf(h_con)
            loss_c = class_criterion(class_logits, label_con.long())
        else:
            loss_c = 0
        
        if mode == 'fast':
            loss_con = self.contrast_s(h, pos)
            return loss_c, loss_con, embeds_inter,atten_inter_list
                       
        else:
            # run on permutated inter samples
            embeds_inter_1,_ = self.LRP_attention(nei_adj_permut, ligand_exp, receptor_exp)
            # negative sample
            embeds_inter_2,_ = self.LRP_attention(nei_adj, ligand_exp_permut, receptor_exp_permut)
        
        
            h1 = self.enco_latent(embeds_inter_1)
            h2 = self.enco_latent(embeds_inter_2)
            
            # build local summary vectors
            nei_emb_h = F.embedding(nei_adj, h)
            g = torch.mean(nei_emb_h, dim=1)
            g = self.sigm(g)  

            ret_1 = self.contrast_inter(g, h, h1)  
            ret_2 = self.contrast(g, h, h2)

            ret_CSL = torch.from_numpy(np.concatenate([np.ones([ligand_exp.shape[0], 1]), np.zeros([ligand_exp.shape[0], 1])], axis=1))
            loss_CSL = nn.BCEWithLogitsLoss()               
            loss_1 = loss_CSL(ret_1, ret_CSL)
            loss_2 = loss_CSL(ret_2, ret_CSL)
            loss_con = lamb_1*loss_1+lamb_2*loss_2
            
            return loss_c, loss_con, embeds_inter,embeds_inter_2, atten_inter_list



def Train_CCC_model_no_intra(adata_rna, links_database, gene_cell_pd, spot_loc, hidden_dim, attn_drop, layers_hidden, tau, locMeasure = 'euclidean',lamb_1 = 1, lamb_2 = 1, lamb_3 = 1, mode = 'fast', no_label = False, no_spatial = False, neig_number = 10, pure_cutoff = 0.2, sub_epochs = 200, per_num_cut = 1, epochs = 1000, lr = 0.001, weight_decay=0, use_cuda = 0):
    '''
      Args:
        adata_rna: the adata for RNA
        in_dim: the input feature dimension used in the model
        out_dim: the dimesion of latent embeddings (default: 50)
        gamma: hyperparameter (default:0.1)
        label_name: the column in adata, which is used to store the cell type information
        lr: learning rate
        epochs: the number of iterations
        
    '''
    nei_adj = get_neig_index(spot_loc, locMeasure, neig_number) # obtain the adj of each data
    if no_spatial:
        nei_adj = permutation_adj_full(nei_adj)
    type_record, _ = get_cell_type_pairs(adata_rna, nei_adj,label = None)
    if not no_label:
        scores = get_nich_score(type_record) # entropy for each node
        # get index of pure nodes
        indices = np.where(scores < pure_cutoff)[1] # use this indices to classifier
        if len(indices) < 5:
            no_label = True
    else:
        indices = None
        
    # get ligand and receptor data
    spots_ligand_pd, spots_recep_pd,LRP_name = get_lr_data_no_tfg(links_database, gene_cell_pd)
    spots_ligand_pd, spots_recep_pd = get_average_lr(nei_adj, spots_ligand_pd, spots_recep_pd)# smooth
    
    
    spots_ligand = torch.FloatTensor(spots_ligand_pd.values)
    spots_recep = torch.FloatTensor(spots_recep_pd.values)
    nei_adj_permut = permutation_adj(nei_adj)# feature is fixed, but around neighbors changed
    gene_cell_pd_permut = gene_cell_pd.sample(frac=1, axis=1) 
    spots_ligand_pd_permut, spots_recep_pd_permut,_ = get_lr_data_no_tfg(links_database, gene_cell_pd_permut)    

    spots_ligand_permut = torch.FloatTensor(spots_ligand_pd_permut.values)
    spots_recep_permut = torch.FloatTensor(spots_recep_pd_permut.values)
    per_num = 1
    cellName = spots_ligand_pd.index
    
    pos = get_cell_positive_pairs(adata_rna, spot_loc,neig_number,nei_adj,no_spatial)
    pos = torch.FloatTensor(pos.values)
    cci_pairs = spots_ligand.size(1)
    print('Size of CCC pairs: ' + str(cci_pairs))
    
    label = torch.tensor(adata_rna.obs['ref'].to_numpy().astype(int))
    n_class = len(set(list(label.numpy())))
    
    model = CCI_model_no_intra(cci_pairs, hidden_dim, attn_drop, layers_hidden, n_class, tau) # layers is [args.cci_pairs, 100]
    optim = torch.optim.Adam(model.parameters(), lr = lr, weight_decay = weight_decay)
    print('Start model training')
    if use_cuda:
        model.cuda()
        nei_adj = nei_adj.cuda()
        spots_ligand = spots_ligand.cuda()
        spots_recep = spots_recep.cuda()
        pos = pos.cuda()

    cnt_wait = 0
    best = 1e9
    best_t = 0
    rela_loss = 1000
    starttime = datetime.datetime.now()
    train_loss_list = []
    CCI_combined_list = []
    for epoch in range(epochs):
        model.train()
        optim.zero_grad()

        if epoch <= sub_epochs:
            mode = 'fast'
            loss_c,loss_con,LR_inter_activity, atten_inter_list= model(nei_adj, label, spots_ligand, spots_recep, nei_adj_permut, spots_ligand_permut, spots_recep_permut, indices,lamb_1,lamb_2,pos,mode,no_label, no_spatial)
        else:
            mode = 'discriminator'
            loss_c,loss_con,LR_inter_activity, LR_inter_activity_2, atten_inter_list= model(nei_adj, label, spots_ligand, spots_recep, nei_adj_permut, spots_ligand_permut, spots_recep_permut, indices,lamb_1,lamb_2,pos,mode,no_label, no_spatial)
        
        cost = loss_c+loss_con
        train_loss_list.append(cost)
        if (epoch % 10 == 0) and (len(train_loss_list) >= 2):
            print( str(epoch) + " cost: " + str(cost.data.cpu()) + " " + "relative decrease ratio: "+ str(abs(train_loss_list[-1] - train_loss_list[-2]) / train_loss_list[-2]).data.cpu())

        if epoch > sub_epochs:
            # permute
            nei_adj_permut = permutation_adj(nei_adj)# feature is fixed, but around neighbors changed
            spots_ligand_pd_permut, spots_recep_pd_permut,  _ = get_lr_data_no_tfg(links_database, gene_cell_pd_permut)
            spots_ligand_permut = torch.FloatTensor(spots_ligand_pd_permut.values)
            spots_recep_permut = torch.FloatTensor(spots_recep_pd_permut.values)
            
            per_num = per_num + 1
            if (epoch % 10 == 0) and per_num > 1:
                # restore background scores
                # concat all the values
                if LR_inter_activity_2 is not None:
                    CCI_combined_list.append(LR_inter_activity_2.data.cpu())
                print(len(CCI_combined_list))
                
                if per_num_cut is not None:
                    if per_num >= per_num_cut:
                        print( epoch )
                        break
                        
                if per_num > np.floor(100000/len(label)):
                    print( epoch )
                    break

        cost.backward()
        optim.step()

    model.eval()
    endtime = datetime.datetime.now()
    time = (endtime - starttime).seconds
    print("Total time: ", time, "s")
    #torch.save(model.state_dict(), args.outPath + 'CCC_module.pkl')
    #_,_,LR_inter_activity, LR_inter_activity_2, atten_inter_list= model(nei_adj, label, spots_ligand, spots_recep, nei_adj_permut, spots_ligand_permut, spots_recep_permut, indices,lamb_1,lamb_2,pos,mode,no_label, no_spatial)    
    LR_inter_activity_pd = pd.DataFrame(data=LR_inter_activity.data.cpu().numpy(), index = cellName.tolist(), columns = LRP_name)
    # test the significant CCCs
    # combined the recorded CCI combined
    if len(CCI_combined_list) > 1:
        CCI_combined_all = torch.cat(CCI_combined_list, dim=0)
    else:
        CCI_combined_all = LR_inter_activity_2.data.cpu()
    # compute z-score transformation of the data
    _, CCI_mean, CCI_std  = z_score_2d(CCI_combined_all.numpy())   
    # return scores for each value 1-samll number ratio    
    CCI_strength = np.zeros((LR_inter_activity.data.cpu().numpy().shape[0],LR_inter_activity.data.cpu().numpy().shape[1]))
    n_total = CCI_combined_all.numpy().shape[0]*CCI_combined_all.numpy().shape[1]
    for p in range(LR_inter_activity.data.cpu().numpy().shape[0]):
        for q in range(LR_inter_activity.data.cpu().numpy().shape[1]):
            CCI_strength[p,q] = 1- np.sum(CCI_combined_all.numpy() < LR_inter_activity.data.cpu().numpy()[p,q])/n_total
                
    CCI_strength_pd = pd.DataFrame(data=CCI_strength, index = cellName.tolist(), columns = LRP_name)
    
    result_LR = get_regchat_result_LR_inter(LR_inter_activity_pd, CCI_strength_pd, atten_inter_list)
    return result_LR, LR_inter_activity_pd, CCI_strength_pd, CCI_mean,CCI_std,nei_adj


def Train_CCC_model(adata_rna, links_database, gene_cell_pd, spot_loc, hidden_dim, attn_drop, layers_hidden, tau, locMeasure = 'euclidean',lamb_1 = 1, lamb_2 = 1, lamb_3 = 1, mode = 'fast', no_label = False, no_spatial = False, neig_number = 10, pure_cutoff = 0.2, sub_epochs = 200, per_num_cut = 1, epochs = 1000, lr = 0.001, weight_decay=0, use_cuda = 0):
    '''
      Args:
        adata_rna: the adata for RNA
        in_dim: the input feature dimension used in the model
        out_dim: the dimesion of latent embeddings (default: 50)
        gamma: hyperparameter (default:0.1)
        label_name: the column in adata, which is used to store the cell type information
        lr: learning rate
        epochs: the number of iterations
        
    '''
    nei_adj = get_neig_index(spot_loc, locMeasure, neig_number) # obtain the adj of each data
    
    if no_spatial:
        nei_adj = permutation_adj_full(nei_adj)
    type_record, _ = get_cell_type_pairs(adata_rna, nei_adj,label = None)
    
    if not no_label:
        scores = get_nich_score(type_record) # entropy for each node
        # get index of pure nodes
        indices = np.where(scores < pure_cutoff)[1] # use this indices to classifier
        if len(indices) < 5:
            no_label = True
    else:
        indices = None
            
    # get ligand and receptor data
    spots_ligand_pd, spots_recep_pd, tfg_pd_l, LRP_name = get_lr_data(links_database, gene_cell_pd)
    spots_ligand_pd, spots_recep_pd = get_average_lr(nei_adj, spots_ligand_pd, spots_recep_pd)# smooth
    cellName = spots_ligand_pd.index
       
    spots_ligand = torch.FloatTensor(spots_ligand_pd.values)
    spots_recep = torch.FloatTensor(spots_recep_pd.values)
    del spots_ligand_pd, spots_recep_pd

    nei_adj_permut = permutation_adj(nei_adj)# feature is fixed, but around neighbors changed
    gene_cell_pd_permut = gene_cell_pd.sample(frac=1, axis=1) 
    spots_ligand_pd_permut, spots_recep_pd_permut, tfg_pd_l_permut,_ = get_lr_data(links_database, gene_cell_pd_permut)    

    spots_ligand_permut = torch.FloatTensor(spots_ligand_pd_permut.values)
    spots_recep_permut = torch.FloatTensor(spots_recep_pd_permut.values)
    per_num = 1
    spots_tfg_l = []
    spots_tfg_l_permut = []
    tfg_l = []
    for i in range(len(tfg_pd_l)):
        spots_tfg_l.append(torch.FloatTensor(tfg_pd_l[i].values))
        tfg_l.append(tfg_pd_l[i].columns)
        spots_tfg_l_permut.append(torch.FloatTensor(tfg_pd_l_permut[i].values))
    del tfg_pd_l, tfg_pd_l_permut

    pos = get_cell_positive_pairs(adata_rna, spot_loc,neig_number,nei_adj,no_spatial)
    pos = torch.FloatTensor(pos.values)
    cci_pairs = spots_ligand.size(1)
    print('Size of CCC pairs: ' + str(cci_pairs))
    
    label = torch.tensor(adata_rna.obs['ref'].to_numpy().astype(int))
    n_class = len(set(list(label.numpy())))
    
    model = CCI_model(cci_pairs, hidden_dim, attn_drop, layers_hidden, n_class, tau) # layers is [args.cci_pairs, 100]
    optim = torch.optim.Adam(model.parameters(), lr = lr, weight_decay = weight_decay)
    print('Start model training')
    if use_cuda:
        model.cuda()
        nei_adj = nei_adj.cuda()
        spots_ligand = spots_ligand.cuda()
        spots_recep = spots_recep.cuda()
        pos = pos.cuda()

    cnt_wait = 0
    best = 1e9
    best_t = 0
    rela_loss = 1000
    starttime = datetime.datetime.now()
    train_loss_list = []
    CCI_combined_list = []# focused on LRs
    LRFG_combined_list = []# focused on LRFG
    LRF_combined_list = []# focused on LRF
    LG_combined_list = []# focused LG
    for epoch in range(epochs):
        model.train()
        optim.zero_grad()

        if epoch <= sub_epochs:
            mode = 'fast'
            loss_c, loss_con,h,CCI_activity, atten_inter_list, atten_intra_list= model(nei_adj, label, spots_ligand, spots_recep, spots_tfg_l, nei_adj_permut, spots_ligand_permut, spots_recep_permut, spots_tfg_l_permut,indices,lamb_1,lamb_2,lamb_3,pos,mode,no_label, no_spatial)

        else:
            mode = 'discriminator'
            loss_c, loss_con,h,CCI_activity, CCI_activity_3, atten_inter_list, atten_intra_list= model(nei_adj, label, spots_ligand, spots_recep, spots_tfg_l, nei_adj_permut, spots_ligand_permut, spots_recep_permut, spots_tfg_l_permut,indices,lamb_1,lamb_2,lamb_3,pos,mode,no_label, no_spatial)
        if no_label:
            cost = loss_con
        else:
            cost = loss_c + loss_con
            
        train_loss_list.append(cost)

        if (epoch % 10 == 0) and (len(train_loss_list) >= 2):
            print( str(epoch) + " cost: " + str(cost.data.cpu()) + " " + "relative decrease ratio: "+ str(abs(train_loss_list[-1] - train_loss_list[-2]) / train_loss_list[-2]).data.cpu())

        if epoch > sub_epochs:
            # permute
            nei_adj_permut = permutation_adj(nei_adj)# feature is fixed, but around neighbors changed
            gene_cell_pd_permut = gene_cell_pd.sample(frac=1, axis=1) 
            spots_ligand_pd_permut, spots_recep_pd_permut, tfg_pd_l_permut,_ = get_lr_data(links_database, gene_cell_pd_permut)
            spots_ligand_permut = torch.FloatTensor(spots_ligand_pd_permut.values)
            spots_recep_permut = torch.FloatTensor(spots_recep_pd_permut.values)
            spots_tfg_l_permut = []
            for i in range(len(tfg_pd_l_permut)):
                spots_tfg_l_permut.append(torch.FloatTensor(tfg_pd_l_permut[i].values))
            del tfg_pd_l_permut
            per_num = per_num + 1
            if (epoch % 10 == 0) and per_num > 1:
                if CCI_activity_3 is not None:
                    CCI_combined_list.append(CCI_activity_3.data.cpu())
                del CCI_activity_3
                if mode == 'discriminator':
                    LRFG_score_pd_per,_,_,_ = model.get_metapath_score(nei_adj, spots_ligand_permut, spots_recep_permut, spots_tfg_l_permut, LRP_name, tfg_l, links_database)
                    LRFG_combined_list.append(LRFG_score_pd_per.values)
                    LG_score_pd_per = get_LGs(signaling_pathway, LRFG_score_pd_per)
                    LG_combined_list.append(LG_score_pd_per.values)
                    del LRFG_score_pd_per, LG_score_pd_per
                    if per_num_cut is not None:
                        if per_num >= per_num_cut:
                            print( epoch )
                            break
                    elif per_num > np.floor(100000/len(label)):
                        print( epoch )
                        break

        cost.backward()
        optim.step()

    #model.eval()
    endtime = datetime.datetime.now()
    time = (endtime - starttime).seconds
    print("Total time: ", time, "s")

    #torch.save(model.state_dict(), args.outPath + 'CCC_module.pkl')

    LRFG_score_pd,LRF_score_pd,score_l_record, score_g_record = model.get_metapath_score(nei_adj, spots_ligand, spots_recep, spots_tfg_l, LRP_name, tfg_l, links_database)
    LRFG_score_pd.index = cellName.tolist()
    LRF_score_pd.index = cellName.tolist()
    CCI_score_pd = pd.DataFrame(data=CCI_activity.data.cpu().numpy(), index = cellName.tolist(), columns = LRP_name)
    LG_score_pd = get_LGs(signaling_pathway, LRFG_score_pd)
    if len(CCI_combined_list) > 1:
        print(len(CCI_combined_list))
        CCI_combined_all = torch.cat(CCI_combined_list, dim=0)    
    else:
        CCI_combined_all = CCI_combined_list[0]
    del CCI_combined_list
    if mode == 'discriminator':
        LRFG_combined_all = np.hstack(LRFG_combined_list)
        # LGs
        LG_combined_all = np.hstack(LG_combined_list)
    del LRFG_combined_list, LG_combined_list       
    # compute z-score transformation of the data
    _, CCI_mean, CCI_std  = z_score_2d(CCI_combined_all.numpy())
    _, LRFG_mean, LRFG_std  = z_score_2d(LRFG_combined_all)
    _, LG_mean, LG_std  = z_score_2d(LG_combined_all)
    # return scores for each value 1-samll number ratio    CCI_strength = np.zeros((CCI_activity.data.cpu().numpy().shape[0],CCI_activity.data.cpu().numpy().shape[1]))
    LRFG_strength = np.zeros((LRFG_score_pd.values.shape[0],LRFG_score_pd.values.shape[1]))
    LG_strength = np.zeros((LG_score_pd.values.shape[0],LG_score_pd.values.shape[1]))
    
    if (CCI_combined_all.numpy().size < 10000):
        CCI_strength = compute_C(CCI_activity.data.cpu().numpy(),CCI_combined_all.numpy())
    else:
        CCI_strength = compute_C_fast(CCI_activity.data.cpu().numpy(),CCI_combined_all.numpy())
    if LRFG_combined_all.size < 10000:
        LRFG_strength = compute_C(LRFG_score_pd.values,LRFG_combined_all)
    else:
        LRFG_strength = compute_C_fast(LRFG_score_pd.values,LRFG_combined_all)
    if LG_combined_all.size < 10000:
        LG_strength = compute_C(LG_score_pd.values,LG_combined_all)
    else:
        LG_strength = compute_C_fast(LG_score_pd.values,LG_combined_all)  
        

    CCI_strength_pd = pd.DataFrame(data=CCI_strength, index = cellName.tolist(), columns = LRP_name)
    LRFG_strength_pd = pd.DataFrame(data=LRFG_strength, index = cellName.tolist(), columns = LRFG_score_pd.columns)
    LG_strength_pd = pd.DataFrame(data=LG_strength, index = cellName.tolist(), columns = LG_score_pd.columns)
    result_LR = get_regchat_result_LR(CCI_score_pd, CCI_strength_pd, atten_inter_list, atten_intra_list,tfg_l)
    result_LRFG = get_regchat_result_LRFG(LRFG_score_pd, LRFG_strength_pd) 
    result_LG = get_regchat_result_LG(LG_score_pd, LG_strength_pd)
    H = h.data.cpu().numpy()
    return result_LR, result_LRFG, result_LG, H, score_l_record, score_g_record,tfg_l, CCI_strength_pd, LRFG_strength_pd, LG_strength_pd, CCI_score_pd, LRFG_score_pd,LRF_score_pd, LG_score_pd, nei_adj 
