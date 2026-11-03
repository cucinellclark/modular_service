# BV-BRC invocations of `multiqc` (multiqc)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 12 hunk(s) in 6 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/report.py`
- `pybin/run_rnaseq.py`
- `workflows/bvbrc_SARS2Wastewater/snakefile/stats_snakefile`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/16s_analysis`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/microbiome_analysis`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/pathogen_analysis`

## `pybin/run_rnaseq.py:204`

```
    198      genome_data.set_recipe(map_args.recipe)
    199      if genome.get_genome_type() == "bacteria":
    200          genome_data.set_genome(genome)
    201          genome_data.run_queries(output_dir, session)
    202          genome_data.create_system_figures(output_dir)
    203  
>>  204      # call multiqc without any adjustments
    205      if not map_args.disable_reports:
    206          report_manager = report.ReportManager()
    207          # number of samples and conditions
    208          report_stats = {}
    209          sample_count = 0
    210          condition_count = 0
    211          for condition in experiment_dict:
    212              sample_count += len(experiment_dict[condition].get_sample_list())
    213              if condition != "no_condition":
    214                  condition_count += 1
    215          report_stats["num_samples"] = sample_count
    216          report_stats["num_conditions"] = condition_count
```

## `workflows/bvbrc_SARS2Wastewater/snakefile/stats_snakefile:6`

```
      1  from snakemake.utils import validate
      2  
      3  msg = "snakefile command recieved - STATS/Wrap up \n"
      4  sys.stderr.write(msg)
      5  
>>    6  ruleorder: set_aggregate_command > set_freyja_vis > set_timeseries_plot > multiqc
      7  ### Define wildcards ###
      8  pe_zpd_samples = glob_wildcards("staging/pe_reads/{sample}_R{read_num}.fastq.gz").sample
      9  pe_unzpd_samples = glob_wildcards("staging/pe_reads/{sample}_R{read_num}.fastq").sample
     10  se_zpd_samples = glob_wildcards("staging/se_reads/{sample}.fastq.gz").sample
     11  se_unzpd_samples = glob_wildcards("staging/se_reads/{sample}.fastq").sample
     12  samples = pe_zpd_samples+ pe_unzpd_samples + se_zpd_samples + se_unzpd_samples
     13  
     14  ### Define functions for global handelers: Onstart, onsuccess and onerror ###
     15  # Define the onstart handler
     16  def onstart(samples):
     17      print(f"Starting workflow for {wildcards}")
     18  # Define the onsuccess handler
```

## `lib/report.py:19`

```
     13      def run_multiqc(self, output_path):
     14          debug_multiqc = False
     15          remove_data_dir = True
     16          force_overwrite = True
     17          report_name = os.path.join(output_path, "multiqc_report")
     18          multiqc_cmd = [
>>   19              "multiqc",
     20              "--flat",
     21              "-o",
     22              ".",
     23              "-n",
     24              report_name,
     25              "-t",
     26              "simple",
     27              ".",
     28          ]
     29          if remove_data_dir:
     30              multiqc_cmd += ["--no-data-dir"]
     31          if force_overwrite:
```

## `workflows/bvbrc_SARS2Wastewater/snakefile/stats_snakefile:172`

```
    166          tmp_multiqc_dir = directory('output/SARS2-Wastewater-Analysis-BVBRC_multiqc_report_data')
    167      output:
    168          'output/SARS2-Wastewater-Analysis-BVBRC_multiqc_report.html',
    169          cl_multiqc_dir = directory("clean_up/SARS2-Wastewater-Analysis-BVBRC_multiqc_report_data")
    170      shell:
    171          """
>>  172          multiqc --version
    173  
>>  174          multiqc clean_up/. output/. \
    175              -c {input.multiqc_config} \
    176              -o {params.landing_dir} --fullnames \
    177              -f
    178          
    179          mkdir -p {output.cl_multiqc_dir}
    180  
    181          mv {params.tmp_multiqc_dir} {output.cl_multiqc_dir}
    182          """
    183  
    184  rule write_out_versions:
    185      params:
    186          primer_tp = primer_type,
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/16s_analysis:225`

```
    219          tmp_multiqc_report = "clean_up/multiqc_data/Taxonomic-Classification-Service-BVBRC_multiqc_report.html"
    220      output:
    221          out_multiqc_report = "output/Taxonomic-Classification-Service-BVBRC_multiqc_report.html",
    222          cl_multiqc_dir = directory('clean_up/multiqc_data')
    223      shell:
    224          '''
>>  225          multiqc --version
    226  
    227          mkdir -p {output.cl_multiqc_dir}
    228  
>>  229          multiqc {params.landing_dir} \
    230              -c {input.multiqc_config} \
    231              -o {output.cl_multiqc_dir} --fullnames \
    232              -f \
    233              --comment "This report contains information about the raw fastq files, host removed fastq files and kraken2 reports."
    234          
    235  
    236          mv {params.tmp_multiqc_report} {output.out_multiqc_report}
    237          '''
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/microbiome_analysis:216`

```
    210          tmp_multiqc_report = "clean_up/multiqc_data/Taxonomic-Classification-Service-BVBRC_multiqc_report.html"
    211      output:
    212          out_multiqc_report = "output/Taxonomic-Classification-Service-BVBRC_multiqc_report.html",
    213          cl_multiqc_dir = directory('clean_up/multiqc_data')
    214      shell:
    215          '''
>>  216          multiqc --version
    217  
    218          mkdir -p {output.cl_multiqc_dir}
    219  
>>  220          multiqc {params.landing_dir} \
    221              -c {input.multiqc_config} \
    222              -o {output.cl_multiqc_dir} --fullnames \
    223              -f \
    224              --comment "This report contains information about the raw fastq files, host removed fastq files and kraken2 reports."
    225          
    226  
    227          mv {params.tmp_multiqc_report} {output.out_multiqc_report}
    228          '''
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pathogen_analysis:115`

```
    109          tmp_multiqc_report = "clean_up/multiqc_data/Taxonomic-Classification-Service-BVBRC_multiqc_report.html"
    110      output:
    111          out_multiqc_report = "output/Taxonomic-Classification-Service-BVBRC_multiqc_report.html",
    112          cl_multiqc_dir = directory('clean_up/multiqc_data')
    113      shell:
    114          '''
>>  115          multiqc --version
    116  
    117          mkdir -p {output.cl_multiqc_dir}
    118  
>>  119          multiqc {params.landing_dir} \
    120              -c {input.multiqc_config} \
    121              -o {output.cl_multiqc_dir} --fullnames \
    122              -f \
    123              --comment "This report contains information about the raw fastq files, host removed fastq files and kraken2 reports."
    124  
    125          mv {params.tmp_multiqc_report} {output.out_multiqc_report}
    126          '''
```

## `lib/report.py:77`

```
     71          if 'reads_failure' in report_stats and report_stats['reads_failure']:
     72              report_lines.append("<section>\n<h2>Reads Failure</h2>") 
     73              failure_summary = self.create_reads_failure_text(report_stats)
     74              report_lines.append(failure_summary)
     75              report_lines.append("</section>")
     76  
>>   77          # Link to multiqc report for basic sample summary statistics
     78          report_lines.append("<section>\n<h2>MultiQC Report Link</h2>")
     79          report_lines.append(self.create_multiqc_link(workspace_dir))
     80          report_lines.append("</section>")
     81  
     82          # Sample IDs and their conditions that have issues
     83          report_lines.append("<section>\n<h2>Sample Summary Table</h2>")
     84          report_sample_table = self.create_sample_table(experiment_dict, genome)
     85          report_lines.append(report_sample_table)
     86          report_lines.append("</section>")
     87  
     88          # Any figures in report_images
     89          # if genome.get_genome_type() == 'bacteria':
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/16s_analysis:30`

```
     24      'clean_up/multiqc_data',
     25      ]
     26  
     27  ## this adds felxiblity for one sample (1 single end fq or just one paired end, 2 fqs)
     28  ## multisample comparison and visualizations will either fail or be redundant if only one sample present
     29  if len(se_samples) == 1 and len(pe_samples) == 0 or len(se_samples) == 0 and len(pe_samples) == 2:
>>   30      ruleorder: bracken_abundance_estimation > calculate_alpha_diversity > merge_alpha_diversity_stats > generate_sample_krona_plots > generate_sankey_plots > multiqc 
     31      msg = "preforming analysis for only one sample - DOES NOT INCLUDE multisample_comparison.html \n"
     32      sys.stderr.write(msg)
     33  else:
>>   34      ruleorder: bracken_abundance_estimation > calculate_alpha_diversity > merge_alpha_diversity_stats > calculate_beta_diversity > generate_sample_krona_plots > generate_multisample_krona_plots > generate_sankey_plots > multisample_comp_table > clean_up_multisample_html_files > multiqc
     35      msg = "preforming analysis for multiple samples - INCLUDES multisample_comparison.html \n"
     36      sys.stderr.write(msg)
     37      rule_all_list.append('output/multisample_comparison.html')
     38      rule_all_list.append('clean_up/multisample_comparison_files')
     39      rule_all_list.append('output/multisample_krona.html')
     40      rule_all_list.append('output/beta_diversity.csv')
     41  
     42  rule all:
     43      input:
     44          rule_all_list
     45  rule bracken_abundance_estimation:
     46      input:
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/microbiome_analysis:27`

```
     21          'output/Taxonomic-Classification-Service-BVBRC_multiqc_report.html',
     22          'clean_up/multiqc_data',
     23          ]
     24  ## this adds felxiblity for one sample (1 single end fq or just one paired end, 2 fqs)
     25  ## multisample comparison and visualizations will either fail or be redundant if only one sample present
     26  if len(se_samples) == 1 and len(pe_samples) == 0 or len(se_samples) == 0 and len(pe_samples) == 2:
>>   27      ruleorder: bracken_abundance_estimation > calculate_alpha_diversity > merge_alpha_diversity_stats > generate_sample_krona_plots > generate_sankey_plots > multiqc 
     28      msg = "preforming analysis for only one sample - DOES NOT INCLUDE multisample_comparison.html, multisample_krona.html \n"
     29      sys.stderr.write(msg)
     30  else:
>>   31      ruleorder: bracken_abundance_estimation > calculate_alpha_diversity > merge_alpha_diversity_stats > calculate_beta_diversity > generate_sample_krona_plots > generate_multisample_krona_plots > generate_sankey_plots > multisample_comp_table > clean_up_multisample_html_files > multiqc
     32      msg = "preforming analysis for multiple samples - INCLUDES multisample_comparison.html, multisample_krona.html \n"
     33      sys.stderr.write(msg)
     34      rule_all_list.append('output/multisample_comparison.html')
     35      rule_all_list.append('clean_up/multisample_comparison_files')
     36      rule_all_list.append('output/multisample_krona.html')
     37      rule_all_list.append('output/beta_diversity.csv')
     38  
     39  
     40  rule all:
     41      input:
     42          rule_all_list
     43  
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pathogen_analysis:20`

```
     14          expand('clean_up/{sample}_sankey_files', sample=samples),
     15          "output/Taxonomic-Classification-Service-BVBRC_multiqc_report.html"
     16          ]
     17  ## this adds felxiblity for one sample (1 single end fq or just one paired end, 2 fqs)
     18  ## multisample comparison and visualizations will either fail or be redundant if only one sample present
     19  if len(se_samples) == 1 and len(pe_samples) == 0 or len(se_samples) == 0 and len(pe_samples) == 2:
>>   20      ruleorder: generate_sample_krona_plots > generate_multisample_krona_plots > generate_sankey_plots > multiqc
     21      msg = "preforming analysis for only one sample - DOES NOT INCLUDE MULTISAMPLE_COMPARISON.HTML \n"
     22      sys.stderr.write(msg)
     23  
     24  else:
>>   25      ruleorder: generate_sample_krona_plots > generate_multisample_krona_plots > generate_sankey_plots > multisample_comp_table > clean_up_multisample_html_files > multiqc
     26      msg = "preforming analysis for multiple samples - INCLUDES multisample_comparison.html, multisample_krona.html \n"
     27      sys.stderr.write(msg)
     28      rule_all_list.append('output/multisample_comparison.html')
     29      rule_all_list.append('output/multisample_krona.html')
     30      rule_all_list.append('clean_up/multisample_comparison_files')
     31  
     32  
     33  rule all:
     34      input:
     35          rule_all_list
     36  
     37  rule generate_sample_krona_plots:
```

## `lib/report.py:300`

```
    294          bvbrc_ref = "Introducing the Bacterial and Viral Bioinformatics Resource Center (BV-BRC): a resource combining PATRIC, IRD and ViPR. \
    295                      Olson RD, Assaf R, Brettin T, Conrad N, Cucinell C, Davis JJ, Dempsey DM, Dickerman A, Dietrich EM, Kenyon RW, Kuscuoglu M, \
    296                      Lefkowitz EJ, Lu J, Machi D, Macken C, Mao C, Niewiadomska A, Nguyen M, Olsen GJ, Overbeek JC, Parrello B, Parrello V, Porter JS, \
    297                      Pusch GD, Shukla M, Singh I, Stewart L, Tan G, Thomas C, VanOeffelen M, Vonstein V, Wallace ZS, Warren AS, Wattam AR, Xia F, Yoo H, \
    298                      Zhang Y, Zmasek CM, Scheuermann RH, Stevens RL. Nucleic Acids Res. 2022 Nov 9:gkac1003. doi: 10.1093/nar/gkac1003. PMID: 36350631"
    299          reference_list.append("<li>" + bvbrc_ref + "</li>")
>>  300          # multiqc
    301          multiqc_ref = "MultiQC: Summarize analysis results for multiple tools and samples in a single report. Philip Ewels, Måns Magnusson, Sverker Lundin \
    302                          and Max Käller. Bioinformatics (2016) doi: 10.1093/bioinformatics/btw354 PMID: 27312411 "
    303          reference_list.append("<li>" + multiqc_ref + "</li>")
    304          # fastqc
    305          fastqc_ref = "Andrews, S. (2010). FastQC:  A Quality Control Tool for High Throughput Sequence Data [Online]. Available online at: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/"
    306          reference_list.append("<li>" + fastqc_ref + "</li>")
    307          # trimgalore
    308          trimgalore_ref = "FelixKrueger. (n.d.). Felixkrueger/Trimgalore: A wrapper around Cutadapt and FASTQC to consistently apply adapter and quality \
    309                          trimming to FASTQ files, with extra functionality for RRBS Data. GitHub. https://github.com/FelixKrueger/TrimGalore"
    310          reference_list.append("<li>" + trimgalore_ref + "</li>")
    311          # seqtk
    312          seqtk_ref = "lh3. (n.d.). Lh3/SEQTK: Toolkit for processing sequences in FASTA/Q Formats. GitHub. https://github.com/lh3/seqtk"
```

