# BV-BRC invocations of `primer3_core` (primer3)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 2 hunk(s) in 1 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/App-PrimerDesign.pl`

## `plbin/App-PrimerDesign.pl:128`

```
    122      close F;
    123  
    124      my $cwd = getcwd();
    125      chdir($tmpdir);
    126  
    127      my $primer3_output_file = "$params->{output_file}_Primer3_output.txt";
>>  128      my @command = ("primer3_core", "--output", $primer3_output_file);
    129      print "run command: @command\n";
    130      my $out = run(\@command, "<", $p3params_file);
    131      #my ($out, $err) = run_cmd(", @command));
    132      #print STDERR "\nSTDOUT:\n$out\n";
    133      #print STDERR "\nSTDERR:\n$err\n";
    134      my %resultsHash;
    135      print STDERR "Now showing results from runPrimer3\n";
    136      open F, $primer3_output_file;
    137      while (<F>)
    138      {
    139          chomp;
    140          my ($key, $val) = split("=", $_, '2');
```

## `plbin/App-PrimerDesign.pl:53`

```
     47      };
     48      return $pf;
     49  }
     50  
     51  sub design_primers {
     52      my ($app, $app_def, $raw_params, $params) = @_;
>>   53      my %primer3_params; # copy the params that need to be passed to primer3_core
     54      for my $name (keys %{$params}) {
>>   55          next if $name =~ /^[a-z]/; # parameters with lower-case keys are not meant for primer3_core
     56          $primer3_params{$name} = $params->{$name};
     57      }
     58  
     59      my $time1 = `date`;
     60      print "Proc DesignPrimers ", Dumper($app_def, $raw_params, $params);
     61      $global_token = $app->token()->token();
     62      # print STDERR "Global token = $global_token\n";
     63      my @outputs; # array of tuples of (filename, filetype)
     64      my $api = P3DataAPI->new;
     65      my $tmpdir = File::Temp->newdir( "/tmp/PrimerDesign_XXXXX", CLEANUP => !$debug );
     66      system("chmod", "755", "$tmpdir");
     67      print STDERR "created temp dir: $tmpdir, cleanup = ", !$debug, "\n";
```

