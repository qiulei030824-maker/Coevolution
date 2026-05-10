#!/bin/bash
# Batch ESMC Embedding for Multiple FASTA Files
# Usage: bash batch_run_esmc.sh /path/to/fasta_dir/ /path/to/output_dir/

set -e

if [ $# -lt 2 ]; then
    echo "Usage: bash batch_run_esmc.sh <input_fasta_dir> <output_base_dir>"
    echo "  <input_fasta_dir>   Directory containing .fasta files"
    echo "  <output_base_dir>   Base directory for per-file outputs"
    exit 1
fi

FASTA_DIR="$1"
OUTPUT_BASE="$2"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

export HF_ENDPOINT=https://hf-mirror.com

mkdir -p "$OUTPUT_BASE"

for fasta in "$FASTA_DIR"/*.fasta; do
    [ -f "$fasta" ] || continue
    name=$(basename "$fasta" .fasta)
    outdir="$OUTPUT_BASE/$name"
    echo "=============================================="
    echo "[$(date '+%H:%M:%S')] Processing: $name"
    echo "  Input : $fasta"
    echo "  Output: $outdir"
    echo "=============================================="

    python "$SCRIPT_DIR/run_esmc_embedding.py" \
        --input "$fasta" \
        --output "$outdir" \
        --model "EvolutionaryScale/esmc-600m-2024-12" \
        --device cpu

    echo ""
done

echo "All done! Outputs in: $OUTPUT_BASE"
echo "Summary:"
for d in "$OUTPUT_BASE"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    npz="$d/esmc_600m_embeddings.npz"
    if [ -f "$npz" ]; then
        python3 -c "
import numpy as np
data = np.load('$npz')
print(f'  $name: {len(data)} seqs, dim={list(data.values())[0].shape[1]}, size={sum(d.nbytes for d in data.values())/1024/1024:.1f}MB')
"
    else
        echo "  $name: FAILED (no output)"
    fi
done
