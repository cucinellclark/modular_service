# BV-BRC invocations of `cd-hit` (cd-hit)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 1 hunk(s) in 1 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/rota-a-genotyper/VIGOR3/prod3/dbutils/findClusters.pl`

## `lib/rota-a-genotyper/VIGOR3/prod3/dbutils/findClusters.pl:84`

```
     78      $workdir = $tmpdir;
     79  }
     80  mkdir $workdir || die "\nCannot create working directory \"$workdir\"\n";
     81  
     82  print "working directory: $workdir\n";
     83  
>>   84  # use cd-hit to reduce redundancy ( 95% identity 95 %coverage)
>>   85  my $cmd = "$myBin/cd-hit -i $infasta -o $workdir/nr -aL $coverage -aS $coverage -G 0 -c $similarity -g 1 -B 1 -t 5 2>&1 | tee $workdir/cluster.log";
     86  print "clustering: $cmd\n";
     87  runCmd('.', $cmd);
     88  print "flushing clustalw buffers...\n";
>>   89  sleep 60;    # give cd-hit time to flush buffers to disk
     90  
     91  # find clusters
     92  print "loading cluster definitions\n";
     93  my %multiclusters;
     94  open( CL, "<$workdir/nr.clstr" ) || die "\nCannot read cluster deflines\n";
     95  my $cluster_id = 0;
     96  my %clusters;
     97  while ( my $member = <CL> ) {
     98      chomp $member;
     99      if ( $member =~ /^>Cluster (.*)$/ ) {        
    100          $cluster_id = $1;
    101      }
```

