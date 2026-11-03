# BV-BRC invocations of `racon` (racon)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 6 hunk(s) in 3 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/p3-submit-CGA.pl`
- `plbin/p3-submit-genome-assembly.pl`
- `pybin/p3x-assembly.py`

## `pybin/p3x-assembly.py:693`

```
    687      #LOG.write("samtools index return code = %d\n"%return_code)
    688      return (bamFileSorted, samtools_version)
    689  
    690  def runRacon(contigFile, read_set, num_threads, save_intermediate=False):
    691      """
    692      Polish (correct) sequence of assembled contigs by comparing to the original long-read sequences
>>  693      Run racon on reads, read-to-contig-sam, contigs. Generate polished contigs.
    694      Return name of polished contigs.
    695      """
    696      LOG.write('runRacon(%s, %s, %s)\n'%(contigFile, read_set.files[0], str(num_threads)))
>>  697      report = {"input_contigs":contigFile, "reads": read_set.files[0], "program": "racon"}
>>  698      command = ["racon", "--version"]
    699      proc = subprocess.Popen(command, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    700      proc.wait()
    701      version_text = proc.stderr.read().decode()
    702      if not version_text:
    703          version_text = proc.stdout.read().decode()
    704      racon_version = version_text.strip()
>>  705      report['program'] = 'racon'
    706      report['version'] = racon_version
    707  
    708      minimap_report = runMinimap(contigFile, read_set, num_threads, outformat='sam', save_intermediate=save_intermediate)
    709      report['minimap report'] = minimap_report
    710      readsToContigsSam = minimap_report['sam']
    711      if not readsToContigsSam:
    712          comment = "runMinimap failed to generate sam file, exiting runRacon"
    713          LOG.write(comment + "\n")
    714          return None
    715  
>>  716      command = ["racon", "-t", str(num_threads), "-u"]
    717      averageQuality = read_set.avg_quality
    718      if averageQuality:
    719          command.extend(['-q', "{:.2f}".format(averageQuality * 0.5)])
    720      command.extend([ read_set.files[0], readsToContigsSam, contigFile])
>>  721      LOG.write("racon command: \n"+' '.join(command)+"\n")
    722      raconContigs = contigFile.replace(".fasta", ".racon.fasta")
>>  723      report['racon command'] = ' '.join(command)
    724  
    725      raconStartTime = time()
    726      with open(raconContigs, 'w') as raconOut:
    727          FNULL = open(os.devnull, 'w') # send stdout to dev/null
    728          return_code = subprocess.call(command, shell=False, stderr=FNULL, stdout=raconOut)
>>  729      LOG.write("racon return code = %d, time = %d seconds\n"%(return_code, time()-raconStartTime))
    730      report['seconds'] = time()-raconStartTime
    731      if return_code != 0:
    732          return None
    733      if not save_intermediate:
    734          os.remove(readsToContigsSam)
    735      raconContigSize = os.path.getsize(raconContigs)
    736      LOG.write("size of raconContigs: %d\n"%raconContigSize)
    737      if raconContigSize < 10:
    738          return None
    739      if re.search("racon.racon.fasta", raconContigs):
    740          shorterFileName = re.sub("racon.racon.fasta", "racon.fasta", raconContigs)
    741          report['original_name'] = raconContigs
    742          shutil.move(raconContigs, shorterFileName)
    743          LOG.write("renaming {} to {}\n".format(raconContigs, shorterFileName))
    744          raconContigs = shorterFileName
    745      report['output'] = raconContigs
>>  746      comment = "racon, input %s, output %s"%(contigFile, raconContigs)
    747      LOG.write(comment+"\n")
    748      #os.remove(contigFile) #delete old one
    749      return report
    750  
    751  def runPilon(contigFile, read_set, num_threads, pilon_jar=None, save_intermediate=False):
    752      """ 
    753      polish contigs with short reads (illumina or iontorrent)
    754      first map reads to contigs with bowtie
    755      """
    756      LOG.write("runPilon starting Time = %s\n"%(strftime("%a, %d %b %Y %H:%M:%S", localtime(time()))))
    757      LOG.write("runPilon(%s, %s, %s)\n"%(contigFile, read_set.files[0], str(num_threads)))
    758      bowtieReport = runBowtie(contigFile, read_set, num_threads, outformat='bam', save_intermediate=save_intermediate)
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

## `pybin/p3x-assembly.py:1097`

```
   1091      parser.add_argument('--max_bases', type=int, default=DEFAULT_MAX_BASES, help='downsample reads if more than this (per read set).')
   1092      parser.add_argument('--interleaved', nargs='*', help='list of fastq files which are interleaved pairs')
   1093      parser.add_argument('--recipe', choices=['unicycler', 'flye', 'meta-flye', 'canu', 'spades', 'meta-spades', 'plasmid-spades', 'single-cell', 'rna-spades', 'megahit', 'auto', 'none'], help='assembler to use', default='auto')
   1094      parser.add_argument('--contigs', metavar='fasta', help='perform polishing on existing assembly')
   1095      #parser.add_argument('--only-assembler', action='store true', help='omit spades read error correction')
   1096      
>> 1097      parser.add_argument('--racon_iterations', type=int, default=0, help='number of times to run racon per long-read file', required=False)
   1098      parser.add_argument('--pilon_iterations', type=int, default=0, help='number of times to run pilon per short-read file', required=False)
   1099      parser.add_argument('--pilon_hours', type=float, default=6.0, help='maximum hours to run pilon', required=False)
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
```

## `pybin/p3x-assembly.py:1330`

```
   1324          comment = "assembly failed to generate contigs"
   1325          LOG.write(comment+"\n")
   1326          sys.exit(1) # signal job failure
   1327  
   1328      polishing_records = []
   1329      if args.racon_iterations and contigs:
>> 1330          # now run racon with each long-read file
   1331              for longReadSet in long_reads:
   1332                  for i in range(0, args.racon_iterations):
   1333                      LOG.write("runRacon on {}, {}, platform={}, round={}\n".format(contigs, longReadSet.files[0], longReadSet.platform, i))
   1334                      raconReport = runRacon(contigs, longReadSet, args.threads, save_intermediate=args.debug)
   1335                      raconContigFile = ''
   1336                      if raconReport:
   1337                          if 'output' in raconReport:
   1338                              raconContigFile = raconReport['output']
   1339                          polishing_records.append(raconReport)
>> 1340                          LOG.write("racon output = {}, report={}\n".format(raconContigFile, raconReport))
   1341                          if os.path.exists(raconContigFile):
   1342                              contigs = raconContigFile
   1343                              sys.stderr.write("contigs file is now {}\n".format(contigs))
   1344                          else:
   1345                              break # break out of iterating racon_iterations, go to next long-read file if any
   1346                      else:
   1347                          LOG.write("runRacon failed to return expected data")
   1348                          break
   1349          
   1350      if args.pilon_iterations and contigs:
   1351          pilon_end_time = time() + args.pilon_hours * 60 * 60
   1352          # now run pilon with each short-read file
```

## `plbin/p3-submit-CGA.pl:112`

```
    106  =item --pilon-iter
    107  
    108  Number of pilon iterations (default C<2>).
    109  
    110  =item --racon-iter
    111  
>>  112  Number of racon iterations (default <2>).
    113  
    114  =item --recipe
    115  
    116  Assembly recipe (C<auto>, C<full_spades>, C<fast>, C<miseq>, C<smart>, or C<kiki>; default C<auto>).
    117  
    118  =back
    119  
    120  The following option specifies the contigs for the genome.  If this is specified, the above options relating to reads
    121  should not be used.
    122  
    123  =over 4
    124  
```

## `plbin/p3-submit-genome-assembly.pl:35`

```
     29      The following options describe the processing requested:
     30  
     31      --recipe                      Assembly recipe. Defaults to auto.
     32  				  Valid values are auto, unicycler, canu,
     33  			          spades, meta-spades, plasmid-spades, single-cell
     34      --trim-reads		  Trim reads before assembly
>>   35      --racon-iter		  Number of racon polishing iterations (for long reads)
     36      --pilon-iter		  Number of pilon polishing iterations (for short reads)
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
```

