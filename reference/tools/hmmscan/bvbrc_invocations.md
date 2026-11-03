# BV-BRC invocations of `hmmscan` (hmmscan)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 3 hunk(s) in 2 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/rota-a-genotyper/VIGOR3/prod3/hmm3Evidence.pl`
- `plbin/p3x-retrieve-family-sequences-for-genomes.pl`

## `plbin/p3x-retrieve-family-sequences-for-genomes.pl:49`

```
     43  # Get the command-line options.
     44  my $opt = P3Utils::script_opts(['families', 'genomes'],
     45                  ['alphabet|a=s', 'DNA or protein (default DNA)', { default => 'DNA'}],
     46                  ['output_dir|o=s', 'Output directory.' ],
     47                  ['threads|t=i', 'Threads for mafft'],
     48                  ['align', 'Align sequences with mafft'],
>>   49                  ['hmm', 'Build hmms from alignments with hmmbuild (requires --align)'],
     50                  ['verbose|debug|v', 'Write status messages to STDERR'],
     51          );
     52  # Check the parameters.
     53  my ($families, $genomes) = @ARGV;
     54  if ($opt->verbose) {
     55      print "args=", join(", ", @ARGV), "\n";
     56      print "opt = %$opt\n";
     57      for my $key (keys %$opt) {
     58          print "\t$key\t$opt->{$key}\n";
     59      }
     60  }
     61  if (! $families and $genomes) {
```

## `plbin/p3x-retrieve-family-sequences-for-genomes.pl:154`

```
    148          print "alignment command = $command\n" if $opt->verbose;
    149          system($command);
    150          if ($opt->hmm) {
    151              my $hmm_file = "${fam}.hmm";
    152              my $hmm_aligned_file = "${fam}_hmm_aligned.stk";
    153              #-n PGF_10365126 -o PGF_10365126_hmm_stats.txt -O PGF_10365126_hmm_aligned.stk
>>  154              my @command = ('hmmbuild', '-n', $fam, '-O', $hmm_aligned_file, '--cpu', $threads, $hmm_file, $aligned_output_file);
>>  155              print "hmmbuild command = @command\n" if $opt->verbose;
    156              system(@command);
    157          }
    158      }
    159  }
    160  chdir($original_dir);
    161  
    162  sub get_features_for_one_family {
    163      my ($p3api, $family, $genomes_aref, $md5_type) = @_;
    164      my $family_type = '';
    165      print STDERR "Test type of $family\n" if $opt->verbose;
    166      if ($family =~ /PGF_\d+/) {
    167          $family_type = 'pgfam_id';
```

## `lib/rota-a-genotyper/VIGOR3/prod3/hmm3Evidence.pl:102`

```
     96      my $hmm3out = "$workspace/hmm3.out";
     97      unlink $hmm3out;
     98      
     99      my $hmm3log = "$workspace/hmm3.log";
    100      unlink $hmm3log;
    101  
>>  102      my $cmd = "/usr/local/packages/hmmer-3.0/bin/hmmscan --cut_nc -o $hmm3out /usr/local/db/common/ergatis/PFAM_TIGR/current/ALL_LIB.HMM $qryfasta &> $hmm3log";
    103      runCmd($workspace, $cmd);
    104  
    105  # format htab results
    106      my $htablog = "$workspace/htab.log";
    107      unlink $htablog;
    108  
    109      my $htabout = "$workspace/htab.out";
    110      unlink $htabout;
    111  
    112      $cmd = "/usr/local/devel/ANNOTATION/ard/ergatis-v2r13b2/bin/hmmpfam2htab --input_file $hmm3out --mldbm_file /usr/local/db/common/ergatis/PFAM_TIGR/current/ALL_LIB.HMM.db --output_htab $workspace/htab.tmp # &> $htablog";
    113      runCmd($workspace, $cmd);
    114      open( TMP, "<$workspace/htab.tmp" ) || die "\nCould not read $workspace/htab.tmp\n";
```

