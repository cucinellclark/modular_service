# BV-BRC invocations of `megahit` (megahit)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 9 hunk(s) in 4 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/MetagenomeBinning/MetagenomeBinning.pm`
- `plbin/assemble_metagenomes.pl`
- `plbin/filter_contigs.pl`
- `pybin/p3x-assembly.py`

## `pybin/p3x-assembly.py:207`

```
    201              comment = "Problem running Bandage: "+str(ose)
    202              LOG.write(comment+"\n")
    203      return report
    204  
    205  def runMegahit(read_list, prefix, threads=4, memoryGB=16):
    206      LOG.write("runMegahit\n")
>>  207      proc = subprocess.Popen(["megahit", "--version"], shell=False, stdout=subprocess.PIPE)
    208      version_text = proc.stdout.read().decode()
    209      if version_text:
    210          m = re.search(r"MEGAHIT\s+\S+", version_text, flags=re.IGNORECASE)
    211          if m:
    212              version_text = m.group(0) # entire match
    213      proc.wait()
    214      assembly_data = {}
>>  215      assembly_data['program'] = 'megahit'
    216      assembly_data['version'] = version_text
    217  
    218      memoryBytes = memoryGB * 1024 * 1024 *1024
>>  219      command = ["megahit", "-t", str(threads), '-m', str(memoryBytes)]
    220      for read_set in read_list:
    221          if read_set.length_class == 'short':
    222              if len(read_set.files) > 1:
    223                  command.extend(("-1", read_set.files[0], "-2", read_set.files[1]))
    224              else:
    225                  command.extend(("--read", read_set.files[0]))
    226  
    227      LOG.write(" ".join(command)+"\n")
    228      LOG.flush()
    229      assembly_data['command'] = " ".join(command)
    230      proc = subprocess.run(command, shell=False)
    231      proc.check_returncode()
```

## `lib/Bio/P3/MetagenomeBinning/MetagenomeBinning.pm:582`

```
    576  	    $bytes = $mem;
    577  	}
    578  	$mem = int($bytes / (1024*1024*1024));
    579  	push(@$params, "--memory", $bytes);
    580      }
    581      
>>  582      my @cmd = ("megahit", @$params);
    583      print STDERR "@cmd\n";
    584      my $rc = system(@cmd);
    585      #my $rc = 0;
    586      if ($rc != 0)
    587      {
    588  	die "Error running assembly command: @cmd\n";
    589      }
    590  
    591      $self->app->workspace->save_file_to_file($self->assembly_dir . "/final.contigs.fa", {},
    592  					     $self->output_folder . "/contigs.fasta", 'contigs', 1, 1, $self->token);
    593      $self->app->workspace->save_file_to_file($self->assembly_dir . "/log", {},
    594  					     $self->output_folder . "/megahit.log", 'txt', 1, 1, $self->token);
```

## `pybin/p3x-assembly.py:1278`

```
   1272              LOG.write("auto recipe selecting flye due to presence of long and absence of short read data.\n")
   1273          else:
   1274              comment = "auto recipe failed to find short or long reads\n"
   1275              LOG.write(comment)
   1276              raise Exception(comment)
   1277  
>> 1278      if ("meta" in args.recipe) or (args.recipe == 'megahit'): # meta-spades or meta-flye or megahit
   1279          args.pilon_iterations = 0
   1280          args.racon_iterations = 0
   1281          comment = "Because recipe is for metagenome, turning pilon and racon iterations off."
   1282          LOG.write(comment+"\n")
   1283  
   1284      contigs = ""
   1285      startTime = time()
   1286      assembly_data = None
   1287      if args.recipe == "unicycler":
   1288          spades_exec = None
   1289          if (args.spades_for_unicycler):
   1290              spades_exec = args.spades_for_unicycler
```

## `plbin/assemble_metagenomes.pl:170`

```
    164  =item	-s, --skip
    165  
    166  A file that contains a list of metagenome ids to skip. That is, don't assemble these metagenomes. The file can be tab delimited with the id in the first column making the output of this command a suitable file for the -skip option in a future run.
    167  
    168  =item	-a, --assembler
    169  
>>  170  The assembler to use. The default is megahit. Only megahit is supported at this time.
    171  
    172  =back
    173  
    174  =head1	AUTHORS
    175  
    176  Thomas Brettin
    177  
    178  =cut
    179  
    180  
    181  
    182  1;
```

## `pybin/p3x-assembly.py:1093`

```
   1087      parser.add_argument('--nanopore', metavar='files', nargs='*', help='list of Oxford Nanotech fastq[.gz] files', required=False, default=[])
   1088      parser.add_argument('--fasta', metavar='files', nargs='*', help='list of fasta[.gz] files', required=False, default=[])
   1089      parser.add_argument('--sra', metavar='files', nargs='*', help='list of SRA run accessions (e.g. SRR5070677), will be downloaded from NCBI', required=False)
   1090      parser.add_argument('--anonymous_reads', metavar='files', nargs='*', help='unspecified read files, types automatically inferred.')
   1091      parser.add_argument('--max_bases', type=int, default=DEFAULT_MAX_BASES, help='downsample reads if more than this (per read set).')
   1092      parser.add_argument('--interleaved', nargs='*', help='list of fastq files which are interleaved pairs')
>> 1093      parser.add_argument('--recipe', choices=['unicycler', 'flye', 'meta-flye', 'canu', 'spades', 'meta-spades', 'plasmid-spades', 'single-cell', 'rna-spades', 'megahit', 'auto', 'none'], help='assembler to use', default='auto')
   1094      parser.add_argument('--contigs', metavar='fasta', help='perform polishing on existing assembly')
   1095      #parser.add_argument('--only-assembler', action='store true', help='omit spades read error correction')
   1096      
   1097      parser.add_argument('--racon_iterations', type=int, default=0, help='number of times to run racon per long-read file', required=False)
   1098      parser.add_argument('--pilon_iterations', type=int, default=0, help='number of times to run pilon per short-read file', required=False)
   1099      parser.add_argument('--pilon_hours', type=float, default=6.0, help='maximum hours to run pilon', required=False)
   1100      parser.add_argument('--prefix', default='', help='prefix for output files', required=False)
   1101      parser.add_argument('--genome_size', metavar='base pairs', type=int, default=DEFAULT_GENOME_SIZE, help='genome size for canu or flye, eg 5000000', required=False)
   1102      parser.add_argument('--min_contig_length', type=int, default=300, help='save contigs of this length or longer', required=False)
   1103      parser.add_argument('--min_contig_coverage', type=float, default=5, help='save contigs of this coverage or deeper', required=False)
   1104      #parser.add_argument('--fasta', nargs='*', help='list of fasta files "," between libraries', required=False)
   1105      parser.add_argument('--trusted_contigs', help='for SPAdes, same-species contigs known to be good', required=False)
```

## `plbin/assemble_metagenomes.pl:22`

```
     16  local $Log::Message::Simple::ERROR_FH   = \*LOG;
     17  local $Log::Message::Simple::DEBUG_FH   = \*LOG;
     18  
     19  my $help = 0;
     20  my $verbose = 1;
     21  my ($in, $out, %skip, $skip_file);
>>   22  my $assembler = 'megahit';
     23  our $cfg;
     24  
     25  GetOptions(
     26  	'h'	=> \$help,
     27          'i=s'   => \$in,
     28          'o=s'   => \$out,
     29  	'help'	=> \$help,
     30  	'input=s'  => \$in,
     31  	'output=s' => \$out,
     32          'v'        => \$verbose,
     33          'verbose'  => \$verbose,
     34  	's=s'	=> \$skip_file,
```

## `plbin/filter_contigs.pl:18`

```
     12  
     13  ### set default values
     14  my $help = 0;
     15  my $verbose = 1;
     16  my $coverage = 1;
     17  my $length = 1;
>>   18  my $assembler = 'megahit';
     19  my $PRINT = 0;
     20  
     21  GetOptions(
     22  	'h'	=> \$help,
     23          'i=s'   => \$in,
     24          'o=s'   => \$out,
     25  	'help'	=> \$help,
     26  	'input=s'  => \$in,
     27  	'output=s' => \$out,
     28          'v'        => \$verbose,
     29          'verbose'  => \$verbose,
     30  	'c=f'    => \$coverage,
```

## `pybin/p3x-assembly.py:1301`

```
   1295  
   1296      elif "flye" in args.recipe:
   1297          assembly_data = runFlye(read_list, recipe=args.recipe, threads=args.threads, genome_size=args.genome_size, prefix=args.prefix)
   1298  
   1299      elif "spades" in args.recipe or args.recipe == "single-cell":
   1300          assembly_data = runSpades(read_list, prefix=args.prefix, recipe=args.recipe, threads=args.threads, memoryGB=args.memory)
>> 1301      elif args.recipe == 'megahit':
   1302          assembly_data = runMegahit(read_list, prefix=args.prefix, threads=args.threads, memoryGB=args.memory)
   1303      elif args.recipe == 'none':
   1304          LOG.write("recipe specified as 'none', no assembly will be performed\n")
   1305      else:
   1306          LOG.write("cannot interpret args.recipe: "+args.recipe)
   1307  
   1308      elapsedTime = time() - startTime
   1309      elapsedHumanReadable = ""
   1310      if elapsedTime < 60:
   1311          elapsedHumanReadable = "%.1f minutes"%(elapsedTime/60.0)
   1312      elif elapsedTime < 3600:
   1313          elapsedHumanReadable = "%.2f hours"%(elapsedTime/3600.0)
```

## `lib/Bio/P3/MetagenomeBinning/MetagenomeBinning.pm:484`

```
    478  # current configuration and run the assembly.
    479  #
    480  sub assemble
    481  {
    482      my ($self) = @_;
    483  
>>  484      if ($self->{megahit_mode} || $self->params->{assembler} eq 'megahit')
    485      {
    486  	return $self->assemble_with_megahit();
    487      }
    488      else
    489      {
    490  	return $self->assemble_with_spades();
    491      }
    492  }
    493  
    494  sub assemble_with_spades
    495  {
    496      my($self) = @_;
```

