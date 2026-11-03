# BV-BRC invocations of `quast.py` (quast)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 6 hunk(s) in 4 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `pybin/core-genome-mlst-utils.py`
- `pybin/p3x-assembly.py`
- `pybin/reference_guided_assembly.py`
- `pybin/run_viral_assembly.py`

## `pybin/p3x-assembly.py:41`

```
     35  SAVE_DIR = None
     36  DETAILS_DIR = None
     37  
     38  def runQuast(contigsFile, min_contig_length, num_threads=1):
     39      LOG.write("runQuast: time = %s\n"%(strftime("%a, %d %b %Y %H:%M:%S", localtime(time()))))
     40      quastDir = "quast_out"
>>   41      quastCommand = ["quast.py",
     42                      "-o", quastDir,
     43                      "-t", str(num_threads),
     44                      "--min-contig", str(min_contig_length),
     45                      contigsFile]
     46      LOG.write("running quast: "+" ".join(quastCommand)+"\n")
     47      with open(os.devnull, 'w') as FNULL: # send stdout to dev/null
     48          return_code = subprocess.call(quastCommand, shell=False, stdout=FNULL, stderr=FNULL)
     49      LOG.write("return code = %d\n"%return_code)
     50      report = {}
     51      if return_code == 0:
     52          report['program'] = 'quast'
     53          report['command'] = ' '.join(quastCommand)
     54          report['report_file_path'] = os.path.join(quastDir, "report.txt")
     55          with open(os.path.join(quastDir, "report.txt")) as F:
     56              report['report_text'] = F.read()
>>   57          quastCommand = ["quast.py", "--version"]
     58          proc = subprocess.Popen(quastCommand, shell=False, stdout=subprocess.PIPE)
     59          version_text = proc.stdout.read().decode()
     60          proc.wait()
     61          report["version"] = version_text
     62          return report
     63      else:
     64          return None
     65  
     66  def filterContigsByLengthAndCoverage(inputContigs, read_list, min_contig_length=300, min_contig_coverage=5, num_threads=1, prefix=""):
     67      """ 
     68      Write only sequences at or above min_length and min coverage to output file.
     69      """
```

## `pybin/core-genome-mlst-utils.py:515`

```
    509          threads (int): Number of threads. Defaults to 12.
    510          min_contig (int): Minimum contig size. Defaults to 200.
    511      """
    512      os.makedirs(quast_output_dir, exist_ok=True)
    513  
    514      quast_cmd = [
>>  515          "quast.py",
    516          "-o", quast_output_dir,
    517          "-t", str(threads),
    518          "--min-contig", str(min_contig),
    519          fasta_file
    520      ]
    521  
    522      try:
    523          print(f"Running QUAST with command: {' '.join(quast_cmd)}")
    524          subprocess.run(quast_cmd, check=True)
    525          print("QUAST analysis completed successfully!")
    526      except subprocess.CalledProcessError as e:
    527          print(f"Error running QUAST: {e}")
```

## `pybin/run_viral_assembly.py:263`

```
    257          threads (int): Number of threads to use for QUAST. Defaults to 12.
    258          min_contig (int): Minimum contig size for QUAST analysis. Defaults to 200.
    259      """
    260      os.makedirs(quast_output_dir, exist_ok=True)
    261  
    262      quast_cmd = [
>>  263          "quast.py",
    264          "-o", quast_output_dir,
    265          "-t", str(threads),
    266          "--min-contig", str(min_contig),
    267          fasta_file
    268      ]
    269  
    270      try:
    271          print(f"Running QUAST with command: {' '.join(quast_cmd)}")
    272          subprocess.run(quast_cmd, check=True)
    273          print("QUAST analysis completed successfully!")
    274      except subprocess.CalledProcessError as e:
    275          print(f"Error running QUAST: {e}")
```

## `pybin/reference_guided_assembly.py:600`

```
    594                          all_out.write(fh.read())
    595  
    596      # QUAST on consensus
    597      quast_dir = outdir / "quast_reference_guided"
    598      ensure_dir(quast_dir)
    599      quast_cmd = (
>>  600          f"quast.py -o {quast_dir} -t 4 --min-contig 200 {consensus_primary}"
    601      )
    602      try:
    603          run_command(quast_cmd, f"QUAST reference-guided {sample_name}")
    604          quast_txt = quast_dir / "report.txt"
    605          # Move report.html up one level so it sits next to consensus FASTAs.
    606          quast_html_src = quast_dir / "report.html"
    607          quast_html_top = outdir / "report.html"
    608          if quast_html_src.exists():
    609              shutil.move(str(quast_html_src), str(quast_html_top))
    610              quast_html_rel = "report.html"
    611          else:
    612              quast_html_rel = ""
```

## `pybin/run_viral_assembly.py:584`

```
    578      # Retrieve software versions for reference-guided tools
    579      report_details["tools"] = {
    580        "bwa": get_software_version("bwa"),
    581        "samtools": get_software_version("samtools"),
    582        "bcftools": get_software_version("bcftools"),
    583        "fastp": get_software_version("fastp"),
>>  584        "quast": get_software_version("quast.py"),
    585      }
    586  
    587    else:
    588      # IRMA-based assembly
    589      assembly_output_dir = os.path.join(output_dir, strategy)
    590      lowqc_output_dir = os.path.join(output_dir, f"{strategy}_lowQC")
    591  
    592      if paired_end_lib:
    593        read1 = paired_end_lib.get("read1")
    594        read2 = paired_end_lib.get("read2")
    595        if not read1 or not read2:
    596          print("Error: Missing reads for paired-end library.")
```

## `pybin/run_viral_assembly.py:667`

```
    661      # Move individual segment files to the main output folder
    662      move_fasta_files(assembly_output_dir, output_dir)
    663  
    664      # Retrieve software versions
    665      report_details["tools"] = {
    666        "IRMA": get_software_version("IRMA"),
>>  667        "quast": get_software_version("quast.py")
    668      }
    669  
    670    # Generate HTML report (common to both strategies)
    671    html_report = generate_html_report(report_details)
    672    with open(os.path.join(output_dir, "AssemblyReport.html"), "w") as output_file:
    673      output_file.write(html_report)
```

