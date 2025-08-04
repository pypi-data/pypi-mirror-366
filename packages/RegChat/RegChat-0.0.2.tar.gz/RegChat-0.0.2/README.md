# ![RegChat](https://github.com/lhzhanglabtools/RegChat/blob/main/RegChat_logo.jpg)
![RegChat_Overview](https://github.com/lhzhanglabtools/RegChat/blob/main/RegChat_overview.png)

## Overview

Inferring intercellular and intracellular communications from single cell and spatial multi-omics data using RegChat.


## Installation
The RegChat package is developed based on the Python libraries [Scanpy](https://scanpy.readthedocs.io/en/stable/), [PyTorch](https://pytorch.org/) and [PyG](https://github.com/pyg-team/pytorch_geometric) (*PyTorch Geometric*) framework.

First clone the repository. 

```
git clone https://github.com/lhzhanglabtools/RegChat.git
cd RegChat-main
```

It's recommended to create a separate conda environment for running RegChat:

```
#create an environment called env_RegChat
conda create -n env_RegChat python=3.11

#activate your environment
conda activate env_RegChat
```

Install all the required packages. The torch-geometric library is required, please see the installation steps in https://github.com/pyg-team/pytorch_geometric#installation
```
conda install pyg
conda install conda-forge::pytorch_scatter
conda install conda-forge::pytorch_cluster
conda install conda-forge::pytorch_sparse
```

Install the requirements packages

```
pip install -r requirements.txt
```

Install RegChat. We provide two optional strategies to install RegChat.

```
python setup.py build
python setup.py install
```
OR

```
pip install RegChat
```


## Tutorials

Seven step-by-step tutorials are included in the `Tutorial` folder.

- [Tutorial 1: Running RegChat on simulation data](https://github.com/lhzhanglabtools/RegChat/blob/main/tutorials/run_RegChat_on_simulation_data.ipynb)
- [Tutorial 2: Running RegChat on single cell ISSAAC-seq multi-omics data of mouse cortex slices](https://github.com/lhzhanglabtools/RegChat/blob/main/tutorials/run_RegChat_on_ISSAACseq_data.ipynb)
- [Tutorial 3: Running RegChat on spatial transcriptomics of psoriasis skin brain](https://github.com/lhzhanglabtools/RegChat/blob/main/tutorials/run_RegChat_on_psoriasis_data.ipynb)
- [Tutorial 4: Running RegChat on spatial MISAR-seq multi-omics data of mouse embryonic brain skin](https://github.com/lhzhanglabtools/RegChat/blob/main/tutorials/run_RegChat_on_MISARseq_data.ipynb)

## Support

If you have any questions, please feel free to contact us [zhanglh@whu.edu.cn](mailto:zhanglh@whu.edu.cn). 


