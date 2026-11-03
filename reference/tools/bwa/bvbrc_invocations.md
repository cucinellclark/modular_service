# BV-BRC invocations of `bwa` (bwa)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 7 hunk(s) in 5 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/compute_contig_coverage.pl`
- `plbin/var-map.pl`
- `pybin/p3_tnseq.py`
- `pybin/reference_guided_assembly.py`
- `pybin/run_viral_assembly.py`

## `plbin/var-map.pl:179`

```
    173        -s "cov.bigwig"     or run ("bedGraphToBigWig cov.bedgraph chrom.sizes cov.bigwig");
    174        # BED start position 0-based and the end position 1-based (Example: NC_000962,1987085,1987701,0,616; the 0 coverage base really starts at 1987086)
    175      }
    176  }
    177  
    178  sub map_with_bwa_mem {
>>  179      verify_cmd(qw(bwa samtools));
    180      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    181      -s "read_1.fq"      or run_symlink($read1, "read_1.fq");
    182      -s "read_2.fq"      or run_symlink($read2, "read_2.fq");
>>  183      -s "ref.fa.bwt"     or run("bwa index ref.fa");
>>  184      -s "aln-pe.sam"     or run("bwa mem -t $nthread ref.fa read_1.fq read_2.fq > aln-pe.sam 2>mem.log");
    185      -s "aln.raw.sam"    or run("ln -s -f aln-pe.sam aln.raw.sam");
    186      -s "aln.keep.bam"   or run("samtools view -@ $nthread -f 0x2 -bS aln.raw.sam > aln.keep.bam"); # keep only properly paired reads
    187      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
    188      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
    189    # -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread aln.keep.bam aln.sorted"); # v1.1
    190      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    191      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
    192    # -s "aln.bam"        or run("ln -s -f aln.sorted.bam aln.bam");
    193    # -s "aln.bam.bai"    or run("samtools index aln.bam"); # v1.1
    194      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    195  }
    196  
    197  sub map_with_bwa_mem_se {
>>  198      verify_cmd(qw(bwa samtools));
    199      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    200      -s "read.fq"        or run_symlink($read1, "read.fq");
>>  201      -s "ref.fa.bwt"     or run("bwa index ref.fa");
>>  202      -s "aln-se.sam"     or run("bwa mem -t $nthread ref.fa read.fq > aln-se.sam 2>mem.log");
    203      -s "aln.raw.sam"    or run("ln -s -f aln-se.sam aln.raw.sam");
    204      -s "aln.keep.bam"   or run("samtools view -@ $nthread -bS aln.raw.sam > aln.keep.bam");
    205      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
    206      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
    207      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    208      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
    209      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    210  }
    211  
    212  sub map_with_bwa_mem_strict {
>>  213      verify_cmd(qw(bwa samtools));
    214      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    215      -s "read_1.fq"      or run_symlink($read1, "read_1.fq");
    216      -s "read_2.fq"      or run_symlink($read2, "read_2.fq");
>>  217      -s "ref.fa.bwt"     or run("bwa index ref.fa");
>>  218      -s "aln-pe.sam"     or run("bwa mem -B9 -O16 -E1 -L5 -t $nthread ref.fa read_1.fq read_2.fq > aln-pe.sam 2>mem.log");
    219      -s "aln.raw.sam"    or run("ln -s -f aln-pe.sam aln.raw.sam");
    220      -s "aln.keep.bam"   or run("samtools view -@ $nthread -f 0x2 -q 10 -bS aln.raw.sam > aln.keep.bam"); # keep only properly paired reads
    221      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
    222      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
    223      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    224      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
    225      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    226  }
    227  
    228  sub map_with_bwa_mem_strict_se {
>>  229      verify_cmd(qw(bwa samtools));
    230      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    231      -s "read.fq"        or run_symlink($read1, "read.fq");
>>  232      -s "ref.fa.bwt"     or run("bwa index ref.fa");
>>  233      -s "aln-se.sam"     or run("bwa mem -B9 -O16 -E1 -L5 -t $nthread ref.fa read.fq > aln-se.sam 2>mem.log");
    234      -s "aln.raw.sam"    or run("ln -s -f aln-se.sam aln.raw.sam");
    235      -s "aln.keep.bam"   or run("samtools view -@ $nthread -bS -q 10 aln.raw.sam > aln.keep.bam");
    236      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
    237      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
    238      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    239      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
    240      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    241  }
    242  
    243  sub map_with_bowtie2 {
    244      verify_cmd(qw(bowtie2-build bowtie2 samtools));
    245      -s "ref.fa"         or run_symlink($ref, "ref.fa");
```

## `pybin/p3_tnseq.py:262`

```
    256          contig_ids_str = ",".join(contig_ids)
    257          genome_link = os.path.join(output_path, os.path.basename(genome["genome"]))
    258          final_cleanup = []
    259          if not os.path.exists(genome_link):
    260              subprocess.check_call(["ln", "-s", genome["genome"], genome_link])
    261          bwa_loc = str(
>>  262              subprocess.run(["which", "bwa"], capture_output=True).stdout, "utf-8"
    263          ).strip()
    264          if bwa_loc.startswith("which"):
    265              raise LookupError
    266          sys.stderr.write("Using BWA located at: {}\n".format(bwa_loc))
    267          sys.stderr.flush()
>>  268          # bwa_loc = "/opt/patric-common/runtime/bin/bwa"
    269          cmd = [
    270              "tpp",
    271              "-bwa",
    272              bwa_loc,
    273              "-ref",
    274              genome["genome"],
    275          ]
    276          # thread_count=multiprocessing.cpu_count()
    277          # cmd+=["-p",str(thread_count)]
    278          # if genome["dir"].endswith('/'):
    279          #    genome["dir"]=genome["dir"][:-1]
    280          # genome["dir"]=os.path.abspath(genome["dir"])
```

## `pybin/reference_guided_assembly.py:483`

```
    477          run_command(
    478              f"fastp -i {src} -o {trim_single} {fastp_thr_opt} "
    479              f"-h {outdir / (sample_name + '_fastp.html')} -j {outdir / (sample_name + '_fastp.json')}",
    480              f"Trim single-end {sample_name}",
    481          )
    482  
>>  483      # Align with bwa
    484      if not bwa_index_present(multi_ref):
>>  485          run_command(f"bwa index {multi_ref}", f"BWA index {multi_ref.name}")
    486  
    487      sam = outdir / f"{sample_name}.sam"
    488      bwa_thr_opt = f"-t {align_threads}" if align_threads and align_threads > 0 else ""
    489  
    490      if is_paired:
    491          run_command(
>>  492              f"bwa mem {bwa_thr_opt} {multi_ref} {trim1} {trim2} > {sam}",
    493              f"Align {sample_name} (PE)",
    494          )
    495      else:
    496          run_command(
>>  497              f"bwa mem {bwa_thr_opt} {multi_ref} {trim_single} > {sam}",
    498              f"Align {sample_name} (SE)",
    499          )
    500  
    501      bam_sorted = outdir / f"{sample_name}.sorted.bam"
    502      run_command(
    503          f"samtools view -Sb {sam} | samtools sort -o {bam_sorted}",
    504          f"Sort BAM {sample_name}",
    505      )
    506      run_command(f"samtools index {bam_sorted}", f"Index BAM {sample_name}")
    507  
    508      # Variant calling with bcftools
    509      vcf_gz = outdir / f"{sample_name}.vcf.gz"
```

## `pybin/run_viral_assembly.py:313`

```
    307    except subprocess.CalledProcessError as e:
    308      print(f"Error running IRMA: {e}")
    309      return False, ""
    310  
    311  
    312  # Tools that print version info to stderr (or with no args) rather than --version stdout.
>>  313  _VERSION_STDERR_TOOLS = {"bwa"}
    314  
    315  def get_software_version(software):
    316    try:
    317      if software in _VERSION_STDERR_TOOLS:
    318        # e.g. bwa: called with no args, version line appears in stderr
    319        result = subprocess.run(
    320          [software],
    321          stdout=subprocess.PIPE,
    322          stderr=subprocess.PIPE,
    323        )
    324        output = result.stderr
    325      else:
```

## `plbin/compute_contig_coverage.pl:107`

```
    101  
    102      print $oh $metagenome_id, "\t", $vars->{out_dir} . "/final.contigs.fa\n";
    103  
    104      msg( "cmd: finished", $verbose );
    105  
    106  
>>  107      my $cmd1 = bwa index $contigs;
>>  108      my $cmd2 = bwa mem $contig
    109  
    110      msg ("done processing $filename");
    111    }
    112  }
    113  else {
    114    die "no input found, input is required";
    115  }
    116  
    117  
    118  
    119   
    120  
```

## `pybin/run_viral_assembly.py:580`

```
    574        print(f"Reference-guided assembly failed: {e}")
    575        traceback.print_exc(file=sys.stderr)
    576        report_details["errors"].append("Reference-guided assembly failed.")
    577  
    578      # Retrieve software versions for reference-guided tools
    579      report_details["tools"] = {
>>  580        "bwa": get_software_version("bwa"),
    581        "samtools": get_software_version("samtools"),
    582        "bcftools": get_software_version("bcftools"),
    583        "fastp": get_software_version("fastp"),
    584        "quast": get_software_version("quast.py"),
    585      }
    586  
    587    else:
    588      # IRMA-based assembly
    589      assembly_output_dir = os.path.join(output_dir, strategy)
    590      lowqc_output_dir = os.path.join(output_dir, f"{strategy}_lowQC")
    591  
    592      if paired_end_lib:
```

## `pybin/run_viral_assembly.py:336`

```
    330        )
    331        output = result.stdout or result.stderr
    332  
    333      # Decode tolerantly — some tools (e.g. samtools) include non-UTF-8 chars like ©
    334      text = output.decode("utf-8", errors="replace")
    335  
>>  336      # bwa embeds version as "Version: X.X.X" inside the usage block; strip the label
    337      if software in _VERSION_STDERR_TOOLS:
    338        for line in text.splitlines():
    339          if "version:" in line.lower():
    340            # Extract just the version string after the colon, e.g. "0.7.17-r1188"
    341            version = line.split(":", 1)[-1].strip()
    342            print(f"{software} version: {version}")
    343            return version
    344        return "Unknown"
    345  
    346      version = text.splitlines()[0].strip()
    347      print(f"{software} version: {version}")
    348      return version
```

