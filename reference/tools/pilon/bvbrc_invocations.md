# BV-BRC invocations of `pilon` (pilon)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 6 hunk(s) in 3 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/p3-submit-CGA.pl`
- `plbin/p3-submit-genome-assembly.pl`
- `pybin/p3x-assembly.py`

## `pybin/p3x-assembly.py:769`

```
    763          sys.stderr.write("Problem: runBowtie failed to return expected bamfile {}\n".format(bowtieReport['bam']))
    764          return None
    765      pilon_start_time = time()
    766      if (pilon_jar and os.path.exists(pilon_jar)):
    767          command = ['java', '-Xmx32G', '-jar', pilon_jar, '--genome', contigFile]
    768      else:
>>  769          command = ['pilon', '--genome', contigFile]
    770      if len(read_set.files) > 1:
    771          command.extend(('--frags', bowtieReport['bam']))
    772      else:
    773          command.extend(('--unpaired', bowtieReport['bam']))
    774      pilonPrefix = contigFile.replace(".fasta", "")
    775      m = re.match(".*pilon_(\d+)", pilonPrefix)
    776      if m :
    777          level = int(m.group(1))
    778          pilonPrefix = re.sub("pilon_"+m.group(1), "pilon_{}".format(level+1), pilonPrefix)
    779      else:
    780          pilonPrefix += "_pilon_1"
>>  781      pilonContigs = pilonPrefix  # + ".fasta" this gets added by pilon
    782      command.extend(('--outdir', '.', '--output', pilonContigs, '--changes'))
    783      command.extend(('--threads', str(num_threads)))
    784      LOG.write(" ".join(command)+"\n")
    785      LOG.write("bamfile = {}, size={}\n".format(bowtieReport['bam'], os.path.getsize(bowtieReport['bam'])))
    786      return_code = subprocess.call(command, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
>>  787      LOG.write("pilon return code = %d\n"%return_code)
    788      pilon_time = time() - pilon_start_time
>>  789      LOG.write("pilon duration = %d\n"%(pilon_time))
    790      LOG.flush()
    791      if not save_intermediate:
    792          os.remove(bowtieReport['bam'])
    793          if os.path.exists(bowtieReport['bam']+".bai"):
    794              os.remove(bowtieReport['bam']+".bai")
    795      if return_code != 0:
    796          return None
    797      pilon_changes = 0
    798      with open(pilonContigs+".changes") as CHANGES:
    799          pilon_changes = len(CHANGES.read().splitlines())
    800      if not save_intermediate:
    801          os.remove(pilonContigs+".changes")
    802      if (pilon_jar and os.path.exists(pilon_jar)):
    803          command = ["java", "-jar", pilon_jar, "--version"]
    804      else:
>>  805          command = ['pilon', '--version']
    806      proc = subprocess.run(command, shell=False, capture_output=True, text=True)
    807      pilon_version = proc.stdout
    808  
    809      report = {"input_contigs":contigFile, 
    810              "reads": ":".join(read_set.files), 
>>  811              "program": "pilon", 
    812              "version": pilon_version, 
    813              "output": pilonContigs+".fasta", 
    814              "num_changes": pilon_changes, 
    815              "seconds" : pilon_time,
    816              "bowtie_version": bowtieReport['version']}
    817      if 'samtools_version' in bowtieReport:
    818          report['samtools_version'] = bowtieReport['samtools_version']
    819  
>>  820      comment = "pilon, input %s, output %s, num_changes = %d"%(contigFile, pilonContigs, pilon_changes)
    821      LOG.write(comment+"\n")
    822      if not save_intermediate:
    823          os.remove(contigFile) # clean up old one
    824      return report 
    825  
    826  def calcReadDepth(bamfiles):
    827      """ Return dict of contig_ids to tuple of (coverage, normalized_coverage) """
    828      LOG.write("calcReadDepth(%s)\n"%" ".join(bamfiles))
    829      readDepth = {}
    830      command = ["samtools", "depth"]
    831      if type(bamfiles) is str:
    832          command.append(bamfiles)
```

## `pybin/p3x-assembly.py:1098`

```
   1092      parser.add_argument('--interleaved', nargs='*', help='list of fastq files which are interleaved pairs')
   1093      parser.add_argument('--recipe', choices=['unicycler', 'flye', 'meta-flye', 'canu', 'spades', 'meta-spades', 'plasmid-spades', 'single-cell', 'rna-spades', 'megahit', 'auto', 'none'], help='assembler to use', default='auto')
   1094      parser.add_argument('--contigs', metavar='fasta', help='perform polishing on existing assembly')
   1095      #parser.add_argument('--only-assembler', action='store true', help='omit spades read error correction')
   1096      
   1097      parser.add_argument('--racon_iterations', type=int, default=0, help='number of times to run racon per long-read file', required=False)
>> 1098      parser.add_argument('--pilon_iterations', type=int, default=0, help='number of times to run pilon per short-read file', required=False)
>> 1099      parser.add_argument('--pilon_hours', type=float, default=6.0, help='maximum hours to run pilon', required=False)
   1100      parser.add_argument('--prefix', default='', help='prefix for output files', required=False)
   1101      parser.add_argument('--genome_size', metavar='base pairs', type=int, default=DEFAULT_GENOME_SIZE, help='genome size for canu or flye, eg 5000000', required=False)
   1102      parser.add_argument('--min_contig_length', type=int, default=300, help='save contigs of this length or longer', required=False)
   1103      parser.add_argument('--min_contig_coverage', type=float, default=5, help='save contigs of this coverage or deeper', required=False)
   1104      #parser.add_argument('--fasta', nargs='*', help='list of fasta files "," between libraries', required=False)
   1105      parser.add_argument('--trusted_contigs', help='for SPAdes, same-species contigs known to be good', required=False)
   1106      parser.add_argument('--no_pilon', action='store_true', help='for unicycler', required=False)
   1107      parser.add_argument('--untrusted_contigs', help='for SPAdes, same-species contigs used gap closure and repeat resolution', required=False)
   1108      parser.add_argument('-t', '--threads', metavar='cores', type=int, default=8)
   1109      parser.add_argument('-m', '--memory', metavar='GB', type=int, default=DEFAULT_MEMORY_GIGABYTES, help='RAM limit in Gb')
   1110      parser.add_argument('--trim', action='store_true', help='trim reads with trim_galore at default settings')
   1111      parser.add_argument('--normalize', action='store_true', help='normalize read depth to target depth with BBNorm')
   1112      parser.add_argument('--filtlong', action='store_true', help='filter long reads to target depth using filtlong')
   1113      parser.add_argument('--target_depth', type=int, default=200, help='downsample to this approx. coverage')
>> 1114      parser.add_argument('--pilon_jar', help='path to pilon executable or jar', default=None)
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
   1125      if len(sys.argv) == 1:
   1126          parser.print_help()
```

## `pybin/p3x-assembly.py:1281`

```
   1275              LOG.write(comment)
   1276              raise Exception(comment)
   1277  
   1278      if ("meta" in args.recipe) or (args.recipe == 'megahit'): # meta-spades or meta-flye or megahit
   1279          args.pilon_iterations = 0
   1280          args.racon_iterations = 0
>> 1281          comment = "Because recipe is for metagenome, turning pilon and racon iterations off."
   1282          LOG.write(comment+"\n")
   1283  
   1284      contigs = ""
   1285      startTime = time()
   1286      assembly_data = None
   1287      if args.recipe == "unicycler":
   1288          spades_exec = None
   1289          if (args.spades_for_unicycler):
   1290              spades_exec = args.spades_for_unicycler
   1291          assembly_data = runUnicycler(read_list, threads=args.threads, min_contig_length=args.min_contig_length, prefix=args.prefix, spades_exec=spades_exec )
   1292  
   1293      elif args.recipe == "canu":
```

## `pybin/p3x-assembly.py:1352`

```
   1346                      else:
   1347                          LOG.write("runRacon failed to return expected data")
   1348                          break
   1349          
   1350      if args.pilon_iterations and contigs:
   1351          pilon_end_time = time() + args.pilon_hours * 60 * 60
>> 1352          # now run pilon with each short-read file
   1353          for read_set in short_reads:
   1354              fastqFile = read_set.files[0] # use only read_1 if paired
   1355              for iteration in range(0, args.pilon_iterations):
   1356                  if time() > pilon_end_time:
>> 1357                      LOG.write("Time expended on pilon exceeds allocation of {} hours. Omitting further pilon runs.".format(args.pilon_hours))
   1358                      break
   1359  
   1360                  LOG.write("runPilon(%s, %s, ...)\n"%(contigs, fastqFile))
   1361                  pilonReport = runPilon(contigs, read_set, args.threads, args.pilon_jar, save_intermediate=args.debug)
   1362                  if pilonReport:
   1363                      polishing_records.append(pilonReport)
   1364                      pilonContigFile = pilonReport['output']
   1365                      if pilonContigFile is not None and os.path.exists(pilonContigFile):
   1366                          contigs = pilonContigFile
   1367                          sys.stderr.write("contigs file is now {}\n".format(contigs))
   1368                      else:
   1369                          sys.stderr.write("expected contigs file {} does not exist\n".format(contigs))
```

## `plbin/p3-submit-CGA.pl:108`

```
    102  =item --trim
    103  
    104  If specified, the reads should be trimmed before assembly.
    105  
    106  =item --pilon-iter
    107  
>>  108  Number of pilon iterations (default C<2>).
    109  
    110  =item --racon-iter
    111  
    112  Number of racon iterations (default <2>).
    113  
    114  =item --recipe
    115  
    116  Assembly recipe (C<auto>, C<full_spades>, C<fast>, C<miseq>, C<smart>, or C<kiki>; default C<auto>).
    117  
    118  =back
    119  
    120  The following option specifies the contigs for the genome.  If this is specified, the above options relating to reads
```

## `plbin/p3-submit-genome-assembly.pl:36`

```
     30  
     31      --recipe                      Assembly recipe. Defaults to auto.
     32  				  Valid values are auto, unicycler, canu,
     33  			          spades, meta-spades, plasmid-spades, single-cell
     34      --trim-reads		  Trim reads before assembly
     35      --racon-iter		  Number of racon polishing iterations (for long reads)
>>   36      --pilon-iter		  Number of pilon polishing iterations (for short reads)
     37      --min-contig-len		  Filter out short contigs in the final assembly.
     38      --min-contig-cov		  Filter out contigs with low read depth
     39  				  in the final assembly.
     40      --genome-size		  Estimated genome size (for canu)
     41  
     42      The following options describe the read libraries:
     43  
     44      --platform STR		 The sequencing platform for the next read
     45  				 library or libraries. Valid values are
     46  				 infer, illumina, pacbio, nanopore, iontorrent
     47      --read-orientation-inward	 The reads in the next read library face inward (defaults to true)
     48      --read-orientation-outward	 The reads in the next read library face outward (defaults to false)
```

