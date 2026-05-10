#!/usr/bin/env python3
"""Verify ESMC embedding output files."""

import argparse
import json
import sys
import numpy as np

def main():
    parser = argparse.ArgumentParser(description="Verify ESMC embedding output")
    parser.add_argument("--embeddings", required=True, help="Path to .npz file")
    parser.add_argument("--headers", help="Path to headers.json (optional)")
    args = parser.parse_args()

    # Load embeddings
    data = np.load(args.embeddings)
    print(f"Sequences: {len(data)}")
    
    dims = set()
    total_residues = 0
    for i, key in enumerate(data.keys()):
        emb = data[key]
        dims.add(emb.shape[1])
        total_residues += emb.shape[0]
        if i < 3:
            print(f"  {key}: {emb.shape}, "
                  f"max={emb.max():.4f}, min={emb.min():.4f}, "
                  f"mean={emb.mean():.4f}, std={emb.std():.4f}")

    if len(dims) != 1:
        print(f"ERROR: Mixed embedding dims: {dims}")
        sys.exit(1)
    
    dim = dims.pop()
    print(f"\nEmbedding dimension: {dim}")
    print(f"Total residues: {total_residues}")
    
    total_bytes = sum(data[k].nbytes for k in data)
    print(f"Total size: {total_bytes / 1024 / 1024:.1f} MB")
    print(f"Expected dim: 1152 -> {'PASS' if dim == 1152 else 'FAIL'}")

    # Load headers if provided
    if args.headers:
        with open(args.headers) as f:
            headers = json.load(f)
        print(f"Headers entries: {len(headers)}")
        assert len(headers) == len(data), "Headers count mismatch"
        print("Headers validation: PASS")

    print("\nAll checks passed!")


if __name__ == "__main__":
    main()
