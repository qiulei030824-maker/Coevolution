# ESMC-600M 蛋白质嵌入生成模块

## 概述

本模块使用 **EvolutionaryScale ESMC-600M** 模型（575M 参数）从蛋白质氨基酸序列生成**每残基 1152 维**的嵌入向量（embeddings）。嵌入向量可用于下游分析：序列聚类、进化分析、功能预测等。

## 在 Coevolution 项目中的作用

该模块为蛋白质序列提供基于深度学习的**结构-功能特征编码**，将序列信息映射为高维连续向量空间，支持：
- 同源序列的进化关系分析
- 蛋白质功能域的结构特征提取
- 效应子（effector）的序列-功能关联研究

## 目录结构

```
esmc/protein_embedding/
├── README.md                 # 本文件
├── environment.yml           # Conda 环境配置
├── run_esmc_embedding.py     # 嵌入提取主脚本
├── esmc_usage_tutorial.md    # 详细使用教程（中文）
├── input.fasta               # 示例输入数据（82 条序列）
├── run.sh                    # 一键运行脚本
└── verify_output.py          # 输出验证脚本
```

## 环境配置

### 方法一：使用 Conda（推荐）

```bash
# 从 environment.yml 创建环境
conda env create -f esmc/protein_embedding/environment.yml
conda activate esmc_embedding
```

### 方法二：手动创建

```bash
# 创建 conda 环境
conda create -n esmc_embedding python=3.12 -y
conda activate esmc_embedding

# 安装依赖
pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
pip install numpy biopython huggingface_hub
pip install esm==3.2.3

# 国内用户设置镜像
export HF_ENDPOINT=https://hf-mirror.com
```

## 快速使用

```bash
cd esmc/protein_embedding

# 一键运行
bash run.sh

# 或手动执行
export HF_ENDPOINT=https://hf-mirror.com
python run_esmc_embedding.py \
    --input input.fasta \
    --output ./output/ \
    --model EvolutionaryScale/esmc-600m-2024-12 \
    --device cpu
```

## 输入/输出

### 输入格式：FASTA
```
>sequence_id
MRILPSTGKVVVIGGGVAGLMAARVLKKHPEVKVTVVSSQASPTHPADHLS
```

### 输出文件
| 文件 | 格式 | 说明 |
|------|------|------|
| `esmc_600m_embeddings.npz` | NPZ | 嵌入矩阵，每个序列 (L, 1152) |
| `esmc_600m_headers.json` | JSON | 序列元信息（长度、维度等） |

## 核心方法

采用 **forward hook** 方式捕获最终 LayerNorm 层的输出，避免官方 SDK 在 CPU 上的兼容性问题。

```python
from esm.models.esmc import ESMC
from esm.tokenizers import Tokenizer

model = ESMC.from_pretrained("EvolutionaryScale/esmc-600m-2024-12").eval()
tokenizer = Tokenizer.from_pretrained("EvolutionaryScale/esmc-600m-2024-12")

# 注册 hook
layer_norm = model.transformer.norm
embeddings = {}
def hook_fn(module, input, output):
    embeddings["value"] = output.detach()
handle = layer_norm.register_forward_hook(hook_fn)

# 推理
tokens = tokenizer.encode(sequence)
_ = model(tokens.unsqueeze(0))

# 提取嵌入（去除 BOS/EOS）
seq_emb = embeddings["value"][0, 1:-1, :]  # (L, 1152)
handle.remove()
```

## 模型参数

| 参数 | 值 |
|------|-----|
| 模型 | ESMC-600M |
| 参数量 | 575M |
| 嵌入维度 | 1152 |
| 序列最大长度 | 1024 |
| 推理设备 | CPU / CUDA |

## 引用

```bibtex
@article{esmc2024,
  title={ESM Cambrian: Revealing the mysteries of proteins through evolutionary scale modeling},
  author={EvolutionaryScale},
  year={2024}
}
```