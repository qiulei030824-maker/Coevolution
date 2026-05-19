#!/bin/bash
# SignalP5 Batch Run — 26 species
SIGNALP="$HOME/.local/signalp-5.0b/bin/signalp"
RAW="/data5/qiulei/coevolution/data/insect_genome/raw"
PROJ="/data5/qiulei/coevolution/hemiptera_effector_erc"
OUTDIR="$PROJ/data/effectors/signalp5_results"
LOG="$PROJ/logs/signalp5_batch.log"
MAX_JOBS=8
mkdir -p "$OUTDIR"
echo "Start: $(date)" > "$LOG"
FILES=(); while IFS= read -r f; do FILES+=("$f"); done < <(find "$RAW" -name "*_protein.faa.gz" 2>/dev/null)
for f in "${FILES[@]}"; do
  species=$(basename "$(dirname "$f")")
  sp_out="$OUTDIR/$species"; mkdir -p "$sp_out"
  [ -f "$sp_out/done.flag" ] && continue
  gunzip -c "$f" > "/tmp/${species}.faa"
  (
    export PATH="$HOME/.local/signalp-5.0b/bin:$PATH"
    signalp -fasta "/tmp/${species}.faa" -format short -org euk -prefix "$sp_out/${species}" 2>>"$LOG"
    smry="$sp_out/${species}_summary.signalp5"
    if [ -f "$smry" ]; then
      awk -F'\t' 'NR>1 && $3+0>0.5 {c++} END{print c+0}' "$smry" > "$sp_out/sp_hits.txt"
      touch "$sp_out/done.flag"
    fi
    rm -f "/tmp/${species}.faa"
  ) &
  while [ "$(jobs -r | wc -l)" -ge "$MAX_JOBS" ]; do sleep 5; done
done; wait
echo "End: $(date)" >> "$LOG"
