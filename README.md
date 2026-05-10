# Coevolution

多工具集成仓库，用于蛋白质共进化分析与效应子功能研究。

## 模块结构

```
esmc/                         ← ESMC 蛋白质嵌入模块（本项目）
    └── protein_embedding/    ← 使用 ESMC-600M 生成蛋白质嵌入向量
```

## 模块说明

| 模块 | 路径 | 说明 |
|------|------|------|
| ESMC 蛋白质嵌入 | `esmc/protein_embedding/` | 使用 EvolutionaryScale ESMC-600M (575M) 模型提取蛋白质序列嵌入（1152维） |

## 快速使用

```bash
# ESMC 蛋白质嵌入
conda env create -f esmc/protein_embedding/environment.yml
conda activate esmc_embedding
export HF_ENDPOINT=https://hf-mirror.com
cd esmc/protein_embedding && bash run.sh
```

更多模块将陆续添加。
