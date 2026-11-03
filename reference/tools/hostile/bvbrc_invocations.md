# BV-BRC invocations of `hostile` (hostile)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 2 hunk(s) in 2 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/fastq_utils.py`
- `pybin/fastq_utils.py`

## `pybin/fastq_utils.py:457`

```
    451              r["read2"] += ".paired.fq"
    452      return read_list
    453  
    454  def run_hostile(read_list, output_dir, job_data, tool_params):
    455      """
    456      Run Hostile to remove host sequences from short and long read (meta)genomes.
>>  457      https://github.com/bede/hostile
    458      """
    459      output_dir = Path(output_dir)
    460      print(f"{output_dir=}", file=sys.stderr)
    461  
    462      # Set the cache dir for the index files
    463      # See https://github.com/bede/hostile/issues/32
>>  464      cache_dir = output_dir / "hostile"
    465      cache_dir.mkdir(exist_ok=True, parents=True)
    466      os.environ["HOSTILE_CACHE_DIR"] = str(cache_dir)
    467      print(f"{os.environ['HOSTILE_CACHE_DIR']=}", file=sys.stderr)
    468  
    469      log_path = output_dir / "hostile_report.txt"
    470      print(f"{log_path=}", file=sys.stderr)
    471  
>>  472      base_cmd = ["hostile", "clean", "--force",
    473             "--out-dir", str(output_dir), "--fastq1"]
    474  
    475      for r in read_list:
    476          print(f"{r=}", file=sys.stderr)
    477          if "read2" in r:
    478              cmd = base_cmd + [r["read1"], "--fastq2", r["read2"]]
    479          else:
    480              cmd = base_cmd + [r["read1"],]
    481  
    482          with log_path.open('w') as log_hdl:
    483              subprocess.run(cmd, check=True, stdout=log_hdl)
    484  
```

## `lib/fastq_utils.py:457`

```
    451              r["read2"] += ".paired.fq"
    452      return read_list
    453  
    454  def run_hostile(read_list, output_dir, job_data, tool_params):
    455      """
    456      Run Hostile to remove host sequences from short and long read (meta)genomes.
>>  457      https://github.com/bede/hostile
    458      """
    459      output_dir = Path(output_dir)
    460      print(f"{output_dir=}", file=sys.stderr)
    461  
    462      # Set the cache dir for the index files
    463      # See https://github.com/bede/hostile/issues/32
>>  464      cache_dir = output_dir / "hostile"
    465      cache_dir.mkdir(exist_ok=True, parents=True)
    466      os.environ["HOSTILE_CACHE_DIR"] = str(cache_dir)
    467      print(f"{os.environ['HOSTILE_CACHE_DIR']=}", file=sys.stderr)
    468  
    469      log_path = output_dir / "hostile_report.txt"
    470      print(f"{log_path=}", file=sys.stderr)
    471  
>>  472      base_cmd = ["hostile", "clean", "--force",
    473             "--out-dir", str(output_dir), "--fastq1"]
    474  
    475      for r in read_list:
    476          print(f"{r=}", file=sys.stderr)
    477          if "read2" in r:
    478              cmd = base_cmd + [r["read1"], "--fastq2", r["read2"]]
    479          else:
    480              cmd = base_cmd + [r["read1"],]
    481  
    482          with log_path.open('w') as log_hdl:
    483              subprocess.run(cmd, check=True, stdout=log_hdl)
    484  
```

