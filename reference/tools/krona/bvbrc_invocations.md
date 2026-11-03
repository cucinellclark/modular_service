# BV-BRC invocations of `ktImportText` (krona)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 3 hunk(s) in 3 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `workflows/bvbrc_taxonomic_classification_2/snakefile/16s_analysis`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/microbiome_analysis`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/pathogen_analysis`

## `workflows/bvbrc_taxonomic_classification_2/snakefile/microbiome_analysis:144`

```
    138      input:
    139          bracken_report = 'output/{sample}/bracken_output/{sample}_bracken_report.txt'
    140      output:
    141          krona_html = 'output/{sample}_krona.html'
    142      shell:
    143          '''
>>  144          ktImportTaxonomy -t 5 -m 3 \
    145              {input.bracken_report} \
    146              -o {output.krona_html}
    147          '''
    148  
    149  rule generate_multisample_krona_plots:
    150      input:
    151          bracken_reports = set(expand('output/{sample}/bracken_output/{sample}_bracken_report.txt', sample = samples))
    152      output:
    153          set_krona_plot = 'output/multisample_krona.html'
    154      shell:
    155          '''
>>  156          ktImportTaxonomy -t 5 -m 3 \
    157              {input.bracken_reports} \
    158              -o {output.set_krona_plot}
    159          '''
    160  
    161  rule generate_sankey_plots:
    162      input:
    163          bracken_report = 'output/{sample}/bracken_output/{sample}_bracken_report.txt'
    164      params:
    165          sankey_script = os.path.join(workflow_dir, "scripts/sankey_plot_gen.R"),
    166          tmp_sankey_dir = directory('output/{sample}_sankey_files/')
    167      output:
    168          sankey_plot = 'output/{sample}_sankey.html',
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pathogen_analysis:44`

```
     38      input:
     39          k2report = 'output/{sample}/kraken_output/{sample}_k2_report.txt'
     40      output:
     41          krona_html = 'output/{sample}_krona.html'
     42      shell:
     43          '''
>>   44          ktImportTaxonomy -t 7 -m 3 \
     45              {input.k2report} \
     46              -o {output.krona_html}
     47          '''
     48  
     49  rule generate_multisample_krona_plots:
     50      input:
     51          k_reports = set(expand('output/{sample}/kraken_output/{sample}_k2_report.txt', sample=samples))
     52      output:
     53          set_krona_plot = 'output/multisample_krona.html'
     54      shell:
     55          '''
>>   56          ktImportTaxonomy -t 7 -m 3 \
     57              {input.k_reports} \
     58              -o {output.set_krona_plot}
     59          '''
     60  
     61  rule generate_sankey_plots:
     62      input:
     63          k2report = 'output/{sample}/kraken_output/{sample}_k2_report.txt',
     64      params:
     65          sankey_script = os.path.join(workflow_dir, "scripts/sankey_plot_gen.R"),
     66          tmp_sankey_dir = directory('output/{sample}_sankey_files/')
     67      output:
     68          sankey_plot = 'output/{sample}_sankey.html',
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/16s_analysis:154`

```
    148              -r {input.bracken_report} \
    149              -o {output.krona_file} \
    150              --intermediate-ranks
    151  
    152          sed -i 's/[A-Za-z]__//g' {output.krona_file}
    153  
>>  154          ktImportText \
    155              {output.krona_file} \
    156              -o {output.krona_html}
    157          '''
    158  
    159  rule generate_multisample_krona_plots:
    160      input:
    161          multi_krona_files = set(expand('output/{sample}/bracken_output/{sample}.krona', sample = samples))
    162      output:
    163          set_krona_plot = 'output/multisample_krona.html'
    164      shell:
    165          '''
>>  166          ktImportText {input.multi_krona_files} \
    167              -o {output.set_krona_plot}
    168          '''
    169  
    170  rule generate_sankey_plots:
    171      input:
    172          bracken_report = 'output/{sample}/bracken_output/{sample}_bracken_report.txt'
    173      params:
    174          sankey_script = os.path.join(workflow_dir, "scripts/sankey_plot_gen.R"),
    175          tmp_sankey_dir = directory('output/{sample}_sankey_files/')
    176      output:
    177          sankey_plot = 'output/{sample}_sankey.html',
    178          cl_sankey_dir = directory('clean_up/{sample}_sankey_files')
```

