#!/usr/bin/env python3
"""STEP 1: Multi-copy domain representative selection (longest per species)"""
from pathlib import Path; from Bio import SeqIO; import os
RGENE = Path("/data5/qiulei/01.plant-phylogenomics/RGene")
OUTDIR = Path("/data5/qiulei/coevolution/hemiptera_effector_erc/data/plants/rgene_representatives")
os.makedirs(OUTDIR, exist_ok=True)
MULTI_COPY = ["PF05659","PF00182","PF01476","PF13306","PF08488","PF18805"]
for pf in MULTI_COPY:
  inp = None
  for dn in ["filtered","align"]:
    dp = RGENE / pf / dn
    if dp.exists():
      for f in sorted(dp.glob("*")):
        if f.suffix in [".fa",".fasta"] and f.stat().st_size > 100: inp = f; break
    if inp: break
  if not inp: print(f"❌ {pf}: not found"); continue
  ss = {}
  for rec in SeqIO.parse(str(inp), "fasta"):
    sp = rec.id.split("|")[0].split(".")[0]
    if sp not in ss or len(rec.seq) > ss[sp][1]: ss[sp] = (rec, len(rec.seq))
  out = OUTDIR / f"{pf}_representative.fa"
  with open(out, "w") as f:
    for sp_name in sorted(ss):
      rec,_ = ss[sp_name]
      seq = str(rec.seq).replace("-","")
      f.write(f">{sp_name}|{pf}|{len(seq)}aa\n{seq}\n")
  print(f"✅ {pf}: {len(ss)} species")
