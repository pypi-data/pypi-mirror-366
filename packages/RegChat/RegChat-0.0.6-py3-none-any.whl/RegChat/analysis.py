import numpy as np
import scanpy as sc
import anndata as ad
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import f1_score
import matplotlib.pyplot as plt 
from matplotlib.collections import LineCollection
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, ArrowStyle


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

def plot_communication_double_panel(
    strength_df,          # DataFrame (x,y,Comm_Score)
    coord_df,             # DataFrame (x,y,color)
    res_weighted_df,      # DataFrame
    color_map,            # 
    pathway_name,         # 
    strength_scale=10,    # 
    arrow_rad=0.2,        # 
    point_size=80         # 
):
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, constrained_layout=True)
    
    # ---
    scatter1 = ax1.scatter(
        strength_df['x'], strength_df['y'], 
        c=strength_df['Comm_Score'],
        cmap='viridis', 
        s=point_size, 
        linewidths=0
    )
    
    # 
    for _, row in res_weighted_df.iterrows():
        strength = row['Comm_Score']
        lw = max(0.5, strength * strength_scale)
        arrowstyle = ArrowStyle("Simple", head_length=1, head_width=1.5, tail_width=0.1)
        arrow = FancyArrowPatch(
            (row['Sender_x'], row['Sender_y']),
            (row['Receiver_x'], row['Receiver_y']),
            connectionstyle=f"arc3,rad={arrow_rad}", 
            arrowstyle=arrowstyle, 
            color='black', 
            lw=lw,
            mutation_scale=10
        )
        ax1.add_patch(arrow)
    
    ax1.set_title('Communication Strength Background')
    fig.colorbar(scatter1, ax=ax1, label='Intensity')
    
    # -- ---
    scatter2 = ax2.scatter(
        coord_df['x'], coord_df['y'],
        c=coord_df['color'], 
        alpha=0.9, 
        s=point_size, 
        linewidths=0
    )
    
    # 
    for _, row in res_weighted_df.iterrows():
        strength = row['Comm_Score']
        lw = max(0.5, strength * strength_scale)
        arrowstyle = ArrowStyle("Simple", head_length=1, head_width=1.5, tail_width=0.1)
        arrow = FancyArrowPatch(
            (row['Sender_x'], row['Sender_y']),
            (row['Receiver_x'], row['Receiver_y']),
            connectionstyle=f"arc3,rad={arrow_rad}", 
            arrowstyle=arrowstyle,
            color='black', 
            lw=lw,
            mutation_scale=10
        )
        ax2.add_patch(arrow)
    
    # 
    handles = [
        plt.Line2D(
            [0], [0], 
            marker='o', 
            color='w', 
            label=celltype, 
            markerfacecolor=color, 
            markersize=10
        ) for celltype, color in color_map.items()
    ]
    ax2.legend(
        handles=handles, 
        title='Cell Types', 
        bbox_to_anchor=(1.15, 1), 
        loc='upper right'
    )
    ax2.set_title('Cell Type Communication')
    
    #
    plt.suptitle(f'Communication Direction under: {pathway_name}', y=1.02)
    
    # 
    pathway_name_new = pathway_name.replace('->', '_')
    filename_base = f'Combined_plot_{pathway_name_new}'
    
    # 
    #plt.savefig(f"{figpath}{filename_base}.png", dpi=dpi, bbox_inches=bbox_inches)
    #plt.savefig(f"{figpath}{filename_base}.pdf", bbox_inches=bbox_inches)
    
    plt.show()
    plt.close()
