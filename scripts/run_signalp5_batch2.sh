#!/bin/bash
# SignalP5 Batch2 — 22 aphidbase species
SIGNALP="$HOME/.local/signalp-5.0b/bin/signalp"
RAW="/data5/qiulei/coevolution/data/insect_genome/raw"
PROJ="/data5/qiulei/coevolution/hemiptera_effector_erc"
OUTDIR="$PROJ/data/effectors/signalp5_results"
LOG="$PROJ/logs/signalp5_batch2.log"
MAX_JOBS=8
echo "Batch2 Start: $(date)" > "$LOG"
cd "$PROJ"
SPECIES=(
  Acyrthosiphon_pisum_JIC Aphis_fabae Aphis_rumicis Aphis_thalictri
  Brachycaudus_helichrysi Brachycaudus_klugkisti Cinara_cedri
  Drepanosiphum_platanoidis Eriosoma_laniyerum Hamadryas_cornu
  Macrosiphum_euphorbiae Myzus_cerasi Myzus_varians Nasonovia_ribisnigri
  Neotoxoptera_formosana Pentalonia_nigronervosa Pseudoregma_acericola
  Sitobion_avenae Stomaphis_chinensis Therioaphis_trifolii
  Tuberocephalus_akinire Tuberolachnus_salignus
)
for sp in "${SPECIES[@]}"; do
  sp_out="$OUTDIR/$sp"; mkdir -p "$sp_out"
  [ -f "$sp_out/done.flag" ] && continue
  faa=$(find "$RAW/aphid/$sp" -name "*.faa*" 2>/dev/null | head -1)
  [ -z "$faa" ] && continue
  gunzip -c "$faa" > "/tmp/${sp}.faa" 2>/dev/null
  (
    export PATH="$HOME/.local/signalp-5.0b/bin:$PATH"
    signalp -fasta "/tmp/${sp}.faa" -format short -org euk -prefix "$sp_out/${sp}" 2>>"$LOG"
    smry="$sp_out/${sp}_summary.signalp5"
    if [ -f "$smry" ]; then
      awk -F'\t' 'NR>1 && $3+0>0.5 {c++} END{print c+0}' "$smry" > "$sp_out/sp_hits.txt"
      touch "$sp_out/done.flag"
    fi
    rm -f "/tmp/${sp}.faa"
  ) &
  while [ "$(jobs -r | wc -l)" -ge "$MAX_JOBS" ]; do sleep 10; done
done; wait
total=0
for sp in "${SPECIES[@]}"; do
  f="$OUTDIR/$sp/${sp}_summary.signalp5"
  if [ -f "$f" ]; then
    hits=$(awk -F'\t' 'NR>1 && $3+0>0.5 {c++} END{print c+0}' "$f")
    echo "  $sp: $hits" >> "$LOG"; total=$((total+hits))
  fi
done
echo "Total: $total" >> "$LOG"
echo "End: $(date)" >> "$LOG"
