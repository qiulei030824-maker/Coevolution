# Coevolution — Hemiptera Effector Cross-Kingdom ERC

## Project
Identifies secreted effector proteins from hemipteran insects (aphids, whiteflies, planthoppers)
and analyzes their cross-kingdom coevolution with plant immune genes using
Evolutionary Rate Covariation (ERC).

## Scripts

### Phase 0 — Data Preparation

| Script | Description | Status |
|--------|------------|--------|
| `scripts/01_scan_insect_local.py` | Scan local insect genome dirs for protein files | ✅ Complete |
| `scripts/run_signalp5_batch.sh` | SignalP5 batch run (26 species) | ✅ Complete |
| `scripts/run_signalp5_batch2.sh` | SignalP5 batch2 (22 aphidbase species) | ▶️ Running |
| `scripts/P0_04_select_representatives.py` | Select 1 longest seq/species for multi-copy Pfam domains | ✅ Complete |

### Plant-side ERC Preparation

| Script | Description |
|--------|------------|
| `P0_04_select_representatives.py` | Step 1: Multi-copy domain selection |
| `P0_04_build_lineA_tree.py` | Step 2: IQ-TREE2 partitioned species tree |
| `P0_04_build_supergene.py` | Step 4: Immune supergene CDS concatenation |

## Example Data
- Insect proteomes: `/data5/qiulei/coevolution/data/insect_genome/raw/` (48 species with protein)
- Plant genomes: `/data5/qiulei/coevolution/data/plant_genome/` (119 species)
- R-gene data: `/data5/qiulei/01.plant-phylogenomics/RGene/` (29 Pfam domains)

## Example Output
- `data/effectors/all_candidates.fa` — Secreted protein candidates (SignalP5 filtered)
- `data/plants/rgene_representatives/*.fa` — Representative sequences per species
- `results/00_tree/plant_lineA.treefile` — Partitioned IQ-TREE2 species tree
