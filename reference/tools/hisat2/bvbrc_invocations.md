# BV-BRC invocations of `hisat2` (hisat2)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 16 hunk(s) in 9 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/experiment.py`
- `lib/fastq_utils.py`
- `lib/process.py`
- `plbin/App-FastqUtils.pl`
- `plbin/App-RNASeq.pl`
- `pybin/fastq_utils.py`
- `pybin/run_rnaseq.py`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing`

## `pybin/fastq_utils.py:216`

```
    210              )
    211              archive.close()
    212              # index_prefix = os.path.join(
    213              #     output_dir,
    214              #     os.path.basename(genome["hisat_index"]).replace(".ht2.tar", ""),
    215              # )  # somewhat fragile convention. tar prefix is underlying index prefix
>>  216              cmd = ["hisat2", "--dta-cufflinks", "-x", index_prefix]
>>  217              hisat2_params = parameters.get("hisat2", {})
    218              # thread count
    219              if "-p" in hisat2_params:
    220                  cmd += ["-p", str(hisat2_params["-p"])]
    221              hisat2_used = True
    222          else:
    223              subprocess.run(["bowtie2-build", genome_link, genome_link], check=True)
    224              bt2_threads = parameters.get("bowtie2", {}).get("-p", BT2_THREADS)
    225              cmd = ["bowtie2", "-p", str(bt2_threads), "-x", genome_link]
    226  
    227          print(f"{cmd=}")
    228  
    229          target_dir = genome["output"]
    230          for r in read_list:
    231              rcount = 0
    232              cur_cleanup = []
    233              rcount += 1
    234              samstat_cmd = ["samstat"]
>>  235              cur_cmd = list(cmd)  # hisat2 or bowtie2
    236              read2 = False
    237              # generate output file name, based on input read file(s) name(s).
    238              out_name = "_".join([Path(i[1]).stem.replace(" ", "") for i in r.items() if "read" in i[0]])
    239              sam_path = Path(target_dir) / f"{out_name}.sam"
    240              unmapped_fq_gz_path = Path(target_dir) / f"{out_name}.unmapped.fq.gz"
>>  241              if "read2" in r:  # illumina, using hisat2 or bowtie2
    242                  cur_cmd += [
    243                      "-1", link_space(r["read1"]), "-2", link_space(r["read2"]),
    244                      "-S", str(sam_path),
    245                      "--un-conc-gz", str(unmapped_fq_gz_path),
    246                  ]
    247                  read2 = True
    248              else:
    249                  if hisat2_used:
    250                      cur_cmd += [
    251                          "-U", link_space(r["read1"]),
    252                          "-S", str(sam_path),
    253                          "--un-gz", str(unmapped_fq_gz_path),
```

## `lib/experiment.py:160`

```
    154                  "-xvf",
    155                  self.get_genome_data("hisat_index"),
    156                  "-C",
    157                  os.path.dirname(self.get_genome_data("hisat_index")),
    158              ]
    159              try:
>>  160                  print("unpacking hisat2 index:\n{0}".format(" ".join(tar_cmd)))
    161                  subprocess.check_call(tar_cmd)
>>  162                  print("finished unpcking hisat2 index")
    163              except Exception as e:
>>  164                  sys.stderr.write("Error unpacking hisat2 index: exiting")
    165                  print("error: {0}".format(e))
    166                  sys.exit(-1)
    167              self.add_genome_data("hisat_prefix", index_prefix)
    168          # setup bed file
    169          bed_file = self.get_genome_data("annotation").replace(".gff", ".bed")
    170          # TODO: add --do-not-sort after gff2bed?
    171          bed_cmd = "gff2bed < " + self.get_genome_data("annotation")
    172          try:
    173              print(bed_cmd)
    174              with open(bed_file, "w") as bf:
    175                  subprocess.check_call(bed_cmd, stdout=bf, shell=True)
    176              self.add_genome_data("bed", bed_file)
```

## `lib/fastq_utils.py:216`

```
    210              )
    211              archive.close()
    212              # index_prefix = os.path.join(
    213              #     output_dir,
    214              #     os.path.basename(genome["hisat_index"]).replace(".ht2.tar", ""),
    215              # )  # somewhat fragile convention. tar prefix is underlying index prefix
>>  216              cmd = ["hisat2", "--dta-cufflinks", "-x", index_prefix]
>>  217              hisat2_params = parameters.get("hisat2", {})
    218              # thread count
    219              if "-p" in hisat2_params:
    220                  cmd += ["-p", str(hisat2_params["-p"])]
    221              hisat2_used = True
    222          else:
    223              subprocess.run(["bowtie2-build", genome_link, genome_link], check=True)
    224              bt2_threads = parameters.get("bowtie2", {}).get("-p", BT2_THREADS)
    225              cmd = ["bowtie2", "-p", str(bt2_threads), "-x", genome_link]
    226  
    227          print(f"{cmd=}")
    228  
    229          target_dir = genome["output"]
    230          for r in read_list:
    231              rcount = 0
    232              cur_cleanup = []
    233              rcount += 1
    234              samstat_cmd = ["samstat"]
>>  235              cur_cmd = list(cmd)  # hisat2 or bowtie2
    236              read2 = False
    237              # generate output file name, based on input read file(s) name(s).
    238              out_name = "_".join([Path(i[1]).stem.replace(" ", "") for i in r.items() if "read" in i[0]])
    239              sam_path = Path(target_dir) / f"{out_name}.sam"
    240              unmapped_fq_gz_path = Path(target_dir) / f"{out_name}.unmapped.fq.gz"
>>  241              if "read2" in r:  # illumina, using hisat2 or bowtie2
    242                  cur_cmd += [
    243                      "-1", link_space(r["read1"]), "-2", link_space(r["read2"]),
    244                      "-S", str(sam_path),
    245                      "--un-conc-gz", str(unmapped_fq_gz_path),
    246                  ]
    247                  read2 = True
    248              else:
    249                  if hisat2_used:
    250                      cur_cmd += [
    251                          "-U", link_space(r["read1"]),
    252                          "-S", str(sam_path),
    253                          "--un-gz", str(unmapped_fq_gz_path),
```

## `lib/process.py:1116`

```
   1110                  "bowtie2",
   1111                  "-x",
   1112                  self.genome.get_genome_data("bowtie_prefix"),
   1113              ]
   1114          else:
   1115              align_cmd = [
>> 1116                  "hisat2",
   1117                  "-x",
   1118                  self.genome.get_genome_data("hisat_prefix"),
   1119                  "--mp",
   1120                  "1,0",
   1121                  "--pen-noncansplice",
   1122                  "20",
   1123              ]
   1124          if sample.sample_type == "paired":
   1125              align_cmd += ["-1", reads_list[0], "-2", reads_list[1]]
   1126          elif sample.sample_type == "single":
   1127              align_cmd += ["-U", reads_list[0]]
   1128          align_cmd += ["-S", sam_file, "-p", str(threads)]
```

## `pybin/run_rnaseq.py:341`

```
    335      )
    336      parser.add_argument(
    337          "-d", help="differential expression folder", required=False, default=".diff_exp"
    338      )
    339      # TODO:
    340      # link to genome files (gff, fa)???
>>  341      # link to hisat2 index
    342      # parameters as input json file OR inline
    343      # unit testing parameters
    344  
    345      map_args = parser.parse_args()
    346      print("map_args:\n{0}".format(map_args))
    347  
    348      # set path to use correct version of samtools
    349      os.environ["PATH"] = (
    350          "/disks/patric-common/runtime/samtools-1.9/bin:" + os.environ["PATH"]
    351      )
    352      os.environ["R_LIBS"] = (
    353          "/disks/patric-common/runtime/lib/R/library:" + os.environ.get("R_LIBS", "")
```

## `plbin/App-FastqUtils.pl:173`

```
    167  
    168      my $parallel = $ENV{P3_ALLOCATED_CPU};
    169      my $override = {
    170  	fastqc => { -p => $parallel},
    171  	trim_galore => {-p => $parallel},
    172  	bowtie2 => {-p => $parallel},
>>  173  	hisat2 => {-p => $parallel},
    174  	samtools_view => {-p => $parallel},
    175  	samtools_index => {-p => $parallel},
    176      samtools_sort => {-p => $parallel}
    177      };
    178  
    179      my @cmd = ("p3-fqutils",
    180  	       "--jfile", $jdesc,
    181  	       "--sstring", $sstring,
    182  	       "-p", encode_json($override),
    183  	       "-o", $work_dir);
    184  
    185      warn Dumper(\@cmd, $params_to_app);
```

## `pybin/fastq_utils.py:293`

```
    287                          ["samtools", "sort", "-o", "-", "-"],
    288                          stdin=samtools_view.stdout,
    289                          stdout=outstream,
    290                      )
    291                      samtools_sort.communicate()
    292  
>>  293                  # minimap2 can't write the unmapped reads like bowtie2 and hisat2
    294                  if not (read2 or hisat2_used): # minimap2
    295                      with unmapped_fq_gz_path.open('w') as un_fq_gz_hdl:
    296                          subprocess.run(
    297                              [
    298                                  "samtools", "fastq",
    299                                  "--threads", str(view_threads),
    300                                  "-n", "-f", "4",
    301                                  bam_file_all
    302                              ],
    303                              check=True,
    304                              stdout=un_fq_gz_hdl,
    305                          )
```

## `lib/fastq_utils.py:293`

```
    287                          ["samtools", "sort", "-o", "-", "-"],
    288                          stdin=samtools_view.stdout,
    289                          stdout=outstream,
    290                      )
    291                      samtools_sort.communicate()
    292  
>>  293                  # minimap2 can't write the unmapped reads like bowtie2 and hisat2
    294                  if not (read2 or hisat2_used): # minimap2
    295                      with unmapped_fq_gz_path.open('w') as un_fq_gz_hdl:
    296                          subprocess.run(
    297                              [
    298                                  "samtools", "fastq",
    299                                  "--threads", str(view_threads),
    300                                  "-n", "-f", "4",
    301                                  bam_file_all
    302                              ],
    303                              check=True,
    304                              stdout=un_fq_gz_hdl,
    305                          )
```

## `lib/process.py:1330`

```
   1324                  "bowtie2",
   1325                  "-x",
   1326                  self.genome.get_genome_data("bowtie_prefix"),
   1327              ]
   1328          else:
   1329              sample_align_cmd = [
>> 1330                  "hisat2",
   1331                  "-x",
   1332                  self.genome.get_genome_data("hisat_prefix"),
   1333                  "--mp",
   1334                  "1,0",
   1335                  "--pen-noncansplice",
   1336                  "20",
   1337              ]
   1338          if sample.get_type() == "paired":
   1339              sample_align_cmd += [
   1340                  "-1",
   1341                  sampled_reads_list[0],
   1342                  "-2",
```

## `pybin/fastq_utils.py:25`

```
     19  from fqutil_api import authenticateByEnv, getHostManifest
     20  
     21  # Default bowtie2 threads.
     22  BT2_THREADS = 2
     23  SAM_THREADS = 1
     24  
>>   25  # hisat2 has problems with spaces in filenames
     26  # prevent spaces in filenames. if one exists link the file to a no-space version.
     27  
     28  
     29  def link_space(file_path):
     30      result = file_path
     31      name = os.path.splitext(os.path.basename(file_path))[0]
     32      if " " in name:
     33          clean_name = name.replace(" ", "")
     34          result = file_path.replace(name, clean_name)
     35          if not os.path.exists(result):
     36              os.symlink(file_path, result)
     37              # subprocess.run(["ln", "-s", file_path, result], check=True)
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing:141`

```
    135          out_r2 = 'output/{sample}/hisat2_results/{sample}_host_removed_R2.fastq.gz',
    136      threads: 16
    137      shell:
    138          '''
    139          mkdir -p {params.hisat2_dir}
    140  
>>  141          hisat2 --version
    142  
    143          echo "starting hisat2......"
    144  
>>  145          hisat2 -x {params.hisat_indices_filename} \
    146              -1 {input.r1} \
    147              -2 {input.r2} \
    148              --un-conc-gz \
    149              {params.tmp_name} -S {output.sam} \
    150              --threads {threads}
    151  
    152          mv {params.fq_r1} {output.out_r1}
    153          mv {params.fq_r2} {output.out_r2}
    154          '''
    155  
    156  rule fastqc_on_host_removed_reads:
    157      input:
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing:121`

```
    115          out = 'output/{sample}/hisat2_results/{sample}_host_removed.fastq.gz',
    116      threads: 16
    117      shell:
    118          '''
    119          mkdir -p {params.hisat2_dir}
    120  
>>  121          hisat2 --version
    122  
    123          echo "starting hisat2......"
    124  
>>  125          hisat2 -x {params.hisat_indices_filename} \
    126              -U {input.raw_read} \
    127              --un-gz \
    128              {params.tmp_name} -S {output.sam} \
    129              --threads {threads}
    130  
    131          mv {params.tmp_name} {output.out}
    132          '''
    133  
    134  rule fastqc_on_host_removed_reads:
    135      input:
    136          clean_read = 'output/{sample}/hisat2_results/{sample}_host_removed.fastq.gz',
    137      params:
```

## `lib/fastq_utils.py:25`

```
     19  from fqutil_api import authenticateByEnv, getHostManifest
     20  
     21  # Default bowtie2 threads.
     22  BT2_THREADS = 2
     23  SAM_THREADS = 1
     24  
>>   25  # hisat2 has problems with spaces in filenames
     26  # prevent spaces in filenames. if one exists link the file to a no-space version.
     27  
     28  
     29  def link_space(file_path):
     30      result = file_path
     31      name = os.path.splitext(os.path.basename(file_path))[0]
     32      if " " in name:
     33          clean_name = name.replace(" ", "")
     34          result = file_path.replace(name, clean_name)
     35          if not os.path.exists(result):
     36              os.symlink(file_path, result)
     37              # subprocess.run(["ln", "-s", file_path, result], check=True)
```

## `plbin/App-RNASeq.pl:291`

```
    285      my $data_api = Bio::KBase::AppService::AppConfig->data_api_url;
    286      my $dat = { data_api => "$data_api/genome_feature" };
    287      my $override = {
    288  	cufflinks => { -p => $parallel},
    289  	cuffdiff => {-p => $parallel},
    290  	cuffmerge => {-p => $parallel},
>>  291  	hisat2 => {-p => $parallel},
    292  	bowtie2 => {-p => $parallel},
    293  	stringtie => {-p => $parallel},
    294      htseq => {-p => $parallel}
    295      };
    296      #
    297      # no pretty, ensure it's on one line
    298      #i
    299      my $pstring = encode_json($override);
    300      my $sstring = encode_json($dat);
    301      
    302      my $outdir = "$tmpdir";
    303      
```

## `pybin/fastq_utils.py:677`

```
    671  
    672  def run_fq_util(job_data, output_dir, tool_params={}):
    673      # arguments:
    674      # list of genomes [{"genome":somefile,"annotation":somefile}]
    675      # dictionary of library dictionaries structured as {libraryname:{library:libraryname, replicates:[{read1:read1file, read2:read2file}]}}
    676      # parametrs_file is a json keyed parameters list.
>>  677      # Example tool_params: '{"fastqc":{"-p":"2"},"trim_galore":{"-p":"2"},"bowtie2":{"-p":"2"},"hisat2":{"-p":"2"},"samtools_view":{"-p":"2"},"samtools_index":{"-p":"2"}}'
    678      output_dir = os.path.abspath(output_dir)
    679      if not os.path.isdir(output_dir):
    680          os.makedirs(output_dir)
    681      genome_list, read_list, recipe = setup(job_data, output_dir, tool_params)
    682      # print("genome_list: {}\nread_list: {}\nrecipe: {}".format(genome_list, read_list, recipe), file=sys.stdout)
    683      # sys.stdout.flush()
    684      for step in recipe:
    685          step = step.upper()
    686          if step == "TRIM":
    687              trimmed_reads = run_trim(read_list, output_dir, job_data, tool_params)
    688              read_list = trimmed_reads
    689          elif step == "PAIRED_FILTER":
```

## `lib/fastq_utils.py:677`

```
    671  
    672  def run_fq_util(job_data, output_dir, tool_params={}):
    673      # arguments:
    674      # list of genomes [{"genome":somefile,"annotation":somefile}]
    675      # dictionary of library dictionaries structured as {libraryname:{library:libraryname, replicates:[{read1:read1file, read2:read2file}]}}
    676      # parametrs_file is a json keyed parameters list.
>>  677      # Example tool_params: '{"fastqc":{"-p":"2"},"trim_galore":{"-p":"2"},"bowtie2":{"-p":"2"},"hisat2":{"-p":"2"},"samtools_view":{"-p":"2"},"samtools_index":{"-p":"2"}}'
    678      output_dir = os.path.abspath(output_dir)
    679      if not os.path.isdir(output_dir):
    680          os.makedirs(output_dir)
    681      genome_list, read_list, recipe = setup(job_data, output_dir, tool_params)
    682      # print("genome_list: {}\nread_list: {}\nrecipe: {}".format(genome_list, read_list, recipe), file=sys.stdout)
    683      # sys.stdout.flush()
    684      for step in recipe:
    685          step = step.upper()
    686          if step == "TRIM":
    687              trimmed_reads = run_trim(read_list, output_dir, job_data, tool_params)
    688              read_list = trimmed_reads
    689          elif step == "PAIRED_FILTER":
```

