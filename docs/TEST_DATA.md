# Test Data (P5)

**Status (2026-11-02): built.** `tests/fixtures/manifest.json` (57 fixtures, 7
sets) and `tests/fixtures/fetch_fixtures.py`. T0 and T1 were fetched and verified
(67 MB, about 20 s). All sources are nf-core/test-datasets @ `3170f64e`, except the
four BV-BRC Portiera genomes. RNA-seq uses nf-core data, following nf-core's
own tests: SARS-CoV-2 genome + GTF + reads (hisat2), and the human test region +
GTF + `test_rnaseq` reads and BAM (stringtie/htseq). See
[tests/fixtures/README.md](../tests/fixtures/README.md).

Verified:
- every .gz passes `gzip -t`; re-running fetches nothing
- the nf-core Portiera genome is **sequence-identical to BV-BRC `1206109.14`**
  (same orientation, same start), so Portiera reads can be used with
  `reference_genome_id`-style inputs
- the container tools run on the fixtures: kraken2 with the mini DB classifies 100/100 pairs
  as SARS-CoV-2; mafft aligns the SARS2 proteome; prodigal calls 264 genes on
  Portiera

The research notes below were written before the build.

## Research

Researched 2026-11-02. Goal: small, redistributable fixtures for (a) per-module
smoke tests, (b) empirical output discovery (P4), and (c) end-to-end pipeline
tests, including scatter/gather and multi-genome steps.

## Sources found

### 1. nf-core/test-datasets (`modules` branch). **Primary source.**
`https://raw.githubusercontent.com/nf-core/test-datasets/modules/data/genomics/...`
(MIT-licensed, built for exactly this purpose.) The nf-core `main.nf.test` files
we imported in P3 reference these same files, so we can compare our outputs
with nf-core's own test runs.

Checked by download (read stats computed locally):

| Dataset | Files | Size | Verified stats |
|---|---|---|---|
| **Candidatus Portiera aleyrodidarum** (bacterium, 358 kb) | genome.fasta, proteome.fasta, genome.aln.gz + .nwk, illumina test_1/2 + test_se, nanopore test | ~38 MB | PE: 97,729 × 101 bp per mate, **~55× coverage**; ONT: 7,100 reads, mean 2 kb, **~40×** |
| SARS-CoV-2 (30 kb) | genome.fasta/.gff3, illumina test_1/2, test2_1/2, interleaved, BAM (sorted + bai, SE/PE), VCF/BCF, contigs/scaffolds.fasta, alignment all_sites/informative_sites.fas, **kraken2 + bracken mini DBs**, nanopore test/test_2 | <10 MB | Illumina test_1: **100 reads** (smoke only); ONT test_2: 4,000 reads, mean 536 bp, **~70×** |
| Bacteroides fragilis (5.2 Mb) | genome .fna/.gbff/.gff, illumina test1/test2 PE, nanopore, contigs | ~25 MB | test1: 50,000 × 126 bp, **~2.4× coverage** (mapping/QC only, not assembly) |
| Haemophilus influenzae | genome.fna.gz, genome.aln.gz + nwk | 2 MB | (has a PubMLST scheme, so good for `mlst`; nf-core uses it for AMRFinderPlus) |

### 2. BV-BRC QA suite. **Production-realistic, larger.**
- Test job definitions: `/vol/patric3/QA/applications/App-<App>/tests/*.json`
  (read by `p3x-run-qa-suite`); 472 input references extracted.
- Inputs live in the shared workspace `/olson@patricbrc.org/PATRIC-QA/`
  (`DataSets/<App>/`, `applications/App-<App>/`). **Readable with your token**
  (checked with `p3-ls`).
- Already-tiny files: `DataSets/FastqUtils/SRR1201673_{1,2}.1k.fastq`
  (1k pairs), `ERR3457743.1k.fastq`, `ERR1777068.5k.fastq`, plus
  `ERR3457743.1k.&()%$#@!<>|{}[].fastq` (a **special-characters filename
  test**: keep it for path-quoting tests).
- Most read sets are 50 MB – 3 GB and need subsampling (`seqtk sample`).
- SRA accessions used by QA (all public): GenomeAssembly2 `ERR1913166,
  ERR7916233 (workshop SPAdes/Unicycler/metaSPAdes), SRR2568388`; Variation
  `SRR847052, ERR3549716, SRR10961160`; TaxonomicClassification
  `SRR12486988, SRR14092310, SRR26088207, SRR26127838`; SARS2Assembly
  `SRR11092063, SRR11621984, SRR11786917, ERR4192740`; ViralAssembly
  `SRR28752451/2`; MetagenomeBinning `SRR8580939`; RNASeq `SRR10075886–97`,
  … (full list: `reference/qa_test_inputs.tsv`).
- The QA runner (`p3x-run-qa.pl`) binds the reference databases into the
  container. This answers part of P6:
  `/vol/patric3/production/data-images/patric-data-2022-0119:/opt/patric-common/data`,
  `/vol/blastdb/bvbrc-service`, `/vol/patric3/metagenome_dbs`.

### 3. Local repos (dev_container). Small protein/gene sets.
- `modules/p3_msa/tests/data/{hemoglobin,alpha_globin}.fasta`
- `modules/bvbrc_ha_subtype_conversion/lib/Burke_HA_Reference_Sequences{,_alignment}.fasta`
- QA `App-Homology/tests/{qry_aa,qry_dna}.fa`

### 4. BV-BRC genomes by ID (multi-genome fixtures)
Fetched at fixture-build time with `p3-genome-fasta` (in container). Checked via
`p3-all-genomes`:
- **Portiera set** (matches the nf-core reads): `1206109.14` (BT-B-HRs,
  358,242 bp, Complete, which matches the nf-core reference length), `1239881.13`
  (BT-QVLC, 350,928 bp), `1297582.10` (TV, 280,663 bp), `91844.21` (BT-Z1).
- **Buchnera set** (familiar from BV-BRC QA/annotation tests), all Complete, about
  430–650 kb: `107806.709` (APS, 1 contig), `198804.5` (Sg), `224915.9` (Bp),
  `98785.34` (Ago-UT1), `261317.3` (Cinara), `1241881.3` (Takecallis).

## Proposed fixture tiers

| Tier | Purpose | Size / runtime | Contents |
|---|---|---|---|
| **T0 smoke** | every module runs; CI on each commit | <15 MB, seconds | nf-core SARS-CoV-2 suite + mini kraken2/bracken DBs; local protein sets |
| **T1 realistic-small** | P4 output discovery; e2e pipelines; CI nightly | ~60 MB, minutes | Portiera (PE, SE, ONT, genome, proteome, aln/nwk); SARS-CoV-2 ONT test_2; H. influenzae genome; B. fragilis PE (mapping) |
| **T1-multi** | scatter/gather + multi-genome steps | ~5 MB fetched | samples: SARS2 `test`/`test2`, B. fragilis `test1`/`test2`, Portiera PE vs SE; genomes: Portiera set (4) or Buchnera set (6) |
| **T2 production-like** | manual / pre-release, not CI | 100s MB–GB | BV-BRC QA datasets + SRA accessions above, subsampled to 50–200k reads; real DBs via the bind mounts |

## Module coverage (T0/T1)

| Module group | Fixture |
|---|---|
| read QC: fastp, trim_galore, cutadapt, fastqc, seqtk, bbnorm, multiqc | SARS2 illumina (T0); Portiera PE/SE (T1) |
| long-read QC: filtlong, fastplong | Portiera ONT; SARS2 ONT |
| short assembly: spades, megahit, unicycler | Portiera PE (~55×) |
| long/hybrid: flye, canu, unicycler-hybrid, racon, pilon | Portiera ONT (~40×) + PE |
| viral assembly | SARS2 ONT test_2 (~70×); IRMA needs influenza reads (see gaps) |
| assembly QC: quast (+ref) | outputs above + Portiera genome / SARS2 genome |
| mapping: bwa, bowtie2, minimap2, kma | reads vs Portiera / SARS2 reference |
| bam/variants: samtools, bcftools, freebayes, snippy, bedtools, snpEff | nf-core SARS2 BAM/VCF (T0); Portiera reads vs `1206109.14` (T1) |
| annotation: prodigal, glimmer3, tRNAscan-SE, minced, phispy, hmmscan, vigor4, genomad, checkv | Portiera genome; SARS2 genome (vigor4, genomad) |
| AMR / typing: amrfinder, mlst | H. influenzae genome |
| homology: blast, diamond, mmseqs, cd-hit | Portiera proteome; hemoglobin / HA sets |
| alignment / trees: mafft, muscle, clustalw, Gblocks, FastTree, RAxML, raxml-ng, iqtree2 | hemoglobin/HA sets; SARS2 & Portiera alignments |
| multi-genome: parsnp, kSNP4, progressiveMauve, chewBBACA | Portiera set / Buchnera set |
| taxonomy: kraken2, bracken, krona | nf-core SARS2 mini DBs (T0); real DB under bind mount (T2) |

## Gaps / to decide
- ~~RNA-seq~~: resolved with nf-core data (see Status). There is still no bacterial
  RNA-seq set; the QA `DataSets/RNA-seq` subsets remain an option for T2.
- **Influenza** (IRMA): nf-core has influenza *genomes* (included in T0: H5N1
  Italy, test-genome-A1), but no reads. IRMA still needs a small read set.
- **SARS2 surveillance**: pangolin-data v1.29 is in the manifest as T2; the ARTIC v3
  primer BED is in T0; freyja runs on the nf-core SARS2 BAM (as in nf-core's own
  test). It still needs freyja barcodes (check the container) for `demix`.
- **chewBBACA**: needs a schema; check the cgMLST service's schema location.
- **diamond / antiSMASH** crash on the dev host (see PREPROCESSING), so they can only be
  tested on compute nodes.

## Proposed layout

```
tests/fixtures/
  manifest.json            # source URL/path/accession, sha256, tier, license
  fetch_fixtures.py        # downloads/subsamples into tests/fixtures/data (gitignored)
  data/                    # not committed
```
Commit only the manifest and the script; keep data out of git (or on `/vol`).

## Appendix: QA input list
`reference/qa_test_inputs.tsv` (app, test, kind, param, value). Regenerate with:
```bash
python3 -I tools/extract_qa_inputs.py /vol/patric3/QA/applications > reference/qa_test_inputs.tsv
```
