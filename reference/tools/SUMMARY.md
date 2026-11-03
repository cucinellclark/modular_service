# Tool metadata summary

- P1 introspection: generated 2026-11-02T14:52:03 in `/vol/patric3/production/containers/ubuntu-176-build12-2.sif`
- P2 BV-BRC invocations: 1253 files scanned under `/opt/p3/deployment`
- P3 nf-core modules: commit `b4070340f85cc0822351c854733820811ac4339a 2026-11-02`

Per tool: `<id>/version.txt`, `<id>/help.txt`, `<id>/bvbrc_invocations.md`, `<id>/nfcore/<module>/{meta.yml,main.nf}`.

| id | category | version | path | help | BV-BRC refs (hunks/files) | nf-core modules | notes |
|---|---|---|---|---|---|---|---|
| clustalw | alignment | 1.83 | `/opt/patric-common/runtime/bin/clustalw` | yes | 16/7 | none |  |
| gblocks | alignment | ? | `/opt/patric-common/runtime/bin/Gblocks` | no | 0/0 | none | Interactive menu when run without a file; batch usage: Gblocks <aln> -t=p\|d -b5=... ; no help flag. |
| mafft | alignment | 7.526 | `/opt/patric-common/runtime/bin/mafft` | yes | 25/20 | mafft/align |  |
| muscle | alignment | 3.8.31 | `/opt/patric-common/runtime/bin/muscle` | yes | 19/12 | muscle |  |
| progressivemauve | alignment | 1.2.0 | `/usr/bin/progressiveMauve` | yes | 1/1 | none |  |
| amrfinder | annotation | 4.0.3 | `/opt/patric-common/runtime/bin/amrfinder` | yes | 3/1 | amrfinderplus/run, amrfinderplus/update |  |
| antismash | annotation | ? | `/opt/patric-common/runtime/antismash-7-1-0-1/bin/antismash` | yes | 0/0 | antismash/antismash | Not on PATH; own venv under runtime/antismash-7-1-0-1. Core dumped on the dev host (2026-11-02), like diamond; verify on compute nodes. |
| checkv | annotation | 0.7.0 | `/opt/patric-common/runtime/bin/checkv` | yes | 3/2 | checkv/endtoend |  |
| genomad | annotation | 1.12.0 | `/opt/patric-common/runtime/bin/genomad` | yes | 9/3 | genomad/endtoend, genomad/download |  |
| glimmer3 | annotation | 3.02b | `/usr/lib/tigr-glimmer/glimmer3` | yes | 6/4 | none |  |
| hmmscan | annotation | 3.3.2 | `/usr/bin/hmmscan` | yes | 3/2 | hmmer/hmmsearch, hmmer/hmmpress |  |
| minced | annotation | 0.4.2 | `/opt/patric-common/runtime/bin/minced` | yes | 0/0 | none |  |
| phispy | annotation | 4.2.21 | `/opt/patric-common/runtime/bin/phispy` | yes | 6/5 | phispy |  |
| prodigal | annotation | 2.6.3 | `/usr/bin/prodigal` | yes | 5/2 | prodigal |  |
| trnascan | annotation | 2.0.9 | `/usr/bin/tRNAscan-SE` | yes | 4/2 | trnascanse |  |
| vigor4 | annotation | 4.1.20220621 | `/opt/patric-common/runtime/bin/vigor4` | yes | 10/5 | none |  |
| canu | assembly | 2.0 | `/usr/bin/canu` | yes | 8/4 | canu |  |
| flye | assembly | 2.9.1 | `/opt/patric-common/runtime/bin/flye` | yes | 5/2 | flye |  |
| irma | assembly | 1.2.0 | `/opt/patric-common/runtime/bin/IRMA` | yes | 5/2 | none |  |
| megahit | assembly | 1.2.9 | `/usr/bin/megahit` | yes | 9/4 | megahit |  |
| pilon | assembly | 1.24 | `/usr/bin/pilon` | yes | 6/3 | pilon |  |
| racon | assembly | 1.5.0 | `/usr/bin/racon` | yes | 6/3 | racon |  |
| spades | assembly | 4.0.0 | `/opt/patric-common/runtime/bin/spades.py` | yes | 2/1 | spades |  |
| unicycler | assembly | 0.4.8 | `/usr/bin/unicycler` | yes | 6/3 | unicycler |  |
| quast | assembly_qc | 5.2.0 | `/opt/patric-common/runtime/bin/quast.py` | yes | 6/4 | quast |  |
| htseq-count | expression | 2.0.9 | `/opt/patric-common/runtime/bin/htseq-count` | yes | 1/1 | htseq/count |  |
| stringtie | expression | 2.2.1 | `/usr/bin/stringtie` | yes | 6/4 | stringtie/stringtie |  |
| blastn | homology | 2.15.0 | `/opt/patric-common/runtime/bin/blastn` | yes | 117/35 | blast/blastn, blast/makeblastdb |  |
| blastp | homology | 2.15.0 | `/opt/patric-common/runtime/bin/blastp` | yes | 54/22 | blast/blastp |  |
| cd-hit | homology | 4.8.1 | `/opt/patric-common/runtime/bin/cd-hit` | yes | 1/1 | cdhit/cdhit, cdhit/cdhitest |  |
| diamond | homology | ? | `/usr/bin/diamond` | no | 7/6 | diamond/blastp, diamond/makedb | Crashed with 'Illegal instruction' on the dev host (2026-11-02); likely CPU-ISA dependent, verify on compute nodes. |
| mmseqs | homology | ? | `/opt/patric-common/runtime/bin/mmseqs` | yes | 5/3 | mmseqs/easysearch, mmseqs/easycluster, mmseqs/createdb | `mmseqs version` prints '17' but runtime dir is mmseqs2-13-45111; confirm which binary is on PATH. |
| bowtie2 | mapping | 2.4.4 | `/usr/bin/bowtie2` | yes | 21/9 | bowtie2/build, bowtie2/align |  |
| bwa | mapping | 0.7.17 | `/usr/bin/bwa` | yes | 7/5 | bwa/index, bwa/mem |  |
| hisat2 | mapping | 2.2.1 | `/usr/bin/hisat2` | yes | 16/9 | hisat2/build, hisat2/align |  |
| kma | mapping | 1.4.15 | `/opt/patric-common/runtime/bin/kma` | yes | 3/3 | kma/index, kma/kma |  |
| minimap2 | mapping | 2.24 | `/usr/bin/minimap2` | yes | 13/8 | minimap2/index, minimap2/align |  |
| samtools | mapping | 1.13 | `/usr/bin/samtools` | yes | 38/21 | samtools/sort, samtools/index, samtools/view, samtools/faidx, samtools/stats, samtools/depth, samtools/consensus | PATH resolves /usr/bin/samtools 1.13; runtime also has samtools-1.11 and samtools-1.20 dirs. |
| primer3 | other | 2.0 | `/usr/bin/primer3_core` | yes | 2/1 | none |  |
| fasttree | phylogeny | 2.1.11 | `/opt/patric-common/runtime/bin/FastTree` | yes | 24/12 | fasttree |  |
| iqtree2 | phylogeny | 2.4.0 | `/opt/patric-common/runtime/bin/iqtree2` | yes | 0/0 | iqtree |  |
| ksnp4 | phylogeny | 4.1 | `/opt/patric-common/runtime/bin/kSNP4` | yes | 10/3 | none |  |
| parsnp | phylogeny | 2.1.2 | `/opt/patric-common/runtime/bin/parsnp` | yes | 0/0 | parsnp |  |
| raxml-ng | phylogeny | 1.2.2 | `/opt/patric-common/runtime/bin/raxml-ng` | yes | 0/0 | raxmlng |  |
| raxmlhpc | phylogeny | 8.2.12 | `/usr/bin/raxmlHPC-PTHREADS-SSE3` | yes | 11/6 | raxmlng |  |
| bbduk | read_qc | 38.95 | `/usr/bin/bbduk.sh` | yes | 0/0 | bbmap/bbduk |  |
| bbnorm | read_qc | 38.95 | `/usr/bin/bbnorm.sh` | yes | 2/1 | bbmap/bbnorm |  |
| cutadapt | read_qc | 4.9 | `/opt/patric-common/runtime/bin/cutadapt` | yes | 5/4 | cutadapt |  |
| fastp | read_qc | 1.3.2 | `/opt/patric-common/runtime/bin/fastp` | yes | 2/2 | fastp |  |
| fastplong | read_qc | 0.4.1 | `/opt/patric-common/runtime/bin/fastplong` | yes | 0/0 | fastplong |  |
| fastqc | read_qc | 0.12.1 | `/opt/patric-common/runtime/bin/fastqc` | yes | 28/12 | fastqc |  |
| filtlong | read_qc | 0.2.1 | `/opt/patric-common/runtime/bin/filtlong` | yes | 6/4 | filtlong |  |
| hostile | read_qc | 1.1.0 | `/opt/patric-common/runtime/bin/hostile` | yes | 2/2 | hostile/clean |  |
| seqtk | read_qc | 1.4 | `/opt/patric-common/runtime/bin/seqtk` | yes | 9/6 | seqtk/sample, seqtk/seq, seqtk/subseq |  |
| trim_galore | read_qc | 0.6.5d | `/opt/patric-common/runtime/bin/trim_galore` | yes | 13/9 | trimgalore |  |
| multiqc | reporting | 1.25 | `/opt/patric-common/runtime/bin/multiqc` | yes | 12/6 | multiqc |  |
| bracken | taxonomy | 2.9 | `/opt/patric-common/runtime/bin/bracken` | yes | 4/2 | bracken/bracken |  |
| kraken2 | taxonomy | 2.1.2 | `/opt/patric-common/runtime/bin/kraken2` | yes | 13/9 | kraken2/kraken2 |  |
| krona | taxonomy | 2.8.1 | `/opt/patric-common/runtime/bin/ktImportText` | yes | 3/3 | krona/ktimporttext |  |
| chewbbaca | typing | 3.3.10 | `/opt/patric-common/runtime/bin/chewBBACA.py` | yes | 10/3 | chewbbaca/allelecall, chewbbaca/createschema |  |
| freyja | typing | 1.5.1 | `/opt/patric-common/runtime/bin/freyja` | yes | 13/6 | freyja/variants, freyja/demix, freyja/boot |  |
| mlst | typing | 2.23.0 | `/opt/patric-common/runtime/bin/mlst` | yes | 7/5 | mlst |  |
| pangolin | typing | 4.3.1 | `/opt/patric-common/runtime/bin/pangolin` | yes | 4/2 | pangolin/run |  |
| bcftools | variants | 1.13 | `/usr/bin/bcftools` | yes | 12/6 | bcftools/mpileup, bcftools/call, bcftools/consensus, bcftools/view |  |
| bedtools | variants | 2.30.0 | `/usr/bin/bedtools` | yes | 3/3 | bedtools/genomecov, bedtools/coverage |  |
| freebayes | variants | 1.3.6 | `/opt/patric-common/runtime/bin/freebayes` | yes | 5/2 | freebayes |  |
| snippy | variants | 4.6.0 | `/opt/patric-common/runtime/bin/snippy` | yes | 3/2 | snippy/run, snippy/core |  |
| snpeff | variants | 4.3t | `/opt/patric-common/runtime/bin/snpEff.sh` | yes | 2/1 | snpeff/snpeff |  |
