# BV-BRC invocations of `prodigal` (prodigal)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 5 hunk(s) in 2 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Prodigal.pm`
- `plbin/rast_call_CDSs_using_prodigal.pl`

## `lib/Prodigal.pm:110`

```
    104      
    105      my $cmd = join q( ), @cmd;
    106      
    107      my $hostname = `hostname`;
    108      chomp $hostname;
    109      my $event = {
>>  110  	tool_name => "prodigal",
    111  	version => $version,
    112  	execute_time => scalar gettimeofday,
    113  	parameters => \@cmd,
    114  	hostname => $hostname,
    115      };
    116  
    117      warn "Run: $cmd\n" if $ENV{DEBUG};
    118      my $res = system( @cmd );
    119      if ($res != 0) {
    120  	die "cmd failed with rc=$res: $cmd";
    121      }
    122      
```

## `lib/Prodigal.pm:87`

```
     81      }
     82      
     83      my $trans_file = "$tmp_dir/translations";
     84      my $sco_file   = "$tmp_dir/calls.sco";
     85  
     86      #
>>   87      # Determine prodigal version.
     88      #
     89      my($prodigal_path, $version) = find_path_and_version($prodigal);
     90      
     91      my @cmd = ($prodigal_path,
     92  	       "-m",
     93  	       "-a", $trans_file,
     94  	       "-g", $genetic_code,
     95  	       "-i", $tmp_contigs_filename,
     96  	       "-f", "sco",
     97  	       "-o", $sco_file,
     98  	       );
     99  
```

## `lib/Prodigal.pm:229`

```
    223      {
    224  	warn "Could not find $prodigal in $ENV{PATH}, trying without full path\n";
    225  	$prodigal_path = $prodigal;
    226      }
    227      
    228      #
>>  229      # Determine prodigal version.
    230      #
    231      my $version;
    232      
    233      my $stdout;
    234      my $stderr;
    235      if (IPC::Run::run([$prodigal_path, "-v"], ">", \$stdout, "2>", \$stderr))
    236      {
    237  	if ($stderr =~ /(Prodigal.*)\n/mg)
    238  	{
    239  	    $version = $1;
    240  	}
    241      }
```

## `plbin/rast_call_CDSs_using_prodigal.pl:97`

```
     91  
     92      my $id = join(".", $typed_prefix, $cur_id_suffix);
     93      $cur_id_suffix++;
     94      &GenomeTypeObject::add_feature($genomeTO, { -id         => $id,
     95  						-type       => 'CDS',
     96  						-location   => [[ $contig, $beg, $strand, $length ]],
>>   97  						-annotator  => 'prodigal',
     98  						-annotation => 'Add feature called by PRODIGAL',
     99  						-analysis_event_id   => $event_id,
    100  						    -protein_translation => $translation,
    101  					    }
    102  				   );
    103  }
    104  
    105  $genomeTO->destroy_to_file($out_fh);
    106  close($out_fh);
```

## `lib/Prodigal.pm:44`

```
     38  
     39  sub run_prodigal
     40  {
     41      my ($params) = @_;
     42      my ($line, $contig_id);
     43      
>>   44      my $prodigal = 'prodigal';
     45      
     46      my $genetic_code = $params->{-genetic_code} or die "missing -genetic_code parameter";
     47      my $contigs      = $params->{-contigs}      or die "missing -contigs parameter";
     48      
     49      #
     50      # Create temporary directory and FASTA for the contig data.
     51      #
     52      my @tmpdir = defined($params->{-tmpdir}) ? (DIR => $params->{-tmpdir}) : (TMPDIR => 1);
     53      my $tmp_dir = tempdir('tmpdir_prodigal_XXXXXXXX', @tmpdir);
     54  
     55      print STDERR "contig=$tmp_dir\n" if $ENV{DEBUG};
     56      
```

