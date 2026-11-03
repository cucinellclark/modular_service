# BV-BRC invocations of `filtlong` (filtlong)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 6 hunk(s) in 4 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/MobileElementDetection.pm`
- `lib/ReadLibrary.py`
- `plbin/App-GenomeAssembly2.pl`
- `pybin/p3x-assembly.py`

## `plbin/App-GenomeAssembly2.pl:234`

```
    228      #
    229      if ($params->{normalize})
    230      {
    231  	push(@params, '--normalize');
    232      }
    233  
>>  234      # We use filtlong here.
    235      #
    236      if ($params->{filtlong})
    237      {
    238  	push(@params, '--filtlong');
    239      }
    240  
>>  241      # Target depth for down-sampling by bbnorm and/or filtlong
    242      #
    243      if ($params->{target_depth})
    244      {
    245  	push(@params, '--target_depth', $params->{target_depth});
    246      }
    247  
    248      #
    249      # Contig filtering options
    250      #
    251      push(@params, "--min_contig_length", $params->{min_contig_len});
    252  
    253       push(@params, "--min_contig_coverage", $params->{min_contig_cov});
    254  
    255      #
    256      # Genome size; used as parameter for canu and flye
>>  257      # also used for filtlong downsampling to target_depth multiple of estimated genome size
    258      #
    259      push(@params, "--genome_size", $params->{genome_size});
    260  
    261      #
    262      # MAX_BASES is the upper limit on how much data gets analyzed
    263      #
    264      if (exists $params->{max_bases}) {
    265          push(@params, "--max_bases", $params->{max_bases});
    266          }
    267      elsif ($MAX_BASES) {
    268          push(@params, "--max_bases", $MAX_BASES);
    269      }
```

## `lib/ReadLibrary.py:505`

```
    499  
    500          ReadLibrary.LOG.write("normalize process time: {}\n".format(time() - startTime))
    501          return
    502  
    503      def filter_long_reads(self, target_bases, illumina_reads=None, save_original=False):
    504          """
>>  505          use filtlong to downsample long reads based on quality and kmer-matches to illlumina (proxy for accuracy)
    506          """
    507          ReadLibrary.LOG.write(f"filter_long_reads()\nreference = {illumina_reads}\n")
    508          if self.num_bases < target_bases:
    509              ReadLibrary.LOG.write(f" number of bases ({self.num_bases}) is already below target_bases ({target_bases}), skipping.\n")
    510              return 0
    511  
    512          startTime = time()
    513          self.store_current_version()
    514  
    515          if not self.length_class == 'long':
    516              raise Exception("trying to run filt_long on reads NOT marked as length_class=='long'")
    517  
>>  518          proc = subprocess.run("filtlong --version", shell=True, capture_output=True, text=True)
>>  519          ReadLibrary.program_version['filtlong'] = proc.stdout.strip()
    520  
    521          self.transformation = f"filter reads to target depth"
    522          ReadLibrary.LOG.write(self.transformation+"\n")
    523          ReadLibrary.LOG.write("files = "+", ".join(self.files)+"\n")
    524          read_file = self.files[0]
    525          out_file = os.path.basename(read_file) # will write to current working directory
    526          if out_file.endswith("gz"):
    527              out_file = out_file[:-3]
    528          if out_file.endswith(".fq"):
    529              out_file = out_file[:-3]
    530          if out_file.endswith(".fastq"):
    531              out_file = out_file[:-6]
    532          out_file += "_filtlong.fq"
    533  
    534          self.files[0] = out_file
    535          
    536          out_fh = open(out_file, 'w')
    537  
>>  538          command = ['filtlong', '--target_bases', str(target_bases)] 
    539          if illumina_reads:
    540              command.extend(['--illumina_1', illumina_reads.files[0]])
    541              command.extend(['--illumina_2', illumina_reads.files[1]])
    542          command.append(read_file)
>>  543          ReadLibrary.LOG.write("filtlong, command line = "+" ".join(command)+"\n")
    544          self.command = " ".join(command)+"\n"
    545          proc = subprocess.Popen(command, shell=False, stdout=out_fh, stderr=open(os.devnull, 'w'))
    546          proc.wait()
    547          out_fh.close()
    548          self.file_size[0] = os.path.getsize(out_file)
    549          self.files[0] = out_file
    550          if not save_original: 
    551              os.unlink(read_file) # free up disk space
    552          self.study_reads()
    553          ReadLibrary.LOG.write("after filtlong: files = "+", ".join(self.files)+"\n")
    554  
    555      def down_sample_reads(self, proportion_to_sample, save_original=False):
    556          """
>>  557          read file over size limit, down-sample using seqtk or filtlong
    558          """
    559          startTime = time()
    560          ReadLibrary.LOG.write(f"down_sample_reads({proportion_to_sample})\n")
    561          self.store_current_version()
    562          comment = ''
    563  
    564          self.command = ''
    565          self.transformation =f'downsample readset to {int(proportion_to_sample*100)}%'
    566          ReadLibrary.LOG.write(comment+"\n")
    567          ReadLibrary.LOG.write("files = "+", ".join(self.files)+"\n")
    568          if self.length_class == 'long':
    569              suffix = "_filtlong.fastq"
```

## `lib/ReadLibrary.py:590`

```
    584                  out_file = out_file[:-6]
    585              out_file += suffix
    586              
    587              out_fh = open(out_file, 'w')
    588              if self.length_class == 'long':
    589                  num_bases_to_save = int(proportion_to_sample * self.num_bases)
>>  590                  command = ['filtlong', '--target_bases', str(num_bases_to_save), read_file] 
    591              else:
    592                  num_reads_to_save = int(proportion_to_sample * self.num_reads / len(self.files))
    593                  command = ['seqtk', 'sample', '-2', read_file, str(num_reads_to_save)]
    594              ReadLibrary.LOG.write("downsample, command line = "+" ".join(command)+"\n")
    595              self.command += " ".join(command)+"\n"
    596              proc = subprocess.Popen(command, shell=False, stdout=out_fh, stderr=open(os.devnull, 'w'))
    597              proc.wait()
    598              out_fh.close()
    599              self.file_size[i] = os.path.getsize(out_file)
    600              self.files[i] = out_file
    601              if not save_original:  
    602                  os.unlink(read_file) # delete large original file to free up temp space
```

## `lib/ReadLibrary.py:16`

```
     10  import glob
     11  import shutil
     12  import copy
     13  from time import time, localtime, strftime, sleep
     14  
     15  def capture_filtlong_version():
>>   16      if not 'filtlong' in ReadLibrary.program_version:
>>   17          proc = subprocess.run("filtlong --version", shell=True, capture_output=True, text=True)
>>   18          ReadLibrary.program_version['filtlong'] = proc.stdout.strip()
     19  
     20  def capture_seqtk_version():
     21      if not 'seqtk' in ReadLibrary.program_version:
     22          proc = subprocess.run("seqtk", capture_output=True, text=True)
     23          for line in proc.stderr.split("\n"):
     24              m = re.match("Version:\s*(\S.*\S)", line)
     25              if m:
     26                  seqtk_version = m.group(1)
     27                  ReadLibrary.program_version['seqtk'] = seqtk_version
     28                  break
     29  
     30  def constrain_total_bases(read_library_list, total_bases_limit, save_original=False):
```

## `pybin/p3x-assembly.py:1112`

```
   1106      parser.add_argument('--no_pilon', action='store_true', help='for unicycler', required=False)
   1107      parser.add_argument('--untrusted_contigs', help='for SPAdes, same-species contigs used gap closure and repeat resolution', required=False)
   1108      parser.add_argument('-t', '--threads', metavar='cores', type=int, default=8)
   1109      parser.add_argument('-m', '--memory', metavar='GB', type=int, default=DEFAULT_MEMORY_GIGABYTES, help='RAM limit in Gb')
   1110      parser.add_argument('--trim', action='store_true', help='trim reads with trim_galore at default settings')
   1111      parser.add_argument('--normalize', action='store_true', help='normalize read depth to target depth with BBNorm')
>> 1112      parser.add_argument('--filtlong', action='store_true', help='filter long reads to target depth using filtlong')
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
   1123  
   1124  
```

## `lib/MobileElementDetection.pm:310`

```
    304      
    305      print "Starting genome assembly using GenomeAssembly2 app\n";
    306      
    307      # Extract assembly-related parameters from the incoming params
    308      my @assembly_keys = qw(paired_end_libs single_end_libs srr_ids recipe 
    309                            racon_iter pilon_iter trim target_depth normalize 
>>  310                            filtlong genome_size min_contig_len min_contig_cov
    311                            max_bases debug);
    312      
    313      my $assembly_input = { map { exists $params->{$_} ? ($_, $params->{$_}) : () } @assembly_keys };
    314      
    315      # Set assembly-specific output parameters
    316      # Use the job result folder as the base, similar to ComprehensiveGenomeAnalysis.pm
    317      my $assembly_folder = $app->result_folder . "/assembly";
    318      $assembly_input->{output_path} = $assembly_folder;
    319      $assembly_input->{output_file} = "assembly";
    320      
    321      $assembly_input->{recipe} ||= 'auto';
    322      
```

