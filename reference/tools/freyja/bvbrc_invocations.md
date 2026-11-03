# BV-BRC invocations of `freyja` (freyja)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 13 hunk(s) in 6 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `workflows/bvbrc_SARS2Wastewater/scripts/edit_time_metadata_csv.py`
- `workflows/bvbrc_SARS2Wastewater/scripts/time_series_plots.py`
- `workflows/bvbrc_SARS2Wastewater/scripts/write_html_report.py`
- `workflows/bvbrc_SARS2Wastewater/snakefile/freyja_snakefile`
- `workflows/bvbrc_SARS2Wastewater/snakefile/stats_snakefile`
- `workflows/bvbrc_SARS2Wastewater/snakefile/wrapper.py`

## `workflows/bvbrc_SARS2Wastewater/snakefile/freyja_snakefile:41`

```
     35  ### Define global handlers ###
     36  onstart: onstart
     37  onsuccess: onsuccess
     38  onerror: onerror
     39  configfile: "config.json"
     40  workflow_dir = config["workflow_dir"]
>>   41  ### freyja variant variables ###
     42  minimum_base_quality_score_val = config["params"]["minimum_base_quality_score"]
>>   43  ### freyja command variables ###
     44  barcodes_path = config["barcodes_path"]
     45  curated_lineages = config["curated_lineages_path"]
     46  lineages = config["lineages_path"]
     47  eps_val = config["params"]["minimum_lineage_abundance"]
     48  covcut_val = config["params"]["coverage_estimate"]
     49  depthcutoff_val = config["params"]["minimum_coverage_depth"]
     50  if config["params"]["confirmedonly"] == True:
     51      confirmed_only_status = "--confirmedonly"
     52  else:
     53      confirmed_only_status = ""
>>   54  ### freyja aggregate variables ###
     55  minimum_genome_coverage_val = config["params"]["minimum_genome_coverage"]
>>   56  ### freyja plot variables ###
     57  agg_minimum_lineage_abundance_val = config["params"]["agg_minimum_lineage_abundance"]
     58  
     59  # Load the JSON data
     60  with open("config.json") as f:
     61      data = json.load(f)
     62      # Extract data from single_end_libs with dates (ignore without dates)
     63      single_end_data = [(entry['sample_id'], entry['sample_level_date']) 
     64                     for entry in data['params']['single_end_libs'] 
     65                     if entry.get('sample_level_date') is not None]
     66  
     67      # Extract data from paired_end_libs with dates (ignore without dates)
     68      # paired_end_data = [(entry['sample_id'], entry.get('sample_level_date', None)) for entry in data['params']['paired_end_libs']]
```

## `workflows/bvbrc_SARS2Wastewater/snakefile/stats_snakefile:37`

```
     31      pass
     32  
     33  ### Define global handlers ###
     34  onstart: onstart
     35  onsuccess: onsuccess
     36  onerror: onerror
>>   37  ### freyja command variables ###
     38  configfile: "config.json"
     39  workflow_dir = config["workflow_dir"]
     40  barcodes_path = config["barcodes_path"]
     41  curated_lineages = config["curated_lineages_path"]
     42  lineages = config["lineages_path"]
     43  last_barcode_update = config["last_barcode_update"]
>>   44  ### freyja aggregate variables ###
     45  minimum_genome_coverage_val = config["params"]["minimum_genome_coverage"]
>>   46  ### freyja plot variables ###
     47  agg_minimum_lineage_abundance_val = config["params"]["agg_minimum_lineage_abundance"]
     48  
     49  # Initialize lists to store primers and primer versions
     50  primer_type = []
     51  primer_version = []
     52  
     53  # Extract primers and primer versions from paired_end_libs
     54  for lib in config['params']['paired_end_libs']:
     55      primer_type.append(lib.get('primers'))
     56      primer_version.append(lib.get('primer_version'))
     57  
     58  # Extract primers and primer versions from single_end_libs
```

## `workflows/bvbrc_SARS2Wastewater/snakefile/wrapper.py:275`

```
    269          sys.stderr.write(msg)
    270          cmd = common_params + ["--snakefile",  SNAKEFILE]
    271          subprocess.run(cmd)
    272      # once the snake files complete, check for the iVar bam files
    273      complete = preprocessing_check(output_dir, input_dict)
    274  
>>  275      print('starting freyja command')
    276      SNAKEFILE = os.path.join(SNAKEFILE_DIR, "freyja_snakefile")
    277      cmd = common_params + ["--snakefile",  SNAKEFILE]
    278      subprocess.run(cmd)
    279      print('starting stats/wrap up command')
    280      SNAKEFILE = os.path.join(SNAKEFILE_DIR, "stats_snakefile")
    281      cmd = common_params + ["--snakefile",  SNAKEFILE]
    282      subprocess.run(cmd)
    283      # final file check for only the samples that passed iVar trimming
    284      freyja_check = post_processing_check(complete, output_dir)
    285      if freyja_check == True:
    286          msg = "Wastewater Analysis is complete \n"
    287          sys.stderr.write(msg)
```

## `workflows/bvbrc_SARS2Wastewater/scripts/time_series_plots.py:98`

```
     92      variants_df = pd.DataFrame(rows)
     93      return variants_df
     94  
     95  
     96  def get_variant_day_info(df, dates_df):
     97      merged_df = {}
>>   98      # first get variant information from the freyja output file
     99      freyja_info = get_variant_info(df)
    100      variant_info = get_variant_info(df)
    101      merged_df = pd.merge(variant_info, dates_df, left_on='sample_id', right_on='sample')
    102      merged_df["formatted_date"] = pd.to_datetime(merged_df['date']).dt.date
    103      return merged_df
    104  
    105  def day_variant_plot(merged_df, day_variant_out):
    106      # group rows that have the same sample id together
    107      # group sample ids with the same date together 
    108      # varaints will group together
    109      # merged_df['normalized'] = merged_df[['date','Percent']].groupby(['date'])['Percent'].transform(lambda x: x / x.sum())
    110      merged_df['normalized'] = merged_df[['date','abundance']].groupby(['date'])['abundance'].transform(lambda x: x / x.sum())    
```

## `workflows/bvbrc_SARS2Wastewater/scripts/edit_time_metadata_csv.py:12`

```
      6  
      7  df = pd.read_csv("sample_time_metadata.csv")
      8  mask = []
      9  for index, row in df.iterrows():
     10      sample_id = row["Sample"].replace("_freyja_variants.tsv", "")
     11  
>>   12      variant_file_path = os.path.join("output", sample_id, "freyja", row["Sample"])
     13      if os.path.exists(variant_file_path):
     14          mask.append(True)
     15      else:
     16          mask.append(False)
     17  filtered_df = df[mask]
     18  
     19  # drop index 
     20  filtered_df.to_csv("edited_sample_time_metadata.csv", index=False)
```

## `workflows/bvbrc_SARS2Wastewater/snakefile/freyja_snakefile:197`

```
    191          ext = "_freyja_result.tsv",
    192          minimum_genome_coverage = minimum_genome_coverage_val,
    193      output:
    194          single_aggregate = "output/{sample}/{sample}_aggregated_result.tsv",
    195      shell:
    196          """
>>  197          freyja aggregate \
    198              {params.freyja_dir} \
    199              --ext {params.ext} \
    200              --output {output.single_aggregate}
    201          """
    202  
    203  rule freyja_variant_plot:
    204      input:
    205          single_aggregate = "output/{sample}/{sample}_aggregated_result.tsv",
    206      params:
    207          agg_minimum_lineage_abundance = agg_minimum_lineage_abundance_val,
    208          lineage_yml = lineages,
    209          minimum_genome_coverage = minimum_genome_coverage_val,
    210          variant_plot_msg = "tmp/{sample}_sample_variant_plot_error.txt",
    211      output:
    212          variant_plot = "output/{sample}/{sample}_variant_plot.svg",
    213      shell:
    214          """
>>  215          freyja plot \
    216              {input.single_aggregate} \
    217              --lineageyml {params.lineage_yml} \
    218              --mincov {params.minimum_genome_coverage} \
    219              --thresh {params.agg_minimum_lineage_abundance} \
    220              --output {output.variant_plot} > {params.variant_plot_msg}
    221          """
    222  
    223  rule freyja_lineage_plot:
    224      input:
    225          single_aggregate = "output/{sample}/{sample}_aggregated_result.tsv",
    226      params:
    227          agg_minimum_lineage_abundance = agg_minimum_lineage_abundance_val,
```

## `workflows/bvbrc_SARS2Wastewater/snakefile/freyja_snakefile:132`

```
    126  rule freyja_variants:
    127      input:
    128          ivar_bam_sorted = "output/{sample}/assembly/{sample}.sorted.bam",
    129          reference = "output/{sample}/assembly/reference_trimmed.fa",
    130      params:
    131          eps = eps_val,
>>  132          freyja_analysis_dir = directory("output/{sample}/freyja"),
    133          minimum_base_quality_score = minimum_base_quality_score_val,
    134          tmp_dir = directory("./tmp/")
    135      output:
    136          variants = "output/{sample}/freyja/{sample}_freyja_variants.tsv",
    137          depth = "output/{sample}/freyja/{sample}_freyja.depths",
    138      shell:
    139          """
    140          mkdir -p {params.freyja_analysis_dir}
    141  
>>  142          freyja variants \
    143              {input.ivar_bam_sorted} \
    144              --minq {params.minimum_base_quality_score} \
    145              --variants {output.variants} \
    146              --depths {output.depth} \
    147              --ref {input.reference}
    148          """
    149  
    150  rule freyja_demix:
    151      input:
    152          barcodes = barcodes_path,
    153          curated_lineages_ = curated_lineages,
    154          variants = "output/{sample}/freyja/{sample}_freyja_variants.tsv",
```

## `workflows/bvbrc_SARS2Wastewater/snakefile/freyja_snakefile:170`

```
    164          freyja_file = "output/{sample}/freyja/{sample}_freyja_result.tsv",
    165          tmp_freyja = "tmp/{sample}_freyja_result.tsv"
    166      shell:
    167          """
    168          mkdir -p {params.tmp_dir}
    169  
>>  170          freyja demix \
    171              --eps {params.eps} \
    172              --barcodes {input.barcodes} \
    173              --meta {input.curated_lineages_} \
    174              --covcut {params.covcut} \
    175              --output {output.freyja_file} {params.confirmedonly} \
    176              --depthcutoff {params.depthcutoff} \
    177              {input.variants} \
    178              {input.depth} \
    179              > {params.error_msg}
    180  
    181          cp {output.freyja_file} {output.tmp_freyja}
    182          """
```

## `workflows/bvbrc_SARS2Wastewater/snakefile/freyja_snakefile:236`

```
    230          lineage_yml = lineages,
    231          lineage_plot_msg = "tmp/{sample}_sample_lineage_plot_error.txt"
    232      output:
    233          lineage_plot = "output/{sample}/{sample}_lineage_plot.svg",
    234      shell:
    235          """
>>  236          freyja plot \
    237              {input.single_aggregate} \
    238              --lineages \
    239              --lineageyml {params.lineage_yml} \
    240              --mincov {params.minimum_genome_coverage} \
    241              --thresh {params.agg_minimum_lineage_abundance} \
    242              --output {output.lineage_plot} > {params.lineage_plot_msg}
    243          """
    244  
    245  rule clean_up_fastqc_zip_se:
    246      input:
    247          zip_path = "output/{se_sample}/fastqc_results/{se_sample}_fastqc.zip",
    248          ivar_zip_path = "output/{se_sample}/fastqc_results/{se_sample}.ivar_fastqc.zip",
```

## `workflows/bvbrc_SARS2Wastewater/snakefile/stats_snakefile:104`

```
     98          tmp_dir = directory("tmp/"),
     99          ext = "_freyja_result.tsv ",
    100      output:
    101          aggregated = "output/freyja_result.tsv",
    102      shell:
    103          """
>>  104          freyja aggregate \
    105              {params.tmp_dir} \
    106              --ext {params.ext} \
    107              --output {output.aggregated}
    108          """
    109  
    110  rule set_freyja_vis:
    111      input:
    112          # Using the tmp message file incase a sample files to stil populate even if some samples fail
    113          # Using set to ensure all files try to run demix. Then use any availble demix results.
    114          aggregated = "output/freyja_result.tsv"
    115      params:
    116          sample_plots_script = os.path.join(workflow_dir, "scripts/sample_level_plots.py")
```

## `workflows/bvbrc_SARS2Wastewater/scripts/write_html_report.py:109`

```
    103          warning_text="No warnings were generated during your analysis."
    104      # assembly plots
    105      image_paths = find_assembly_plots("assembly_images")
    106      #set up the barcodes
    107      barcode_version=read_barcode_version("barcode_version.txt")
    108  
>>  109      # set up the freyja plots 
    110      lineage_plot = "plots/lineages_plot.html"
    111      variant_plot = "plots/variants_plot.html"
    112  
    113      standard_plot_header, standard_plot_description, standard_lineage_plot, standard_variant_plot = (
    114          ("<h3>Lineage and Variant Abundance by Sample</h3>",
    115          "<p>Below are stacked bar graphs showing the relative abundance of variants (left) and lineages (right) across the samples.<p>",
    116          read_plotly_html(lineage_plot),
    117          read_plotly_html(variant_plot))
    118          if os.path.exists(lineage_plot) else
    119          ("", "", "", "")
    120      )
    121      # Time series plots - Day
```

## `workflows/bvbrc_SARS2Wastewater/snakefile/freyja_snakefile:94`

```
     88  
     89  # Define base rule all
     90  rule_all_list = [
     91          expand("output/{sample}/freyja/{sample}_freyja_variants.tsv", sample=samples),
     92          expand("output/{sample}/freyja/{sample}_freyja_result.tsv", sample=samples),
     93          expand("output/{sample}/{sample}_aggregated_result.tsv", sample=samples),
>>   94          # commenting out freyja plots for now
     95          # expand("output/{sample}/{sample}_variant_plot.svg", sample=samples),
     96          # expand("output/{sample}/{sample}_lineage_plot.svg", sample=samples),
     97          expand("assembly_images/{sample}.detail.png", sample=samples)
     98      ]
     99  
    100  ### append clean up rule for fastQC zip to rule all depending on the paired reads vs single end reads ###
    101  pe_samples = pe_zpd_samples + pe_unzpd_samples
    102  se_samples = se_zpd_samples + se_unzpd_samples
    103  if len(pe_samples) > 0:
    104          rule_all_list.append(expand("clean_up/{pe_sample}/fastqc_results/{pe_sample}_R1_fastqc.zip", pe_sample=pe_samples))
    105          rule_all_list.append(expand("clean_up/{pe_sample}/fastqc_results/{pe_sample}_R2_fastqc.zip", pe_sample=pe_samples))
    106  if len(se_samples) >0:
```

## `workflows/bvbrc_SARS2Wastewater/snakefile/stats_snakefile:199`

```
    193          """
    194          echo "The results may vary depending on the version of Freyja, its dependences and the barcode file used. The barcode file is a .tsv file that is used in lineage-determination defined by the UShER global phylogenetic tree. We update the barcodes every two weeks.\n Below are the versions of the tools used in this analysis. \n" >> {output.version_log}
    195  
    196          echo "primer type: {params.primer_tp}" >> {output.version_log}
    197  
    198          echo "primer version: {params.primer_v}" >> {output.version_log}
>>  199          freyja --version >> {output.version_log}
    200  
    201          echo "Barcode version:" >> {output.version_log}
    202  
    203          cat {params.last_barcode_update_file} >> {output.version_log}
    204  
    205          ivar version >> {output.version_log}
    206  
    207          samtools version >> {output.version_log}
    208  
    209          cat {params.last_barcode_update_file} >> {output.barcode_version}
    210          """
```

