# BV-BRC invocations of `seqtk` (seqtk)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 9 hunk(s) in 6 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/CmdRunner.pm`
- `lib/ReadLibrary.py`
- `lib/process.py`
- `lib/report.py`
- `plbin/sars2-cdc-illumina.pl`
- `plbin/sars2-onecodex.pl`

## `lib/ReadLibrary.py:593`

```
    587              out_fh = open(out_file, 'w')
    588              if self.length_class == 'long':
    589                  num_bases_to_save = int(proportion_to_sample * self.num_bases)
    590                  command = ['filtlong', '--target_bases', str(num_bases_to_save), read_file] 
    591              else:
    592                  num_reads_to_save = int(proportion_to_sample * self.num_reads / len(self.files))
>>  593                  command = ['seqtk', 'sample', '-2', read_file, str(num_reads_to_save)]
    594              ReadLibrary.LOG.write("downsample, command line = "+" ".join(command)+"\n")
    595              self.command += " ".join(command)+"\n"
    596              proc = subprocess.Popen(command, shell=False, stdout=out_fh, stderr=open(os.devnull, 'w'))
    597              proc.wait()
    598              out_fh.close()
    599              self.file_size[i] = os.path.getsize(out_file)
    600              self.files[i] = out_file
    601              if not save_original:  
    602                  os.unlink(read_file) # delete large original file to free up temp space
    603  
    604          ReadLibrary.LOG.write("after: files = "+", ".join(self.files)+"\n")
    605          self.process_time = time() - startTime
```

## `lib/ReadLibrary.py:21`

```
     15  def capture_filtlong_version():
     16      if not 'filtlong' in ReadLibrary.program_version:
     17          proc = subprocess.run("filtlong --version", shell=True, capture_output=True, text=True)
     18          ReadLibrary.program_version['filtlong'] = proc.stdout.strip()
     19  
     20  def capture_seqtk_version():
>>   21      if not 'seqtk' in ReadLibrary.program_version:
>>   22          proc = subprocess.run("seqtk", capture_output=True, text=True)
     23          for line in proc.stderr.split("\n"):
     24              m = re.match("Version:\s*(\S.*\S)", line)
     25              if m:
     26                  seqtk_version = m.group(1)
>>   27                  ReadLibrary.program_version['seqtk'] = seqtk_version
     28                  break
     29  
     30  def constrain_total_bases(read_library_list, total_bases_limit, save_original=False):
     31      # apply the experiment-wide limit to set of reads
     32      # sample each library proportionally so total is capped to limit
     33      ReadLibrary.LOG.write(f"constrain_total_bases of {len(read_library_list)} input libraries to {total_bases_limit}\n")
     34      total_bases = 0
     35      long_read_bases = 0
     36      short_read_bases = 0
     37      for library in read_library_list:
     38          if not library.num_bases:
     39              library.study_reads()
```

## `lib/process.py:1295`

```
   1289              sample_file = r.split(".")  # TODO: change where this is output?
   1290              sample_file[len(sample_file) - 1] = "sampled"
   1291              sample_file.append("fq")
   1292              sample_file = ".".join(sample_file)
   1293              sampled_reads_list.append(sample_file)
   1294              sample_cmd = [
>> 1295                  "seqtk",
   1296                  "sample",
   1297                  "-s",
   1298                  "42",
   1299                  r,
   1300                  str(self.sampled_reads),
   1301              ]
   1302              sample.add_command("sample" + str(readNum), sample_cmd, "running")
   1303              print("Running command:\n{0}".format(" ".join(sample_cmd)))
   1304              try:
   1305                  # TODO: ENABLE
   1306                  with open(sample_file, "w") as so:
   1307                      subprocess.check_call(sample_cmd, stdout=so)
```

## `plbin/sars2-onecodex.pl:254`

```
    248  
    249  #
    250  # Clean up the ID line too to eliminate warnings later.
    251  #
    252  my $ok = $runner->run(["perl", "-pe", 's/^(>\S+).*$/\1/', $reference],
    253  		      '|',
>>  254  		      ["seqtk", "trimfq", "-e", 33, '-'], '>',  $trimmed);
    255  
    256  $ok or die "Failure $? running seqtk\n";
    257  
    258  #
    259  # Run the mapper
    260  # 
    261  
    262  $runner->run(["minimap2",
    263  	  @minimap_opts,
    264  	  $trimmed,
    265  	  @inputs,
    266  	  "-o", "$int_dir/minimap.out"]);
```

## `plbin/sars2-onecodex.pl:402`

```
    396  
    397  $runner->run(["sed",
    398  	  '/>/ s/$/ | One Codex consensus sequence/'],
    399  	 "<",
    400  	 "$ivar_file.fa",
    401  	 '|',
>>  402  	 [qw(seqtk seq -l 60 -)],
    403  	 ">",
    404  	 "$out_dir/$base.fasta");
    405  
    406  $runner->run(["cat", $reference, "$out_dir/$base.fasta"],
    407  	 '|',
    408  	 ["mafft", "--auto", "-"],
    409  	 '>',
    410  	 "$out_dir/$base.align");
    411  
    412  
    413  #
    414  # Create coverage plot
```

## `plbin/sars2-cdc-illumina.pl:265`

```
    259      @con1 = ( qw(samtools mpileup -aa -d 8000 -uf), $reference, $bamfile);
    260  }
    261  my @con2 = qw(bcftools call -Mc);
    262  my @con3 = ("tee", "-a", $vcf );
    263  my @con4 = qw(vcfutils.pl vcf2fq -D 100000000);
    264  push(@con4, "-d", $opt->min_depth);
>>  265  my @con5 = qw(seqtk seq -A -);
    266  my @con6 = qw(sed 2~2s/[actg]/N/g);
>>  267  my @con7 = qw(seqtk seq -l 60 -);
    268  
    269  $runner->run(\@con1, '|',
    270  	 \@con2, '|',
    271  	 \@con3, '|',
    272  	 \@con4, '|',
    273  	 \@con5, '|',
    274  	 \@con6, '|',
    275  	 \@con7, '>', $consensusfasta);
    276  
    277  #
    278  # Make sure any vcf files in the output folder are bgzipped/indexed.
    279  #
```

## `lib/Bio/P3/CmdRunner.pm:127`

```
    121  	if ($v =~ /version\s+(\S+)/)
    122  	{
    123  	    return $1;
    124  	}
    125  	return undef;
    126      }
>>  127      elsif ($base eq 'seqtk' ||
    128  	   $base eq 'samtools' ||
    129  	   $base eq 'tabix' ||
    130  	   $base eq 'bgzip' ||
    131  	   $base eq 'bcftools' ||
    132  	   $base eq 'bamclipper.sh')
    133      {
    134  	my $v;
    135  	IPC::Run::run([$cmd], '2>', \$v, '<', '/dev/null');
    136  	if ($v =~ /Version:\s+(\S+)/)
    137  	{
    138  	    return $1;
    139  	}
```

## `lib/ReadLibrary.py:557`

```
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

## `lib/report.py:311`

```
    305          fastqc_ref = "Andrews, S. (2010). FastQC:  A Quality Control Tool for High Throughput Sequence Data [Online]. Available online at: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/"
    306          reference_list.append("<li>" + fastqc_ref + "</li>")
    307          # trimgalore
    308          trimgalore_ref = "FelixKrueger. (n.d.). Felixkrueger/Trimgalore: A wrapper around Cutadapt and FASTQC to consistently apply adapter and quality \
    309                          trimming to FASTQ files, with extra functionality for RRBS Data. GitHub. https://github.com/FelixKrueger/TrimGalore"
    310          reference_list.append("<li>" + trimgalore_ref + "</li>")
>>  311          # seqtk
>>  312          seqtk_ref = "lh3. (n.d.). Lh3/SEQTK: Toolkit for processing sequences in FASTA/Q Formats. GitHub. https://github.com/lh3/seqtk"
    313          # samtools
    314          samtools_ref = "Heng Li, Bob Handsaker, Alec Wysoker, Tim Fennell, Jue Ruan, Nils Homer, Gabor Marth, Goncalo Abecasis, Richard Durbin, \
    315                          1000 Genome Project Data Processing Subgroup, The Sequence Alignment/Map format and SAMtools, Bioinformatics, Volume 25, \
    316                          Issue 16, 15 August 2009, Pages 2078–2079, https://doi.org/10.1093/bioinformatics/btp352"
    317          reference_list.append("<li>" + samtools_ref + "</li>")
    318          # bowtie/hisat
    319          bowtie_ref = "Langmead B, Salzberg SL. Fast gapped-read alignment with Bowtie 2. Nat Methods. 2012 Mar 4;9(4):357-9. doi: 10.1038/nmeth.1923. PMID: 22388286; PMCID: PMC3322381."
    320          hisat_ref = "Kim, D., Paggi, J.M., Park, C. et al. Graph-based genome alignment and genotyping with HISAT2 and HISAT-genotype. Nat Biotechnol 37, 907–915 (2019). https://doi.org/10.1038/s41587-019-0201-4"
    321          reference_list.append("<li>" + bowtie_ref + "</li>")
    322          reference_list.append("<li>" + hisat_ref + "</li>")
    323          # stringtie
    324          stringtie_ref = "Pertea M, Pertea GM, Antonescu CM, Chang TC, Mendell JT, Salzberg SL. StringTie enables improved reconstruction of a transcriptome from RNA-seq reads. \
```

