# BV-BRC invocations of `amrfinder` (amrfinder)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 3 hunk(s) in 1 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/p3x-compute-specialty-amrfinder.pl`

## `plbin/p3x-compute-specialty-amrfinder.pl:123`

```
    117  }
    118  elsif ($amr_orgs{$genus})
    119  {
    120      @organism_flag = ("-O" => $genus);
    121  }
    122  
>>  123  my @cmd = ("amrfinder",
    124  	   "--threads", $opt->parallel,
    125  	   "--protein", $in_file,
    126  	   "--output", $out_file,
    127  	   @organism_flag);
    128  
    129  print STDERR "Invoke AMRFinder: @cmd\n";
    130  
    131  my $ok = run(\@cmd,
    132  	     init => sub { $ENV{TMPDIR} = "$work_dir"; });
    133  
    134  $ok or die "Error $? running @cmd\n";
    135  
```

## `plbin/p3x-compute-specialty-amrfinder.pl:44`

```
     38  				     
     39  print($usage->text), exit if $opt->help;
     40  print($usage->text), exit 1 if (@ARGV != 0);
     41  
     42  chomp(my $hostname = `hostname -f`);
     43  
>>   44  # amrfinder -p /vol/patric3/downloads/genomes/83332.12/83332.12.PATRIC.faa -O "Mycobacterium_tuberculosis" --threads 24
     45  
     46  my $orig_dir = getcwd();
     47  
     48  my $gto_in;
     49  
     50  if ($opt->in)
     51  {
     52      $gto_in = GenomeTypeObject->new({file => $opt->in});
     53      $gto_in or die "Error reading GTO from " . $opt->in . "\n";
     54  }
     55  else
     56  {
```

## `plbin/p3x-compute-specialty-amrfinder.pl:90`

```
     84  
     85  my $db_version = "Undetermined";
     86  my $sw_version = "Undetermined";
     87  my %amr_orgs;
     88  {
     89      my($stderr, $stdout);
>>   90      run(["amrfinder", "--list_organisms"],
     91  	">", \$stdout,
     92  	"2>", \$stderr);
     93  
     94      if ($stdout =~ /^Available --organism options:\s+(.*)$/m)
     95      {
     96  	%amr_orgs = map { $_ => 1 } split(/,\s+/, $1);
     97      }
     98  
     99      if ($stderr =~ /Software version:\s+(\S+)/m)
    100      {
    101  	$sw_version = $1;
    102      }
```

