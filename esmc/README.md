# ESMC — 蛋白质嵌入（Protein Embedding）模块

本模块是 Coevolution 项目的子模块，使用 **EvolutionaryScale ESMC-600M** 模型将蛋白质氨基酸序列编码为高维嵌入向量，用于下游的进化分析、功能预测和效应子研究。

## 模块结构

```
esmc/
└── protein_embedding/          ← 蛋白质嵌入生成
    ├── README.md               # 模块使用说明
    ├── environment.yml         # Conda 环境配置
    ├── run_esmc_embedding.py   # 嵌入提取主脚本（支持命令行参数）
    ├── esmc_usage_tutorial.md  # 详细中文使用教程
    ├── run.sh                  # 一键运行脚本
    ├── verify_output.py        # 输出验证脚本
    └── input.fasta             # 示例输入数据（82 条 AT1G09070 直系同源序列）
```

## 快速开始

```bash
# 1. 创建环境
conda env create -f esmc/protein_embedding/environment.yml
conda activate esmc_embedding

# 2. 运行（国内用户请设置镜像）
export HF_ENDPOINT=https://hf-mirror.com
cd esmc/protein_embedding && bash run.sh
```

## 输出

每条蛋白质序列生成一个 (L, 1152) 的嵌入矩阵（L = 序列长度），保存为 NPZ 格式。

## Coevolution 项目中的角色

ESM 蛋白质语言模型在 Coevolution 项目中承担**结构-功能特征编码**角色：
- 将氨基酸序列映射到 1152 维连续向量空间
- 为下游分析（聚类、进化树、效应子功能预测）提供特征输入
- 与 AlphaFold2 结构预测互补，提供基于序列的深度表示
