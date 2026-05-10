#!/usr/bin/env python3
"""
ESMC-600M embedding extraction via forward hook on final LayerNorm.

Usage:
    python run_esmc_embedding.py --input input.fasta --output ./output/

Args:
    --input    : Input FASTA file path
    --output   : Output directory (default: ./output/)
    --model    : HuggingFace model ID (default: EvolutionaryScale/esmc-600m-2024-12)
    --device   : Device (cpu / cuda:0, default: cpu)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def parse_args():
    parser = argparse.ArgumentParser(
        description="ESMC-600M Protein Embedding Extraction"
    )
    parser.add_argument(
        "--input", type=str, required=True,
        help="Input FASTA file path"
    )
    parser.add_argument(
        "--output", type=str, default="./output/",
        help="Output directory (default: ./output/)"
    )
    parser.add_argument(
        "--model", type=str,
        default="EvolutionaryScale/esmc-600m-2024-12",
        help="HuggingFace model ID"
    )
    parser.add_argument(
        "--device", type=str, default="cpu",
        help="Device: cpu or cuda:0 (default: cpu)"
    )
    return parser.parse_args()


def load_fasta(fasta_path):
    """Load sequences from FASTA file."""
    from Bio import SeqIO
    
    sequences = []
    seq_ids = []
    for record in SeqIO.parse(fasta_path, "fasta"):
        seq = str(record.seq).upper()
        valid = "".join(c for c in seq if c in "ACDEFGHIKLMNPQRSTVWY")
        sequences.append(valid)
        seq_ids.append(record.id)
    
    total_res = sum(len(s) for s in sequences)
    print(f"Loaded {len(sequences)} sequences, total residues: {total_res}")
    return seq_ids, sequences


def load_model(model_name, device):
    """Load ESMC model and tokenizer."""
    from esm.models.esmc import ESMC
    from esm.tokenizers import Tokenizer
    
    print(f"Loading model from {model_name}...")
    t0 = time.time()
    
    model = ESMC.from_pretrained(model_name).eval()
    tokenizer = Tokenizer.from_pretrained(model_name)
    
    if device != "cpu":
        model = model.to(device)
    
    param_count = sum(p.numel() for p in model.parameters())
    print(f"Model loaded in {time.time()-t0:.1f}s ({param_count/1e6:.0f}M params)")
    return model, tokenizer


def extract_embeddings(model, tokenizer, seq_ids, sequences, device):
    """Extract embeddings using forward hook on final LayerNorm."""
    layer_norm = model.transformer.norm
    embeddings_cache = {}

    def hook_fn(module, input, output):
        embeddings_cache["value"] = output.detach()

    handle = layer_norm.register_forward_hook(hook_fn)

    results = {}
    total_start = time.time()

    with torch.no_grad():
        for i, (seq_id, seq) in enumerate(zip(seq_ids, sequences)):
            t0 = time.time()
            
            tokens = tokenizer.encode(seq)
            input_tensor = tokens.unsqueeze(0)
            if device != "cpu":
                input_tensor = input_tensor.to(device)
            
            _ = model(input_tensor)
            
            emb = embeddings_cache["value"]
            seq_emb = emb[0, 1:-1, :].cpu().numpy().astype(np.float32)
            
            results[seq_id] = seq_emb
            
            elapsed = time.time() - t0
            print(f"  [{i+1}/{len(sequences)}] {seq_id} "
                  f"({seq_emb.shape[0]} aa, {elapsed:.1f}s)")

    handle.remove()
    
    total_time = time.time() - total_start
    print(f"\nTotal time: {total_time:.0f}s ({total_time/60:.1f}min)")
    return results


def save_results(results, output_dir):
    """Save embeddings as NPZ and metadata as JSON."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save embeddings
    npz_path = output_path / "esmc_600m_embeddings.npz"
    np.savez_compressed(npz_path, **results)
    
    # Save headers
    headers = {
        seq_id: {
            "id": seq_id,
            "length": emb.shape[0],
            "embedding_dim": emb.shape[1],
            "dtype": str(emb.dtype),
        }
        for seq_id, emb in results.items()
    }
    json_path = output_path / "esmc_600m_headers.json"
    with open(json_path, "w") as f:
        json.dump(headers, f, indent=2)
    
    # Summary
    total_bytes = sum(emb.nbytes for emb in results.values())
    print(f"Embeddings saved: {npz_path}")
    print(f"Headers saved: {json_path}")
    print(f"Summary: {len(results)} sequences, "
          f"dim={list(headers.values())[0]['embedding_dim']}, "
          f"size={total_bytes/1024/1024:.1f} MB")


def main():
    args = parse_args()
    
    print("=" * 60)
    print("ESMC-600M Protein Embedding Extraction")
    print("=" * 60)
    
    # Load sequences
    seq_ids, sequences = load_fasta(args.input)
    
    # Load model
    model, tokenizer = load_model(args.model, args.device)
    
    # Extract embeddings
    results = extract_embeddings(
        model, tokenizer, seq_ids, sequences, args.device
    )
    
    # Save results
    save_results(results, args.output)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
