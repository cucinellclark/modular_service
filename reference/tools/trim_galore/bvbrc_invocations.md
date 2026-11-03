# BV-BRC invocations of `trim_galore` (trim_galore)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 13 hunk(s) in 9 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/ReadLibrary.py`
- `lib/fastq_utils.py`
- `lib/process.py`
- `plbin/App-FastqUtils.pl`
- `pybin/demo_read_library.py`
- `pybin/fastq_utils.py`
- `pybin/p3x-assembly.py`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing_16s`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing_16s`

## `pybin/fastq_utils.py:96`

```
     90      return prefix_pos
     91  
     92  
     93  def run_trim(read_list, output_dir, job_data, tool_params):
     94      rcount = 0
     95      trimmed_reads = []
>>   96      threads = get_param("trim_galore", "-p", tool_params)
>>   97      trim_base_cmd = ["trim_galore", "-j", str(threads) if threads else "1"]
     98      for r in read_list:
     99          tr = copy.deepcopy(r)
    100          tr["fastqc"] = []
    101          cur_check = []
    102          rename_files = {}
    103          rcount += 1
>>  104          # trim_galore --gzip --paired -o ../fonsynbiothr/trimmed_reads/ ../fonsynbiothr/fastq_files/926M_RNA_S8_L001_R1_001.fastq ../fonsynbiothr/fastq_files/926M_RNA_S8_L001_R2_001.fastq
    105          trim_cmd = trim_base_cmd + ["--gzip", "-o", output_dir]
    106          if "read2" in r:
    107              trim_cmd += ["--paired", r["read1"], r["read2"]]
    108              pre_pos = find_prefix(r["read1"])
    109              old_name = os.path.join(
    110                  output_dir,
    111                  ".".join(os.path.basename(r["read1"]).split(".")[0:pre_pos])
    112                  + "_val_1.fq.gz",
    113              )
    114              cur_check.append(old_name)
    115              new_name = os.path.join(
    116                  output_dir,
```

## `lib/ReadLibrary.py:204`

```
    198          return
    199  
    200      def trim_short_reads(self):
    201          startTime = time()
    202          ReadLibrary.LOG.write("trim_short_reads()\n")
    203  
>>  204          command = ["trim_galore", "--version"]
    205          proc = subprocess.run(command, shell=False, capture_output=True, text=True)
    206          version_text = proc.stdout.strip()
    207          m = re.search(r"(version\s+\S+)", version_text)
    208          if m:
>>  209              trim_galore_version = "trim_galore " + m.group(1)
>>  210              ReadLibrary.program_version['trim_galore'] = trim_galore_version
    211  
    212          self.problem = []
    213          read_file_base = re.sub("(.*?)\..*", "\\1", self.files[0])
    214          read_file_base = re.sub("(.*)_R[12].*", "\\1", read_file_base)
    215          trim_directory = read_file_base + "_trim_dir"
>>  216          command = ['trim_galore', '-j', str(ReadLibrary.NUM_THREADS), '-o', trim_directory]
    217          if len(self.files) > 1:
    218              command.extend(["--paired", self.files[0], self.files[1]])
    219          else:
    220              command.append(self.files[0])
    221  
    222          ReadLibrary.LOG.write("command: "+" ".join(command)+"\n")
    223          proc = subprocess.Popen(command, shell=False, stderr=subprocess.PIPE, text=True)
    224          trimGaloreStderr = proc.stderr.read()
    225          return_code = proc.wait()
    226          ReadLibrary.LOG.write("return code = %d\n"%return_code)
    227          trimReads = glob.glob(trim_directory + "/*val_?.fq")
    228          if not trimReads:
```

## `lib/fastq_utils.py:96`

```
     90      return prefix_pos
     91  
     92  
     93  def run_trim(read_list, output_dir, job_data, tool_params):
     94      rcount = 0
     95      trimmed_reads = []
>>   96      threads = get_param("trim_galore", "-p", tool_params)
>>   97      trim_base_cmd = ["trim_galore", "-j", str(threads) if threads else "1"]
     98      for r in read_list:
     99          tr = copy.deepcopy(r)
    100          tr["fastqc"] = []
    101          cur_check = []
    102          rename_files = {}
    103          rcount += 1
>>  104          # trim_galore --gzip --paired -o ../fonsynbiothr/trimmed_reads/ ../fonsynbiothr/fastq_files/926M_RNA_S8_L001_R1_001.fastq ../fonsynbiothr/fastq_files/926M_RNA_S8_L001_R2_001.fastq
    105          trim_cmd = trim_base_cmd + ["--gzip", "-o", output_dir]
    106          if "read2" in r:
    107              trim_cmd += ["--paired", r["read1"], r["read2"]]
    108              pre_pos = find_prefix(r["read1"])
    109              old_name = os.path.join(
    110                  output_dir,
    111                  ".".join(os.path.basename(r["read1"]).split(".")[0:pre_pos])
    112                  + "_val_1.fq.gz",
    113              )
    114              cur_check.append(old_name)
    115              new_name = os.path.join(
    116                  output_dir,
```

## `lib/process.py:1735`

```
   1729                      sample.get_id()
   1730                  )
   1731              )
   1732              sample.set_command_status("fastqc", e)
   1733              return False
   1734  
>> 1735      # runs trim_galore on samples
   1736      # TODO: option for rerunning fastqc?
   1737      # TODO: option for adapter specification
   1738      def run_trimming(self, sample, threads):
   1739          sample_dir = sample.get_path()
   1740          reads = sample.get_reads_as_list()
   1741          trimmed_reads = []
   1742          trim_cmd = [
>> 1743              "trim_galore",
   1744              "--output_dir",
   1745              sample_dir,
   1746              "--cores",
   1747              str(threads),
   1748          ]
   1749          if sample.get_type() == "paired":
   1750              # trimmed_reads.append(os.path.join(sample_dir,os.path.basename(reads[0]).split(".")[0]+"_val_1.fq.gz"))
   1751              # trimmed_reads.append(os.path.join(sample_dir,os.path.basename(reads[1]).split(".")[0]+"_val_2.fq.gz"))
   1752              trim_cmd += ["--paired"]
   1753          # if sample.get_type() == "single":
   1754          #    trimmed_reads.append(os.path.join(sample_dir,os.path.basename(reads[0]).split('.')[0]+"_trimmed.fq.gz"))
   1755          trim_cmd += reads
```

## `pybin/p3x-assembly.py:1110`

```
   1104      #parser.add_argument('--fasta', nargs='*', help='list of fasta files "," between libraries', required=False)
   1105      parser.add_argument('--trusted_contigs', help='for SPAdes, same-species contigs known to be good', required=False)
   1106      parser.add_argument('--no_pilon', action='store_true', help='for unicycler', required=False)
   1107      parser.add_argument('--untrusted_contigs', help='for SPAdes, same-species contigs used gap closure and repeat resolution', required=False)
   1108      parser.add_argument('-t', '--threads', metavar='cores', type=int, default=8)
   1109      parser.add_argument('-m', '--memory', metavar='GB', type=int, default=DEFAULT_MEMORY_GIGABYTES, help='RAM limit in Gb')
>> 1110      parser.add_argument('--trim', action='store_true', help='trim reads with trim_galore at default settings')
   1111      parser.add_argument('--normalize', action='store_true', help='normalize read depth to target depth with BBNorm')
   1112      parser.add_argument('--filtlong', action='store_true', help='filter long reads to target depth using filtlong')
   1113      parser.add_argument('--target_depth', type=int, default=200, help='downsample to this approx. coverage')
   1114      parser.add_argument('--pilon_jar', help='path to pilon executable or jar', default=None)
   1115      parser.add_argument('--canu_exec', default="canu", help='path to canu executable (def "canu")')
   1116      parser.add_argument('--spades_for_unicycler', help='path to spades.py suitable for unicycler')
   1117      parser.add_argument('--bandage', action='store_true', help='generate image of assembly path using Bandage')
   1118      parser.add_argument('--maxContigsForBandage', type=int, default=100, help='only generage Bandage for this or fewer contigs')
   1119      parser.add_argument('--params_json', help='JSON file with additional information.')
   1120      parser.add_argument('--path_prefix', '--path-prefix', help="Add the given directories to the PATH", nargs='*', required=False)
   1121      parser.add_argument('-v', '--verbose', action='store_true', help="Output more progress information.", required=False)
   1122      parser.add_argument('--debug', action='store_true', help="Save intermediate files.", required=False)
```

## `plbin/App-FastqUtils.pl:171`

```
    165      print JDESC JSON::XS->new->pretty(1)->encode($params_to_app);
    166      close(JDESC);
    167  
    168      my $parallel = $ENV{P3_ALLOCATED_CPU};
    169      my $override = {
    170  	fastqc => { -p => $parallel},
>>  171  	trim_galore => {-p => $parallel},
    172  	bowtie2 => {-p => $parallel},
    173  	hisat2 => {-p => $parallel},
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
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing_16s:103`

```
     97          tmp_r2 = 'output/{sample}/trimmed_reads/{sample}_R2_val_2.fq.gz',
     98      output: 
     99          r1 = 'output/{sample}/trimmed_reads/{sample}_R1_trimmed.fastq.gz',
    100          r2 = 'output/{sample}/trimmed_reads/{sample}_R2_trimmed.fastq.gz'
    101      shell:
    102          '''
>>  103              trim_galore --gzip --paired -o {params.out_dir} {input.r1} {input.r2}
    104  
    105              mv {params.tmp_r1} {output.r1}
    106              mv {params.tmp_r2} {output.r2}
    107          '''
    108  
    109  rule fastqc_on_trimmed_reads:
    110      input:
    111          trimmed_read = 'output/{sample}/trimmed_reads/{sample}_R{read_num}_trimmed.fastq.gz',
    112      params:
    113          fastqc_dir = 'output/{sample}/fastqc_results/trimmed_reads',
    114      output:
    115          fastqc_html = 'output/{sample}/fastqc_results/trimmed_reads/{sample}_R{read_num}_trimmed_fastqc.html',
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing_16s:87`

```
     81      output:
     82          trimmed_read = 'output/{sample}/trimmed_read/{sample}_trimmed.fastq.gz',
     83          trimming_report = 'output/{sample}/trimmed_read/{sample}.fastq.gz_trimming_report.txt'
     84      shell:
     85          '''
     86              mkdir -p {params.out_dir}
>>   87              trim_galore --gzip -o {params.out_dir} {input.raw_read}
     88  
     89              mv {params.tmp_name} {output.trimmed_read}
     90          '''
     91  
     92  rule fastqc_on_trimmed_read:
     93      input:
     94          trimmed_read = 'output/{sample}/trimmed_read/{sample}_trimmed.fastq.gz',
     95      params:
     96          fastqc_dir = 'output/{sample}/fastqc_results/trimmed_read'
     97      output:
     98          fastqc_html = 'output/{sample}/fastqc_results/trimmed_read/{sample}_trimmed_fastqc.html',
     99          fastqc_zip = 'output/{sample}/fastqc_results/trimmed_read/{sample}_trimmed_fastqc.zip'
```

## `pybin/demo_read_library.py:34`

```
     28      parser.add_argument('--nanopore', metavar='files', nargs='*', help='list of Oxford Nanotech fastq[.gz] files', required=False, default=[])
     29      parser.add_argument('--fasta', metavar='files', nargs='*', help='list of fasta[.gz] files', required=False, default=[])
     30      parser.add_argument('--anonymous_reads', metavar='files', nargs='*', help='unspecified read files, types automatically inferred.')
     31      parser.add_argument('--max_bases', type=int, default=MAX_BASES, help='downsample reads if more than this total bases.')
     32      parser.add_argument('--interleaved', nargs='*', help='list of fastq files which are interleaved pairs')
     33      parser.add_argument('-t', '--threads', metavar='cores', type=int, default=4)
>>   34      parser.add_argument('--trim', action='store_true', help='trim reads with trim_galore at default settings')
     35      parser.add_argument('--normalize', action='store_true', help='normalize read depth with BBNorm at default settings')
     36  
     37      args = parser.parse_args()
     38      
     39      WORK_DIR = args.outputDirectory
     40      ReadLibrary.WORK_DIR = WORK_DIR   
     41      if not os.path.exists(WORK_DIR):
     42          os.mkdir(WORK_DIR)
     43      ReadLibrary.NUM_THREADS = args.threads
     44      ReadLibrary.LOG = sys.stderr
     45      read_list = []
     46      if args.anonymous_reads:
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

## `pybin/p3x-assembly.py:23`

```
     17  Flye, Unicycler, Spades or canu as appropriate: 
     18      canu if only long reads (pacbio or nanopore), 
     19      Unicycler if illumina or iontorrent 
     20      and Unicycler for hybrid assemblies, eg Illumina plus PacBio
     21      or Spades if requested
     22  It can auto-detect read types (illumina, iontorrent, pacbio, nanopore)
>>   23  It can run trim_galore prior to assembling.
     24  It can run Quast to generate assembly quality statistics.
     25  It can perform 'polishing' using Pilon (for Illumina) or Racon (for pacbio or nanopore reads)
     26  TODO: properly handle different kinds of pacbio reads
     27  """
     28  
     29  DEFAULT_GENOME_SIZE = 5000000
     30  DEFAULT_MAX_BASES=1e10 # this is 2000X coverage for a 5M genome
     31  DEFAULT_MEMORY_GIGABYTES = 128
     32  LOG = None # create a log file at start of main()
     33  START_TIME = None
     34  WORK_DIR = None
     35  SAVE_DIR = None
```

## `lib/ReadLibrary.py:254`

```
    248                  with open(new_report_file, 'w') as F:
    249                      for rf in report_files:
    250                          with open(rf) as RF:
    251                              F.write(RF.read())
    252                  self.trim_report = new_report_file
    253          else:
>>  254              comment = "trim_galore did not generate trimmed reads"
    255              ReadLibrary.LOG.write(comment+"\n")
    256              self.problem.append(comment)
    257  
    258  
    259          self.processing_time = time() - startTime
    260          ReadLibrary.LOG.write("trim_short_reads duration: {}\n".format(self.processing_time))
    261          return
    262  
    263      def study_reads(self):
    264          """
    265          Determine read count and avg read length. 
    266          If paired, read both files.  
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

