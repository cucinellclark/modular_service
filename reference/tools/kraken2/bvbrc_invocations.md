# BV-BRC invocations of `kraken2` (kraken2)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 13 hunk(s) in 9 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/TaxonomicClassification/Report.tt`
- `workflows/bvbrc_taxonomic_classification_2/scripts/pavian_multisample_comparsion.R`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/16s_analysis`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/microbiome_analysis`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/pathogen_analysis`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing_16s`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing_16s`

## `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing:26`

```
     20  # update rule all according to saving the classified and unclassified sequences in the Kraken2 command
     21  if save_classified == True:
     22      cf = "--classified-out"
     23      co = "{sample}_classified_reads.fastq"
     24      co_gz = "output/{sample}/kraken_output/{sample}_classified_reads.fastq.gz"
     25      rule_all_list.append(expand("output/{sample}/kraken_output/{sample}_classified_reads.fastq.gz", sample=samples))
>>   26      msg = "Adding save classified sequences to kraken2 command. \n"
     27      sys.stderr.write(msg)
     28  else:
     29      cf = ""
     30      co = ""
     31      co_gz = ""
     32  
     33  if save_unclassified == True:
     34      ucf = "--unclassified-out"
     35      uco = "{sample}_unclassified_reads.fastq"
     36      uco_gz = "output/{sample}/kraken_output/{sample}_unclassified_reads.fastq.gz"
     37      rule_all_list.append(expand("output/{sample}/kraken_output/{sample}_unclassified_reads.fastq.gz", sample=samples))
>>   38      msg = "Adding save unclassified sequences to kraken2 command. \n"
     39      sys.stderr.write(msg)
     40  else:
     41      ucf = ""
     42      uco = ""
     43      uco_gz = ""
     44  
     45  
     46  host_dict = {"homo_sapiens": "GCF_000001405.39_GRCh38.p13_genomic",
     47      "mus_musculus": "GCF_000001635.26_GRCm38.p6_genomic",
     48      "rattus_norvegicus" : "GCF_000001895.5_Rnor_6.0_genomic",
     49      "caenorhabditis_elegans" : "GCF_000002985.6_WBcel235_genomic",
     50      "drosophila_melanogaster_strain" : "GCF_000001215.4_Release_6_plus_ISO1_MT_genomic",
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing_16s:27`

```
     21  # update rule all according to saving the classified and unclassified sequences in the Kraken2 command
     22  if save_classified == True:
     23      cf = "--classified-out"
     24      co = "{sample}_classified_reads.fastq"
     25      co_gz = "output/{sample}/kraken_output/{sample}_classified_reads.fastq.gz"
     26      rule_all_list.append(expand("output/{sample}/kraken_output/{sample}_classified_reads.fastq.gz", sample=samples))
>>   27      msg = "Adding save classified sequences to kraken2 command. \n"
     28      sys.stderr.write(msg)
     29  else:
     30      cf = ""
     31      co = ""
     32      co_gz = ""
     33  
     34  if save_unclassified == True:
     35      ucf = "--unclassified-out"
     36      uco = "{sample}_unclassified_reads.fastq"
     37      uco_gz = "output/{sample}/kraken_output/{sample}_unclassified_reads.fastq.gz"
     38      rule_all_list.append(expand("output/{sample}/kraken_output/{sample}_unclassified_reads.fastq.gz", sample=samples))
>>   39      msg = "Adding save unclassified sequences to kraken2 command. \n"
     40      sys.stderr.write(msg)
     41  else:
     42      ucf = ""
     43      uco = ""
     44      uco_gz = ""
     45  
     46  
     47  rule all:
     48      input:
     49          rule_all_list
     50  
     51  rule fastqc_raw_reads:
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing:30`

```
     24      co = "{sample}_classified_reads#.fastq"
     25      co_1 = "{sample}_classified_reads_1.fastq"
     26      co_2 = "{sample}_classified_reads_2.fastq"
     27      co_r1 = "output/{sample}/kraken_output/{sample}_classified_reads_R1.fastq.gz"
     28      co_r2 = "output/{sample}/kraken_output/{sample}_classified_reads_R2.fastq.gz"
     29      rule_all_list.append(expand("output/{sample}/kraken_output/{sample}_classified_reads_R{read_num}.fastq.gz", sample=samples, read_num=read_nums))
>>   30      msg = "Adding save classified sequences to kraken2 command. \n"
     31      sys.stderr.write(msg)
     32  else:
     33      cf = ""
     34      co = ""
     35      co_1 = ""
     36      co_2 = " "
     37      co_r1 = ""
     38      co_r2 = " "
     39  
     40  if save_unclassified == True:
     41      ucf = "--unclassified-out"
     42      uco = "{sample}_unclassified_reads#.fastq"
     43      uco_1 = "{sample}_unclassified_reads_1.fastq"
     44      uco_2 = "{sample}_unclassified_reads_2.fastq"
     45      uco_r1 = "output/{sample}/kraken_output/{sample}_unclassified_reads_R1.fastq.gz"
     46      uco_r2 = "output/{sample}/kraken_output/{sample}_unclassified_reads_R2.fastq.gz"
     47      rule_all_list.append(expand("output/{sample}/kraken_output/{sample}_unclassified_reads_R{read_num}.fastq.gz", sample=samples, read_num=read_nums))
>>   48      msg = "Adding save unclassified sequences to kraken2 command. \n"
     49      sys.stderr.write(msg)
     50  else:
     51      ucf = ""
     52      uc = ""
     53      uco = ""
     54      uco_1 = ""
     55      uco_2 = ""
     56      uco_r1 = ""
     57      uco_r2 = " "
     58  
     59  host_dict = {"homo_sapiens": "GCF_000001405.39_GRCh38.p13_genomic",
     60      "mus_musculus": "GCF_000001635.26_GRCm38.p6_genomic",
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing_16s:33`

```
     27      co = "{sample}_classified_reads#.fastq"
     28      co_1 = "{sample}_classified_reads_1.fastq"
     29      co_2 = "{sample}_classified_reads_2.fastq"
     30      co_r1 = "output/{sample}/kraken_output/{sample}_classified_reads_R1.fastq.gz"
     31      co_r2 = "output/{sample}/kraken_output/{sample}_classified_reads_R2.fastq.gz"
     32      rule_all_list.append(expand("output/{sample}/kraken_output/{sample}_classified_reads_R{read_num}.fastq.gz", sample=samples, read_num=read_nums))
>>   33      msg = "Adding save classified sequences to kraken2 command. \n"
     34      sys.stderr.write(msg)
     35  else:
     36      cf = ""
     37      co = ""
     38      co_1 = ""
     39      co_2 = " "
     40      co_r1 = ""
     41      co_r2 = " "
     42  
     43  if save_unclassified == True:
     44      ucf = "--unclassified-out"
     45      uco = "{sample}_unclassified_reads#.fastq"
     46      uco_1 = "{sample}_unclassified_reads_1.fastq"
     47      uco_2 = "{sample}_unclassified_reads_2.fastq"
     48      uco_r1 = "output/{sample}/kraken_output/{sample}_unclassified_reads_R1.fastq.gz"
     49      uco_r2 = "output/{sample}/kraken_output/{sample}_unclassified_reads_R2.fastq.gz"
     50      rule_all_list.append(expand("output/{sample}/kraken_output/{sample}_unclassified_reads_R{read_num}.fastq.gz", sample=samples, read_num=read_nums))
>>   51      msg = "Adding save unclassified sequences to kraken2 command. \n"
     52      sys.stderr.write(msg)
     53  else:
     54      ucf = ""
     55      uc = ""
     56      uco = ""
     57      uco_1 = ""
     58      uco_2 = ""
     59      uco_r1 = ""
     60      uco_r2 = " "
     61  
     62  
     63  rule all:
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing:196`

```
    190          k2report = 'output/{sample}/kraken_output/{sample}_k2_report.txt',
    191      threads: 16
    192      shell:
    193          '''
    194          mkdir -p {params.kraken_dir}
    195  
>>  196          kraken2 --db {params.database} \
    197              --threads {threads} \
    198              --minimum-hit-groups 3 \
    199              --report-minimizer-data \
    200              --memory-mapping \
    201              {params.classified_flag} \
    202              {params.classified_out} \
    203              {params.unclassified_flag} \
    204              {params.unclassified_out} \
    205              --report {output.k2report} \
    206              --confidence {params.ci} \
    207              --paired {input.kraken2_input_r1} {input.kraken2_input_r2} \
    208              --output {output.k2_output}
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing_16s:149`

```
    143          k2report = 'output/{sample}/kraken_output/{sample}_k2_report.txt',
    144      threads: 16
    145      shell:
    146          '''
    147          mkdir -p {params.kraken_dir}
    148  
>>  149          kraken2 --db {params.database} \
    150              --threads {threads} \
    151              --minimum-hit-groups 3 \
    152              --report-minimizer-data \
    153              --memory-mapping \
    154              {params.classified_flag} \
    155              {params.classified_out} \
    156              {params.unclassified_flag} \
    157              {params.unclassified_out} \
    158              --report {output.k2report} \
    159              --confidence {params.ci} \
    160              --paired {input.kraken2_input_r1} {input.kraken2_input_r2} \
    161              --output {output.k2_output}
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing:173`

```
    167          k2report = 'output/{sample}/kraken_output/{sample}_k2_report.txt'
    168      threads: 16
    169      shell:
    170          '''
    171          mkdir -p {params.kraken_dir}
    172  
>>  173          kraken2 --db {params.database} \
    174              --threads {threads} \
    175              --minimum-hit-groups 3 \
    176              --report-minimizer-data \
    177              --memory-mapping \
    178              {params.classified_flag} \
    179              {params.classified_fq} \
    180              {params.unclassified_flag} \
    181              {params.unclassified_fq} \
    182              --report {output.k2report} \
    183              {input.kraken2_input} \
    184              --confidence {params.ci} \
    185              --output {output.k2_output}
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing_16s:132`

```
    126          k2report = 'output/{sample}/kraken_output/{sample}_k2_report.txt'
    127      threads: 16
    128      shell:
    129          '''
    130          mkdir -p {params.kraken_dir}
    131  
>>  132          kraken2 --db {params.database} \
    133              --threads {threads} \
    134              --minimum-hit-groups 3 \
    135              --report-minimizer-data \
    136              --memory-mapping \
    137              {params.classified_flag} \
    138              {params.classified_fq} \
    139              {params.unclassified_flag} \
    140              {params.unclassified_fq} \
    141              --report {output.k2report} \
    142              {input.kraken2_input} \
    143              --confidence {params.ci} \
    144              --output {output.k2_output}
```

## `lib/Bio/P3/TaxonomicClassification/Report.tt:85`

```
     79  <li> NCBI taxonomic ID number
     80  <li> Indented scientific name
     81  </ol>
     82  <p>
     83  You may find documentation on the report format 
     84  <a href="https://ccb.jhu.edu/software/kraken2/index.shtml?t=manual#sample-report-output-format" target="_blank">
>>   85  in the kraken2 manual</a>.
     86  
     87  <p>
     88  The classification was performed by the <a target="_blank" href="https://ccb.jhu.edu/software/kraken2/index.shtml">
     89  Kraken2 taxonomic sequence classification system</a>. The interactive chart was generated by
     90  <a target="_blank" href="https://github.com/marbl/Krona/wiki">Krona</a>.
```

## `workflows/bvbrc_taxonomic_classification_2/scripts/pavian_multisample_comparsion.R:98`

```
     92  
     93  ## apply table coloring/style to the data 
     94  multi_sample_table <- DT::datatable(reads_zscore_df, rownames = FALSE,
     95                  filter = "bottom", selection = "single", escape = FALSE,
     96                  caption = "This is a tabular view of the identification results from multiple samples.
     97    The goal is to identify which microbes unique within each sample or common amongst all samples. The values in the
>>   98    table are the robust z-score calculated from the from the kraken2 report. The robust z-score is the median absolute
     99    deviation. This method is chosen to reduce impact from outliers in the data, providing a more reliable measure of
    100    relative position within the data distribution. 
    101    
    102     When intpreting the robust z-score consider that a positive robust
    103    z-score indicates that t the number of fragments assigned to that taxa was above the median or central tendancy of the
    104    data. Conversly, a negitive robust z-score indicates that the number of fragments assigned to that taxa was below the
    105    median or central tendancy of the data. The magnitude (represented as the value of the z-score) indicates the distance of
    106    the data point from the central tendency in terms of the robust measure of dispersion.
    107  
    108     The intensity of the red for each cell is calculated by putting the read scores into quantiles probabilites ranging from
    109    0.05 to 0.95 with an increment of 0.05. This means that the intensity of the color represents the relative position in the
    110     datasets disribution for that datapoint. 
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/16s_analysis:233`

```
    227          mkdir -p {output.cl_multiqc_dir}
    228  
    229          multiqc {params.landing_dir} \
    230              -c {input.multiqc_config} \
    231              -o {output.cl_multiqc_dir} --fullnames \
    232              -f \
>>  233              --comment "This report contains information about the raw fastq files, host removed fastq files and kraken2 reports."
    234          
    235  
    236          mv {params.tmp_multiqc_report} {output.out_multiqc_report}
    237          '''
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/microbiome_analysis:224`

```
    218          mkdir -p {output.cl_multiqc_dir}
    219  
    220          multiqc {params.landing_dir} \
    221              -c {input.multiqc_config} \
    222              -o {output.cl_multiqc_dir} --fullnames \
    223              -f \
>>  224              --comment "This report contains information about the raw fastq files, host removed fastq files and kraken2 reports."
    225          
    226  
    227          mv {params.tmp_multiqc_report} {output.out_multiqc_report}
    228          '''
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pathogen_analysis:123`

```
    117          mkdir -p {output.cl_multiqc_dir}
    118  
    119          multiqc {params.landing_dir} \
    120              -c {input.multiqc_config} \
    121              -o {output.cl_multiqc_dir} --fullnames \
    122              -f \
>>  123              --comment "This report contains information about the raw fastq files, host removed fastq files and kraken2 reports."
    124  
    125          mv {params.tmp_multiqc_report} {output.out_multiqc_report}
    126          '''
```

