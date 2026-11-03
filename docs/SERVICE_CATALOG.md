# Existing BV-BRC Services (App-*)

Source: app specs snapshot in [`reference/app_specs/`](../reference/app_specs/)
(compact parameter dump: [`reference/app_specs_summary.txt`](../reference/app_specs_summary.txt)).

Why this matters for the modular service:
1. **Command-line mining**: each service already encodes tested invocations
   and defaults for the tools it wraps (see TOOL_INVENTORY "Used by").
2. **I/O vocabulary**: their workspace types (`ReadFile`, `Contigs`, …) are
   the types our modules must accept and emit to fit into BV-BRC.
3. **Coexistence**: a modular pipeline may later want to call a whole service
   as one node (e.g. RASTtk annotation is hard to decompose).

Outputs are **not declared** in any spec. The column below gives inputs only;
outputs must be read from each script.

| Service | Purpose | Typed inputs | Main tools |
|---|---|---|---|
| GenomeAssembly2 | WGS assembly | ReadFile (PE/SE), SRR | p3x-assembly.py: trim_galore, bbnorm, filtlong, spades, megahit, unicycler, flye, canu, racon, pilon, quast |
| GenomeAssembly | legacy assembly | ReadFile, SRR, Contigs | (legacy) |
| ViralAssembly | viral assembly | ReadFile, SRR, genome id | IRMA, fastp, bwa, bcftools, quast |
| SARS2Assembly | SARS-CoV-2 assembly | ReadFile, SRR | primer-trim/consensus pipeline |
| GenomeAnnotation | RASTtk annotation | Contigs | RASTtk (prodigal, glimmer3, tRNAscan, phispy, minced, kmer annot.) |
| GenomeAnnotationGenbank | annotate/import GenBank | genbank_file | RASTtk |
| ComprehensiveGenomeAnalysis | assembly → annotation → report | ReadFile/SRR/Contigs/genbank | chains GenomeAssembly2 + GenomeAnnotation (child jobs) |
| ComprehensiveSARS2Analysis | SARS2 assembly+annotation | (spec has `#` comments) | chains services |
| FastqUtils | trim / QC / align / host removal | ReadFile, SRR | trim_galore, fastqc, bowtie2, hisat2, minimap2, hostile |
| TaxonomicClassification | read classification | ReadFile, SRR | Snakemake: kraken2, bracken, Krona, multiqc |
| MetagenomeBinning | metagenome assembly + binning + annotation | ReadFile, SRR, Contigs | spades/megahit, binning, checkv, vigor4, RASTtk |
| MetagenomicReadMapping | map reads to gene sets (AMR, VF) | ReadFile, SRR, protein fasta | kma |
| Variation | SNV calling | ReadFile, SRR, ref genome id | bwa/bowtie2, samtools, freebayes, bcftools, snippy, snpEff |
| RNASeq | RNA-seq | ReadFile, SRR, ref genome id | hisat2, samtools, stringtie, DESeq2 |
| TnSeq | Tn-seq | reads, ref genome id | bwa, TRANSIT |
| DifferentialExpression | expression transform | ExpList, ExpMetadata | |
| Homology | BLAST | fasta / ids / groups | blastn/blastp/blastx/tblastn |
| GenomeComparison | proteome comparison | genome ids, protein fasta, feature groups | blastp |
| MSA | multiple alignment + SNP | fasta, feature/genome groups | mafft, muscle, progressiveMauve |
| GeneTree | gene tree | fasta (aligned or not), feature/genome groups | mafft/muscle, FastTree, raxmlHPC |
| CodonTree | PGFam codon tree | genome ids / groups | mafft/muscle, raxmlHPC |
| GenomeAlignment | whole-genome MSA | genome ids | progressiveMauve |
| WholeGenomeSNPAnalysis | WG SNP tree | genome group / genome_fasta | kSNP4 (Snakemake) |
| CoreGenomeMLST | cgMLST | genome group / genome_fasta | chewBBACA, mlst (Snakemake) |
| ComparativeSystems | subsystem/pathway comparison | genome ids / groups | BV-BRC data API |
| MetaCATS | metadata-driven site association | alignment, groups, tsv | mafft, stats |
| SubspeciesClassification | viral subspecies | fasta / genome group | mafft, tree placement |
| HASubtypeNumberingConversion | influenza HA numbering | fasta / features | blastp, muscle |
| TreeSort | reassortment inference | fasta / groups | FastTree, TreeSort |
| Genomad | mobile elements | fasta (wsid) | genomad |
| MobileElementDetection | assembly + genomad | ReadFile, SRR, fasta | assembly + genomad |
| SARS2Wastewater | lineage abundance | ReadFile, SRR | Snakemake: freyja, fastqc, multiqc |
| PrimerDesign | primers | sequence | primer3_core |
| SequenceSubmission / CEIRRDataSubmission | data submission | fasta, metadata | vigor4 / validators |
| ModelReconstruction / GapfillModel / RunProbModelSEEDJob | metabolic models | genome, model, media | ModelSEED |
| Docking / StabilityPrediction | structure | PDB, SMILES | docking, ThermoMPNN |
| Date / Sleep | test apps | none | none |

Scripts also exist in the container for `App-PhylogeneticTree` and
`App-FluxBalanceAnalysis`, which have no app spec in the snapshot.
