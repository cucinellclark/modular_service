# BV-BRC invocations of `bracken` (bracken)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 4 hunk(s) in 2 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `workflows/bvbrc_taxonomic_classification_2/snakefile/16s_analysis`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/microbiome_analysis`

## `workflows/bvbrc_taxonomic_classification_2/snakefile/microbiome_analysis:130`

```
    124          beta_diversity_csv = 'output/beta_diversity.csv',
    125          beta_diversity_html= 'output/beta_stats_heatmap.html'
    126      shell:
    127          '''
    128          beta_diversity.py \
    129          --input {input.bracken_outputs} \
>>  130          --type bracken \
    131          --level S \
    132          > {params.temp_beta_diversity_csv}
    133          
    134          python3 {params.beta_stats_cleanup_script} {params.temp_beta_diversity_csv} {output.beta_diversity_csv} {output.beta_diversity_html}
    135          '''
    136  
    137  rule generate_sample_krona_plots:
    138      input:
    139          bracken_report = 'output/{sample}/bracken_output/{sample}_bracken_report.txt'
    140      output:
    141          krona_html = 'output/{sample}_krona.html'
    142      shell:
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/16s_analysis:61`

```
     55          bracken_output = 'output/{sample}/bracken_output/{sample}_bracken_output.txt',
     56          bracken_report = 'output/{sample}/bracken_output/{sample}_bracken_report.txt'
     57      shell:
     58          '''
     59          mkdir -p {params.bracken_dir}
     60  
>>   61          est_abundance.py \
     62              -i {input.k2report} \
     63              -k {params.kmer_distr} \
     64              -o {output.bracken_output} \
     65              -l {params.level_of_abundance_estimation} \
     66              --out-report {output.bracken_report} \
     67              -t 10
     68          '''
     69  
     70  rule calculate_alpha_diversity:
     71      input:
     72          bracken_output = 'output/{sample}/bracken_output/{sample}_bracken_output.txt',
     73      params:
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/16s_analysis:132`

```
    126          beta_diversity_csv = 'output/beta_diversity.csv',
    127          beta_diversity_html= 'output/beta_stats_heatmap.html'
    128      shell:
    129          '''
    130          beta_diversity.py \
    131          --input {input.bracken_outputs} \
>>  132          --type bracken \
    133          --level {params.level_of_abundance_estimation} \
    134          > {params.temp_beta_diversity_csv}
    135          
    136          python3 {params.beta_stats_cleanup_script} {params.temp_beta_diversity_csv} {output.beta_diversity_csv} {output.beta_diversity_html}
    137          '''
    138  
    139  rule generate_sample_krona_plots:
    140      input:
    141          bracken_report = 'output/{sample}/bracken_output/{sample}_bracken_report.txt'
    142      output:
    143          krona_file = 'output/{sample}/bracken_output/{sample}.krona',
    144          krona_html = 'output/{sample}_krona.html'
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/microbiome_analysis:60`

```
     54          bracken_output = 'output/{sample}/bracken_output/{sample}_bracken_output.txt',
     55          bracken_report = 'output/{sample}/bracken_output/{sample}_bracken_report.txt'
     56      shell:
     57          '''
     58          mkdir -p {params.bracken_dir}
     59  
>>   60          est_abundance.py \
     61              -i {input.k2report} \
     62              -k {params.kmer_distr} \
     63              -o {output.bracken_output} \
     64              -l {params.level_of_abundance_estimation} \
     65              --out-report {output.bracken_report} \
     66              -t 10
     67          '''
     68  
     69  rule calculate_alpha_diversity:
     70      input:
     71          bracken_output = 'output/{sample}/bracken_output/{sample}_bracken_output.txt',
     72      params:
```

