#!/usr/bin/env python3
"""Scan local insect genomes for protein files"""
import os, csv
base = "/data5/qiulei/coevolution/data/insect_genome/raw"
output = "/data5/qiulei/coevolution/hemiptera_effector_erc/data/insect_local_status.tsv"
accession_file = "/data5/qiulei/coevolution/data/insect_genome/HEMIPTERA_ACCESSION_REFERENCE.tsv"
tax_info = {}
if os.path.exists(accession_file):
  with open(accession_file) as f:
    for line in f:
      if line.startswith("#") or not line.strip(): continue
      parts = line.strip().split("\t")
      if len(parts) >= 6: tax_info[parts[1]] = {"accession": parts[0], "group": parts[4], "priority": parts[5]}
rows = []
for group_dir in sorted(os.listdir(base)):
  group_path = os.path.join(base, group_dir)
  if not os.path.isdir(group_path): continue
  for sp_dir in sorted(os.listdir(group_path)):
    sp_path = os.path.join(group_path, sp_dir)
    if not os.path.isdir(sp_path): continue
    faa_files = [os.path.join(r,f) for r,_,fs in os.walk(sp_path) for f in fs if f.endswith(("_protein.faa.gz",".faa.gz"))]
    info = tax_info.get(sp_dir, {})
    rows.append({"species": sp_dir, "group": group_dir, "priority": info.get("priority","unknown"), "accession": info.get("accession",""), "protein_available": "yes" if faa_files else "no"})
with open(output, "w", newline="") as f:
  w = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter="\t")
  w.writeheader(); w.writerows(rows)
proteins = sum(1 for r in rows if r["protein_available"] == "yes")
print(f"Written {len(rows)} species, {proteins} with protein files")
