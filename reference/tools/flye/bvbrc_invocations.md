# BV-BRC invocations of `flye` (flye)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 5 hunk(s) in 2 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/App-GenomeAssembly2.pl`
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

## `pybin/p3x-assembly.py:479`

```
    473      if os.path.exists("canu.contigs.gfa"):
    474          shutil.move("canu.contigs.gfa", os.path.join(DETAILS_DIR, prefix+"assembly_graph.gfa"))
    475      elif os.path.exists("canu.unitigs.gfa"):
    476          shutil.move("canu.unitigs.gfa", os.path.join(DETAILS_DIR, prefix+"assembly_graph.gfa"))
    477      return assembly_data
    478  
>>  479  def runFlye(read_list, recipe="flye", threads=1, genome_size=DEFAULT_GENOME_SIZE, prefix="flye_", memory=128):
    480      LOG.write("runFlye: Time = %s\n"%(strftime("%a, %d %b %Y %H:%M:%S", localtime(time()))))
    481      comment = """
>>  482  usage: flye (--pacbio-raw | --pacbio-corr | --pacbio-hifi | --nano-raw |
    483      --nano-corr | --nano-hq ) file1 [file_2 ...]
    484      --out-dir PATH
    485  
    486      [--genome-size SIZE] [--threads int] [--iterations int]
    487      [--meta] [--polish-target] [--min-overlap SIZE]
    488      [--keep-haplotypes] [--debug] [--version] [--help] 
    489      [--scaffold] [-uresume] [--resume-from] [--stop-after] 
    490      [--read-error float] [--extra-params]
    491      """
>>  492      # first get flye version
>>  493      p = subprocess.Popen(['flye', "--version"], shell=False, stdout=subprocess.PIPE)
    494      version_text = p.stdout.readline().decode().rstrip()
    495      assembly_data = {}
>>  496      assembly_data['program'] = 'flye'
    497      assembly_data['version'] = version_text
    498      p.wait()
    499  
    500      pacbio_reads = []
    501      nanopore_reads = []
    502      for read_set in read_list:
    503          #print("look at {}, type {}".platform(read_set.files[0], read_set.platform))
    504          if read_set.platform == 'pacbio':
    505              pacbio_reads.append(read_set.files[0])
    506          if read_set.platform == 'nanopore':
    507              nanopore_reads.append(read_set.files[0])
>>  508      command = ['flye', "--out-dir", '.', "--genome-size", str(genome_size), '--threads', str(threads)]
    509      if recipe == 'meta-flye':
    510          command.append("--meta")
    511      if pacbio_reads:
    512          command.append("--pacbio-raw")
    513          command.extend(pacbio_reads)
    514      elif nanopore_reads:
    515          command.append("--nano-raw")
    516          command.extend(nanopore_reads)
    517      #if memory:
    518      #    command.extend(['-str(memory)+"g")
    519      LOG.write(" ".join(command)+"\n")
    520      if not pacbio_reads + nanopore_reads:
```

## `pybin/p3x-assembly.py:1296`

```
   1290              spades_exec = args.spades_for_unicycler
   1291          assembly_data = runUnicycler(read_list, threads=args.threads, min_contig_length=args.min_contig_length, prefix=args.prefix, spades_exec=spades_exec )
   1292  
   1293      elif args.recipe == "canu":
   1294          assembly_data = runCanu(read_list, canu_exec=args.canu_exec, threads=args.threads, genome_size=args.genome_size, memory=args.memory, prefix=args.prefix)
   1295  
>> 1296      elif "flye" in args.recipe:
   1297          assembly_data = runFlye(read_list, recipe=args.recipe, threads=args.threads, genome_size=args.genome_size, prefix=args.prefix)
   1298  
   1299      elif "spades" in args.recipe or args.recipe == "single-cell":
   1300          assembly_data = runSpades(read_list, prefix=args.prefix, recipe=args.recipe, threads=args.threads, memoryGB=args.memory)
   1301      elif args.recipe == 'megahit':
   1302          assembly_data = runMegahit(read_list, prefix=args.prefix, threads=args.threads, memoryGB=args.memory)
   1303      elif args.recipe == 'none':
   1304          LOG.write("recipe specified as 'none', no assembly will be performed\n")
   1305      else:
   1306          LOG.write("cannot interpret args.recipe: "+args.recipe)
   1307  
   1308      elapsedTime = time() - startTime
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
```

## `pybin/p3x-assembly.py:1271`

```
   1265                  args.recipe = "spades"
   1266                  LOG.write("auto recipe selecting spades due to presence of short fasta read data.\n")
   1267              else:
   1268                  args.recipe = "unicycler"
   1269                  LOG.write("auto recipe selecting unicycler due to presence of short fastq read data.\n")
   1270          elif len(long_reads):
>> 1271              args.recipe = "flye"
>> 1272              LOG.write("auto recipe selecting flye due to presence of long and absence of short read data.\n")
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
```

