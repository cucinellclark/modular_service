# Tool Inventory (container `ubuntu-176-build12-2.sif`)

These are the candidate **modules**. "Used by" is from grepping
`plbin/App-*.pl`, `lib/Bio/P3`, `lib/Bio/KBase/AppService`, `pybin`, and
`workflows/` in the container. A blank means no direct hit: the tool may be
unused, or invoked indirectly (e.g. RASTtk calls prodigal/glimmer/tRNAscan).
Existing invocations are the best source for tested command lines and defaults.

Full binary listing: [`reference/container_runtime_bin.txt`](../reference/container_runtime_bin.txt).

## Read QC / preprocessing

| Tool | Path | Used by |
|---|---|---|
| fastp / fastplong | runtime/bin | reference_guided_assembly.py, run_viral_assembly.py |
| trim_galore (+cutadapt) | runtime/bin | FastqUtils, p3x-assembly.py, taxonomic 16s snakefiles |
| cutadapt | runtime/bin | CmdRunner.pm |
| fastqc | runtime/bin | FastqUtils, Wastewater, TaxonomicClassification |
| filtlong | runtime/bin | GenomeAssembly2 |
| bbduk.sh / bbnorm.sh | /usr/bin | (p3x-assembly normalize) |
| seqtk | runtime/bin | |
| hostile (host read removal) | runtime/bin | fastq_utils.py |
| multiqc | runtime/bin | TaxonomicClassification, RNASeq, Wastewater |

## Assembly & polishing

| Tool | Path | Used by |
|---|---|---|
| spades.py (4.0.0) | runtime/bin | p3x-assembly.py, MetagenomeBinning |
| megahit | /usr/bin | p3x-assembly.py, MetagenomeBinning |
| flye (2.9.1) | runtime/bin | GenomeAssembly2 |
| unicycler | /usr/bin | p3x-assembly.py |
| canu | /usr/bin | GenomeAssembly2 |
| racon, pilon | /usr/bin | p3x-assembly.py |
| IRMA | runtime/bin | ViralAssembly (run_viral_assembly.py) |
| quast.py / quast-lg.py | runtime/bin | p3x-assembly.py, viral assembly, cgMLST |

## Read mapping / variants

| Tool | Path | Used by |
|---|---|---|
| bwa | /usr/bin | TnSeq, viral assembly |
| bowtie2 | /usr/bin | FastqUtils, GenomeAssembly2, RNASeq |
| hisat2 | /usr/bin | RNASeq, FastqUtils, taxonomic snakefiles |
| minimap2 | /usr/bin | p3x-assembly.py, fastq_utils.py |
| samtools (1.11, 1.20) / bcftools (1.17) | /usr/bin, runtime | Variation, RNASeq, GenomeAssembly2 |
| freebayes | runtime/bin | Variation |
| snippy (4.6.0) | runtime/bin | Variation |
| snpEff | runtime/bin | Variation |
| bedtools | /usr/bin | |
| kma | runtime/bin | MetagenomicReadMapping |

## Annotation / feature calling

| Tool | Path | Used by |
|---|---|---|
| RASTtk pipeline | `Bio::P3::GenomeAnnotationApp` | GenomeAnnotation (custom_pipeline steps) |
| prodigal, glimmer3, tRNAscan-SE (2.0.12) | /usr/bin, /usr/lib/tigr-glimmer | via RASTtk |
| phispy, minced | runtime/bin | via RASTtk (prophage, CRISPR) |
| vigor4 | runtime/bin | viral annotation, MetagenomeBinning, SequenceSubmission |
| amrfinder (4.0.3) | runtime/bin | |
| genomad, checkv | runtime/bin | Genomad, MobileElementDetection, MetagenomeBinning |
| antismash (7.1) | runtime/ | |
| hmmscan | /usr/bin | |

## Homology / clustering

| Tool | Path | Used by |
|---|---|---|
| blastn/blastp (+) | runtime/bin | Homology, GenomeComparison, HA subtype |
| diamond | /usr/bin | |
| mmseqs2 | runtime/bin | |
| cd-hit family | runtime/bin | |

## Alignment & phylogeny

| Tool | Path | Used by |
|---|---|---|
| mafft (all modes) | runtime/bin | MSA, GeneTree, MetaCATS, CodonTree, subspecies |
| muscle (3.8.31) | runtime/bin | MSA, GeneTree, CodonTree |
| clustalw | runtime/bin | |
| progressiveMauve | /usr/bin | MSA, GenomeAlignment |
| Gblocks | runtime/bin | |
| FastTree (+MP) | runtime/bin | GeneTree, PhylogeneticTree, TreeSort |
| raxmlHPC (-PTHREADS) | /usr/bin | CodonTree, GeneTree, CGA |
| raxml-ng, iqtree2 | runtime/bin | |
| parsnp (2.1.2) | runtime/bin | |
| kSNP4 | runtime/bin | WholeGenomeSNPAnalysis |

## Taxonomy / typing / surveillance

| Tool | Path | Used by |
|---|---|---|
| kraken2 (+bracken, KronaTools ktImportText) | runtime/bin | TaxonomicClassification |
| mlst (2.23.0) | runtime/bin | cgMLST |
| chewBBACA (3.3.10) | runtime/bin | CoreGenomeMLST |
| freyja (1.5.1) | runtime/bin | SARS2Wastewater |
| pangolin | runtime/bin | SARS2 reports |

## Expression

| Tool | Path | Used by |
|---|---|---|
| stringtie | /usr/bin | RNASeq |
| htseq-count | runtime/bin | |
| R 4.2.3 (DESeq2 etc.) | runtime/ | RNASeq / DiffExp |

## Other

primer3_core (PrimerDesign), ProteinMPNN / ThermoMPNN (StabilityPrediction),
circos, ete3, FigTree, snakemake, conda.

## Not present (checked)

medaka, trimmomatic, metabat2, checkm, busco, salmon, kallisto, seqkit,
trimal, vsearch, vina. Adding any of these would need a container rebuild
(or a sidecar container; see OPEN_QUESTIONS).
