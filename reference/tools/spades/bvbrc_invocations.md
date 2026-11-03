# BV-BRC invocations of `spades.py` (spades)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 2 hunk(s) in 1 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `pybin/p3x-assembly.py`

## `pybin/p3x-assembly.py:310`

```
    304      contigsFile = "contigs.fasta"
    305      shutil.move("assembly.fasta", contigsFile) #rename to canonical name
    306      return assembly_data
    307  
    308  def runSpades(read_list, prefix="", recipe=None, threads=4, memoryGB=DEFAULT_MEMORY_GIGABYTES):
    309      LOG.write("runSpades Time = %s\n"%(strftime("%a, %d %b %Y %H:%M:%S", localtime())))
>>  310      command = ["spades.py", "--version"]
    311      proc = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    312      version_text = proc.stdout.read().decode().strip()
    313      if not version_text: # as of v3.14.1 this output came to stderr instead of stdout
    314          version_text = proc.stderr.read().decode().strip()
    315      proc.wait()
    316      assembly_data = {}
    317      assembly_data['program'] = 'spades'
    318      assembly_data['version'] = version_text
    319  
>>  320      command = ["spades.py", "--threads", str(threads), "-o", "."]
    321      if recipe == 'single-cell':
    322          command.append("--sc")
    323      if memoryGB:
    324          command.extend(["-m", str(memoryGB)])
    325      if recipe == "meta-spades":
    326          command.append("--meta")
    327      if recipe == "rna-spades":
    328          command.append("--rna")
    329          #
    330          # Validate arguments for metagenomic spades. It can only run with
    331          # a single paired-end library.
    332          #
```

## `pybin/p3x-assembly.py:1116`

```
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

