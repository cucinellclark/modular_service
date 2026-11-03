# BV-BRC invocations of `bowtie2` (bowtie2)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 21 hunk(s) in 9 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/CmdRunner.pm`
- `lib/fastq_utils.py`
- `lib/process.py`
- `plbin/App-FastqUtils.pl`
- `plbin/App-RNASeq.pl`
- `plbin/sars2-cdc-illumina.pl`
- `plbin/var-map.pl`
- `pybin/fastq_utils.py`
- `pybin/p3x-assembly.py`

## `plbin/var-map.pl:244`

```
    238      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    239      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
    240      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    241  }
    242  
    243  sub map_with_bowtie2 {
>>  244      verify_cmd(qw(bowtie2-build bowtie2 samtools));
    245      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    246      -s "read_1.fq"      or run_symlink($read1, "read_1.fq");
    247      -s "read_2.fq"      or run_symlink($read2, "read_2.fq");
    248      -s "ref.1.bt2"      or run("bowtie2-build ref.fa ref");
>>  249      -s "aln.raw.sam"    or run("bowtie2 -p $nthread -x ref -1 $read1 -2 $read2 -S aln.raw.sam");
    250      -s "aln.keep.bam"   or run("samtools view -@ $nthread -f 0x2 -q 10 -bS aln.raw.sam > aln.keep.bam"); # keep only properly paired reads
    251      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
    252      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
    253      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    254      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
    255      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    256  }
    257  
    258  sub map_with_bowtie2_se {
>>  259      verify_cmd(qw(bowtie2-build bowtie2 samtools));
    260      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    261      -s "read.fq"        or run_symlink($read1, "read.fq");
    262      -s "ref.1.bt2"      or run("bowtie2-build ref.fa ref");
>>  263      -s "aln.raw.sam"    or run("bowtie2 -p $nthread -x ref -U $read1 -S aln.raw.sam");
    264      -s "aln.keep.bam"   or run("samtools view -@ $nthread -bS -q 10 aln.raw.sam > aln.keep.bam");
    265      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
    266      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
    267      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    268      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
    269      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    270  }
    271  
    272  sub map_with_mosaik {
    273      # https://github.com/wanpinglee/MOSAIK/wiki/QuickStart
    274      verify_cmd(qw(MosaikBuild MosaikAligner samtools));
    275      my $bin_dir = dirname(which('MosaikAligner'));
```

## `pybin/fastq_utils.py:224`

```
    218              # thread count
    219              if "-p" in hisat2_params:
    220                  cmd += ["-p", str(hisat2_params["-p"])]
    221              hisat2_used = True
    222          else:
    223              subprocess.run(["bowtie2-build", genome_link, genome_link], check=True)
>>  224              bt2_threads = parameters.get("bowtie2", {}).get("-p", BT2_THREADS)
>>  225              cmd = ["bowtie2", "-p", str(bt2_threads), "-x", genome_link]
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

## `pybin/p3x-assembly.py:580`

```
    574          report['bam'] = contigBam
    575          report['samtools_version'] = samtools_version
    576      return report
    577              
    578  def runBowtie(contigFile, read_set, num_threads, outformat='bam', save_intermediate=False):
    579      """
>>  580      index contigsFile, then run bowtie2, then convert sam file to pos-sorted bam and index
    581      """
    582      LOG.write("runBowtie(%s, %s, %s, %s) %s\n"%(contigFile, read_set.files[0], str(num_threads), outformat, strftime("%a, %d %b %Y %H:%M:%S", localtime(time()))))
    583      report = {}
>>  584      report['program'] = 'bowtie2'
>>  585      command = ["bowtie2", '--version']
    586      proc = subprocess.run(command, shell=False, text=True, capture_output=True)
    587      m = re.search("version\s+(\S+)", proc.stdout + proc.stderr)
    588      if m:
    589          report['version'] = m.group(1)
    590  
    591      if os.path.exists("bowtie_index_dir"):
    592          # delete dir and all files there
    593          shutil.rmtree('bowtie_index_dir')
    594      os.mkdir("bowtie_index_dir")
    595      command = ["bowtie2-build", "--threads", str(num_threads), contigFile, 'bowtie_index_dir/'+contigFile]
    596      LOG.write("executing: "+" ".join(command)+"\n")
    597      return_code = subprocess.call(command, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
```

## `pybin/p3x-assembly.py:607`

```
    601          return None
    602  
    603      fastqBase = read_set.files[0]
    604      fastqBase = re.sub(r"\..*", "", fastqBase)
    605      samFile = contigFile+"_"+fastqBase+".sam"
    606  
>>  607      command = ["bowtie2", "-p", str(num_threads)]
    608      command.extend(["-x", 'bowtie_index_dir/'+contigFile])
    609      if len(read_set.files) > 1:
    610          #sys.stderr.write("we have a pair of read files\n")
    611          command.extend(('-1', read_set.files[0], '-2', read_set.files[1]))
    612      else:
    613          #sys.stderr.write("we have a list with a single read file\n")
    614          command.extend(('-U', read_set.files[0]))
    615      if read_set.format == 'fasta':
    616          command.append('-f')
    617      command.extend(('-S', samFile))
    618      LOG.write(" ".join(command)+"\n")
    619      return_code = subprocess.call(command, shell=False) #, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
>>  620      LOG.write("bowtie2 return code = %d\n"%return_code)
    621      #shutil.rmtree('bowtie_index_dir')
    622      report['command'] = ' '.join(command)
    623      report['sam'] = samFile
    624      if not save_intermediate:
    625          shutil.rmtree('bowtie_index_dir')# delete dir and all files there
    626      if outformat == 'bam':
    627          (contigsBam, samtools_version) = convertSamToBam(samFile, num_threads,  save_sam=save_intermediate)
    628          LOG.write('got bam file %s\n'%contigsBam)
    629          report['bam'] = contigsBam
    630          report['samtools_version'] = samtools_version
    631      return report
    632  
```

## `pybin/p3x-assembly.py:1023`

```
   1017                      if key == 'seconds':
   1018                          value = "{:.2f}".format(info[key])
   1019                      HTML.write("<tr><td>%s:</td><td>%s</td></tr>\n"%(key, value))
   1020                  HTML.write("<tr></tr>\n") # blank row
   1021                  program_version[info['program']] = info["version"]
   1022                  if 'bowtie2_version' in info:
>> 1023                      program_version['bowtie2'] = info['bowtie2_version']
   1024                  if 'samtools_version' in info:
   1025                      program_version['samtools'] = info['samtools_version']
   1026          HTML.write("</tbody></table>\n")
   1027          HTML.write("</section>\n")
   1028  
   1029      if "quast" in assembly_data:
   1030          HTML.write("<section><h2>Quast Report</h2>\n")
   1031          if 'report_text' in assembly_data["quast"]:
   1032              HTML.write("<pre>\n")
   1033              HTML.write(assembly_data["quast"]["report_text"])
   1034              HTML.write("\n</pre>\n")
   1035          HTML.write("</section>\n")
```

## `pybin/p3x-assembly.py:1051`

```
   1045              """)
   1046          for key in sorted(assembly_data['contig_filtering']):
   1047              HTML.write("<tr><td>{}:</td><td>{}</td></tr>\n".format(key, assembly_data['contig_filtering'][key])) 
   1048          HTML.write("</tbody></table>\n")
   1049          HTML.write("</section>\n")
   1050          if 'bowtie2_version' in assembly_data['contig_filtering']:
>> 1051              program_version['bowtie2'] = assembly_data['contig_filtering']['bowtie2_version']
   1052          if 'samtools_version' in assembly_data['contig_filtering']:
   1053              program_version['samtools'] = assembly_data['contig_filtering']['samtools_version']
   1054  
   1055      HTML.write('<div>\n<h2>Preprocessing of Reads</h2>\n')
   1056      for read_set in read_list:
   1057          read_set.writeHtml(HTML)
   1058      HTML.write("</div>\n")
   1059  
   1060      HTML.write("<section><h2>Tools Used:</h2>\n")
   1061      HTML.write("""
   1062          <table class="med-table kv-table">
   1063              <thead class="table-header">
```

## `lib/fastq_utils.py:224`

```
    218              # thread count
    219              if "-p" in hisat2_params:
    220                  cmd += ["-p", str(hisat2_params["-p"])]
    221              hisat2_used = True
    222          else:
    223              subprocess.run(["bowtie2-build", genome_link, genome_link], check=True)
>>  224              bt2_threads = parameters.get("bowtie2", {}).get("-p", BT2_THREADS)
>>  225              cmd = ["bowtie2", "-p", str(bt2_threads), "-x", genome_link]
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

## `plbin/sars2-cdc-illumina.pl:193`

```
    187      $runner->run(\@cutadapt1, '|', \@cutadapt2);
    188      
    189      #
    190      # Step 2. Mapping with bowtie. 
    191      #
    192      
>>  193      my @bowtie = ("bowtie2",
    194  		  "--sensitive-local",
    195  		  "-p", $threads,
    196  		  "-x", $reference,
    197  		  "-1", $trim1,
    198  		  "-2", $trim2,
    199  		  "-S", $samfile);
    200      $runner->run(\@bowtie, '2>', "$out_dir/bowtie2.err");
    201  }
    202  elsif ($mode eq 'SE')
    203  {
    204      #
    205      # Step 1. Adapter trimming.
```

## `plbin/sars2-cdc-illumina.pl:229`

```
    223      $runner->run(\@cutadapt);
    224      
    225      #
    226      # Step 2. Mapping with bowtie. 
    227      #
    228      
>>  229      my @bowtie = ("bowtie2",
    230  	      "--sensitive-local",
    231  	      "-p", $threads,
    232  	      "-x", $reference,
    233  	      "-U", $trim,
    234  	      "-S", $samfile);
    235      $runner->run(\@bowtie, '2>', "$out_dir/bowtie2.err");
    236  }
    237     
    238  #
    239  # Create bam format output
    240  #
    241  
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

## `lib/process.py:1110`

```
   1104          sample_dir = self.genome.get_sample_path(sample.get_id())
   1105          print("sample_dir = {0}".format(sample_dir))
   1106          reads_list = sample.get_reads_as_list()
   1107          sam_file = os.path.join(sample_dir, sample.get_id() + ".sam")
   1108          if self.genome.get_genome_type() == "bacteria":
   1109              align_cmd = [
>> 1110                  "bowtie2",
   1111                  "-x",
   1112                  self.genome.get_genome_data("bowtie_prefix"),
   1113              ]
   1114          else:
   1115              align_cmd = [
   1116                  "hisat2",
   1117                  "-x",
   1118                  self.genome.get_genome_data("hisat_prefix"),
   1119                  "--mp",
   1120                  "1,0",
   1121                  "--pen-noncansplice",
   1122                  "20",
```

## `lib/process.py:1324`

```
   1318          print("sampled reads list:\n{0}".format(sampled_reads_list))
   1319          # align sampled reads
   1320          # TODO: enable for host
   1321          sampled_sam = os.path.join(sample_dir, sample.get_id() + "_sample.sam")
   1322          if self.genome.get_genome_type() == "bacteria":
   1323              sample_align_cmd = [
>> 1324                  "bowtie2",
   1325                  "-x",
   1326                  self.genome.get_genome_data("bowtie_prefix"),
   1327              ]
   1328          else:
   1329              sample_align_cmd = [
   1330                  "hisat2",
   1331                  "-x",
   1332                  self.genome.get_genome_data("hisat_prefix"),
   1333                  "--mp",
   1334                  "1,0",
   1335                  "--pen-noncansplice",
   1336                  "20",
```

## `plbin/App-FastqUtils.pl:172`

```
    166      close(JDESC);
    167  
    168      my $parallel = $ENV{P3_ALLOCATED_CPU};
    169      my $override = {
    170  	fastqc => { -p => $parallel},
    171  	trim_galore => {-p => $parallel},
>>  172  	bowtie2 => {-p => $parallel},
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
    184  
```

## `lib/Bio/P3/CmdRunner.pm:176`

```
    170      }
    171      elsif ($base eq 'cat' ||
    172  	   $base eq 'sed' ||
    173  	   $base eq 'tee' ||
    174  	   $base eq 'medaka' ||
    175  	   $base eq 'bowtie2-build' ||
>>  176  	   $base eq 'bowtie2' ||
    177  	   $base eq 'vcf_mask_lowcoverage.pl')
    178      {
    179  	my $v;
    180  	IPC::Run::run([$cmd, '--version'], '>', \$v, '<', '/dev/null');
    181  	if ($v =~ /(\S+)$/m)
    182  	{
    183  	    return $1;
    184  	}
    185  	return undef;
    186  
    187      }
    188  
```

## `plbin/App-RNASeq.pl:292`

```
    286      my $dat = { data_api => "$data_api/genome_feature" };
    287      my $override = {
    288  	cufflinks => { -p => $parallel},
    289  	cuffdiff => {-p => $parallel},
    290  	cuffmerge => {-p => $parallel},
    291  	hisat2 => {-p => $parallel},
>>  292  	bowtie2 => {-p => $parallel},
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
    304      my $exps     = params_to_exps($params);
```

## `plbin/var-map.pl:18`

```
     12  use Getopt::Long;
     13  
     14  my $usage = <<"End_of_Usage";
     15  
     16  usage: $0 [options] ref.fq reads_1.fq [reads_2.fq]
     17  
>>   18         -a algo          - alignment algorithm [bwa_mem bwa_mem_strict bowtie2 mosaik last] (D = bwa_mem)
     19         -o dir           - output directory (D = ref_reads_[algo])
     20         -t int           - number of threads (D = 8)
     21         -m size          - max memory per thread; suffix K/M/G recognized (D = 2G)
     22         --vc tool        - variant calling [bcftools freebayes] (D = freebayes)
     23  
     24  End_of_Usage
     25  
     26  my ($help, $algo, $memory, $nthread, $outdir, $paired, $vc, $path_prefix);
     27  
     28  GetOptions("h|help"        => \$help,
     29         "path-prefix=s" => \$path_prefix,
     30             "a|algo=s"      => \$algo,
```

## `pybin/fastq_utils.py:21`

```
     15  from multiprocessing import Process
     16  from pathlib import Path
     17  import requests
     18  import pycurl
     19  from fqutil_api import authenticateByEnv, getHostManifest
     20  
>>   21  # Default bowtie2 threads.
     22  BT2_THREADS = 2
     23  SAM_THREADS = 1
     24  
     25  # hisat2 has problems with spaces in filenames
     26  # prevent spaces in filenames. if one exists link the file to a no-space version.
     27  
     28  
     29  def link_space(file_path):
     30      result = file_path
     31      name = os.path.splitext(os.path.basename(file_path))[0]
     32      if " " in name:
     33          clean_name = name.replace(" ", "")
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

## `lib/fastq_utils.py:21`

```
     15  from multiprocessing import Process
     16  from pathlib import Path
     17  import requests
     18  import pycurl
     19  from fqutil_api import authenticateByEnv, getHostManifest
     20  
>>   21  # Default bowtie2 threads.
     22  BT2_THREADS = 2
     23  SAM_THREADS = 1
     24  
     25  # hisat2 has problems with spaces in filenames
     26  # prevent spaces in filenames. if one exists link the file to a no-space version.
     27  
     28  
     29  def link_space(file_path):
     30      result = file_path
     31      name = os.path.splitext(os.path.basename(file_path))[0]
     32      if " " in name:
     33          clean_name = name.replace(" ", "")
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

