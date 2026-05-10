#!/bin/bash
# ESMC-600M Protein Embedding - One-click Run Script
# Usage: bash run.sh

set -e

# Configuration
INPUT_FASTA="input.fasta"
OUTPUT_DIR="./output"
MODEL="EvolutionaryScale/esmc-600m-2024-12"
DEVICE="cpu"

# Set HF mirror for users in China
export HF_ENDPOINT=https://hf-mirror.com

# Run embedding extraction
python run_esmc_embedding.py \
    --input "$INPUT_FASTA" \
    --output "$OUTPUT_DIR" \
    --model "$MODEL" \
    --device "$DEVICE"

# Verify output
python verify_output.py \
    --embeddings "$OUTPUT_DIR/esmc_600m_embeddings.npz"

echo "Done! Output saved to: $OUTPUT_DIR"
