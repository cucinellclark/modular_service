# P4 output discovery results

Generated 2026-11-02T15:48:13 from `reference/tools/*/runs/*.json` (tests/discovery/run_discovery.py).

Runs: 110; ok: 103; not ok: 7

| set | run | tool | version | status | wall s | max RSS MB | outputs | main outputs (kind) |
|---|---|---|---|---|---|---|---|---|
| annotation | amrfinder_nucleotide | amrfinder | 4.0.3 | ok | 8.93 | 44.3 | 2 | `amr_nuc.tsv` (text), `amr_nuc.fna` (fasta) |
| annotation | amrfinder_protein | amrfinder | 4.0.3 | ok | 8.68 | 102.9 | 1 | `amr_protein.tsv` (text) |
| annotation | antismash_minimal | antismash |  | failed | 8.68 | 132.8 | 0 |  |
| annotation | checkv_e2e | checkv | 0.7.0 | ok | 28.64 | 1034.1 | 264 | `out/tmp/hmmsearch.txt` (text), `out/tmp/proteins/1.fna` (fasta), `out/viruses.fna` (fasta), `out/tmp/diamond.tsv` (text), +260 more |
| annotation | genomad_e2e | genomad | 1.12.0 | ok | 557.23 | 18690.9 | 39 | `out/genome_summary/genome_virus.fna` (fasta), `out/genome_annotate/genome_proteins.faa` (fasta), `out/genome_summary/genome_virus_proteins.faa` (fasta), `out/genome_summary.log` (text), +35 more |
| annotation | glimmer3_from_scratch | glimmer3 | 3.02b | ok | 1.73 | 25.6 | 5 | `icm` (binary), `g3.detail` (text), `train.fasta` (fasta), `g3.predict` (fasta), +1 more |
| annotation | hmmscan_proteome | hmmscan | 3.3.2 | ok | 0.32 | 14.7 | 3 | `hmmscan.txt` (text), `domtbl.txt` (text), `tbl.txt` (text) |
| annotation | hmmsearch_proteome | hmmscan | 3.3.2 | ok | 0.32 | 20.1 | 3 | `hmmsearch.txt` (text), `domtbl.txt` (text), `tbl.txt` (text) |
| annotation | minced | minced | 0.4.2 | ok | 19.26 | 272.2 | 2 | `crisprs.txt` (text), `crisprs.gff` (gff) |
| annotation | phispy | phispy | 4.2.21 | ok | 94.15 | 685.1 | 3 | `phispy/genome.gbff` (genbank), `phispy/phispy.log` (text), `phispy/prophage_coordinates.tsv` (text) |
| annotation | prodigal_meta | prodigal | 2.6.3 | ok | 10.89 | 42.2 | 3 | `genes.fna` (fasta), `proteins.faa` (fasta), `genes.gff` (gff) |
| annotation | prodigal_single | prodigal | 2.6.3 | ok | 0.82 | 9.7 | 4 | `starts.txt` (text), `genes.fna` (fasta), `proteins.faa` (fasta), `genes.gff` (gff) |
| annotation | trnascan_bacterial | trnascan | 2.0.9 | ok | 14.95 | 63.0 | 4 | `trna.ss` (text), `trna.gff` (gff), `trna_stats.txt` (text), `trna.txt` (text) |
| annotation | vigor4_flua | vigor4 | 4.1.20220621 | ok | 23.88 | 1992.6 | 8 | `vigor/flua.aln` (fasta), `vigor/flua.cds` (fasta), `vigor/flua.rpt` (text), `vigor/flua.gff3` (gff), +4 more |
| annotation | vigor4_sarscov2 | vigor4 | 4.1.20220621 | ok | 94.0 | 1364.0 | 8 | `vigor/sarscov2.aln` (fasta), `vigor/sarscov2.cds` (fasta), `vigor/sarscov2.pep` (index), `vigor/sarscov2.rpt` (text), +4 more |
| assembly | canu_nano | canu | 2.0 | ok | 135.04 | 3380.3 | 383 | `out/correction/asm.corStore/seqDB.v001.dat` (binary), `out/asm.seqStore/blobs.0003` (binary), `out/asm.seqStore/blobs.0001` (binary), `out/asm.correctedReads.fasta.gz` (fasta), +379 more |
| assembly | flye_nano | flye | 2.9.1 | ok | 79.26 | 8301.9 | 32 | `out/20-repeat/read_alignment_dump` (text), `out/10-consensus/consensus.fasta` (fasta), `out/00-assembly/draft_assembly.fasta` (fasta), `out/20-repeat/repeat_graph_edges.fasta` (fasta), +28 more |
| assembly | flye_nano_sarscov2 | flye | 2.9.1 | failed | 49.79 | 8254.6 | 3 | `out/flye.log` (text), `out/params.json` (json), `out/00-assembly/draft_assembly.fasta` (fasta) |
| assembly | megahit_pe | megahit | 1.2.9 | ok | 6.53 | 267.6 | 73 | `out/intermediate_contigs/k21.contigs.fa` (fasta), `out/intermediate_contigs/k29.contigs.fa` (fasta), `out/intermediate_contigs/k39.contigs.fa` (fasta), `out/intermediate_contigs/k59.contigs.fa` (fasta), +69 more |
| assembly | pilon_polish | pilon | 1.24 | ok | 12.65 | 2856.4 | 3 | `out/pilon.vcf` (vcf), `out/pilon.fasta` (fasta), `out/pilon.changes` (text) |
| assembly | quast_multi | quast | 5.2.0 | ok | 4.27 | 128.8 | 64 | `quast/icarus_viewers/alignment_viewer.html` (html), `quast/icarus_viewers/contig_size_viewer.html` (html), `quast/report.html` (html), `quast/icarus.html` (html), +60 more |
| assembly | quast_noref | quast | 5.2.0 | ok | 1.77 | 101.4 | 15 | `quast/icarus_viewers/contig_size_viewer.html` (html), `quast/report.html` (html), `quast/icarus.html` (html), `quast/report.pdf` (image), +11 more |
| assembly | quast_ref | quast | 5.2.0 | ok | 5.43 | 125.6 | 51 | `quast/icarus_viewers/alignment_viewer.html` (html), `quast/icarus_viewers/contig_size_viewer.html` (html), `quast/report.html` (html), `quast/icarus.html` (html), +47 more |
| assembly | racon_polish | racon | 1.5.0 | ok | 2.22 | 87.1 | 1 | `polished.fasta` (fasta) |
| assembly | spades_hybrid | spades | 4.0.0 | ok | 24.97 | 1036.8 | 113 | `out/corrected/test_2.fastq00.0_0.cor.fastq.gz` (fastq), `out/corrected/test_1.fastq00.0_0.cor.fastq.gz` (fastq), `out/K55/assembly_graph.fastg` (fasta), `out/assembly_graph.fastg` (fasta), +109 more |
| assembly | spades_isolate_pe | spades | 4.0.0 | ok | 11.34 | 250.5 | 102 | `out/K55/assembly_graph.fastg` (fasta), `out/assembly_graph.fastg` (fasta), `out/K55/assembly_graph_with_scaffolds.gfa` (text), `out/assembly_graph_with_scaffolds.gfa` (text), +98 more |
| assembly | spades_isolate_se | spades | 4.0.0 | ok | 11.9 | 134.6 | 101 | `out/K55/assembly_graph.fastg` (fasta), `out/assembly_graph.fastg` (fasta), `out/K55/assembly_graph_with_scaffolds.gfa` (text), `out/assembly_graph_with_scaffolds.gfa` (text), +97 more |
| assembly | spades_meta_pe | spades | 4.0.0 | ok | 17.46 | 248.3 | 114 | `out/corrected/test_2.fastq00.0_0.cor.fastq.gz` (fastq), `out/corrected/test_1.fastq00.0_0.cor.fastq.gz` (fastq), `out/K55/assembly_graph.fastg` (fasta), `out/assembly_graph.fastg` (fasta), +110 more |
| assembly | spades_rnaviral_ont | spades | 4.0.0 | ok | 7.54 | 178.6 | 125 | `out/spades.log` (text), `out/K55/simplified_contigs/contigs.seq` (binary), `out/K33/simplified_contigs/contigs.seq` (binary), `out/K21/simplified_contigs/contigs.seq` (binary), +121 more |
| assembly | unicycler_hybrid | unicycler | 0.4.8 | ok | 286.22 | 506.9 | 8 | `out/003_bridges_applied.gfa` (text), `out/assembly.fasta` (fasta), `out/005_polished.gfa` (text), `out/assembly.gfa` (text), +4 more |
| assembly | unicycler_long | unicycler | 0.4.8 | ok | 9.24 | 311.2 | 6 | `out/001_string_graph.gfa` (text), `out/assembly.fasta` (fasta), `out/003_racon_polished.gfa` (text), `out/assembly.gfa` (text), +2 more |
| assembly | unicycler_short | unicycler | 0.4.8 | ok | 97.56 | 287.9 | 7 | `out/001_best_spades_graph.gfa` (text), `out/002_overlaps_removed.gfa` (text), `out/003_bridges_applied.gfa` (text), `out/assembly.fasta` (fasta), +3 more |
| homology | blastn_tab | blastn | 2.15.0 | ok | 17.26 | 38.2 | 1 | `hits.tsv` (text) |
| homology | blastp_tab | blastp | 2.15.0 | ok | 14.91 | 25.7 | 1 | `hits.tsv` (text) |
| homology | blastp_xml | blastp | 2.15.0 | ok | 12.7 | 26.8 | 1 | `hits.xml` (text) |
| homology | cdhit_est | cd-hit | 4.8.1 | ok | 0.32 | 91.0 | 2 | `clusters.fna` (fasta), `clusters.fna.clstr` (fasta) |
| homology | cdhit_prot | cd-hit | 4.8.1 | ok | 0.17 | 173.7 | 2 | `clusters.faa` (fasta), `clusters.faa.clstr` (fasta) |
| homology | diamond_blastp | diamond |  | ok | 9.79 | 21.2 | 2 | `protdb.dmnd` (index), `hits.tsv` (text) |
| homology | makeblastdb_nucl | blastn | 2.15.0 | ok | 5.1 | 17.7 | 8 | `nucdb.nsq` (index), `nucdb.ndb` (index), `nucdb.ntf` (index), `nucdb.njs` (index), +4 more |
| homology | makeblastdb_prot | blastp | 2.15.0 | ok | 5.4 | 22.0 | 10 | `protdb.psq` (index), `protdb.pdb` (index), `protdb.phr` (index), `protdb.ptf` (index), +6 more |
| homology | mmseqs_easy_cluster | mmseqs |  | ok | 8.38 | 867.1 | 7 | `clu_all_seqs.fasta` (fasta), `clu_rep_seq.fasta` (fasta), `clu_cluster.tsv` (text) |
| homology | mmseqs_easy_search | mmseqs |  | ok | 10.44 | 867.0 | 1 | `hits.m8` (text) |
| mapping_variants | bcftools_call | bcftools | 1.13 | ok | 0.17 | 36.8 | 3 | `calls.vcf.gz` (vcf), `calls.vcf.gz.csi` (index), `inputs/genome.fasta.fai` (text) |
| mapping_variants | bcftools_consensus | bcftools | 1.13 | ok | 0.11 | 4.0 | 1 | `consensus.fa` (fasta) |
| mapping_variants | bedtools_genomecov | bedtools | 2.30.0 | ok | 0.57 | 5.0 | 1 | `coverage.bedgraph` (text) |
| mapping_variants | bowtie2_align_pe | bowtie2 | 2.4.4 | ok | 7.35 | 35.6 | 4 | `aln.sam` (sam), `unaligned_2.fastq.gz` (fastq), `unaligned_1.fastq.gz` (fastq), `bowtie2.log` (text) |
| mapping_variants | bowtie2_build | bowtie2 | 2.4.4 | ok | 1.57 | 96.9 | 6 | `refidx.1.bt2` (index), `refidx.rev.1.bt2` (index), `refidx.2.bt2` (index), `refidx.rev.2.bt2` (index), +2 more |
| mapping_variants | bwa_index | bwa | 0.7.17 | ok | 0.17 | 6.1 | 5 | `inputs/genome.fasta.bwt` (index), `inputs/genome.fasta.sa` (index), `inputs/genome.fasta.pac` (index), `inputs/genome.fasta.ann` (index), +1 more |
| mapping_variants | bwa_mem_pe | bwa | 0.7.17 | ok | 2.82 | 157.0 | 1 | `aln.sam` (sam) |
| mapping_variants | freebayes | freebayes | 1.3.6 | ok | 0.11 | 3.8 | 1 | `freebayes.vcf` (vcf) |
| mapping_variants | hisat2_align_rnaseq | hisat2 | 2.2.1 | ok | 2.32 | 16.1 | 2 | `aln.sam` (sam), `summary.txt` (text) |
| mapping_variants | hisat2_build | hisat2 | 2.2.1 | ok | 6.08 | 96.3 | 8 | `refidx.1.ht2` (index), `refidx.5.ht2` (index), `refidx.2.ht2` (index), `refidx.6.ht2` (index), +4 more |
| mapping_variants | kma_map | kma | 1.4.15 | ok | 0.11 | 7.4 | 4 | `kma_out.aln` (fasta), `kma_out.frag.gz` (text), `kma_out.fsa` (fasta), `kma_out.res` (text) |
| mapping_variants | minimap2_index | minimap2 | 2.24 | ok | 0.03 | 8.2 | 1 | `ref.mmi` (index) |
| mapping_variants | minimap2_ont | minimap2 | 2.24 | ok | 5.47 | 365.8 | 1 | `aln.sam` (sam) |
| mapping_variants | minimap2_sr | minimap2 | 2.24 | ok | 0.97 | 95.9 | 1 | `aln.sam` (sam) |
| mapping_variants | samtools120_consensus | samtools | 1.13 | ok | 5.93 | 11.2 | 1 | `consensus.fa` (fasta) |
| mapping_variants | samtools_consensus | samtools | 1.13 | failed | 0.16 | 3.3 | 0 |  |
| mapping_variants | samtools_depth | samtools | 1.13 | ok | 0.01 | 3.6 | 1 | `depth.tsv` (text) |
| mapping_variants | samtools_faidx | samtools | 1.13 | ok | 0.03 | 3.3 | 1 | `inputs/genome.fasta.fai` (text) |
| mapping_variants | samtools_sort_index | samtools | 1.13 | ok | 0.27 | 4.4 | 2 | `sorted.bam` (bam), `sorted.bam.bai` (index) |
| mapping_variants | samtools_stats | samtools | 1.13 | ok | 0.03 | 4.1 | 3 | `stats.txt` (text), `flagstat.txt` (text), `idxstats.txt` (text) |
| mapping_variants | samtools_view_filter | samtools | 1.13 | ok | 2.22 | 3.9 | 1 | `filtered.bam` (bam) |
| mapping_variants | snippy_pe | snippy | 4.6.0 | ok | 27.54 | 158.4 | 31 | `out/snps.bam` (bam), `out/reference/genomes/ref.fa` (fasta), `out/reference/ref.fa` (fasta), `out/snps.consensus.subs.fa` (fasta), +25 more |
| mapping_variants | snpeff_ann | snpeff | 4.3t | ok | 3.52 | 117.7 | 3 | `snpEff_summary.html` (html), `annotated.vcf` (vcf), `snpEff_genes.txt` (text) |
| phylogeny | clustalw | clustalw | 1.83 | ok | 220.94 | 15.6 | 2 | `aligned.fasta` (fasta), `unaligned.dnd` (newick) |
| phylogeny | fasttree_aa | fasttree | 2.1.11 | ok | 3.27 | 37.9 | 1 | `tree.nwk` (newick) |
| phylogeny | fasttree_nt | fasttree | 2.1.11 | ok | 2.47 | 128.1 | 1 | `tree.nwk` (newick) |
| phylogeny | gblocks_dna | gblocks |  | ok | 0.12 | 4.2 | 2 | `aln.fas-gb.htm` (html), `aln.fas-gb` (fasta) |
| phylogeny | iqtree2_fast | iqtree2 | 2.4.0 | ok | 0.27 | 12.9 | 6 | `iq.log` (text), `iq.iqtree` (text), `iq.ckp.gz` (text), `iq.mldist` (text), +2 more |
| phylogeny | iqtree2_mfp_ufboot | iqtree2 | 2.4.0 | ok | 1.12 | 20.5 | 9 | `iq.log` (text), `iq.ckp.gz` (text), `iq.iqtree` (text), `iq.model.gz` (text), +5 more |
| phylogeny | ksnp4 | ksnp4 | 4.1 | ok | 60.11 | 3001.4 | 53 | `out/SNPs_all` (text), `out/SNPs_in_majority0.5` (text), `out/core_SNPs` (text), `out/ClusterInfo.SNPs_all.ML` (text), +49 more |
| phylogeny | mafft_auto_dna | mafft | 7.526 | ok | 1.57 | 30.2 | 1 | `aligned.fasta` (fasta) |
| phylogeny | mafft_linsi_protein | mafft | 7.526 | ok | 8.42 | 2336.8 | 1 | `aligned.fasta` (fasta) |
| phylogeny | muscle | muscle | 3.8.31 | ok | 193.82 | 956.2 | 1 | `aligned.fasta` (fasta) |
| phylogeny | parsnp_core | parsnp | 2.1.2 | failed | 0.77 | 49.3 | 0 |  |
| phylogeny | progressivemauve | progressivemauve | 1.2.0 | ok | 14.92 | 97.4 | 7 | `inputs/1206109.14.fna.sslist` (binary), `inputs/1239881.13.fna.sslist` (binary), `aln.xmfa` (fasta), `inputs/1297582.10.fna.sslist` (binary), +3 more |
| phylogeny | raxml_ng | raxml-ng | 1.2.2 | ok | 0.21 | 7.3 | 6 | `rng.raxml.reduced.phy` (index), `rng.raxml.log` (text), `rng.raxml.rba` (binary), `rng.raxml.bestModel` (text), +2 more |
| phylogeny | raxmlhpc | raxmlhpc | 8.2.12 | ok | 0.12 | 4.7 | 6 | `inputs/all_sites.fas.reduced` (text), `RAxML_info.run` (text), `RAxML_log.run` (text), `RAxML_bestTree.run` (newick), +2 more |
| readqc | bbduk_pe | bbduk | 38.95 | ok | 5.98 | 241.2 | 3 | `clean_2.fastq.gz` (fastq), `clean_1.fastq.gz` (fastq), `stats.txt` (text) |
| readqc | bbnorm_pe | bbnorm | 38.95 | ok | 13.0 | 12904.3 | 2 | `norm_2.fastq.gz` (fastq), `norm_1.fastq.gz` (fastq) |
| readqc | cutadapt_pe | cutadapt | 4.9 | ok | 0.92 | 51.9 | 4 | `out_2.fastq.gz` (fastq), `out_1.fastq.gz` (fastq), `cutadapt.json` (json), `cutadapt.log` (text) |
| readqc | fastp_pe | fastp | 1.3.2 | ok | 37.34 | 1162.7 | 4 | `trimmed_2.fastq.gz` (fastq), `trimmed_1.fastq.gz` (fastq), `fastp.html` (html), `fastp.json` (json) |
| readqc | fastp_se | fastp | 1.3.2 | ok | 10.89 | 1127.7 | 3 | `trimmed.fastq.gz` (fastq), `fastp.html` (html), `fastp.json` (json) |
| readqc | fastplong_ont | fastplong | 0.4.1 | ok | 0.77 | 200.1 | 3 | `fastplong.json` (json), `fastplong.html` (html), `filtered.fastq.gz` (fastq) |
| readqc | fastqc_ont | fastqc | 0.12.1 | ok | 3.42 | 397.4 | 2 | `fastqc/test_fastqc.html` (html), `fastqc/test_fastqc.zip` (archive) |
| readqc | fastqc_pe | fastqc | 0.12.1 | ok | 4.43 | 378.4 | 4 | `fastqc/test_2_fastqc.html` (html), `fastqc/test_1_fastqc.html` (html), `fastqc/test_2_fastqc.zip` (archive), `fastqc/test_1_fastqc.zip` (archive) |
| readqc | filtlong_ont | filtlong | 0.2.1 | ok | 2.87 | 235.5 | 1 | `filtered.fastq.gz` (fastq) |
| readqc | hostile_pe | hostile | 1.1.0 | ok | 17.2 | 429.1 | 3 | `out/test_1.clean_1.fastq.gz` (fastq), `out/test_2.clean_2.fastq.gz` (fastq), `hostile.json` (json) |
| readqc | multiqc_fastqc | multiqc | 1.25 | ok | 10.77 | 111.8 | 17 | `multiqc/multiqc_report.html` (html), `multiqc/multiqc_data/multiqc_data.json` (json), `multiqc/multiqc_data/fastqc_per_sequence_gc_content_plot_Percentages.txt` (text), `multiqc/multiqc_data/fastqc_per_sequence_gc_content_plot_Counts.txt` (text), +13 more |
| readqc | seqtk_fq2fa | seqtk | 1.4 | ok | 0.17 | 3.4 | 1 | `reads.fasta` (fasta) |
| readqc | seqtk_sample | seqtk | 1.4 | ok | 0.32 | 3.4 | 1 | `sub_1.fastq.gz` (fastq) |
| readqc | trim_galore_pe | trim_galore | 0.6.5d | ok | 6.08 | 32.7 | 6 | `out/test_2_val_2.fq.gz` (fastq), `out/test_1_val_1.fq.gz` (fastq), `out/test_2.fastq.gz_trimming_report.txt` (text), `out/test_1.fastq.gz_trimming_report.txt` (text), +2 more |
| readqc | trim_galore_pe_fastqc | trim_galore | 0.6.5d | ok | 12.44 | 287.4 | 10 | `out/test_2_val_2.fq.gz` (fastq), `out/test_1_val_1.fq.gz` (fastq), `out/test_2_val_2_fastqc.html` (html), `out/test_1_val_1_fastqc.html` (html), +6 more |
| typing_expression | bracken_est_abundance | bracken | 2.9 | ok | 0.06 | 11.5 | 2 | `bracken_report.txt` (text), `bracken.tsv` (text) |
| typing_expression | bracken_mini | bracken | 2.9 | failed | 0.11 | 8.7 | 0 |  |
| typing_expression | chewbbaca_allelecall | chewbbaca | 3.3.10 | ok | 23.23 | 183.4 | 291 | `schema/schema_seed/pre_computed/DNAtable1` (binary), `schema/schema_seed/pre_computed/PROTEINtable1` (binary), `calls/cds_coordinates.tsv` (text), `calls/results_contigsInfo.tsv` (text), +287 more |
| typing_expression | chewbbaca_createschema | chewbbaca | 3.3.10 | ok | 43.13 | 178.7 | 602 | `schema/cds_coordinates.tsv` (text), `schema/schema_seed/.genes_list` (binary), `schema/schema_seed/1297582-protein134.fasta` (fasta), `schema/schema_seed/short/1297582-protein134_short.fasta` (fasta), +598 more |
| typing_expression | freyja_demix | freyja | 1.5.1 | failed | 6.63 | 189.0 | 0 |  |
| typing_expression | freyja_demix_csv | freyja | 1.5.1 | ok | 15.9 | 1156.6 | 1 | `demix.tsv` (text) |
| typing_expression | freyja_variants | freyja | 1.5.1 | ok | 13.2 | 75.1 | 3 | `depths.tsv` (text), `variants.tsv` (text), `inputs/genome.fasta.fai` (text) |
| typing_expression | htseq_count | htseq-count | 2.0.9 | ok | 1.42 | 47.0 | 1 | `counts.tsv` (text) |
| typing_expression | kraken2_mini_pe | kraken2 | 2.1.2 | ok | 1.45 | 7.8 | 6 | `cl_1.fq` (fastq), `cl_2.fq` (fastq), `classified.tsv` (text), `report.txt` (text), +2 more |
| typing_expression | krona_text | krona | 2.8.1 | ok | 0.5 | 9.4 | 1 | `krona.html` (html) |
| typing_expression | mlst_hinfluenzae | mlst | 2.23.0 | ok | 13.31 | 129.9 | 2 | `mlst.json` (json), `mlst.tsv` (text) |
| typing_expression | pangolin | pangolin | 4.3.1 | failed | 3.22 | 88.9 | 0 |  |
| typing_expression | pangolin_skip_scorpio | pangolin | 4.3.1 | ok | 11.04 | 493.3 | 1 | `lineage_report.csv` (text) |
| typing_expression | primer3_generic | primer3 | 2.0 | ok | 0.12 | 7.0 | 1 | `primers.txt` (text) |
| typing_expression | stringtie_ballgown | stringtie | 2.2.1 | ok | 0.07 | 6.0 | 7 | `bg/transcripts.gtf` (gff), `bg/e_data.ctab` (text), `bg/t_data.ctab` (text), `gene_abund.tab` (text), +3 more |
| typing_expression | stringtie_guided | stringtie | 2.2.1 | ok | 0.11 | 6.0 | 2 | `assembled.gtf` (gff), `gene_abund.tab` (text) |

## Failures

### antismash_minimal (failed, exit 1)
```
    result = _run_antismash(sequence_file, options)
  File "/opt/patric-common/runtime/antismash-7-1-0-1/lib/python3.10/site-packages/antismash/main.py", line 720, in _run_antismash
    check_prerequisites(options.all_enabled_modules, options)
  File "/opt/patric-common/runtime/antismash-7-1-0-1/lib/python3.10/site-packages/antismash/main.py", line 617, in check_prerequisites
    raise RuntimeError("Modules failing prerequisites")
RuntimeError: Modules failing prerequisites
```

### bracken_mini (failed, exit 2)
```
python3: can't open file '/opt/patric-common/runtime/bin/src/est_abundance.py': [Errno 2] No such file or directory
```

### flye_nano_sarscov2 (failed, exit 1)
```
[2026-11-02 15:40:11] INFO: Assembled 0 disjointigs
[2026-11-02 15:40:11] INFO: Generating sequence
[2026-11-02 15:40:12] INFO: Filtering contained disjointigs
[2026-11-02 15:40:12] INFO: Contained seqs: 0
[2026-11-02 15:40:12] ERROR: No disjointigs were assembled - please check if the read type and genome size parameters are correct
[2026-11-02 15:40:12] ERROR: Pipeline aborted
```

### freyja_demix (failed, exit 1)
```
  File "/opt/patric-common/runtime/frejya-1.5.1/lib/python3.14/site-packages/pandas/io/feather_format.py", line 149, in read_feather
    import_optional_dependency("pyarrow")
    ~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^
  File "/opt/patric-common/runtime/frejya-1.5.1/lib/python3.14/site-packages/pandas/compat/_optional.py", line 161, in import_optional_dependency
    raise ImportError(msg) from err
ImportError: `Import pyarrow` failed.  Use pip or conda to install the pyarrow package.
```

### pangolin (failed, exit 1)
```
  File "/opt/patric-common/runtime/pangolin/lib/python3.8/concurrent/futures/thread.py", line 57, in run
Shutting down, this might take some time.
Exiting because a job execution failed. Look above for error message
Shutting down, this might take some time.
Exiting because a job execution failed. Look above for error message
Complete log: .snakemake/log/2026-11-02T154441.909702.snakemake.log
```

### parsnp_core (failed, exit 1)
```
15:38:22 - [1;37mINFO[0m - |--Parsnp 2.1.2--|

15:38:22 - [1;31mCRITICAL[0m - harvesttools not in system path!
```

### samtools_consensus (failed, exit 1)
```
[main] unrecognized command 'consensus'
```

