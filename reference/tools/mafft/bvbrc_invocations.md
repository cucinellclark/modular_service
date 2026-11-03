# BV-BRC invocations of `mafft` (mafft)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 25 hunk(s) in 20 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/CmdRunner.pm`
- `lib/alignment.pm`
- `lib/ffxtree.pm`
- `lib/gjoalignment.pm`
- `lib/phylocode.py`
- `plbin/App-GeneTree.pl`
- `plbin/App-MSA.pl`
- `plbin/App-MetaCATS.pl`
- `plbin/p3x-retrieve-family-sequences-for-genomes.pl`
- `plbin/sars2-compute-variation.pl`
- `plbin/sars2-onecodex.pl`
- `pybin/p3x-build-codon-tree.py`
- `pybin/run_subspecies_classification.py`
- `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/FCP_Ali_Utils.pm`
- `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/FCP_Main_Utils.pm`
- `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/FCP_Nterm_Utils.pm`
- `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/fasta-cluster-pssm.pl`
- `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/gto-dir-to-alis-and-trees.pl`
- `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/gtos-dir-to-wgs-tree-single-seg.pl`
- `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/prots_to_alis_and_trees.pl`

## `plbin/App-GeneTree.pl:1155`

```
   1149      end_step("Align with muscle");
   1150  }
   1151  
   1152  sub run_mafft {
   1153      my ($unaligned, $aligned) = @_;
   1154      print STDERR "run_mafft($unaligned, $aligned)\n";
>> 1155      my ($step_comments, $step_info) = start_step("Align with mafft");
   1156      my $parallel = $ENV{P3_ALLOCATED_CPU};
>> 1157      my $cmd = ["mafft", "--auto"];
   1158      if ($parallel) {
   1159          push @$cmd, "--thread", $parallel;
   1160      }
   1161      push @$cmd, $unaligned;
   1162      my $comment = join(" ", @$cmd);
   1163      add_step_command_line($comment);
   1164      print STDERR $comment, "\n" if $debug;
   1165      my $out;
   1166      open $out, ">$aligned";
   1167      run($cmd, ">", $out);
>> 1168      end_step("Align with mafft");
   1169  }
   1170  
   1171  sub curl_text {
   1172      my ($url) = @_;
   1173      my @headers = ("-H", "Accept:text/tsv");
   1174      if ($global_token) { push @headers, "-H", "Authorization:$global_token"}
   1175      my @cmd = ("curl", $url, @headers);
   1176      print STDERR join(" ", @cmd), "\n" if $debug;
   1177      my ($out) = run_cmd(\@cmd);
   1178      return $out;
   1179  }
   1180  
```

## `plbin/App-MSA.pl:490`

```
    484                  print OUTF $line;
    485              }
    486          }
    487          close(INF) or die $!;
    488          close(OUTF) or die $!;
    489      }
>>  490      elsif ($recipe eq "mafft") {
    491          print STDOUT "Running mafft.\n";
    492          my $strategy = lc($params_to_app->{strategy});
    493          print STDOUT "Selected strategy: $strategy";
    494          my @mafft_cmd;
    495          given ($strategy) {
    496              when ($_ eq "fftns1") {
>>  497                  @mafft_cmd = ("mafft", "--retree", 1, "--maxiterate", 0, "$work_dir/input.fasta");
    498              }
    499              when ($_ eq "fftns2") {
    500                  @mafft_cmd = ("fftns", "$work_dir/input.fasta");
    501              }
    502              when ($_ eq "fftnsi") {
    503                  @mafft_cmd = ("fftnsi", "$work_dir/input.fasta");
    504              }
    505              when ($_ eq "einsi") {
    506                  @mafft_cmd = ("einsi", "$work_dir/input.fasta");
    507              }
    508              when ($_ eq "linsi") {
    509                  @mafft_cmd = ("linsi", "$work_dir/input.fasta");
    510              }
    511              when ($_ eq "ginsi") {
    512                  @mafft_cmd = ("ginsi", "$work_dir/input.fasta");
    513              }
    514              default {
>>  515                  @mafft_cmd = ("mafft", "--auto", "--preservecase", "$work_dir/input.fasta");
    516              }	
    517          } 
    518          my $string_cmd = join(" ", @mafft_cmd);
>>  519          my @mafft_version = ("mafft", "--version");
    520          run(\@mafft_version, "2>>", "$work_dir/mafft.job.log");
    521          run_cmd(\@mafft_version);
    522          open(MAFFT_LOG, '>>', "$work_dir/mafft.job.log") or die $!;
    523          print MAFFT_LOG "$string_cmd\n";
    524          close(MAFFT_LOG) or die $!;
    525          print STDERR "$string_cmd\n";
    526          my $ok = run(\@mafft_cmd, "1>", "$work_dir/output.afa", "2>>", "$work_dir/mafft.job.log");
    527          if (!$ok) {
    528              die "Mafft command failed.\n";
    529          }
    530          print STDOUT "Finished mafft.\n"
    531      }
```

## `plbin/App-MetaCATS.pl:137`

```
    131          }
    132      } else {
    133          die("Unrecognized input type.");
    134      }
    135      if (($input_type eq "groups") or ($input_type eq "auto")) {
    136          # Align the sequences.
>>  137          my @mafft_cmd = ("mafft", "--auto", "--preservecase", $ofile);
    138          my $string_cmd = join(" ", @mafft_cmd);
    139          print STDOUT "Running mafft.\n";
    140          print STDOUT "$string_cmd\n";
    141          $seqFile = "$work_dir/output.afa";
    142          my $ok = run(\@mafft_cmd, "1>", $seqFile, "2>", "$work_dir/$prefix.mafft.log");
    143          if (!$ok) {
    144              die "Mafft command failed.\n";
    145          }
    146          print STDOUT "Finished mafft.\n";
    147      }
    148      # Replace leading and trailing gaps with the '#' symbol in the sequence file.
    149      open my $fh, '<', "$seqFile" or die "Cannot open $seqFile: $!";
```

## `plbin/p3x-retrieve-family-sequences-for-genomes.pl:47`

```
     41  
     42  #$| = 1;
     43  # Get the command-line options.
     44  my $opt = P3Utils::script_opts(['families', 'genomes'],
     45                  ['alphabet|a=s', 'DNA or protein (default DNA)', { default => 'DNA'}],
     46                  ['output_dir|o=s', 'Output directory.' ],
>>   47                  ['threads|t=i', 'Threads for mafft'],
>>   48                  ['align', 'Align sequences with mafft'],
     49                  ['hmm', 'Build hmms from alignments with hmmbuild (requires --align)'],
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
```

## `plbin/p3x-retrieve-family-sequences-for-genomes.pl:146`

```
    140          print $f ">$item->{patric_id}\n$seq_hash->{$item->{$md5_type}}\n";
    141      }
    142      close $f;
    143      if ($opt->align) {
    144          my $aligned_output_file = "${fam}_aligned_" . $opt->alphabet . ".afa";
    145          print "aligning to $aligned_output_file\n" if $opt->verbose;
>>  146          my $command = ("mafft --auto --thread $threads $unaligned_output_file > $aligned_output_file"); #using a string instead of array because redirection is needed - better option is to use open and captuer output and write to file -- TODO
    147          #print "alignment command = ". join(" ", @command), "\n";
    148          print "alignment command = $command\n" if $opt->verbose;
    149          system($command);
    150          if ($opt->hmm) {
    151              my $hmm_file = "${fam}.hmm";
    152              my $hmm_aligned_file = "${fam}_hmm_aligned.stk";
    153              #-n PGF_10365126 -o PGF_10365126_hmm_stats.txt -O PGF_10365126_hmm_aligned.stk
    154              my @command = ('hmmbuild', '-n', $fam, '-O', $hmm_aligned_file, '--cpu', $threads, $hmm_file, $aligned_output_file);
    155              print "hmmbuild command = @command\n" if $opt->verbose;
    156              system(@command);
    157          }
    158      }
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/prots_to_alis_and_trees.pl:112`

```
    106  	open (OUT, ">$prefix.$anno.aa"); 
    107  	&gjoseqlib::print_alignment_as_fasta(\*OUT, @{$hash{$_}});
    108  }
    109  
    110  foreach (@fastas)
    111  {
>>  112  	system "mafft --thread 64 --reorder $prefix.$_.aa >$prefix.$_.fa";
    113  	system "alignment_density.pl -p $prefix.$_ -m $min_len -t < $prefix.$_.fa  > $prefix.$_.data";
    114  	system "FastTree -wag <$prefix.$_.keep.fa>$prefix.$_.nwk";
    115  	system "remove_bad_tree_tips.pl <$prefix.$_.nwk >$prefix.$_.pruned.nwk";
    116  	system "svr_tree_to_html -raw -a $prefix.names -c $prefix.fam <$prefix.$_.pruned.nwk>$prefix.$_.html";
    117  }
    118  
    119  
    120  
    121  
    122  
    123  
    124  
```

## `plbin/sars2-onecodex.pl:408`

```
    402  	 [qw(seqtk seq -l 60 -)],
    403  	 ">",
    404  	 "$out_dir/$base.fasta");
    405  
    406  $runner->run(["cat", $reference, "$out_dir/$base.fasta"],
    407  	 '|',
>>  408  	 ["mafft", "--auto", "-"],
    409  	 '>',
    410  	 "$out_dir/$base.align");
    411  
    412  
    413  #
    414  # Create coverage plot
    415  #
    416  
    417  $runner->run(["samtools", "depth", "$int_dir/$base.isorted.bam"], '>', "$out_dir/$base.depth");
    418  
    419  if (-s "$out_dir/$base.depth")
    420  {
```

## `pybin/run_subspecies_classification.py:313`

```
    307                  traceback.print_exc()
    308                  sys.exit(-1)
    309  
    310          # Step 3: Run MAFFT to add query sequences to reference MSA
    311          mafft_output = self.output_dir / MAFFT_OUTPUT_F_NAME
    312          mafft_cmd = [
>>  313              "mafft", "--keeplength", "--add",
    314              str(self.input_file), str(reference_mfa_file)
    315          ]
    316          try:
    317              with mafft_output.open("w") as o:
    318                  if self.result_only:
    319                      subprocess.check_call(mafft_cmd, stdout=o, stderr=sys.stderr)
    320                  else:
    321                      subprocess.check_call(mafft_cmd, stdout=o)
    322          except Exception as e:
    323              print(f"Error running mafft:\n{e}")
    324              traceback.print_exc()
    325              sys.exit(-1)
```

## `lib/alignment.pm:165`

```
    159  
    160      my $add      = $opts->{ add }      || undef;
    161      my $profile  = $opts->{ profile }  || $opts->{ in2 } || $opts->{ seed } || undef;
    162         $seqs   ||= $opts->{ seqs }     || $opts->{ in }  || $opts->{ in1 };
    163      my $version  = $opts->{ version }  || 0;
    164  
>>  165      my $mafft = SeedTkRun::executable_for( $opts->{ mafft } || $opts->{ program } || 'mafft' )
>>  166          or print STDERR "Could not locate executable file for 'mafft'.\n"
    167              and return undef;
    168  
    169      if ( $version )
    170      {
    171          my $tmpdir = SeedTkRun::location_of_tmp( $opts );
    172          my $tmpF   = SeedTkRun::tmp_file_name( "version", '', $tmpdir );
    173  
    174          SeedTkRun::system_with_redirect( $mafft, "--help", { stderr => $tmpF } );
    175          open( MAFFT, $tmpF ) or die "Could not open $tmpF";
    176          my @info = <MAFFT>;
    177          close( MAFFT );
    178          unlink( $tmpF );
```

## `lib/gjoalignment.pm:234`

```
    228  
    229      my $add      = $opts->{ add }      || undef;
    230      my $profile  = $opts->{ profile }  || $opts->{ in2 } || $opts->{ seed } || undef;
    231         $seqs   ||= $opts->{ seqs }     || $opts->{ in }  || $opts->{ in1 };
    232      my $version  = $opts->{ version }  || 0;
    233  
>>  234      my $mafft = SeedAware::executable_for( $opts->{ mafft } || $opts->{ program } || 'mafft' )
>>  235          or print STDERR "Could not locate executable file for 'mafft'.\n"
    236              and return undef;
    237  
    238      if ( $version )
    239      {
    240          my $tmpdir = SeedAware::location_of_tmp( $opts );
    241          my ( $tmpFH, $tmpF ) = File::Temp::tempfile( "version_XXXXXX", DIR => $tmpdir, UNLINK => 1 );
    242          close( $tmpFH );
    243  
    244          SeedAware::system_with_redirect( $mafft, "--help", { stderr => $tmpF } );
    245          open( MAFFT, $tmpF ) or die "Could not open $tmpF";
    246          ( $version ) = grep { /MAFFT/ } <MAFFT>;
    247          close( MAFFT );
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/FCP_Nterm_Utils.pm:325`

```
    319                      base => "${ali_base}_${cluster_num}"
    320                  };
    321                  $cluster_num++;
    322                  $new_alignments++;
    323                  
    324                  # Align the new file with MAFFT
>>  325                  my $mafft_cmd = "mafft --thread 24 --quiet --reorder $out_file > ${out_file}.aligned";
    326                  print STDERR "  Running MAFFT on $out_file\n";
    327                  my $mafft_ret = system $mafft_cmd;
    328                  
    329                  if ($mafft_ret == 0) 
    330                  {
    331                      # Replace the original file with the aligned version
    332                      rename("${out_file}.aligned", $out_file) or
    333                          die "Cannot rename ${out_file}.aligned to $out_file: $!\n";
    334                  } 
    335                  else 
    336                  {
    337                      print STDERR "  Warning: MAFFT execution failed for $out_file\n";
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/gto-dir-to-alis-and-trees.pl:124`

```
    118  		
    119  		my $des = "$anno"."##"."[$name]"."##"."[$qual]";
    120  		push @seqs, ([$id, $des, $aa]);
    121  	}	
    122  	
    123  	&gjoseqlib::print_alignment_as_fasta(\*OUT2, @seqs);
>>  124  	system "mafft --thread 24 --reorder $file.aa >$file.fa";
    125  	system "FastTree -wag <$file.fa>$file.nwk";
    126  	system "svr_tree_to_html -c $color_file -raw -bar -a $name_file <$file.nwk>$file.html";
    127  
    128  }
    129  
    130  
    131  
    132  
    133  
    134  
    135  
    136  
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/gtos-dir-to-wgs-tree-single-seg.pl:102`

```
     96  }
     97  close CLR;
     98  close NAME;
     99  
    100  open (OUT, ">$prefix.dna");
    101  &gjoseqlib::print_alignment_as_fasta(\*OUT, @seqs);
>>  102  system "mafft --thread 24 --reorder $prefix.dna >$prefix.fa";
    103  system "FastTree -nt -gtr <$prefix.fa>$prefix.nwk";
    104  system "svr_tree_to_html -c $prefix.colors -raw -bar -a $$prefix.name <$prefix.nwk>$prefix.html";
    105  
    106  
    107  
    108  
    109  
    110  
    111  
    112  
    113  
    114  
```

## `pybin/p3x-build-codon-tree.py:43`

```
     37  parser.add_argument("--excessGenesProp", metavar="prop", type=float, default=0.5, help="multiplier of maxGenes to add to filter out low-scoring alignments")
     38  parser.add_argument("--excessGenesFixed", metavar="#", type=int, default=20, help="fixed excess genes to add to filter out low-scoring alignments")
     39  parser.add_argument("--bootstrapReps", metavar="#", type=int, default=0, help="number of raxml 'fast boostrap' replicates")
     40  parser.add_argument("--maxGenomesMissing", metavar="#", type=int, default=0, help="genomes allowed to lack a member of any homolog group")
     41  parser.add_argument("--maxAllowedDups", metavar="#", type=int, default=0, help="duplicated gene occurrences allowed within homolog group")
     42  
>>   43  parser.add_argument("--aligner", metavar="program", type=str, choices=('muscle', 'mafft'), default="mafft", help="program to align protein sequences")
     44  parser.add_argument("--endGapTrimThreshold", metavar="maxPropGaps", type=float, default=0.5, help="stringency of end-gap trimming, 0-1.0, lower for less trimming")
     45  parser.add_argument("--raxmlExecutable", metavar="program_name", type=str, default="raxml", help="program to call, possibly with path")
     46  parser.add_argument("--rateModel", metavar="model", type=str, choices = ['CAT', 'GAMMA'], default="CAT", help="variable rate category model CAT|GAMMA")
     47  parser.add_argument("--proteinModel", metavar="model", type=str, default="AUTO", help="raxml protein substitution model")
     48  parser.add_argument("--protein_sample_prop", metavar="0.XX", type=float, default=0.5, help="proportion of positions to sample for discovery of optimal model")
     49  parser.add_argument("--analyzeCodons", action='store_true', help="analyze only codon nucleotides")
     50  parser.add_argument("--analyzePos3Codons", action='store_true', help="analyze codon-position 3 nucleotides in addition")
     51  parser.add_argument("--analyzeProteins", action='store_true', help="analyze only amino acids")
     52  parser.add_argument("--threads", "-t", metavar="T", type=int, default=2, help="threads for raxml")
     53  parser.add_argument("--deferRaxml", action='store_true', help="does not run raxml")
     54  parser.add_argument("--exitBeforeAlignment", action='store_true', help="Don't align, useful for getting PGFam matrix")
     55  parser.add_argument("--writePgfamAlignments", action='store_true', help="write fasta alignment per homolog used for tree")
```

## `lib/ffxtree.pm:2687`

```
   2681      SeedAware::system_with_redirect( $mafft, @params, $redirects );
   2682      
   2683      my @ali = &gjoseqlib::read_fasta( $tmpout );
   2684      foreach $_ ( @ali ) { $_->[1] = $comment{$_->[0]} }
   2685  
   2686      my $treestr;
>> 2687      my $treeF  = "input.tree";  # mafft uses a hardcoded guide tree
   2688      if ( $tree && open( TREE, "<$treeF" ) ) {
   2689          $treestr = join( "", <TREE> ); close( TREE );
   2690      }
   2691      if ( $opts->{ treeout } ) {
   2692          SeedAware::system_with_redirect( "cp", $treeF, $opts->{ treeout } );
   2693      }
   2694  
   2695      unlink( $tmpin, $tmpout,
   2696              ( $profile ? $tmpin2 : () ),
   2697              ( $tree    ? $treeF  : () )
   2698            );
   2699  
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/FCP_Main_Utils.pm:368`

```
    362      print STDERR "Put $leftover_seqs sequences from $small_clusters small clusters into Leftover_Seqs.aa\n";
    363      
    364      # Only align leftover sequences if there are any
    365      if ($leftover_seqs > 0 && -s "Leftover_Seqs.aa") 
    366      {
    367          print STDERR "Aligning leftover sequences with MAFFT...\n";
>>  368          my $ret = system "mafft --thread 24 --quiet --reorder Leftover_Seqs.aa > Leftover_Seqs.fa";
    369          
    370          if ($ret != 0) 
    371          {
    372              die "MAFFT execution failed with return code $ret: $!\n";
    373          }
    374          
    375          print STDERR "MAFFT alignment of leftover sequences completed successfully\n";
    376      }
    377      else
    378      {
    379          print STDERR "No leftover sequences to align, skipping MAFFT step\n";
    380          # Create an empty Leftover_Seqs.fa file for consistency
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/FCP_Nterm_Utils.pm:392`

```
    386      close($log_fh);
    387      
    388      # Re-align leftover sequences with MAFFT
    389      if (-s "Leftover_Seqs.aa") 
    390      {
    391          print STDERR "Re-aligning leftover sequences...\n";
>>  392          my $ret = system "mafft --thread 24 --quiet --reorder Leftover_Seqs.aa > Leftover_Seqs.fa";
    393          
    394          if ($ret != 0) 
    395          {
    396              print STDERR "Warning: MAFFT execution failed for Leftover_Seqs.aa: $!\n";
    397          }
    398      }
    399      
    400      print STDERR "Reclustering complete\n";
    401      return 1;
    402  }
    403  
    404  # Generate PSSM for an alignment
```

## `plbin/p3x-retrieve-family-sequences-for-genomes.pl:9`

```
      3  
      4      p3x-retrieve-family-sequences-for-genomes.pl [options] families genomes
      5  
      6  This script runs a multiple sequence alignment program for all pgfam sequences for a set of genomes.
      7  Protein families and genomes can be specified as either a comma-separated list or by a file with one p[gl]fam (or SOG) or genome_id per line.
      8  Output is one fasta file per protein family.
>>    9  Can optionally align with mafft, yielding an aligned fasta (.afa) file per family.
     10  
     11  =head2 Parameters
     12  
     13  The two positional parameters are the protein families (comma-separated or file of ids) and genomes (comma-separated or file of ids).
     14  
     15  The command-line options are as follows.
     16  
     17  =over 4
     18  
     19  =item alphabet
     20  
     21  DNA or protein (default DNA)
```

## `plbin/sars2-compute-variation.pl:222`

```
    216  	print $tmp ">$feat->{id}\n$feat->{protein_translation}\n";
    217      }
    218      close($tmp);
    219  
    220      my $aln;
    221      my $err;
>>  222      my $ok = run(["mafft",
    223  		  "--auto", "--keeplength",
    224  		  "--addfragments", $tmp,
    225  		  reference_spike_aa_path],
    226  		 ">", \$aln,
    227  		 '2>', \$err);
    228  
    229      open(ALN, "<", \$aln);
    230      my $out;
    231  
    232      my @refaa = split //, $ref_seq;
    233  
    234      my @out_vars;
```

## `lib/Bio/P3/CmdRunner.pm:152`

```
    146  	if ($v =~ /^(\S+)/)
    147  	{
    148  	    return $1;
    149  	}
    150  	return undef;
    151      }
>>  152      elsif ($base eq 'mafft')
    153      {
    154  	my $v;
    155  	IPC::Run::run([$cmd, "--version"], '2>', \$v, '<', '/dev/null');
    156  	if ($v =~ /^(\S+)/)
    157  	{
    158  	    return $1;
    159  	}
    160  	return undef;
    161      }
    162      elsif ($base eq 'minimap2' ||
    163  	   $base eq 'gnuplot'
    164  	  )
```

## `lib/ffxtree.pm:2554`

```
   2548  
   2549      my $add      = $opts->{ add }      || undef;
   2550      my $profile  = $opts->{ profile }  || $opts->{ in2 } || $opts->{ seed } || undef;
   2551      $seqs   ||= $opts->{ seqs }     || $opts->{ in }  || $opts->{ in1 };
   2552      my $version  = $opts->{ version }  || 0;
   2553  
>> 2554      my $mafft = SeedAware::executable_for( $opts->{ mafft } || $opts->{ program } || 'mafft' );
   2555      
   2556      if ( $version ) {
   2557          return undef if ! open( MAFFT, "$mafft --help |" );
   2558          my @info = <MAFFT>;
   2559          close( MAFFT );
   2560          $version = $info[2];    # second line of MAFFT usage info
   2561          return $version;
   2562      }
   2563  
   2564      my %prog_val  = map { $_ => 1 }
   2565          qw( aamatrix
   2566              bl
```

## `lib/phylocode.py:301`

```
    295          comment = "Error in muscle alignment: {}\n".format(ve)
    296          sys.stderr.write(comment)
    297          LOG.write(comment)
    298      return(alignment)
    299  
    300  def alignSeqRecordsMafft(seqRecords):
>>  301      mafftProcess = subprocess.Popen(['mafft', '--quiet', '--auto', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    302      SeqIO.write(seqRecords, mafftProcess.stdin, 'fasta')
    303      mafftProcess.stdin.close()
    304      #alphabet=None
    305      #for s in seqRecords:
    306      #    alphabet=s.seq.alphabet
    307      #    break # only need first one
    308      alignment = None
    309      try:
    310          alignment = AlignIO.read(mafftProcess.stdout, "fasta") #, alphabet=alphabet)
    311          alignment.sort()
    312      except ValueError as ve:
    313          alignment = None
>>  314          comment = "Error in mafft alignment: {}\n".format(ve)
    315          sys.stderr.write(comment)
    316          LOG.write(comment)
    317      return(alignment)
    318  
    319  def calcAlignmentStats(alignment):
    320      # analyze a BioPython MultipleSeqAlignment object to describe conservation levels
    321      stats = {'num_pos':0, 'num_seqs':0, 'sum_squared_freq':0, 'mean_squared_freq':0, 'gaps':0, 'prop_gaps':0}
    322      num_pos = alignment.get_alignment_length()
    323      num_seqs = len(alignment)
    324      if num_pos == 0 or num_seqs == 0: 
    325          return stats
    326      numGaps = 0
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/fasta-cluster-pssm.pl:193`

```
    187  		{
    188  			&gjoseqlib::print_alignment_as_fasta(\*OUT2, ([$_, $seqH->{$_}->{ANNO}, $seqH->{$_}->{SEQ}]));
    189  		}
    190  	}
    191  }
    192  close OUT2;
>>  193  system "mafft --thread 24 --quiet --reorder $base/$tmp/Leftover_Seqs.aa>Leftover_Seqs.fa";
    194  
    195  
    196  
    197  mkdir ("alis"); 
    198  mkdir ("corrected_alis"); 
    199  mkdir ("pssms"); 
    200  
    201  opendir (DIR, "$base/$tmp/clusters");
    202  my @clusterF = grep{$_ !~ /^\./}readdir(DIR); 
    203  close DIR;
    204  
    205  open (REP, ">Curation_Report");
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/FCP_Ali_Utils.pm:37`

```
     31          my $ali_file = $file;
     32          $ali_file =~ s/\.fasta//g;
     33          
     34          print STDERR "\n\nAligning $file\n";
     35          
     36          # Align the sequences with MAFFT
>>   37          open(my $in_fh, "mafft --thread 24 --quiet --reorder $base/$tmp/clusters/$file |") or die "Cannot run MAFFT: $!\n";
     38          my @ali = &gjoseqlib::read_fasta($in_fh);
     39          close($in_fh);
     40  
     41          # Print the original alignment
     42          open(my $out_fh, ">alis/$ali_file.fa") or die "Cannot open alis/$ali_file.fa for writing: $!\n";
     43          &gjoseqlib::print_alignment_as_fasta($out_fh, @ali);
     44          close($out_fh);
     45  
     46          # Process the alignment
     47          my $ali_data = process_alignment(\@ali, $options);
     48          
     49          # Write to report file
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/fasta-cluster-pssm.pl:214`

```
    208  foreach (@clusterF)
    209  {
    210  	my $file = $_;
    211  	my $ali_file = $_;
    212  	$ali_file =~ s/\.fasta//g;
    213  	print STDERR "\n\nAligning $file\n"; 
>>  214  	open (IN, "mafft --thread 24 --quiet --reorder $base/$tmp/clusters/$file |");
    215  	my @ali = &gjoseqlib::read_fasta(\*IN); 
    216  	close IN; 
    217  
    218  	#print the original alignment
    219  	#I might eventually want to turn this off.
    220  	open (OUT, ">alis/$ali_file.fa"); 
    221  	&gjoseqlib::print_alignment_as_fasta(\*OUT, @ali);
    222  	close OUT;
    223  	
    224  		
    225  	# get rid of any sequences containing too many dashes.
    226  	my @ali2;
```

