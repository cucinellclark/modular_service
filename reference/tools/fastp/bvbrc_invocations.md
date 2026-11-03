# BV-BRC invocations of `fastp` (fastp)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 2 hunk(s) in 2 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `pybin/reference_guided_assembly.py`
- `pybin/run_viral_assembly.py`

## `pybin/reference_guided_assembly.py:458`

```
    452  
    453      if not contigs:
    454          raise ValueError(f"No sequences detected in reference FASTA {multi_ref}")
    455  
    456      is_paired = bool(read1 and read2)
    457  
>>  458      # Trimming with fastp
    459      fastp_thr_opt = f"--thread {fastp_threads}" if fastp_threads and fastp_threads > 0 else ""
    460  
    461      trim1 = outdir / f"{sample_name}_1.trim.fastq"
    462      trim2 = outdir / f"{sample_name}_2.trim.fastq"
    463      trim_single = outdir / f"{sample_name}.trim.fastq"
    464  
    465      if is_paired:
    466          if not (read1 and read2):
    467              raise ValueError("Both read1 and read2 must be provided for paired-end reference-guided assembly.")
    468          run_command(
>>  469              f"fastp -i {read1} -I {read2} -o {trim1} -O {trim2} {fastp_thr_opt} "
    470              f"-h {outdir / (sample_name + '_fastp.html')} -j {outdir / (sample_name + '_fastp.json')}",
    471              f"Trim paired-end {sample_name}",
    472          )
    473      else:
    474          if not read_single and not read1:
    475              raise ValueError("A single-end read file must be provided for reference-guided assembly.")
    476          src = read_single or read1  # type: ignore[assignment]
    477          run_command(
>>  478              f"fastp -i {src} -o {trim_single} {fastp_thr_opt} "
    479              f"-h {outdir / (sample_name + '_fastp.html')} -j {outdir / (sample_name + '_fastp.json')}",
    480              f"Trim single-end {sample_name}",
    481          )
    482  
    483      # Align with bwa
    484      if not bwa_index_present(multi_ref):
    485          run_command(f"bwa index {multi_ref}", f"BWA index {multi_ref.name}")
    486  
    487      sam = outdir / f"{sample_name}.sam"
    488      bwa_thr_opt = f"-t {align_threads}" if align_threads and align_threads > 0 else ""
    489  
    490      if is_paired:
```

## `pybin/run_viral_assembly.py:583`

```
    577  
    578      # Retrieve software versions for reference-guided tools
    579      report_details["tools"] = {
    580        "bwa": get_software_version("bwa"),
    581        "samtools": get_software_version("samtools"),
    582        "bcftools": get_software_version("bcftools"),
>>  583        "fastp": get_software_version("fastp"),
    584        "quast": get_software_version("quast.py"),
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
```

