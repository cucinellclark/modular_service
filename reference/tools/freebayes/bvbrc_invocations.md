# BV-BRC invocations of `freebayes` (freebayes)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 5 hunk(s) in 2 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/App-Variation.pl`
- `plbin/var-map.pl`

## `plbin/App-Variation.pl:170`

```
    164  
    165      my $ref_id = $params->{reference_genome_id} or die "Reference genome is required for variation analysis\n";
    166  
    167      my $has_gbk = prepare_ref_data($ref_id, $tmpdir);
    168  
    169      my $mapper = $params->{mapper} || 'bwa_mem';
>>  170      my $caller = $params->{caller} || 'freebayes';
    171  
    172      my $map = "var-map";
    173  
    174      my $threads = $ENV{P3_ALLOCATED_CPU} // 2;
    175  
    176      my @basecmd = ($map, "--path-prefix", $path_prefix);
    177      push @basecmd, ("-a", $mapper);
    178      push @basecmd, ("--vc", $caller);
    179      push @basecmd, ("--threads", $threads);
    180      push @basecmd, "$tmpdir/$ref_id/$ref_id.fna";
    181  
    182      my $lib_txt = "$tmpdir/libs.txt";
```

## `plbin/App-Variation.pl:115`

```
    109  
    110  sub process_variation_data {
    111      my ($app, $app_def, $raw_params, $params) = @_;
    112  
    113      system("samtools", "--version") == 0 or die "samtools --version failed";
    114      system("bcftools", "--version") == 0 or die "bcftools --version failed";
>>  115      system("freebayes", "--version") == 0 or die "freebayes --version failed";
    116      system("snippy", "--version") == 0 or die "snippy --version failed";
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
```

## `plbin/App-Variation.pl:21`

```
     15  use File::Which;
     16  use IPC::Run 'run';
     17  use List::Util qw(min max);
     18  
     19  #
     20  # Arrange for the proper samtools/bcftools.
>>   21  # Assume freebayes in default bin.
     22  #
     23  
     24  my $path_prefix;
     25  
     26  BEGIN {
     27      my $rt = $ENV{KB_RUNTIME};
     28      $path_prefix = "$rt/samtools-1.17/bin:$rt/bcftools-1.17/bin";
     29      $ENV{PATH} = "$path_prefix:$ENV{PATH}";
     30  }
     31  
     32  #
     33  # Find right snpeff name to use
```

## `plbin/var-map.pl:22`

```
     16  usage: $0 [options] ref.fq reads_1.fq [reads_2.fq]
     17  
     18         -a algo          - alignment algorithm [bwa_mem bwa_mem_strict bowtie2 mosaik last] (D = bwa_mem)
     19         -o dir           - output directory (D = ref_reads_[algo])
     20         -t int           - number of threads (D = 8)
     21         -m size          - max memory per thread; suffix K/M/G recognized (D = 2G)
>>   22         --vc tool        - variant calling [bcftools freebayes] (D = freebayes)
     23  
     24  End_of_Usage
     25  
     26  my ($help, $algo, $memory, $nthread, $outdir, $paired, $vc, $path_prefix);
     27  
     28  GetOptions("h|help"        => \$help,
     29         "path-prefix=s" => \$path_prefix,
     30             "a|algo=s"      => \$algo,
     31             "m|memory=s"    => \$memory,
     32             "o|outdir=s"    => \$outdir,
     33             "p|paired"      => \$paired,
     34             "t|threads=i"   => \$nthread,
```

## `plbin/var-map.pl:67`

```
     61  }
     62  
     63  $nthread ||= 8;
     64  $memory  ||= '2G'; $memory .= 'G' if $memory =~ /\d$/;
     65  $algo    ||= 'bwa_mem'; $algo .= "_se" if !$read2;
     66  $algo      =~ s/-/_/g; $algo = lc $algo;
>>   67  $vc      ||= 'freebayes'; $vc = lc $vc;
     68  $outdir  ||= generate_dir_name($algo, $ref, $read1);
     69  
     70  print "READS = $read1 $read2\n";
     71  print "ALGO = $algo\n";
     72  
     73  if (eval "defined(&map_with_$algo)") {
     74      print "> $outdir\n";
     75      make_path($outdir);
     76      chdir($outdir);
     77      eval "&map_with_$algo";
     78      if ($@) {
     79          print $@;
```

