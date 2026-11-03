# BV-BRC invocations of `bedtools` (bedtools)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 3 hunk(s) in 3 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/fastq_utils.py`
- `plbin/var-map.pl`
- `pybin/fastq_utils.py`

## `plbin/var-map.pl:158`

```
    152        run("bcftools consensus -c chain -f modified_ref.fa var.norm.vcf.gz > consensus");
    153        print "compute_consensus ended\n";
    154      }
    155  }
    156  
    157  sub compute_stats {
>>  158      verify_cmd(qw(samtools bedtools));
    159      -s "ref.fa.fai"     or run("samtools faidx ref.fa");
    160      if (-s "aln.raw.sam") {
    161        -s "raw.flagstat" or run("samtools flagstat aln.raw.sam > raw.flagstat");
    162      }
    163      if (-s "aln.bam") {
    164        -s "flagstat"       or run("samtools flagstat aln.bam > flagstat");
    165        -s "stats"          or run("samtools stats aln.bam -c 1,8000,1 > stats");
    166        # -s "depth"          or run("samtools depth aln.bam > depth");
>>  167        -s "depth"          or run("bedtools genomecov -ibam aln.bam -d > depth");
>>  168        -s "depth.hist"     or run("bedtools genomecov -ibam aln.bam > depth.hist");
>>  169        -s "cov.bedgraph"   or run("bedtools genomecov -ibam aln.bam -bga > cov.bedgraph");
>>  170        -s "uncov.10"       or run("bedtools genomecov -ibam aln.bam -bga | perl -ne 'chomp; \@c=split/\t/; \$ln=\$c[2]-\$c[1]; print join(\"\\t\", \@c, \$ln).\"\\n\" if \$c[3]<10;' > uncov.10" );
    171        -s "ref.fa.fai"     or run ("samtools faidx ref.fa");
    172        -s "chrom.sizes"     or run ("cut -f1,2 ref.fa.fai > chrom.sizes");
    173        -s "cov.bigwig"     or run ("bedGraphToBigWig cov.bedgraph chrom.sizes cov.bigwig");
    174        # BED start position 0-based and the end position 1-based (Example: NC_000962,1987085,1987701,0,616; the 0 coverage base really starts at 1987086)
    175      }
    176  }
    177  
    178  sub map_with_bwa_mem {
    179      verify_cmd(qw(bwa samtools));
    180      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    181      -s "read_1.fq"      or run_symlink($read1, "read_1.fq");
    182      -s "read_2.fq"      or run_symlink($read2, "read_2.fq");
```

## `pybin/fastq_utils.py:334`

```
    328                      "-n",
    329                      "-@",
    330                      str(sam_sort),
    331                      bam_file_aligned,
    332                  ]
    333                  bam2fq_cmd = [
>>  334                      "bedtools",
    335                      "bamtofastq",
    336                      "-i",
    337                      bam_file_sort_name,
    338                      "-fq",
    339                      fastq_file_aligned,
    340                  ]
    341                  bam2fqgz_cmd = ["gzip", fastq_file_aligned]
    342                  if read2:  # paired end
    343                      bam2fq_cmd += ["-fq2", fastq_file_aligned2]
    344                      bam2fqgz_cmd += [fastq_file_aligned2]
    345                  print(" ".join(sort_name_cmd))
    346                  # Need to sort by name to convert to fastq: samtools sort -n myBamFile.bam myBamFile.sortedByName
    347                  subprocess.run(
    348                      sort_name_cmd, check=True, stdout=open(bam_file_sort_name, "w")
    349                  )
    350                  cur_cleanup.append(bam_file_sort_name)
    351                  print((" ".join(bam2fq_cmd)))
    352                  with open(os.path.join(target_dir, "bedtools.log.txt"), "a") as fd:
>>  353                      print("Redirecting bedtools stderr to a log.", file=sys.stderr)
    354                      print(bam_file_sort_name, file=fd)
    355                      fd.flush()
    356                      subprocess.run(bam2fq_cmd, check=True, stderr=fd)
    357                  subprocess.run(bam2fqgz_cmd, check=True)
    358                  samtools_index_threads = parameters.get("samtools_index", {}).get(
    359                      "-p", "1"
    360                  )
    361                  if not samtools_index_threads:
    362                      samtools_index_threads = SAM_THREADS
    363                  subprocess.run(
    364                      [
    365                          "samtools",
```

## `lib/fastq_utils.py:334`

```
    328                      "-n",
    329                      "-@",
    330                      str(sam_sort),
    331                      bam_file_aligned,
    332                  ]
    333                  bam2fq_cmd = [
>>  334                      "bedtools",
    335                      "bamtofastq",
    336                      "-i",
    337                      bam_file_sort_name,
    338                      "-fq",
    339                      fastq_file_aligned,
    340                  ]
    341                  bam2fqgz_cmd = ["gzip", fastq_file_aligned]
    342                  if read2:  # paired end
    343                      bam2fq_cmd += ["-fq2", fastq_file_aligned2]
    344                      bam2fqgz_cmd += [fastq_file_aligned2]
    345                  print(" ".join(sort_name_cmd))
    346                  # Need to sort by name to convert to fastq: samtools sort -n myBamFile.bam myBamFile.sortedByName
    347                  subprocess.run(
    348                      sort_name_cmd, check=True, stdout=open(bam_file_sort_name, "w")
    349                  )
    350                  cur_cleanup.append(bam_file_sort_name)
    351                  print((" ".join(bam2fq_cmd)))
    352                  with open(os.path.join(target_dir, "bedtools.log.txt"), "a") as fd:
>>  353                      print("Redirecting bedtools stderr to a log.", file=sys.stderr)
    354                      print(bam_file_sort_name, file=fd)
    355                      fd.flush()
    356                      subprocess.run(bam2fq_cmd, check=True, stderr=fd)
    357                  subprocess.run(bam2fqgz_cmd, check=True)
    358                  samtools_index_threads = parameters.get("samtools_index", {}).get(
    359                      "-p", "1"
    360                  )
    361                  if not samtools_index_threads:
    362                      samtools_index_threads = SAM_THREADS
    363                  subprocess.run(
    364                      [
    365                          "samtools",
```

