# BV-BRC invocations of `cutadapt` (cutadapt)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 5 hunk(s) in 4 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/CmdRunner.pm`
- `lib/process.py`
- `plbin/sars2-cdc-illumina.pl`
- `plbin/sars2-cdc-nanopore.pl`

## `plbin/sars2-cdc-illumina.pl:159`

```
    153      if ($threads > 1)
    154      {
    155  	$t1 = int($threads / 2);
    156  	$t2 = $t2 = $threads - $t1;
    157      }
    158      
>>  159      my @cutadapt1 = qw(cutadapt
    160  		       -g GTTTCCCAGTCACGATA
    161  		       -G GTTTCCCAGTCACGATA
    162  		       -a TATCGTGACTGGGAAAC
    163  		       -A TATCGTGACTGGGAAAC
    164  		       -g ACACTCTTTCCCTACACGACGCTCTTCCGATCT 
    165  		       -G ACACTCTTTCCCTACACGACGCTCTTCCGATCT
    166  		       -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA
    167  		       -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT
    168  		       -n 3
    169  		       -q 25);
    170  
    171      push(@cutadapt1,
    172  	 "-j", $t1,
    173  	 "--interleaved", $pe_read_1, $pe_read_2,
    174  	 @min_rl,
    175  	);
    176      
>>  177      my @cutadapt2 = qw(cutadapt
    178  		       --interleaved
    179  		       -u 30);
    180      push(@cutadapt2, 
    181  	 "-j", $t2,
    182  	 "-o", $trim1,
    183  	 "-p", $trim2,
    184  	 @min_rl,
    185  	 "-");
    186      
    187      $runner->run(\@cutadapt1, '|', \@cutadapt2);
    188      
    189      #
```

## `plbin/sars2-cdc-illumina.pl:210`

```
    204      #
    205      # Step 1. Adapter trimming.
    206      #
    207      
    208      my $trim = "$int_dir/$base.trim.fastq";
    209      
>>  210      my @cutadapt = qw(cutadapt
    211  		  -g GTTTCCCAGTCACGATA
    212  		  -a TATCGTGACTGGGAAAC
    213  		  -g ACACTCTTTCCCTACACGACGCTCTTCCGATCT 
    214  		  -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA
    215  		  -n 3
    216  		  -q 25);
    217      push(@cutadapt,
    218  	 "-j", $threads,
    219  	 $se_read, "-o", $trim,
    220  	 @min_rl,
    221  	);
    222  
```

## `lib/Bio/P3/CmdRunner.pm:142`

```
    136  	if ($v =~ /Version:\s+(\S+)/)
    137  	{
    138  	    return $1;
    139  	}
    140  	return undef;
    141      }
>>  142      elsif ($base eq 'cutadapt')
    143      {
    144  	my $v;
    145  	IPC::Run::run([$cmd, "--version"], '>', \$v, '<', '/dev/null');
    146  	if ($v =~ /^(\S+)/)
    147  	{
    148  	    return $1;
    149  	}
    150  	return undef;
    151      }
    152      elsif ($base eq 'mafft')
    153      {
    154  	my $v;
```

## `lib/process.py:1786`

```
   1780                  "Trimming encountered an error in Sample {0}:\ncheck error log file".format(
   1781                      sample.get_id()
   1782                  )
   1783              )
   1784              sample.set_command_status("trim", e)
   1785              return False
>> 1786          # TODO: remove cutadapt log files: _cutadapt.log
   1787          for r in sample.get_reads_as_list():
   1788              if not os.path.exists(r):
   1789                  print("{0} does not exist".format(r))
```

## `plbin/sars2-cdc-nanopore.pl:117`

```
    111  $ENV{PATH} = "$ENV{KB_RUNTIME}/medaka/bin:$ENV{PATH}";
    112  
    113  #
    114  # Step 1. Adapter trimming.
    115  #
    116  
>>  117  my @cutadapt = qw(cutadapt
    118  		  -m 300
    119  		  -M 1200
    120  		  -q 15 );
    121  
    122  my @filtered;
    123  for my $fastqfile (@reads)
    124  {
    125      my $bn = basename($fastqfile);
    126      $bn =~ s/\.gz$//;
    127      $bn =~ s/\.[^.]+$//;
    128      my $fastqfiltered = "$int_dir/$bn.filtered.fastq";
    129  
```

