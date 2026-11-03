# P4: Empirical output discovery on Slurm

This step runs every candidate tool on the test fixtures inside the BV-BRC
container, then records **what it actually writes**. For each file it records
the path, size, sha256, detected format, read/record counts and a short
preview. It also records runtime, peak memory and exit status. These results
become the `outputs:` and `resources:` of the module descriptors.

```
tests/discovery/
  sets/NN_<set>.yaml     run definitions, grouped by resource class (one Slurm array per set)
  run_discovery.py       runner (inside the container): count | resources | list | indices | run | summarize
  discovery.sbatch       one array task = one run (binds the same NFS data paths as production)
  submit.sh              submits sets as job arrays, plus a summary job that waits for all of them
  logs/<set>/            Slurm stdout/stderr (gitignored)
results -> reference/tools/<tool>/runs/<run_id>.json, summary -> reference/tools/DISCOVERY.md
```

## Usage

```bash
python3 tests/fixtures/fetch_fixtures.py --container $(cat singularity_container_ref.txt)   # once
tests/discovery/submit.sh --dry-run all              # show what would be submitted
tests/discovery/submit.sh readqc mapping             # some sets (names match sets/*<name>*.yaml)
tests/discovery/submit.sh all                        # everything (107 runs) + summary job
tests/discovery/submit.sh --only spades_meta_pe,flye_nano assembly   # re-run specific runs
tests/discovery/submit.sh --keep --only pilon_polish assembly        # keep the node workdir for debugging
squeue -u $USER
singularity exec $(cat singularity_container_ref.txt) python3 tests/discovery/run_discovery.py summarize
```

Defaults: account `cli`, partition `compute`, at most 6 concurrent tasks per set
(`--throttle`). Each task works in node-local scratch (`/disks/tmp`, then
`/scratch/tmp`, then `/tmp`), and its work directory is deleted afterwards.
Only the result JSON is written back to the repo, because the home NFS is
98% full.

## Sets

| Set | Runs | Resources | Covers |
|---|---|---|---|
| 01_readqc | 15 | 4 cpu, 16G, 1h | fastp, fastplong, trim_galore, cutadapt, fastqc, filtlong, bbduk, bbnorm, seqtk, hostile, multiqc |
| 02_assembly | 17 | 8 cpu, 32G, 4h | spades (isolate/meta/SE/hybrid/rnaviral), megahit, unicycler (short/hybrid/long), flye, canu, racon, pilon, quast |
| 03_mapping_variants | 23 | 4 cpu, 16G, 1h | bwa, bowtie2, hisat2, minimap2, samtools (incl. 1.13 vs 1.20 consensus), bcftools, freebayes, snippy, snpEff, bedtools, kma |
| 04_annotation | 15 | 4 cpu, 24G, 2h | prodigal, glimmer3, tRNAscan-SE, minced, phispy, vigor4, amrfinder, genomad, checkv, hmmscan/hmmsearch, antiSMASH |
| 05_homology | 10 | 4 cpu, 16G, 1h | makeblastdb, blastp/blastn, diamond, mmseqs2, cd-hit |
| 06_phylogeny | 14 | 4 cpu, 16G, 2h | mafft, muscle, clustalw, progressiveMauve, Gblocks, FastTree, RAxML, raxml-ng, iqtree2, parsnp, kSNP4 |
| 07_typing_expression | 13 | 4 cpu, 16G, 1h | kraken2, bracken, krona, mlst, chewBBACA, freyja, pangolin, stringtie, htseq-count, primer3 |

## Run definition

```yaml
- id: pilon_polish                 # unique; becomes reference/tools/<tool>/runs/<id>.json
  tool: pilon                      # tool id from tools/tool_list.json
  mode: paired_frags               # free text: which variant of the tool this is
  inputs: {DRAFT: portiera_genome, R1: portiera_illumina_1}   # env var -> fixture id (":dir" for unpacked DBs)
  prep: |                          # optional setup; files it creates are NOT counted as outputs
    bwa index $DRAFT; ...
  cmd: pilon --genome $DRAFT ...   # the tracked command (bash -euo pipefail), timed with /usr/bin/time -v
  timeout: 7200                    # optional, seconds
```
The environment provides `$CPU`, `$MEM_GB`, `$WORKDIR` and `$TMPDIR`. Inputs are copied
into `inputs/`, and index files written next to them (e.g. `bwa index`) **are**
counted as outputs. A run's outputs are every file that is new or modified after `cmd`.

## Notes
- Some runs are expected to fail. Each is labelled as such in the set file, and
  each failure tells us something: `samtools_consensus` (PATH samtools 1.13 has no
  `consensus`), and `diamond_blastp` / `antismash_minimal` (illegal instruction on
  the dev host; this checks the compute nodes).
- Database paths match production: geNomad
  `/vol/bvbrc/production/application-backend/genomad/genomad_db`, CheckV
  `runtime/checkv-db/checkv-db-v1.0`, vigor4 `sarscov2_db` / `flua_db`
  (bundled), freyja barcodes (latest dated dir under
  `application-backend/bvbrc_SARS2Wastewater/`), hostile cache
  (`application-backend/fastqutils/reference_indices/hostile_cache`),
  pangolin-data 1.30 (bundled). snpEff has no prebuilt databases, so its run
  builds one from the SARS-CoV-2 GFF3 first.
- Not covered yet: IRMA (no influenza reads), Kraken2 with the real BV-BRC
  databases (large; `kraken_db` partition), chewBBACA AlleleCall against a
  production schema.
