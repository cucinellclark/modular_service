# BV-BRC invocations of `checkv` (checkv)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 3 hunk(s) in 2 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/MetagenomeBinning/MetagenomeBinning.pm`
- `plbin/vbins_generate.pl`

## `plbin/vbins_generate.pl:62`

```
     56  
     57  $| = 1;
     58  # Get the command-line options.
     59  my $opt = P3Utils::script_opts('checkvDB binDir',
     60  			       ['maxError|M=f', 'maximum permissible confidence error', { default => '10.0' }],
     61  			       ['minPct|p=f', 'minimum permissible percent of virus present', { default => '10.0' }],
>>   62  			       ['threads|t=i', 'number of threads for checkv', { default => 1 }],
     63      );
     64  my $stats = Stats->new();
     65  my $maxError = $opt->maxerror;
     66  if ($maxError <= 0.0) {
     67      die "Maximum error must be > 0.";
     68  }
     69  my $minPct = $opt->minpct;
     70  if ($minPct > 100.0) {
     71      die "Minimum percent must be <= 100.";
     72  }
     73  my ($checkVDb, $binDir) = @ARGV;
     74  if (! $checkVDb) {
```

## `plbin/vbins_generate.pl:86`

```
     80      die "No binning directory specified.";
     81  } elsif (! -d $binDir) {
     82      die "Binning directory $binDir not found.";
     83  } elsif (! -s "$binDir/unbinned.fasta") {
     84      die "Binning directory $binDir does not have unbinned contig FASTA file.";
     85  }
>>   86  # Invoke checkv to identify viral contigs.
>>   87  my @parms = ('checkv', 'completeness', "-t", $opt->threads, "$binDir/unbinned.fasta", "$binDir/checkv", '-d', $checkVDb);
     88  my $cmd = join(" ", @parms);
     89  print "Running: $cmd\n";
     90  my $rc = system($cmd);
     91  if ($rc) {
     92      die "Error in CheckV (rc = $rc).\n";
     93  }
     94  if ($rc == 0) {
>>   95      # Now we must process the checkv output.
     96      print "Processing checkV output for $binDir.\n";
     97      $stats->Add(outputRuns => 1);
     98      my $checkv = CVUtils->new($checkVDb, $binDir, $binDir, logH => \*STDOUT, stats => $stats, maxE => $maxError, minP => $minPct);
     99      $checkv->CreateBins();
    100  }
    101  print "All done:\n" . $stats->Show();
    102  
```

## `lib/Bio/P3/MetagenomeBinning/MetagenomeBinning.pm:88`

```
     82      # if (!$params->{force_local_assembly} && bebop_binning_user && bebop_binning_key)
     83      # {
     84      # 	$cpu = 1;
     85      # }
     86  
     87      #
>>   88      # Require the checkv database if we are doing viral binning.
     89      # Also bump the cpu request up.
     90      #
     91      if ($params->{perform_viral_binning})
     92      {
     93  	$cpu = 8;
     94  	my $db = $ENV{CHECKVDB};
     95  	if (!defined($db))
     96  	{
     97  	    die "Checkv database environment CHECKVDB not defined\n";
     98  	}
     99  	elsif (! -s $db)
    100  	{
```

