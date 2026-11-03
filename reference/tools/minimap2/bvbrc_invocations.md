# BV-BRC invocations of `minimap2` (minimap2)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 13 hunk(s) in 8 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/CmdRunner.pm`
- `lib/fastq_utils.py`
- `plbin/p3-submit-variation-analysis.pl`
- `plbin/sars2-cdc-nanopore.pl`
- `plbin/sars2-onecodex.pl`
- `plbin/var-map.pl`
- `pybin/fastq_utils.py`
- `pybin/p3x-assembly.py`

## `plbin/var-map.pl:361`

```
    355      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    356      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
    357      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    358  }
    359  
    360  sub map_with_minimap2 {
>>  361      verify_cmd(qw(minimap2 samtools));
    362      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    363      -s "read_1.fq"      or run_symlink($read1, "read_1.fq");
    364      -s "read_2.fq"      or run_symlink($read2, "read_2.fq");
>>  365      -s "aln-pe.sam"     or run("minimap2 -t $nthread -a ref.fa read_1.fq read_2.fq -o aln-pe.sam");
    366      -s "aln.raw.sam"    or run("ln -s -f aln-pe.sam aln.raw.sam");
    367      -s "aln.keep.bam"   or run("samtools view -@ $nthread -bS aln.raw.sam > aln.keep.bam");
    368      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
    369      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
    370      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    371      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
    372      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    373  }
    374  
    375  sub map_with_minimap2_se {
>>  376      verify_cmd(qw(minimap2 samtools));
    377      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    378      -s "read.fq"        or run_symlink($read1, "read.fq");
>>  379      -s "aln-se.sam"     or run("minimap2 -t $nthread -a ref.fa read.fq -o aln-se.sam");
    380      -s "aln.raw.sam"    or run("ln -s -f aln-se.sam aln.raw.sam");
    381      -s "aln.keep.bam"   or run("samtools view -@ $nthread -bS aln.raw.sam > aln.keep.bam");
    382      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
    383      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
    384      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    385      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
    386      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    387  }
    388  
    389  sub map_with_snippy {
    390      verify_cmd(qw(snippy));
    391      -s "ref.fa"         or run_symlink($ref, "ref.fa");
```

## `pybin/fastq_utils.py:187`

```
    181      else:
    182          return []
    183  
    184  def run_alignment(genome_list, read_list, parameters, output_dir, job_data):
    185      # modifies condition_dict sub replicates to include 'bowtie' dict recording output files
    186  
>>  187      # Get a minimap2 command ready for potential duty.
>>  188      mm2_cmd = ["minimap2", "-a"] # . . . '-a' is to output in SAM format
>>  189      mm2_params = parameters.get("minimap2", {})
    190      # thread count (tool default is 3)
    191      if "-t" in mm2_params:
    192          mm2_cmd += ["-t", str(mm2_params["-t"])]
    193  
    194      for genome in genome_list:
    195          genome_link = genome["genome_link"]
    196          final_cleanup = []
    197          hisat2_used = False
    198          if "hisat_index" in genome and genome["hisat_index"]:
    199              archive = tarfile.open(genome["hisat_index"])
    200              archive.extractall(path=output_dir)
    201              indices = []
```

## `pybin/fastq_utils.py:255`

```
    249                  if hisat2_used:
    250                      cur_cmd += [
    251                          "-U", link_space(r["read1"]),
    252                          "-S", str(sam_path),
    253                          "--un-gz", str(unmapped_fq_gz_path),
    254                      ]
>>  255                  else:  # minimap2
    256                      cur_cmd = mm2_cmd
    257                      cur_cmd += [
    258                          *get_minimap_preset(r.get("platform", None)),
    259                          "-o", str(sam_path),
    260                          genome_link,
    261                          link_space(r["read1"]),
    262                          ]
    263              print(f"{cur_cmd=}")
    264              cur_cleanup.append(str(sam_path))
    265              bam_file_all =        str(sam_path.with_suffix(".all.bam"))
    266              bam_file_aligned =    str(sam_path.with_suffix(".aligned.bam"))
    267              bam_file_sort_name =  str(sam_path.with_suffix(".aligned.name.bam"))
```

## `pybin/p3x-assembly.py:544`

```
    538          shutil.move("assembly_graph.gfa", os.path.join(DETAILS_DIR, prefix+"assembly_graph.gfa"))
    539      return assembly_data
    540  
    541  def runMinimap(contigFile, read_set, num_threads, outformat='sam', save_intermediate=False):
    542      LOG.write("runMinimap: Time = %s\n"%(strftime("%a, %d %b %Y %H:%M:%S", localtime(time()))))
    543      """
>>  544      Map long reads to contigs by minimap2 (read paf-file, readsFile; generate paf file).
    545      """
    546      report = {}
    547      LOG.write("runMinimap(%s, %s, %s, %s)\n"%(contigFile, read_set.files[0], str(num_threads), outformat))
>>  548      command = ["minimap2", "--version"]
    549      proc = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, text=True)
    550      proc.wait()
    551      version_text = proc.stdout.read()
>>  552      report['program'] = 'minimap2'
    553      report['version'] = version_text.strip()
    554  
    555      # map long reads to contigs
    556      contigSam = contigFile.replace(".fasta", ".sam")
>>  557      command = ["minimap2", "-t", str(num_threads)]
    558      if read_set.platform == 'nanopore':
    559          command.extend(["-x", "map-ont"])
    560      elif read_set.platform == 'pacbio':
    561          command.extend(["-x", "map-pb"])
    562      command.extend(["-a", "-o", contigSam, contigFile, read_set.files[0]])
    563      tempTime = time()
    564      LOG.write(' '.join(command)+"\n")
    565      report['command'] = ' '.join(command)
    566      return_code = subprocess.call(command, shell=False, stderr=subprocess.DEVNULL)
    567      if return_code != 0:
>>  568          LOG.write("minimap2 map return code = %d, time = %d seconds\n"%(return_code, time() - tempTime))
    569          return None
    570      report['sam'] = contigSam
    571  
    572      if outformat == 'bam':
    573          (contigBam, samtools_version) = convertSamToBam(contigSam, num_threads, save_sam=save_intermediate)
    574          report['bam'] = contigBam
    575          report['samtools_version'] = samtools_version
    576      return report
    577              
    578  def runBowtie(contigFile, read_set, num_threads, outformat='bam', save_intermediate=False):
    579      """
    580      index contigsFile, then run bowtie2, then convert sam file to pos-sorted bam and index
```

## `lib/fastq_utils.py:187`

```
    181      else:
    182          return []
    183  
    184  def run_alignment(genome_list, read_list, parameters, output_dir, job_data):
    185      # modifies condition_dict sub replicates to include 'bowtie' dict recording output files
    186  
>>  187      # Get a minimap2 command ready for potential duty.
>>  188      mm2_cmd = ["minimap2", "-a"] # . . . '-a' is to output in SAM format
>>  189      mm2_params = parameters.get("minimap2", {})
    190      # thread count (tool default is 3)
    191      if "-t" in mm2_params:
    192          mm2_cmd += ["-t", str(mm2_params["-t"])]
    193  
    194      for genome in genome_list:
    195          genome_link = genome["genome_link"]
    196          final_cleanup = []
    197          hisat2_used = False
    198          if "hisat_index" in genome and genome["hisat_index"]:
    199              archive = tarfile.open(genome["hisat_index"])
    200              archive.extractall(path=output_dir)
    201              indices = []
```

## `lib/fastq_utils.py:255`

```
    249                  if hisat2_used:
    250                      cur_cmd += [
    251                          "-U", link_space(r["read1"]),
    252                          "-S", str(sam_path),
    253                          "--un-gz", str(unmapped_fq_gz_path),
    254                      ]
>>  255                  else:  # minimap2
    256                      cur_cmd = mm2_cmd
    257                      cur_cmd += [
    258                          *get_minimap_preset(r.get("platform", None)),
    259                          "-o", str(sam_path),
    260                          genome_link,
    261                          link_space(r["read1"]),
    262                          ]
    263              print(f"{cur_cmd=}")
    264              cur_cleanup.append(str(sam_path))
    265              bam_file_all =        str(sam_path.with_suffix(".all.bam"))
    266              bam_file_aligned =    str(sam_path.with_suffix(".aligned.bam"))
    267              bam_file_sort_name =  str(sam_path.with_suffix(".aligned.name.bam"))
```

## `plbin/sars2-cdc-nanopore.pl:140`

```
    134  
    135      $runner->run(\@cmd);
    136      push(@filtered, $fastqfiltered);
    137  }
    138  
    139  #
>>  140  # Step 2. Mapping with minimap2
    141  #
    142  
>>  143  my @minimap = ("minimap2",
    144  	       "-L",
    145  	       "-a",
    146  	       "-x", "map-ont",
    147  	       "-t", $threads,
    148  	       $reference,
    149  	       @filtered);
    150  $runner->run(\@minimap, ">", $samfile);
    151  
    152  #
    153  # Create bam format output
    154  #
    155  
```

## `plbin/sars2-onecodex.pl:262`

```
    256  $ok or die "Failure $? running seqtk\n";
    257  
    258  #
    259  # Run the mapper
    260  # 
    261  
>>  262  $runner->run(["minimap2",
    263  	  @minimap_opts,
    264  	  $trimmed,
    265  	  @inputs,
    266  	  "-o", "$int_dir/minimap.out"]);
    267  
    268  if ($opt->delete_reads)
    269  {
    270      print STDERR "Deleting inputs @inputs\n";
    271      unlink(@inputs);
    272  }
    273  
    274  $runner->run_with_timeout(960, ["samtools",
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
>>  294                  if not (read2 or hisat2_used): # minimap2
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
    306  
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
>>  294                  if not (read2 or hisat2_used): # minimap2
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
    306  
```

## `lib/Bio/P3/CmdRunner.pm:162`

```
    156  	if ($v =~ /^(\S+)/)
    157  	{
    158  	    return $1;
    159  	}
    160  	return undef;
    161      }
>>  162      elsif ($base eq 'minimap2' ||
    163  	   $base eq 'gnuplot'
    164  	  )
    165      {
    166  	my $v;
    167  	IPC::Run::run([$cmd, '--version'], '>', \$v, '<', '/dev/null');
    168  	chomp $v;
    169  	return $v;
    170      }
    171      elsif ($base eq 'cat' ||
    172  	   $base eq 'sed' ||
    173  	   $base eq 'tee' ||
    174  	   $base eq 'medaka' ||
```

## `plbin/p3-submit-variation-analysis.pl:101`

```
     95  use Bio::KBase::AppService::CommonSpec;
     96  use Bio::KBase::AppService::ReadSpec;
     97  use Bio::KBase::AppService::UploadSpec;
     98  use Bio::KBase::AppService::GenomeIdSpec;
     99  
    100  use constant CALLERS => { 'FreeBayes' => 1, 'BCFtools' => 1, 'Snippy' => 1 };
>>  101  use constant MAPPERS => { 'BWA-mem' => 1, 'BWA-mem-strict' => 1, 'Bowtie2' => 1, 'LAST' => 1, 'minimap2' => 1, 'Snippy' => 1 };
    102  
    103  # Insure we're logged in.
    104  my $p3token = P3AuthToken->new();
    105  if (! $p3token->token()) {
    106      die "You must be logged into BV-BRC to use this script.";
    107  }
    108  # Get a common-specification processor, an uploader, and a reads-processor.
    109  my $commoner = Bio::KBase::AppService::CommonSpec->new();
    110  my $uploader = Bio::KBase::AppService::UploadSpec->new($p3token);
    111  my $reader = Bio::KBase::AppService::ReadSpec->new($uploader);
    112  
    113  # Get the application service helper.
```

## `plbin/sars2-onecodex.pl:157`

```
    151  my @se_read_files = @{$opt->se_read};
    152  
    153  #
    154  # Unpack the lists of -1 and -2 reads into pairs and verify the counts match.
    155  #
    156  # We also construct the @inputs list which is just the linearized list of
>>  157  # files. We assume the pair files are named such that minimap2 is happy with them.
    158  #
    159  
    160  my @inputs = @se_read_files;
    161  
    162  my @pe_read_files;
    163  
    164  my $n1 = @{$opt->pe_read_1};
    165  my $n2 = @{$opt->pe_read_2};
    166  
    167  if ($n1 != $n2)
    168  {
    169      die "Mismatch in paired end read file counts ($n1 mate-1, $n2 mate-2)\n";
```

