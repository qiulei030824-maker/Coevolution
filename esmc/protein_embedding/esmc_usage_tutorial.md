# ESMC-600M 蛋白质嵌入生成使用教程

## 概述

本教程说明如何使用 **EvolutionaryScale ESMC-600M** 模型从蛋白质序列生成嵌入向量（embeddings）。ESMC-600M 是基于蛋白质语言的 Transformer 模型（575M 参数），可将每条蛋白质序列编码为**每残基 1152 维**的嵌入向量，适用于下游任务（聚类、进化分析、功能预测等）。

---

## 1. 环境配置

### 1.1 使用 Conda（推荐）

```bash
# 从 environment.yml 创建环境
conda env create -f environment.yml
conda activate esmc_embedding

# 国内用户设置 HuggingFace 镜像
export HF_ENDPOINT=https://hf-mirror.com
```

### 1.2 手动配置

```bash
conda create -n esmc_embedding python=3.12 -y
conda activate esmc_embedding

# 安装 PyTorch (CPU 版)
pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu

# 安装其他依赖
pip install numpy biopython huggingface_hub
pip install esm==3.2.3

# 国内用户设置镜像
export HF_ENDPOINT=https://hf-mirror.com
```

### 1.3 模型缓存

模型首次运行时自动下载到 `~/.cache/huggingface/hub/`，约 2.3GB。
已缓存路径：
```
~/.cache/huggingface/hub/models--EvolutionaryScale--esmc-600m-2024-12/
```

---

## 2. 模型与 Tokenizer

### 2.1 加载方式

```python
from esm.models.esmc import ESMC
from esm.tokenizers import Tokenizer

# 加载模型（CPU 推理）
model = ESMC.from_pretrained(
    "EvolutionaryScale/esmc-600m-2024-12",
).eval()

# 加载 tokenizer
tokenizer = Tokenizer.from_pretrained("EvolutionaryScale/esmc-600m-2024-12")
```

### 2.2 模型架构参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 参数量 | 575M | Transformer 总参数量 |
| 嵌入维度 | 1152 | 每个残基的输出向量维度 |
| 层数 | ~30 | Transformer 编码器层数 |
| 注意力头 | ~18 | 多头注意力头数 |
| 序列最大长度 | 1024 | 最大支持残基数 |
| 输出位置 | 最终 LayerNorm 后 | 嵌入提取位置 |

### 2.3 Tokenizer 说明

```python
# Tokenizer 自动添加 BOS/EOS
tokens = tokenizer.encode(sequence)
# 输入序列 "MRIL..." (281 aa) -> tokens shape [283]
# 即 seq_len + 2 (BOS + EOS)
```

---

## 3. 嵌入提取方法

**推荐使用 forward hook** 方式提取最终 LayerNorm 的嵌入，而非官方的 ESMProtein/LogitsConfig API（后者在 CPU 上会卡死）。

### 3.1 核心原理

```python
# 在模型的最终 LayerNorm 层注册 forward hook
# forward 时自动捕获该层输出
layer_norm = model.transformer.norm
embeddings_cache = {}

def hook_fn(module, input, output):
    embeddings_cache["value"] = output.detach()

handle = layer_norm.register_forward_hook(hook_fn)

# 推理后提取嵌入
_ = model(tokens.unsqueeze(0))
emb = embeddings_cache["value"]  # (1, seq_len+2, 1152)
seq_emb = emb[0, 1:-1, :]       # (seq_len, 1152) 去除 BOS/EOS

handle.remove()
```

---

## 4. 运行方式

### 4.1 一键运行

```bash
cd esmc/protein_embedding
bash run.sh
```

### 4.2 手动运行

```bash
export HF_ENDPOINT=https://hf-mirror.com

python run_esmc_embedding.py \
    --input input.fasta \
    --output ./output/ \
    --model EvolutionaryScale/esmc-600m-2024-12 \
    --device cpu
```

### 4.3 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--input` | 必填 | 输入 FASTA 文件路径 |
| `--output` | `./output/` | 输出目录 |
| `--model` | `EvolutionaryScale/esmc-600m-2024-12` | HuggingFace 模型 ID |
| `--device` | `cpu` | 推理设备 (`cpu` / `cuda:0`) |

---

## 5. 输入/输出格式

### 5.1 输入：FASTA

```fasta
>sequence_id_1
MRILPSTGKVVVIGGGVAGLMAARVLKKH
>sequence_id_2
MARIAPTGKVVVVGGGLAGLVAARVLQRK
```

- 仅接受标准 20 种氨基酸：`ACDEFGHIKLMNPQRSTVWY`
- 建议序列长度 ≤ 900 残基

### 5.2 输出：NPZ + JSON

**嵌入文件（`esmc_600m_embeddings.npz`）：**

```python
import numpy as np
data = np.load("esmc_600m_embeddings.npz")
print(data["seq001"].shape)  # (L, 1152)
```

**头信息文件（`esmc_600m_headers.json`）：**

```json
{
    "seq001": {
        "id": "seq001",
        "length": 281,
        "embedding_dim": 1152,
        "dtype": "float32"
    }
}
```

---

## 6. 输出验证

```bash
python verify_output.py \
    --embeddings ./output/esmc_600m_embeddings.npz \
    --headers ./output/esmc_600m_headers.json
```

预期输出（示例数据 82 条序列）：
```
Sequences: 82
  AT1G09070.1_AT: (283, 1152) max=12.34 min=-9.87
  AT1G09070.2_AT: (281, 1152) max=11.56 min=-8.92
Embedding dimension: 1152
Total size: 93.8 MB
Expected dim: 1152 -> PASS
All checks passed!
```

---

## 7. 嵌入数据使用示例

### 7.1 PCA 降维可视化

```python
import numpy as np
from sklearn.decomposition import PCA

data = np.load("./output/esmc_600m_embeddings.npz")
seq_ids = list(data.keys())

# Mean pooling
emb_matrix = np.array([data[sid].mean(axis=0) for sid in seq_ids])

# PCA to 2D
pca = PCA(n_components=2)
coords = pca.fit_transform(emb_matrix)
print(f"Variance explained: {pca.explained_variance_ratio_.sum():.2%}")
```

### 7.2 序列相似性分析

```python
from sklearn.metrics.pairwise import cosine_similarity

sim_matrix = cosine_similarity(emb_matrix)
target = 0
top5 = np.argsort(sim_matrix[target])[::-1][1:6]
for idx in top5:
    print(f"  {seq_ids[idx]}: {sim_matrix[target][idx]:.4f}")
```

---

## 8. 常见问题

### Q: 模型加载失败？
确认设置了 `export HF_ENDPOINT=https://hf-mirror.com`（国内用户）。

### Q: 为什么用 forward hook？
官方 `ESMProtein` + `LogitsConfig` API 在 CPU 上会无限卡死。

### Q: 嵌入维度为什么是 1152？
ESMC-600M 的隐藏层维度为 1152，与模型参数量（575M）对应。

### Q: 能否用 GPU？
可以，指定 `--device cuda:0` 即可。

---

## 9. 参考

- [EvolutionaryScale ESMC](https://github.com/evolutionaryscale/esm)
- [HuggingFace ESMC-600M](https://huggingface.co/EvolutionaryScale/esmc-600m-2024-12)

---

*生成日期：2026-05-10*
