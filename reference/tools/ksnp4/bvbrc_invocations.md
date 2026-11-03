# BV-BRC invocations of `kSNP4` (ksnp4)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 10 hunk(s) in 3 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `pybin/whole_genome_snp_utils.py`
- `workflows/bvbrc_WholeGenomeSNPAnalysis/snakefile/prep_ksnp_snakefile`
- `workflows/bvbrc_WholeGenomeSNPAnalysis/snakefile/run_ksnp_snakefile`

## `pybin/whole_genome_snp_utils.py:1219`

```
   1213      pass
   1214  
   1215  
   1216  @cli.command()
   1217  @click.argument("service_config")
   1218  def clean_fasta_filenames(service_config):
>> 1219      """Ensure files adhere to the rules defined by kSNP4"""
   1220      with open(service_config) as file:
   1221          data = json.load(file)
   1222          raw_fasta_dir = data["raw_fasta_dir"]
   1223          clean_fasta_dir = data["clean_data_dir"]
   1224          for index, filename in enumerate(sorted(os.listdir(raw_fasta_dir)), start=1):
   1225              original_path = os.path.join(raw_fasta_dir, filename)
   1226              new_name = ksnp4_filename_format(filename)
   1227              copy_new_file(clean_fasta_dir, new_name, filename, original_path)
   1228  
   1229  @cli.command()
   1230  @click.argument("service_config")
   1231  def convert_to_phyloxml_trees(service_config):
>> 1232      """Use genome IDs in the tree files for phyloxml to connect the existing metadata. Iterate through each tree file to remove kSNP4 formating restrictions."""
   1233      with open(service_config) as file:
   1234          data = json.load(file)
   1235      ### start organize output files ###
   1236      work_dir = data["work_data_dir"]
   1237      if not os.path.exists(work_dir):
   1238          sys.stderr.write("Work directory, {}, does not exist".format(work_dir))
   1239          return
   1240      for filename in os.listdir(work_dir):
   1241          file_path = os.path.join(work_dir, filename)
   1242          # Skip directories
   1243          if not os.path.isfile(file_path):
   1244              continue
```

## `pybin/whole_genome_snp_utils.py:1301`

```
   1295      destination_dir = data["output_data_dir"]
   1296      organize_files_by_type(work_dir, destination_dir)
   1297  
   1298  @cli.command()
   1299  @click.argument("kchooser_report")
   1300  def find_optimum_k(kchooser_report):
>> 1301      """ Parse the kChooser report for the optimum K value for the kSNP4 command."""
   1302      parse_optimum_k(kchooser_report)
   1303  
   1304  @cli.command()
   1305  @click.argument("service_config")
   1306  @click.argument("html_report_path")
   1307  def write_html_report(service_config, html_report_path):
   1308      """Write an interactive report summarizing all outputs"""
   1309      # run the functions here 
   1310      report_data = {}
   1311      with open(service_config) as file:
   1312          data = json.load(file)
   1313      clean_data_dir = data["clean_data_dir"]
```

## `workflows/bvbrc_WholeGenomeSNPAnalysis/snakefile/run_ksnp_snakefile:14`

```
      8              return int(value) if value.isdigit() else None
      9      except:
     10          print("An exception occurred")
     11          return None  # Return None if file is missing or doesn't contain a valid number
     12          # this will crash the job
     13  
>>   14  msg = 'Checkpoint 5: snakefile command recieved - kSNP4 analysis \n'
     15  sys.stderr.write(msg)
     16  
     17  current_directory = os.getcwd()
     18  
     19  # Load the JSON data
     20  with open("{}/config.json".format(current_directory)) as f:
     21      data = json.load(f)
     22  clean_fasta_dir = data["clean_data_dir"]
     23  work_data_dir = data["work_data_dir"]
     24  majority_threshold = data["params"]["majority-threshold"]
     25  
     26  
```

## `workflows/bvbrc_WholeGenomeSNPAnalysis/snakefile/prep_ksnp_snakefile:4`

```
      1  import json
      2  import os
      3  
>>    4  msg = 'Checkpoint 3: snakefile command recieved - Prepping files for kSNP4 \n'
      5  sys.stderr.write(msg)
      6  
      7  current_directory = os.getcwd()
      8  
      9  # Load the JSON data
     10  with open('{}/config.json'.format(current_directory)) as f:
     11      data = json.load(f)
     12  clean_fasta_dir = data["clean_data_dir"]
     13  work_data_dir = data["work_data_dir"]
     14  rule_all_list = [
     15                  "{}/clean_fastas_complete.txt".format(work_data_dir),
     16                  "{}/ksnp4_input_file.txt".format(clean_fasta_dir),
```

## `workflows/bvbrc_WholeGenomeSNPAnalysis/snakefile/run_ksnp_snakefile:99`

```
     93  #         touchpoint = "{}/kSNP_annotation_command_touchpoint.txt".format(current_directory)
     94  
     95  #     shell:
     96  #         """
     97  #         echo {params.optimum_k}
     98  
>>   99  #         kSNP4 \
    100  #             -in {input.ksnp_in_file}\
    101  #             -outdir {params.out_dir} \
    102  #             -k {params.optimum_k} \
    103  #             -annotate {input.annotated_genome_list} \
    104  #             -core \
    105  #             -NJ \
    106  #             -ML \
    107  #             -vcf \
    108  #             -debug \
    109  #             -CPU 7
    110  
    111  #         touch {output.touchpoint}
```

## `workflows/bvbrc_WholeGenomeSNPAnalysis/snakefile/prep_ksnp_snakefile:56`

```
     50  rule run_kchooser:
     51      input:
     52          ksnp4_in_file = "{}/ksnp4_input_file.txt".format(clean_fasta_dir)
     53      params:
     54          clean_fasta_dir_ = clean_fasta_dir,
     55          current_directory_ = directory(current_directory),
>>   56          ksnp4_in_file = "ksnp4_input_file.txt" # using this relative path because kSNP4 is picky
     57      output:
     58          output_from_kchooser = "{}/Kchooser4_ksnp4_input_file.report".format(clean_fasta_dir),
     59          optimum_k_txt = "{}/optimum_k.txt".format(work_data_dir)
     60      shell:
     61          """
     62          cd {params.clean_fasta_dir_}
     63  
     64          Kchooser4 -in {params.ksnp4_in_file}
     65  
     66          cd {params.current_directory_}
     67  
     68          whole_genome_snp_utils find-optimum-k  {output.output_from_kchooser} > {output.optimum_k_txt}
```

## `workflows/bvbrc_WholeGenomeSNPAnalysis/snakefile/run_ksnp_snakefile:70`

```
     64          core_SNPs_matrix = "{}/core_SNPs_matrix.fasta".format(work_data_dir)
     65  
     66      shell:
     67          """
     68          echo {params.optimum_k}
     69  
>>   70          kSNP4 \
     71              -in {input.ksnp_in_file}\
     72              -outdir {params.out_dir} \
     73              -k {params.optimum_k} \
     74              -min_frac {params.majority_threshold} \
     75              -core \
     76              -NJ \
     77              -ML \
     78              -vcf \
     79              -debug \
     80              -CPU 7
     81  
     82          touch {output.touchpoint}
```

## `pybin/whole_genome_snp_utils.py:203`

```
    197                      <div class="title">Whole Genome SNP Analysis Report</div>
    198                          </a>
    199                  </header>
    200              <p> Explore the results of your Whole Genome SNP analysis in this interactive report. This service uses a reference-free tool for identifying Single Nucleotide Polymorphisms (SNPs) called kSNP4.  This reference free tool identifies SNPs through a k-mer based analysis.  Note, you can download the images of the plots in this report by clicking on the camera icon in the upper left-hand corner. Poor quality assemblies can impact the performance of this service.</p>
    201              <h3>About the Analysis Workflow</h3>
    202              <p> 
>>  203              kSNP4 identifies SNPs and does phylogenetic analysis without genome alignment or the use of reference genomes. They estimate phylogenetic trees based on 3 methods: parsimony, neighbor joining (NJ), and maximum likelihood (ML). The tool creates three groups, All SNPs, Core SNPs and SNPs within a majority threshold.
    204               
    205               Our pipeline begins by selecting the optimum k-mer size by reviewing your genomes with a series of add-length k-mers to seek the shortest length for which each k-mer occurs only once in the median-sized genome.
    206               
>>  207               While kSNP4 runs it identifies SNPs across the three genome groups (All, Core, Majority).  Then constructs phylogenetic trees based on the SNPs. Static images of the trees are available in this report. The trees are also viewable in the website's phylogenetic tree viewer with the ability to map metadata to the tree. Other files available are multiple alignment of all SNP positions and related files. A companion program, kSNPdist creates a SNP distance matrix for each genome group.</p>
    208              <h2>Getting to Know the Input Data</h2>
    209              <h3>Input Genomes</h3>
    210              <p>
    211              {input_genome_table}
    212              <p>
    213              <div class="plot-container">
    214                  <div class="plot" id="Genome Length Box Plot">
    215                  {barplot_html}
    216                  </div>
    217              </div>
    218              <h3>Input Genome Metadata</h3>
    219              <!-- DataTables CSS -->
```

## `pybin/whole_genome_snp_utils.py:358`

```
    352              <p>A SNP is considered Homoplastic which that SNP occurs in two or more unrelated positions on the same tree.</p>
    353              <ul style="list-style-type: disc; padding-left: 25;">
    354              <li><b>Parsimony</b> the parsimony tree method is a good fit for small datasets with close relatives and low divergency. It estimated by creating a consensus of up to 100 equally parsimonious trees. It seeks a tree topology that explains the observed sequence data with the smallest possible number of evolutionary changes.</li>
    355              <li><b>Maximum Likelihood</b> the maximum likelihood tree is a good fit for datasets with substantial divergency and complex substitution patterns. It is constructed by finding the tree topology that has the highest likelihood of producing the observed sequence data. </li>
    356              <li><b>Neighbor Joining</b> this tree method is a good fit for exploratory analysis, especially with very large datasets. This is a distance-based method that constructs a tree by iteratively finding pairs of taxa (neighbors) that minimize  the total branch length at each step.  It uses distance matrix (pairwise genetic distances between sequences).</li>
    357              </ul>
>>  358              <p>Please visit the kSNP4 documentation for more information about the many trees created by this service.<p>
    359              {heatmap_html}
    360              <h3>References</h3>
    361  
    362              <ol type="1">
    363              <li>Olson RD, Assaf R, Brettin T, Conrad N, Cucinell C, Davis JJ, Dempsey DM, Dickerman A, Dietrich EM, Kenyon RW, Kuscuoglu M, Lefkowitz EJ, Lu J, Machi D, Macken C, Mao C, Niewiadomska A, Nguyen M, Olsen GJ, Overbeek JC, Parrello B, Parrello V, Porter JS, Pusch GD, Shukla M, Singh I, Stewart L, Tan G, Thomas C, VanOeffelen M, Vonstein V, Wallace ZS, Warren AS, Wattam AR, Xia F, Yoo H, Zhang Y, Zmasek CM, Scheuermann RH, Stevens RL.</li>
    364              <li>Hall, B. G., & Nisbet, J. (2023). Building phylogenetic trees from genome sequences with KSNP4. Molecular Biology and Evolution, 40(11). https://doi.org/10.1093/molbev/msad235 </li>
    365              </ol>
    366          </body>
    367          </html>
    368          """.format(input_genome_table = input_genome_table, barplot_html=barplot_html, snp_distribution_html=snp_distribution_html,  homoplastic_snps_html=homoplastic_snps_html, \
    369                  heatmap_html=heatmap_html, majority_percentage=majority_percentage, majority_threshold=majority_threshold, metadata_json_string=metadata_json_string)
    370      return html_template
```

## `pybin/whole_genome_snp_utils.py:794`

```
    788      majority_threshold=majority_threshold,
    789      )
    790      return heatmap_template, metadata_json_string
    791  
    792  
    793  def edit_newick_genome_id(raw_nwk, clean_nwk):
>>  794      """Reverts genome ids in kSNP4 formatted Newick files to match genome ids for phyloxml"""
    795      click.echo("Reverting genome IDs {}".format(raw_nwk))
    796      if os.path.isfile(raw_nwk) == True and os.path.getsize(raw_nwk) > 0:
    797          # Using bio phylo package to ensure accuracy as some files have extra details
    798          fix_labels_with_phylo(raw_nwk, clean_nwk)
    799          return clean_nwk
    800      else:
    801          msg = "{} is either empty or not found... cannot edit genome ids for phyloxml".format(raw_nwk)
    802          sys.stderr.write(msg)
    803  
    804  
    805  def fix_labels_with_phylo(raw_nwk, clean_nwk):
    806      tree = Phylo.read(raw_nwk, "newick")
```

