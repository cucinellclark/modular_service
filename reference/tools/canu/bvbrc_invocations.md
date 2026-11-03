# BV-BRC invocations of `canu` (canu)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 8 hunk(s) in 4 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/GenomeAssembly2.json`
- `plbin/App-GenomeAssembly2.pl`
- `plbin/p3-submit-genome-assembly.pl`
- `pybin/p3x-assembly.py`

## `plbin/App-GenomeAssembly2.pl:256`

```
    250      #
    251      push(@params, "--min_contig_length", $params->{min_contig_len});
    252  
    253       push(@params, "--min_contig_coverage", $params->{min_contig_cov});
    254  
    255      #
>>  256      # Genome size; used as parameter for canu and flye
    257      # also used for filtlong downsampling to target_depth multiple of estimated genome size
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
```

## `pybin/p3x-assembly.py:407`

```
    401          gfa_candidates = glob.glob("*gfa")
    402          if gfa_candidates:
    403              LOG.write("found gfa file: {}\n".format(gfa_candidates[-1]))
    404              shutil.move(gfa_candidates[-1], os.path.join(DETAILS_DIR, assemblyGraphFile))
    405      return assembly_data
    406  
>>  407  def runCanu(read_list, canu_exec="canu", threads=1, genome_size=DEFAULT_GENOME_SIZE, memory=DEFAULT_MEMORY_GIGABYTES, prefix=""):
    408      LOG.write("runCanu: Tiime = %s\n"%(strftime("%a, %d %b %Y %H:%M:%S", localtime(time()))))
    409      comment = """
>>  410  usage: canu [-version] [-citation] \
    411              [-correct | -trim | -assemble | -trim-assemble] \
    412              [-s <assembly-specifications-file>] \
    413              -p <assembly-prefix> \
    414              -d <assembly-directory> \
    415              genomeSize=<number>[g|m|k] \
    416              [other-options] \
    417              [-pacbio-raw | -pacbio-corrected | -nanopore-raw | -nanopore-corrected] file1 file2 ...
    418  
    419      https://canu.readthedocs.io/en/latest/parameter-reference.html
    420      """
>>  421      # canu -d /localscratch/allan/canu_assembly -p p6_25X gnuplotTested=true genomeSize=5m useGrid=false -pacbio-raw pacbio_p6_25X.fastq
>>  422      # first get canu version
    423      p = subprocess.Popen([canu_exec, "--version"], shell=False, stdout=subprocess.PIPE)
    424      canu_version = p.stdout.readline().decode().rstrip()
    425      assembly_data = {}
>>  426      assembly_data['program'] = 'canu'
    427      assembly_data['version'] = canu_version
    428      p.wait()
    429  
>>  430      command = [canu_exec, "-d", '.', "-p", "canu", "genomeSize=%d"%genome_size]
    431      command.extend(["maxMemory=" + str(memory), "maxThreads=" + str(threads)])
    432      if "1.7" in canu_version:
    433          # special handling for this version
    434          command.append("gnuplotTested=true")
    435          command.append("stopOnReadQuality=false")
    436      
    437      pacbio_reads = []
    438      nanopore_reads = []
    439      for read_set in read_list:
    440          if read_set.platform == 'pacbio':
    441              pacbio_reads.append(read_set.files[0])
    442          if read_set.platform == 'nanopore':
```

## `pybin/p3x-assembly.py:453`

```
    447      if nanopore_reads:
    448          command.append("-nanopore-raw")
    449          command.extend(nanopore_reads)
    450      if not len(pacbio_reads) + len(nanopore_reads):
    451          LOG.write("no long read files available for canu.\n")
    452          return None
>>  453      LOG.write("canu command =\n"+" ".join(command)+"\n")
    454      LOG.flush()
    455  
    456      return_code = subprocess.call(command, shell=False)
    457      assembly_data['command'] = " ".join(command)
    458  
    459      if os.path.exists("canu.report"):
    460          LOG.write("details_dir = %s\n"%DETAILS_DIR)
    461          LOG.write("canu_report file name = %s\n"%(prefix+"canu_report.txt"))
    462          canuReportFile = os.path.join(DETAILS_DIR, (prefix+"canu_report.txt"))
    463          LOG.write("moving canu.report to %s\n"%canuReportFile)
    464          shutil.move("canu.report", canuReportFile)
    465      
```

## `pybin/p3x-assembly.py:1293`

```
   1287      if args.recipe == "unicycler":
   1288          spades_exec = None
   1289          if (args.spades_for_unicycler):
   1290              spades_exec = args.spades_for_unicycler
   1291          assembly_data = runUnicycler(read_list, threads=args.threads, min_contig_length=args.min_contig_length, prefix=args.prefix, spades_exec=spades_exec )
   1292  
>> 1293      elif args.recipe == "canu":
   1294          assembly_data = runCanu(read_list, canu_exec=args.canu_exec, threads=args.threads, genome_size=args.genome_size, memory=args.memory, prefix=args.prefix)
   1295  
   1296      elif "flye" in args.recipe:
   1297          assembly_data = runFlye(read_list, recipe=args.recipe, threads=args.threads, genome_size=args.genome_size, prefix=args.prefix)
   1298  
   1299      elif "spades" in args.recipe or args.recipe == "single-cell":
   1300          assembly_data = runSpades(read_list, prefix=args.prefix, recipe=args.recipe, threads=args.threads, memoryGB=args.memory)
   1301      elif args.recipe == 'megahit':
   1302          assembly_data = runMegahit(read_list, prefix=args.prefix, threads=args.threads, memoryGB=args.memory)
   1303      elif args.recipe == 'none':
   1304          LOG.write("recipe specified as 'none', no assembly will be performed\n")
   1305      else:
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
>> 1101      parser.add_argument('--genome_size', metavar='base pairs', type=int, default=DEFAULT_GENOME_SIZE, help='genome size for canu or flye, eg 5000000', required=False)
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
   1114      parser.add_argument('--pilon_jar', help='path to pilon executable or jar', default=None)
>> 1115      parser.add_argument('--canu_exec', default="canu", help='path to canu executable (def "canu")')
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
   1127          sys.exit(2)
```

## `pybin/p3x-assembly.py:17`

```
     11  import glob
     12  from ReadLibrary import ReadLibrary
     13  from ReadLibrary import constrain_total_bases
     14  
     15  """
     16  This script organizes a command line for an assembly program: 
>>   17  Flye, Unicycler, Spades or canu as appropriate: 
>>   18      canu if only long reads (pacbio or nanopore), 
     19      Unicycler if illumina or iontorrent 
     20      and Unicycler for hybrid assemblies, eg Illumina plus PacBio
     21      or Spades if requested
     22  It can auto-detect read types (illumina, iontorrent, pacbio, nanopore)
     23  It can run trim_galore prior to assembling.
     24  It can run Quast to generate assembly quality statistics.
     25  It can perform 'polishing' using Pilon (for Illumina) or Racon (for pacbio or nanopore reads)
     26  TODO: properly handle different kinds of pacbio reads
     27  """
     28  
     29  DEFAULT_GENOME_SIZE = 5000000
     30  DEFAULT_MAX_BASES=1e10 # this is 2000X coverage for a 5M genome
```

## `lib/GenomeAssembly2.json:128`

```
    122  			"id":"recipe",
    123  			"label":"Assembly recipe",
    124  			"required": 0,
    125  			"default": "auto",
    126  			"desc":"Recipe used for assembly",
    127  			"type":"enum",
>>  128  			"enum": ["auto", "unicycler", "canu", "spades", "meta-spades", "plasmid-spades", "single-cell" ]
    129  		},
    130  		{
    131  			# new parameter
    132  			"id":"racon_iter",
    133  			"label":"Racon iterations",
    134  			"required": 0,
    135  			"default": 2,
    136  			#"range": [0,1,2,3,4]
    137  			"desc":"Racon polishing iterations (for long reads)",
    138  			"type":"int"
    139  		},
    140  		{
```

## `plbin/p3-submit-genome-assembly.pl:32`

```
     26      --single-end-lib LIB	 A single end read library. May be repeated.
     27      --srr-id STR		 Sequence Read Archive Run ID. May be repeated.
     28  
     29      The following options describe the processing requested:
     30  
     31      --recipe                      Assembly recipe. Defaults to auto.
>>   32  				  Valid values are auto, unicycler, canu,
     33  			          spades, meta-spades, plasmid-spades, single-cell
     34      --trim-reads		  Trim reads before assembly
     35      --racon-iter		  Number of racon polishing iterations (for long reads)
     36      --pilon-iter		  Number of pilon polishing iterations (for short reads)
     37      --min-contig-len		  Filter out short contigs in the final assembly.
     38      --min-contig-cov		  Filter out contigs with low read depth
     39  				  in the final assembly.
>>   40      --genome-size		  Estimated genome size (for canu)
     41  
     42      The following options describe the read libraries:
     43  
     44      --platform STR		 The sequencing platform for the next read
     45  				 library or libraries. Valid values are
     46  				 infer, illumina, pacbio, nanopore, iontorrent
     47      --read-orientation-inward	 The reads in the next read library face inward (defaults to true)
     48      --read-orientation-outward	 The reads in the next read library face outward (defaults to false)
     49  
     50  =cut
     51  
     52  use strict;
```

