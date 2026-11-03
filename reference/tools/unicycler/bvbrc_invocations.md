# BV-BRC invocations of `unicycler` (unicycler)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 6 hunk(s) in 3 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/GenomeAssembly2.json`
- `plbin/p3-submit-genome-assembly.pl`
- `pybin/p3x-assembly.py`

## `pybin/p3x-assembly.py:244`

```
    238      if os.path.exists("megahit_out/final.contigs.fa"):
    239          shutil.move("megahit_out/final.contigs.fa", "contigs.fasta") #rename to canonical name
    240      return assembly_data
    241  
    242  def runUnicycler(read_list, threads=1, min_contig_length=0, prefix="", spades_exec=None):
    243      LOG.write("runUnicycler: Time = %s\n"%(strftime("%a, %d %b %Y %H:%M:%S", localtime(time()))))
>>  244      proc = subprocess.Popen(["unicycler", "--version"], shell=False, stdout=subprocess.PIPE)
    245      version_text = proc.stdout.read().decode()
    246      if version_text:
    247          m = re.search(r"Unicycler\s+\S+", version_text, flags=re.IGNORECASE)
    248          if m:
    249              version_text = m.group(0) # entire match
    250      proc.wait()
    251      assembly_data = {}
>>  252      assembly_data['program'] = 'unicycler'
    253      assembly_data['version'] = version_text
    254  
>>  255      command = ["unicycler", "-t", str(threads), "-o", '.']
    256      if min_contig_length:
    257          command.extend(("--min_fasta_length", str(min_contig_length)))
    258      command.extend(("--keep", "2")) # keep files needed for re-run if necessary
    259      command.append("--no_pilon")  # we will run our own, if requested
    260      if spades_exec:
    261          command.extend(("--spades_path", spades_exec));
    262  
>>  263      # apparently unicycler can only accept one read set in each class (I tried multiple ways to submit 2 paired-end sets, failed)
    264      for read_set in read_list:
    265          if read_set.length_class == 'short':
    266              if len(read_set.files) > 1:
    267                  command.extend(("--short1", read_set.files[0], "--short2", read_set.files[1]))
    268              else:
    269                  command.extend(("--unpaired", read_set.files[0]))
    270  
    271          else:
    272              command.extend(("--long", read_set.files[0]))
    273  
    274      LOG.write(" ".join(command)+"\n")
    275      LOG.flush()
```

## `pybin/p3x-assembly.py:284`

```
    278      LOG.write("return code = %d\n"%return_code)
    279  
    280      if not (os.path.exists("assembly.fasta") and os.path.getsize("assembly.fasta")):
    281          comment = "First run of Unicycler resulted in no assembly, try again with more lenient parameters."
    282          LOG.write(comment+"\n")
    283          command.extend(("--mode", "bold", "--min_component_size", "300", "--min_dead_end_size", "300", "--depth_filter", "0.1"))
>>  284          comment = "re-run unicycler with command = "+" ".join(command)
    285          LOG.write(comment+"\n")
    286          with open(os.devnull, 'w') as FNULL: # send stdout to dev/null, it is too big and unicycle.log is better
    287              return_code = subprocess.call(command, shell=False, stdout=FNULL)
    288          LOG.write("return code = %d\n"%return_code)
    289  
    290      assembly_data['command'] = " ".join(command)
    291      unicyclerLogFile = "unicycler.log"
    292      if os.path.exists("unicycler.log"):
    293          unicyclerLogFile = prefix+"unicycler.log"
    294          shutil.move("unicycler.log", os.path.join(DETAILS_DIR, unicyclerLogFile))
    295  
    296      if not os.path.exists("assembly.fasta"):
```

## `pybin/p3x-assembly.py:1268`

```
   1262          LOG.write("number of long reads = {}\n".format(len(long_reads)))
   1263          if len(short_reads):
   1264              if any_short_fasta:
   1265                  args.recipe = "spades"
   1266                  LOG.write("auto recipe selecting spades due to presence of short fasta read data.\n")
   1267              else:
>> 1268                  args.recipe = "unicycler"
>> 1269                  LOG.write("auto recipe selecting unicycler due to presence of short fastq read data.\n")
   1270          elif len(long_reads):
   1271              args.recipe = "flye"
   1272              LOG.write("auto recipe selecting flye due to presence of long and absence of short read data.\n")
   1273          else:
   1274              comment = "auto recipe failed to find short or long reads\n"
   1275              LOG.write(comment)
   1276              raise Exception(comment)
   1277  
   1278      if ("meta" in args.recipe) or (args.recipe == 'megahit'): # meta-spades or meta-flye or megahit
   1279          args.pilon_iterations = 0
   1280          args.racon_iterations = 0
   1281          comment = "Because recipe is for metagenome, turning pilon and racon iterations off."
   1282          LOG.write(comment+"\n")
   1283  
   1284      contigs = ""
   1285      startTime = time()
   1286      assembly_data = None
>> 1287      if args.recipe == "unicycler":
   1288          spades_exec = None
   1289          if (args.spades_for_unicycler):
   1290              spades_exec = args.spades_for_unicycler
   1291          assembly_data = runUnicycler(read_list, threads=args.threads, min_contig_length=args.min_contig_length, prefix=args.prefix, spades_exec=spades_exec )
   1292  
   1293      elif args.recipe == "canu":
   1294          assembly_data = runCanu(read_list, canu_exec=args.canu_exec, threads=args.threads, genome_size=args.genome_size, memory=args.memory, prefix=args.prefix)
   1295  
   1296      elif "flye" in args.recipe:
   1297          assembly_data = runFlye(read_list, recipe=args.recipe, threads=args.threads, genome_size=args.genome_size, prefix=args.prefix)
   1298  
   1299      elif "spades" in args.recipe or args.recipe == "single-cell":
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
>> 1106      parser.add_argument('--no_pilon', action='store_true', help='for unicycler', required=False)
   1107      parser.add_argument('--untrusted_contigs', help='for SPAdes, same-species contigs used gap closure and repeat resolution', required=False)
   1108      parser.add_argument('-t', '--threads', metavar='cores', type=int, default=8)
   1109      parser.add_argument('-m', '--memory', metavar='GB', type=int, default=DEFAULT_MEMORY_GIGABYTES, help='RAM limit in Gb')
   1110      parser.add_argument('--trim', action='store_true', help='trim reads with trim_galore at default settings')
   1111      parser.add_argument('--normalize', action='store_true', help='normalize read depth to target depth with BBNorm')
   1112      parser.add_argument('--filtlong', action='store_true', help='filter long reads to target depth using filtlong')
   1113      parser.add_argument('--target_depth', type=int, default=200, help='downsample to this approx. coverage')
   1114      parser.add_argument('--pilon_jar', help='path to pilon executable or jar', default=None)
   1115      parser.add_argument('--canu_exec', default="canu", help='path to canu executable (def "canu")')
>> 1116      parser.add_argument('--spades_for_unicycler', help='path to spades.py suitable for unicycler')
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
   1128      args = parser.parse_args()
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
     40      --genome-size		  Estimated genome size (for canu)
     41  
     42      The following options describe the read libraries:
     43  
     44      --platform STR		 The sequencing platform for the next read
```

