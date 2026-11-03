# BV-BRC invocations of `progressiveMauve` (progressivemauve)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 1 hunk(s) in 1 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/App-MSA.pl`

## `plbin/App-MSA.pl:457`

```
    451          run_cmd(\@muscle_cmd);
    452          print STDOUT "Finished MUSCLE.\n";
    453      }
    454      elsif ($recipe eq "progressivemauve" or $recipe eq "mauve") {
    455          # The file format is different.
    456          my $mauve_out = "$work_dir/$prefix.xmfa";
>>  457          my @mauve_cmd = ("progressiveMauve", "--output=$mauve_out", "$work_dir/input.fasta");
    458          my $string_cmd = join(" ", @mauve_cmd);
    459          print STDOUT "Running progressiveMauve.\n";
    460          print STDOUT "$string_cmd\n";
    461          my $ok = run(\@mauve_cmd, "&>", "$work_dir/$prefix.mauve.log");
    462          if (!$ok) {
>>  463              die "progressiveMauve command failed.\n";
    464          }
    465          print STDOUT "Finished progressiveMauve.\n";
    466          my @id_arr = ();
    467          open(INF, '<', "$work_dir/input.fasta") or die "Couldn't open file $work_dir/input.fasta. $!";
    468          while (my $line = <INF>) {
    469              if (substr($line, 0, 1) eq ">") {
    470                  push(@id_arr, $line);
    471              }
    472          }
    473          close(INF) or die $!;
    474          open(INF, '<', $mauve_out) or die "Couldn't open file $mauve_out. $!";
    475          open(OUTF, '>', "$work_dir/output.afa") or die "Couldn't open file $work_dir/output.afa. $!";
```

