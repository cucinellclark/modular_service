# BV-BRC invocations of `snippy` (snippy)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 3 hunk(s) in 2 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/App-Variation.pl`
- `plbin/var-map.pl`

## `plbin/var-map.pl:390`

```
    384      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    385      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
    386      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    387  }
    388  
    389  sub map_with_snippy {
>>  390      verify_cmd(qw(snippy));
    391      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    392      -s "read_1.fq"      or run_symlink($read1, "read_1.fq");
    393      -s "read_2.fq"      or run_symlink($read2, "read_2.fq");
>>  394      -s "snps.vcf"       or run("snippy --cpus $nthread --outdir snippy_out --ref ref.fa --R1 read_1.fq --R2 read_2.fq");
    395      -s "aln.bam"        or run("ln -s -f snippy_out/snps.bam aln.bam");
    396      -s "aln.bam.bai"    or run("ln -s -f snippy_out/snps.bam.bai aln.bam.bai");
    397  }
    398  
    399  sub map_with_snippy_se {
>>  400      verify_cmd(qw(snippy));
    401      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    402      -s "read.fq"        or run_symlink($read1, "read.fq");
>>  403      -s "snps.vcf"       or run("snippy --cpus $nthread --outdir snippy_out --ref ref.fa --se read.fq");
    404      -s "aln.bam"        or run("ln -s -f snippy_out/snps.bam aln.bam");
    405      -s "aln.bam.bai"    or run("ln -s -f snippy_out/snps.bam.bai aln.bam.bai");
    406  }
    407  
    408  sub summarize {
    409      my $summary;
    410      if (-s "raw.flagstat") {
    411          my ($reads)         = `head -n1 raw.flagstat` =~ /^(\d+)/;
    412          my ($mapped, $frac) = `grep mapped raw.flagstat|head -n1` =~ /^(\d+).*?([0-9.]+%)/;
    413          $summary .= "Total reads              = $reads\n";
    414          $summary .= "Properly mapped reads    = $mapped ($frac)\n";
    415      } elsif (-s "flagstat") {
```

## `plbin/App-Variation.pl:116`

```
    110  sub process_variation_data {
    111      my ($app, $app_def, $raw_params, $params) = @_;
    112  
    113      system("samtools", "--version") == 0 or die "samtools --version failed";
    114      system("bcftools", "--version") == 0 or die "bcftools --version failed";
    115      system("freebayes", "--version") == 0 or die "freebayes --version failed";
>>  116      system("snippy", "--version") == 0 or die "snippy --version failed";
    117  
    118      #
    119      # Redirect tmp to large NFS if more than 4 input files.
    120      # (HACK)
    121      #
    122  
    123      my $file_count = count_params_files($params);
    124      print STDERR "File count: $file_count\n";
    125      my $bigtmp = "/vol/patric3/tmp";
    126      if ($file_count > 4 && -d $bigtmp)
    127      {
    128  	print STDERR "Changing tmp from $ENV{TEMPDIR} to $bigtmp\n";
```

## `plbin/var-map.pl:81`

```
     75      make_path($outdir);
     76      chdir($outdir);
     77      eval "&map_with_$algo";
     78      if ($@) {
     79          print $@;
     80      } else {
>>   81          #compute_stats() unless ($algo eq "snippy" || $algo eq "snippy_se");
     82          compute_stats();
     83          if ($vc && eval "defined(&call_variant_with_$vc)") {
     84              eval "&call_variant_with_$vc";
     85              print $@ if $@;
     86              compute_consensus() unless $@;
     87          }
     88      else
     89      {
     90          die "No variant calling code available for $vc\n";
     91      }
     92          summarize() unless -s "summary.txt";
     93      }
```

