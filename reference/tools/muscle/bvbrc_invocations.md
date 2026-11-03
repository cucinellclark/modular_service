# BV-BRC invocations of `muscle` (muscle)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 19 hunk(s) in 12 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/alignment.pm`
- `lib/ffxtree.pm`
- `lib/gjoalignment.pm`
- `lib/phylocode.py`
- `lib/rota-a-genotyper/VIGOR3/prod3/VIGOR3.pm`
- `lib/rota-a-genotyper/VIGOR3/prod3/dbutils/muscleGenes.pl`
- `lib/rota-a-genotyper/VIGOR3/prod3/dbutils/muscleProducts.pl`
- `plbin/App-GeneTree.pl`
- `plbin/App-MSA.pl`
- `plbin/snp_analysis.pl`
- `pybin/p3x-build-codon-tree.py`
- `pybin/run_ha_subtype_numbering_conversion.py`

## `plbin/App-GeneTree.pl:1142`

```
   1136      return $tree_graphic_file;
   1137  }
   1138  
   1139  sub run_muscle {
   1140      my ($unaligned, $aligned) = @_;
   1141      print STDERR "run_muscle($unaligned, $aligned)\n";
>> 1142      my ($step_comments, $step_info) = start_step("Align with muscle");
>> 1143      my $cmd = ["muscle", "-in", $unaligned, "-out", $aligned];
   1144      my $comment = join(" ", @$cmd);
   1145      add_step_command_line($comment);
   1146      print STDERR $comment, "\n" if $debug;
   1147      my ($stdout, $stderr) =  run_cmd($cmd);
   1148      $step_info->{details} = $stderr;
>> 1149      end_step("Align with muscle");
   1150  }
   1151  
   1152  sub run_mafft {
   1153      my ($unaligned, $aligned) = @_;
   1154      print STDERR "run_mafft($unaligned, $aligned)\n";
   1155      my ($step_comments, $step_info) = start_step("Align with mafft");
   1156      my $parallel = $ENV{P3_ALLOCATED_CPU};
   1157      my $cmd = ["mafft", "--auto"];
   1158      if ($parallel) {
   1159          push @$cmd, "--thread", $parallel;
   1160      }
   1161      push @$cmd, $unaligned;
```

## `plbin/App-MSA.pl:439`

```
    433      # Run the multiple sequence aligner.
    434      #
    435      my $recipe = lc($params_to_app->{aligner});
    436      if ($aligned_exists && $file_count == 1) {
    437          rename "$work_dir/input.fasta", "$work_dir/output.afa";
    438      }
>>  439      elsif ($recipe eq "muscle") {
    440          # An aln file only displayed 4 out of 8 sequences in MView and JalView for some reason. I could not find anything wrong with the format. Removing clustal w format.
    441      	print STDOUT "Running MUSCLE.\n";
>>  442          my @muscle_version = ("muscle", "-version");
>>  443          my @muscle_cmd =  ("muscle", "-quiet", "-in", "$work_dir/input.fasta", "-fastaout", "$work_dir/output.afa"); # , "-clwstrict", "-clwout", "$work_dir/$prefix.aln");
    444          my $string_cmd = join(" ", @muscle_cmd);
    445          run_cmd(\@muscle_version);
    446          run(\@muscle_version, "1>>", "$work_dir/muscle.job.log");
    447          open(MUSCLE_LOG, '>>', "$work_dir/muscle.job.log") or die $!;
    448          print MUSCLE_LOG "$string_cmd\n";
    449          close(MUSCLE_LOG) or die $!;
    450          print STDOUT "$string_cmd\n";
    451          run_cmd(\@muscle_cmd);
    452          print STDOUT "Finished MUSCLE.\n";
    453      }
    454      elsif ($recipe eq "progressivemauve" or $recipe eq "mauve") {
    455          # The file format is different.
```

## `lib/rota-a-genotyper/VIGOR3/prod3/dbutils/muscleGenes.pl:81`

```
     75      for my $member ( @members ) {
     76          print OUT ">$$member{defline}\n$$member{sequence}\n";
     77      }
     78      close OUT;
     79      print "\n============================================================================================\n";
     80      if ( @members > 1 ) {
>>   81          my $cmd = "$myBin/muscle -clw -in $fastafile -out $musclefile";
     82          print "gene $gene  product $genes{$gene}{product}\n$cmd\n";
     83          $cmd .= "&> /dev/null"; 
     84          runCmd('.', $cmd);
     85          $cmd = "cat $musclefile | sed 's/>/\\n>/'";
     86          my $results = runCmdAndGetResults('.', $cmd);
     87          print "$results\n";
     88          $cmd = "tail -n +4 $musclefile | head -n " .@members;
     89          $results = runCmdAndGetResults('.', $cmd);
     90          my @list = split /\n/, $results;
     91          open( OUT, ">$fastafile" ) || die "\ncannot write to \"$fastafile\"\n" ;
     92          for my $line ( @list ) {
     93              my ( $seqid ) = split / +/, $line;
```

## `lib/rota-a-genotyper/VIGOR3/prod3/dbutils/muscleProducts.pl:82`

```
     76      for my $member ( @members ) {
     77          print OUT ">$$member{defline}\n$$member{sequence}\n";
     78      }
     79      close OUT;
     80      print "\n============================================================================================\n";
     81      if ( @members > 1 ) {
>>   82          my $cmd = "$myBin/muscle -clw -in $fastafile -out $musclefile";
     83          print "product # $productid  product $product\n$cmd\n";
     84          $cmd .= "&> /dev/null"; 
     85          runCmd('.', $cmd);
     86          $cmd = "cat $musclefile | sed 's/>/\\n>/'";
     87          my $results = runCmdAndGetResults('.', $cmd);
     88          print "$results\n";
     89      }
     90  }
     91  exit(0);
```

## `plbin/snp_analysis.pl:131`

```
    125  if($aa_only){ # start of aa loop
    126  	my $aa_file = $result_dir . "/" ."input.fasta";
    127  	my $afa_file  = $result_dir . "/" . "output.afa";
    128  	my $aln_file = $result_dir . "/" . "output.aln";
    129  	if(!$snp_only){
    130  		my $cmd = '';
>>  131  		$cmd = "muscle -in $aa_file -fastaout $afa_file -clwout $aln_file ";
    132  		my $re = &run_command($cmd, 0);
    133  		if($re != 0){
    134  			print MAIN_LOG "\nMuscle failed on this group of $na_count flu protein sequences from $subtype, $host, $segment, and $prot\n\n";
    135  			print "\nMuscle failed on this group of $na_count flu protein sequences from $subtype, $host, $segment, and $prot\n\n";
    136  		}
    137  	}
    138  
    139  	if(-e $aln_file){
    140  		chdir $result_dir or die "cannot change to dir: $prot_dir\n";
    141  		my $aln_file = "output.aln";
    142  		my $zip_file = "output.zip";
    143  		my $cmd = "zip -r $zip_file $aln_file";
```

## `lib/rota-a-genotyper/VIGOR3/prod3/VIGOR3.pm:7870`

```
   7864  
   7865  #if ( getlogin() eq "jhoover" ) { print ">$tmppepid\n$tmppepseq\n>$tmprefid\n$refseq\n" }
   7866      close TMP;
   7867  
   7868      my $cmd = "$myBin/clustalw -align -GAPOPEN=6.0 -GAPEXT=0.3 -infile=$vigorspace/tmp_align_fasta > $vigorspace/tmp_align_fasta.log 2>&1";
   7869  
>> 7870  #"muscle -in $vigorspace/tmp_align_fasta -out $vigorspace/tmp_align_fasta.aln -clwstrict &> $vigorspace/tmp_align_fasta.log";
   7871      &runCmd($vigorspace, $cmd);
   7872  
   7873      my $alignment = &runCmdAndGetResults($vigorspace, "cat tmp_align_fasta.aln");
   7874      $alignment =~ s/[\n\r\s]+$//;
   7875  
   7876      #print $alignment . "\n" . `cat $vigorspace/tmp_align_fasta.log` . "\n";
   7877  
   7878      #unlink "$vigorspace/tmp_align_fasta";
   7879      #unlink "$vigorspace/tmp_align_fasta.aln";
   7880      #unlink "$vigorspace/tmp_align_fasta.log";
   7881  
   7882      return $alignment;
```

## `plbin/snp_analysis.pl:92`

```
     86  if($na_only){
     87  	my $na_file = $result_dir . "/" . "input.fasta";
     88  	my $afa_file = $result_dir . "/" . "output.afa";
     89  	my $aln_file = $result_dir . "/" . "output.aln";
     90  	my $gaf_file= $result_dir . "/" . "output.jpg";
     91  	if(!$snp_only){
>>   92  		my $cmd =  "muscle -in $na_file -fastaout $afa_file -clwout $aln_file";
     93  		my $re = &run_command($cmd, 0);
     94  		if($re != 0){
     95  			print MAIN_LOG "\nMuscle failed on this group of $na_count flu DNA sequences from $subtype, $host, and $segment\n\n";
     96  			print "\nMuscle failed on this group of $na_count flu DNA sequences from $subtype, $host, and $segment\n\n";
     97  		}
     98  	}
     99  
    100  	if(-e $aln_file) {
    101  		chdir $result_dir or die "cannot change to dir: $segment_dir\n";
    102  		my $aln_file = "output.aln";
    103  		my $zip_file = "output.zip";
    104  		my $cmd = "zip -r $zip_file $aln_file";
```

## `pybin/run_ha_subtype_numbering_conversion.py:352`

```
    346              muscle_data.write(f">{query_name}\n")
    347              muscle_data.write(sequence)
    348              muscle_data.write("\n")
    349              muscle_data.write(f">{blast_subtype}\n")
    350              muscle_data.write(reference_sequence)
    351  
>>  352          # Run muscle
    353          try:
>>  354              muscle_cmd = ["muscle", "-in", str(muscle_input_file), "-out", str(muscle_output_file), "-quiet"]
    355              subprocess.check_call(muscle_cmd, shell=False)
    356          except Exception as e:
>>  357              print(f"Error running muscle for {muscle_input_file}: {e}")
    358              sys.exit(1)
    359  
    360          muscle_sequence = {}
    361          with open(muscle_output_file) as muscle_data:
    362              for values in parse_fasta_file(muscle_data):
    363                  muscle_sequence[values["header"]] = values["data"]
    364  
    365          # Combine subtypes from user selection and subtype from blast result
    366          selected_subtypes = [t for t in selected_types if t != blast_subtype]
    367  
    368          # Final result file
    369          result_file = output_dir / f"{query_name}_result.fasta"
```

## `lib/alignment.pm:359`

```
    353      my $add      = $opts->{ add }      || undef;
    354      my $profile  = $opts->{ profile }  || $opts->{ in2 } || undef;
    355      my $refine   = $opts->{ refine }   || 0;
    356         $seqs   ||= $opts->{ seqs }     || $opts->{ in } || $opts->{ in1 };
    357      my $version  = $opts->{ version }  || 0;
    358  
>>  359      my $muscle = SeedTkRun::executable_for( $opts->{ muscle } || $opts->{ program } || 'muscle' )
>>  360          or print STDERR "Could not locate executable file for 'muscle'.\n"
    361              and return undef;
    362  
    363      if ( $version )
    364      {
    365          SeedTkRun::system_with_redirect($muscle, "-version", { stdout => \$version });
    366          chomp $version;
    367          return $version;
    368      }
    369  
    370      my %prog_val  = map { $_ => 1 }
    371                      qw( anchorspacing
    372                          center
```

## `lib/phylocode.py:280`

```
    274      LOG.write("found = {}\n".format(found))
    275      return found
    276  
    277  def alignSeqRecordsMuscle(seqRecords):
    278      try:
    279          #python3
>>  280          muscleProcess = subprocess.Popen(['muscle', '-quiet'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    281      except TypeError:
    282          # python2
>>  283          muscleProcess = subprocess.Popen(['muscle', '-quiet'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    284      SeqIO.write(seqRecords, muscleProcess.stdin, 'fasta')
    285      muscleProcess.stdin.close()
    286      #alphabet=None
    287      #for s in seqRecords:
    288      #    alphabet=s.seq.alphabet
    289      #    break
    290      try:
    291          alignment = AlignIO.read(muscleProcess.stdout, "fasta") #, alphabet=) #alphabet)
    292          alignment.sort()
    293      except ValueError as ve:
    294          alignment = None
>>  295          comment = "Error in muscle alignment: {}\n".format(ve)
    296          sys.stderr.write(comment)
    297          LOG.write(comment)
    298      return(alignment)
    299  
    300  def alignSeqRecordsMafft(seqRecords):
    301      mafftProcess = subprocess.Popen(['mafft', '--quiet', '--auto', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    302      SeqIO.write(seqRecords, mafftProcess.stdin, 'fasta')
    303      mafftProcess.stdin.close()
    304      #alphabet=None
    305      #for s in seqRecords:
    306      #    alphabet=s.seq.alphabet
    307      #    break # only need first one
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

## `lib/gjoalignment.pm:443`

```
    437      my $add      = $opts->{ add }      || undef;
    438      my $profile  = $opts->{ profile }  || $opts->{ in2 } || undef;
    439      my $refine   = $opts->{ refine }   || 0;
    440         $seqs   ||= $opts->{ seqs }     || $opts->{ in } || $opts->{ in1 };
    441      my $version  = $opts->{ version }  || 0;
    442  
>>  443      my $muscle = SeedAware::executable_for( $opts->{ muscle } || $opts->{ program } || 'muscle' )
>>  444          or print STDERR "Could not locate executable file for 'muscle'.\n"
    445              and return undef;
    446  
    447      if ( $version )
    448      {
    449          $version = SeedAware::run_gathering_output( $muscle, "-version" );
    450          chomp $version;
    451          return $version;
    452      }
    453  
    454      my %prog_val  = map { $_ => 1 }
    455                      qw( anchorspacing
    456                          center
```

## `pybin/p3x-build-codon-tree.py:343`

```
    337              #sys.stderr.write(comment)
    338              all_ok = False
    339      if not all_ok:
    340          continue # skip this homology group
    341      if args.debugMode:
    342          LOG.write("protein set for %s has %d seqs\n"%(homologId, len(proteinSeqDict)))
>>  343      if args.aligner == 'muscle':
    344          proteinAlignment = phylocode.alignSeqRecordsMuscle(proteinSeqDict.values())
    345      else:
    346          proteinAlignment = phylocode.alignSeqRecordsMafft(proteinSeqDict.values())
    347      if not proteinAlignment:
    348          continue
    349      proteinAlignment = phylocode.resolveDuplicatesPerPatricGenome(proteinAlignment)
    350      if proteinAlignment:
    351          proteinAlignment.sort()
    352          proteinAlignments[homologId] = proteinAlignment
    353          alignmentStats = phylocode.calcAlignmentStats(proteinAlignment)
    354          # dividing by sqrt(alignment length) yields result intermediate between sum_squared_freq and mean_squared_freq (where squared_freq is the within-column sum of squared state (letter, amino acid) frequency
    355          if alignmentStats['num_pos']:
```

## `plbin/snp_analysis.pl:17`

```
     11  
     12  use vars qw($opt_r $opt_n $opt_a $opt_x $opt_t $opt_o $opt_g $opt_m $opt_c $opt_h $opt_d $opt_z $opt_e $opt_f);
     13  getopts('r:naxt:o:g:m:chdz:ef');
     14  
     15  my $usage = "
     16       DESCRIPTION:
>>   17  	This program do snp analysis. It will use muscle for protein seq and na sequence alignment if no pre-aligned na sequence available.
     18  
     19  
     20       OPTIONS:
     21  	-r root directory for all data generated
     22  	-n na seq only
     23  	-a aa seq only
     24  	-x snp only
     25  	-t subtype
     26  	-o host
     27  	-g segment
     28  	-m protein (eg. PB1)
     29  	-c run clustalw for na sequence alignment
```

## `lib/alignment.pm:126`

```
    120          bootstrap_sample
    121          );
    122  
    123  
    124  =pod
    125  
>>  126    Align sequences with muscle and return the alignment, or alignment and tree.
    127  
    128       \@align                           = align_with_mafft( \@seqs )
    129       \@align                           = align_with_mafft( \@seqs, \%opts )
    130       \@align                           = align_with_mafft( \%opts )
    131     ( \@align, $newick-tree-as-string ) = align_with_mafft( \@seqs )
    132     ( \@align, $newick-tree-as-string ) = align_with_mafft( \@seqs, \%opts )
    133     ( \@align, $newick-tree-as-string ) = align_with_mafft( \%opts )
    134  
    135    If input sequences are not supplied, they must be included as an in or in1
    136    option value.
    137  
    138    Options:
```

## `lib/alignment.pm:321`

```
    315  
    316      return wantarray ? ( \@ali, $treestr ) : \@ali;
    317  }
    318  
    319  =pod
    320  
>>  321    Align sequences with muscle and return the alignment, or alignment and tree.
    322  
    323       \@align                           = align_with_muscle( \@seqs )
    324       \@align                           = align_with_muscle( \@seqs, \%opts )
    325       \@align                           = align_with_muscle( \%opts )
    326     ( \@align, $newick-tree-as-string ) = align_with_muscle( \@seqs )
    327     ( \@align, $newick-tree-as-string ) = align_with_muscle( \@seqs, \%opts )
    328     ( \@align, $newick-tree-as-string ) = align_with_muscle( \%opts )
    329  
    330    If input sequences are not supplied, they must be included as an in or in1
    331    option value.
    332  
    333    Options:
```

## `lib/ffxtree.pm:2512`

```
   2506      my $s;
   2507      $s += ($_ - $m) * ($_ - $m) for @_;
   2508      sprintf "%9f", sqrt $s / @_; 
   2509  }
   2510  
   2511  #===============================================================================
>> 2512  #  Align sequences with muscle and return the alignment, or alignment and tree.
   2513  #
   2514  #     \@align                           = align_with_mafft( \@seqs )
   2515  #     \@align                           = align_with_mafft( \@seqs, \%opts )
   2516  #     \@align                           = align_with_mafft( \%opts )
   2517  #   ( \@align, $newick-tree-as-string ) = align_with_mafft( \@seqs )
   2518  #   ( \@align, $newick-tree-as-string ) = align_with_mafft( \@seqs, \%opts )
   2519  #   ( \@align, $newick-tree-as-string ) = align_with_mafft( \%opts )
   2520  #
   2521  #  If input sequences are not supplied, they must be included as an in or in1
   2522  #  option value.
   2523  #
   2524  #  Options:
```

## `lib/gjoalignment.pm:194`

```
    188          simple_trim_start
    189          simple_trim_end
    190          );
    191  
    192  
    193  #===============================================================================
>>  194  #  Align sequences with muscle and return the alignment, or alignment and tree.
    195  #
    196  #     \@align                           = align_with_mafft( \@seqs )
    197  #     \@align                           = align_with_mafft( \@seqs, \%opts )
    198  #     \@align                           = align_with_mafft( \%opts )
    199  #   ( \@align, $newick-tree-as-string ) = align_with_mafft( \@seqs )
    200  #   ( \@align, $newick-tree-as-string ) = align_with_mafft( \@seqs, \%opts )
    201  #   ( \@align, $newick-tree-as-string ) = align_with_mafft( \%opts )
    202  #
    203  #  If input sequences are not supplied, they must be included as an in or in1
    204  #  option value.
    205  #
    206  #  Options:
```

## `lib/gjoalignment.pm:404`

```
    398  
    399      return wantarray ? ( \@ali, $treestr ) : \@ali;
    400  }
    401  
    402  
    403  #===============================================================================
>>  404  #  Align sequences with muscle and return the alignment, or alignment and tree.
    405  #
    406  #     \@align                           = align_with_muscle( \@seqs )
    407  #     \@align                           = align_with_muscle( \@seqs, \%opts )
    408  #     \@align                           = align_with_muscle( \%opts )
    409  #   ( \@align, $newick-tree-as-string ) = align_with_muscle( \@seqs )
    410  #   ( \@align, $newick-tree-as-string ) = align_with_muscle( \@seqs, \%opts )
    411  #   ( \@align, $newick-tree-as-string ) = align_with_muscle( \%opts )
    412  #
    413  #  If input sequences are not supplied, they must be included as an in or in1
    414  #  option value.
    415  #
    416  #  Options:
```

