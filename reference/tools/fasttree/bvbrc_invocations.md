# BV-BRC invocations of `FastTree` (fasttree)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 24 hunk(s) in 12 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Tree_Builder.pm`
- `lib/ffxtree.pm`
- `plbin/App-GeneTree.pl`
- `plbin/App-MSA.pl`
- `plbin/App-PhylogeneticTree.pl`
- `plbin/p3-submit-gene-tree.pl`
- `plbin/p3-submit-influenza-treesort.pl`
- `plbin/p3x-build-gene-tree.pl`
- `pybin/run_treesort.py`
- `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/gto-dir-to-alis-and-trees.pl`
- `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/gtos-dir-to-wgs-tree-single-seg.pl`
- `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/prots_to_alis_and_trees.pl`

## `plbin/App-GeneTree.pl:945`

```
    939      #end_step("Phylogenetic Inference with Phyml");
    940      return @outputs;
    941  }
    942  
    943  sub run_fasttree {
    944      my ($alignment_file, $alphabet, $model, $output_name, $bootstrap) = @_;
>>  945      #my ($step_comments, $step_info) = start_step("Phylogenetic Inference with FastTree");
    946      my $treeFile = $output_name."_fasttree.nwk";
>>  947      my @cmd = ("FastTree", "-out", $treeFile);
    948      if ($alphabet =~ /DNA/i) {
    949          push @cmd, "-nt", "-gtr";
    950      }
    951      else {
    952          $model = 'lg' if $model !~ /lg|wag/i;
    953          $model = lc($model);
    954          push @cmd, "-$model";
    955      }
    956  
    957      push @cmd, $alignment_file;
    958      my $comment = join(" ", @cmd);
    959      #push @{$step_comments}, $comment; 
```

## `plbin/App-GeneTree.pl:968`

```
    962      my ($out, $err) = run_cmd(\@cmd);
    963      print STDERR "STDOUT:\n$out\n";
    964      print STDERR "STDERR:\n$err\n";
    965  
    966      if ($bootstrap) {
    967          # use raxml to generate 100 data matrices
>>  968          # use fasttree to analyze them
    969          # use compareToBootstrap to count the per-branch support (as proportion)
    970          @cmd = "raxmlHPC-PTHREADS-SSE3  -f j -b 123 -# $bootstrap -s $alignment_file -n boot_matrix -m GTRCAT";
    971          print STDERR "Generate bootstrap matrices:\n" . join(" ", @cmd) . "\n";
    972          system(@cmd);
    973          die "raxml failed to produce BS1" unless -f "$alignment_file.BS1";
    974          my $multi_alignment_file = $alignment_file;
    975          $multi_alignment_file =~ s/\.{3,7}$//;
    976          $multi_alignment_file .= "_${bootstrap}BS.phy";
    977          @cmd = ("cat", "$alignment_file.BS*", ">", $multi_alignment_file);
    978          print STDERR "Concatenate into one file:\n" . join(" ", @cmd) . "\n";
    979          system(join(" ", @cmd)); # requires shell interpolation
    980          system("rm $alignment_file.BS*"); #allow shell expansion
    981          my $multi_tree_file = "multiple_bootstrap_trees.nwk";
>>  982          @cmd = ("FastTree", "-n", $bootstrap, "-out", $multi_tree_file);
    983          if ($alphabet =~ /DNA/i) {
    984              push @cmd, "-nt", "-gtr";
    985          }
    986          else {
    987              push @cmd, "-$model";
    988          }
    989          push @cmd, $multi_alignment_file;
    990          print STDERR "Generate trees for each bootstrapped data matrix:\n" . join(" ", @cmd) . "\n";
    991          system(@cmd);
>>  992          die "FastTree did not generate multiple tree file from boostrapped matrices" unless -f $multi_tree_file;
    993          my $tree_with_support = $output_name."_fasttree_boostrap_prop.nwk"; 
    994          @cmd = ("CompareToBootstrap", $treeFile, $multi_tree_file, ">", $tree_with_support);
    995          print STDERR "Map support onto best tree:\n" . join(" ", @cmd) . "\n";
    996          system(join(' ', @cmd));
    997          die "CompareToBootstrap did not generate tree with support values" unless -s $tree_with_support;
    998          $treeFile = $tree_with_support;
    999      }
   1000  
   1001      #$step_info->{details} = $err;
   1002      
   1003      my @outputs;
   1004      my $logFile = $output_name."_fasttree_log.txt";
   1005      write_file($logFile, $err);
   1006      push @outputs, [$treeFile, 'nwk'];
   1007      push @outputs, [$logFile, 'txt'];
   1008  
   1009      run("ls -ltr");
   1010  
>> 1011      #end_step("Phylogenetic Inference with FastTree");
   1012      return @outputs;
   1013  }
   1014  
   1015  sub retrieve_feature_metadata_by_patric_id {
   1016      my ($api, $patric_id, $feature_fields) = @_;
   1017      my $select_string = "select(" . join(",", @$feature_fields) . ")"; 
   1018      $patric_id = uri_escape($patric_id);
   1019      my $query = "eq(patric_id,$patric_id)&$select_string";
   1020      my ($resp, $data) = $api->submit_query('genome_feature', $query);
   1021      #print STDERR "response=$resp\n" if $debug;
   1022      return $data->[0]; #only one element in return, which is a hash reference
   1023  }
```

## `plbin/App-MSA.pl:653`

```
    647      my $out_type = "aligned_protein_fasta";
    648      my $tree_alphabet = "protein";
    649      if ($dna) {
    650          $out_type = "aligned_dna_fasta";
    651          $tree_alphabet = "DNA";
    652      }
>>  653      @cmd = ("p3x-build-gene-tree", "--program", "fasttree", "--alphabet", $tree_alphabet, "--output_dir", "$work_dir", "$work_dir/$prefix.afa");
    654      run_cmd(\@cmd);
    655      print STDOUT "Completed gene tree creation.\n";
    656  
    657      # 
>>  658      # Reroot the fasttree nwk file using midpoint rooting, then delete the fasttree nwk
    659      #
    660      my $fasttree_nwk = "$work_dir/${prefix}_fasttree.nwk";
    661      # make sure initial nwk file exists
    662      if (-e $fasttree_nwk) {
    663          eval {
    664              my $midpoint_tmp = "$work_dir/${prefix}.nwk";
    665              my $midpoint_nwk = "$work_dir/${prefix}_midpoint.nwk";
    666              my @midpoint_cmd = ("p3x-reformat-tree","--midpoint","-f","newick","-o",$midpoint_tmp,"-i",$fasttree_nwk);
    667              print "midpoint root command: @midpoint_cmd\n";
    668              run_cmd(\@midpoint_cmd);
    669              unlink $fasttree_nwk;
>>  670              # rename midpoint file to same name as fasttree file
    671              # ensures MSA tree viewer does not break
    672              # terminate if rename doesn't work?:or die "Unable to rename: $!"
    673              rename($midpoint_nwk,$fasttree_nwk);
    674          };
    675          if ($@) {
    676              print "error while midpoint rooting nwk file: \n$@\n";
    677          }
    678      }
    679  
    680      #
    681      # Copy output to the workspace.
    682      #
```

## `plbin/p3x-build-gene-tree.pl:52`

```
     46  use File::Spec;
     47  use Tree_Builder;
     48  
     49  #$| = 1;
     50  # Get the command-line options.
     51  my $opt = P3Utils::script_opts('msaFile',
>>   52                  ['program|p=s', 'Program to use to build tree (raxml, phyml, or fasttree) (default raxml)', { default => 'raxml' }],
     53                  ['model|m=s', 'Substitution model (or use GTR for DNA, LG for protein)'],
     54                  ['alphabet|a=s', 'DNA or protein (infer if not specified)'],
     55                  ['bootstrap|b=n', 'Perform n bootstrap pseudoreplicates for branch support values', { default => 0 }],
     56                  ['output_dir|o=s', 'Output directory. (default "./")', { default => "./" }],
     57                  ['verbose|debug|v', 'Write status messages to STDERR'],
     58          );
     59  # Check the parameters.
     60  my $msaFile = $ARGV[0];
     61  if ($opt->verbose) {
     62      print "args=", join(", ", @ARGV), "\n";
     63      print "opt = %$opt\n";
     64      for my $key (keys %$opt) {
```

## `pybin/run_treesort.py:1441`

```
   1435        result_status = False
   1436  
   1437        try:
   1438           cmd = ["prepare_treesort_dataset"]
   1439  
   1440           # Specify the reference tree inference method.
>> 1441           # TODO: Consider supporting RAxML in addition to FastTree and IQ-Tree. 
   1442           if (self.job_data.ref_tree_inference and self.job_data.ref_tree_inference == TreeInference.FastTree.value):
   1443              cmd.append(ScriptOption.FastTree.value)
   1444  
   1445           # The segments (optional)
   1446           if self.job_data.segments:
   1447              cmd.append(ScriptOption.Segments.value)
   1448              cmd.append(self.job_data.segments)
   1449  
   1450           # The input FASTA file
   1451           cmd.append(self.input_filename)
   1452  
   1453           # The reference segment
```

## `lib/Tree_Builder.pm:317`

```
    311      my ($self, $bootstrap) = @_;
    312      chdir($self->{_tmpdir}); 
    313      my $output_base = $self->{_output_base};
    314  
    315      my $treeFile = $output_base."_fasttree.nwk";
    316      my $logFile = $output_base."_fasttree_log.txt";
>>  317      my @cmd = ("FastTree", "-out", $treeFile, "-log", $logFile);
    318      if ($self->{_alphabet} =~ /DNA/i) {
    319          push @cmd, "-nt", "-gtr", "-gamma";
    320      }
    321      elsif ($self->{_model} =~ /lg|wag/i) {
    322          push @cmd, "-" . lc($self->{_model});
    323      } # else defaults to JTT for proteins
    324  
    325      push @cmd, $self->{_alignment_file};
>>  326      my $analysis_descriptor = "Build maximum-likelihood tree using FastTree"; 
    327      my $tree_file_name;
    328      $self->add_analysis_step($analysis_descriptor, join(" ", @cmd));
    329      print STDOUT "run command: ". join(" ", @cmd)."\n" if $debug;
    330      my ($out, $err) = run_cmd(\@cmd);
    331      $self->add_analysis_out_err($out, $err);
    332      $self->add_analysis_tree($treeFile);
    333      $self->add_analysis_log($logFile);
    334  
    335      if ($bootstrap) {
    336          # use raxml to generate 100 data matrices
>>  337          # use fasttree to analyze them
    338          # use compareToBootstrap to count the per-branch support (as proportion)
    339          my $model = "GTRCAT";
    340          $model =  "PROTCATLG" if $self->{_alphabet} =~ /protein/i;
    341          print STDERR "alphabet = $self->{_alphabet} , model = $model\n" if $debug;
    342          @cmd = ('raxmlHPC-PTHREADS-SSE3',  '-f', 'j', '-b', '123', '-#', $bootstrap, '-s', $self->{_alignment_file}, '-n', 'boot_matrix', '-m', $model);
    343          $analysis_descriptor = "Generate bootstrap matrices";
    344          $self->add_analysis_step($analysis_descriptor, join(" ", @cmd));
    345          print STDOUT "run command: ". join(" ", @cmd)."\n" if $debug;
    346          my ($out, $err) = run_cmd(\@cmd);
    347          $self->add_analysis_out_err($out, $err);
    348          die "raxml failed to produce BS1" unless -f "$self->{_alignment_file}.BS1";
    349          my $multi_alignment_file = $self->{_alignment_file};
```

## `lib/Tree_Builder.pm:357`

```
    351          $multi_alignment_file .= "_${bootstrap}BS.phy";
    352          @cmd = ("cat", "$self->{_alignment_file}.BS*", ">", $multi_alignment_file);
    353          print STDERR "Concatenate into one file:\n" . join(" ", @cmd) . "\n";
    354          system(join(" ", @cmd)); # requires shell interpolation
    355          system("rm $self->{_alignment_file}.BS*"); #allow shell expansion
    356          my $multi_tree_file = "multiple_bootstrap_trees.nwk";
>>  357          @cmd = ("FastTree", "-n", $bootstrap, "-out", $multi_tree_file, "-log", "fasttree_bootstrap_log");
    358          if ($self->{_alphabet} =~ /DNA/i) {
    359              push @cmd, "-nt", "-gtr";
    360          }
    361          elsif ($self->{_model} =~ /lg|wag/i) {
    362              push @cmd, "-" . lc($self->{_model});
    363          } # else defaults to jtt for proteins
    364          push @cmd, $multi_alignment_file;
    365          $analysis_descriptor = "Generate trees for each bootstrapped data matrix";
    366          $self->add_analysis_step($analysis_descriptor, join(" ", @cmd));
    367          print STDERR $analysis_descriptor, "\n", join(" ", @cmd), "\n" if $debug;
    368          print STDOUT "run command: ". join(" ", @cmd)."\n" if $debug;
    369          ($out, $err) = run_cmd(\@cmd);
    370          $self->add_analysis_out_err($out, $err);
    371          open CAT, ">>$logFile";
    372          open IN, "fasttree_bootstrap_log";
    373          print CAT <IN>;
    374          close CAT;
    375          $self->add_analysis_log($logFile);
>>  376          die "FastTree did not generate multiple tree file from boostrapped matrices" unless -f $multi_tree_file;
    377          my $tree_with_support = $output_base."_fasttree_boostrap_prop.nwk"; 
    378          @cmd = ("CompareToBootstrap", $treeFile, $multi_tree_file);
    379          $analysis_descriptor = "Map support onto best tree";
    380          $self->add_analysis_step($analysis_descriptor, join(" ", @cmd));
    381          print STDOUT "run command: ". join(" ", @cmd)."\n" if $debug;
    382          print STDOUT "run command: ". join(" ", @cmd)."\n" if $debug;
    383          ($out, $err) = run_cmd(\@cmd);
    384          $self->add_analysis_out_err($out, $err);
    385          open F, ">$tree_with_support";
    386          print F $out;
    387          close F;
    388          die "CompareToBootstrap did not generate tree with support values" unless -s $tree_with_support;
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/prots_to_alis_and_trees.pl:114`

```
    108  }
    109  
    110  foreach (@fastas)
    111  {
    112  	system "mafft --thread 64 --reorder $prefix.$_.aa >$prefix.$_.fa";
    113  	system "alignment_density.pl -p $prefix.$_ -m $min_len -t < $prefix.$_.fa  > $prefix.$_.data";
>>  114  	system "FastTree -wag <$prefix.$_.keep.fa>$prefix.$_.nwk";
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
    125  
    126  
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/gto-dir-to-alis-and-trees.pl:125`

```
    119  		my $des = "$anno"."##"."[$name]"."##"."[$qual]";
    120  		push @seqs, ([$id, $des, $aa]);
    121  	}	
    122  	
    123  	&gjoseqlib::print_alignment_as_fasta(\*OUT2, @seqs);
    124  	system "mafft --thread 24 --reorder $file.aa >$file.fa";
>>  125  	system "FastTree -wag <$file.fa>$file.nwk";
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
    137  
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/gtos-dir-to-wgs-tree-single-seg.pl:103`

```
     97  close CLR;
     98  close NAME;
     99  
    100  open (OUT, ">$prefix.dna");
    101  &gjoseqlib::print_alignment_as_fasta(\*OUT, @seqs);
    102  system "mafft --thread 24 --reorder $prefix.dna >$prefix.fa";
>>  103  system "FastTree -nt -gtr <$prefix.fa>$prefix.nwk";
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
    115  
```

## `plbin/App-PhylogeneticTree.pl:135`

```
    129      {
    130  	push(@cmd, "-unique_species", "false");
    131      }
    132  
    133      my %valid_method = (ml => 'ml',
    134  			parsimony_bl => 'parsimony_bl',
>>  135  			ft => 'FastTree',
>>  136  			FastTree => 'FastTree');
    137      
    138      if ($params->{full_tree_method})
    139      {
    140  	if (my $meth = $valid_method{$params->{full_tree_method}})
    141  	{
    142  	    push(@cmd, "-full_tree_method", $meth);
    143  	}
    144  	else
    145  	{
    146  	    die "Invalid full_tree_method value $params->{full_tree_method}";
    147  	}
    148      }
```

## `lib/ffxtree.pm:245`

```
    239          $flags->{mllen} = 1;
    240          $flags->{gamma} = 1;
    241      }
    242  
    243      my @params = make_params_from_vals_and_flags($vals, $flags);
    244  
>>  245      my $fasttree = SeedAware::executable_for($opts->{fasttree} || $opts->{program} || 'fasttree');
    246  
    247      # print STDERR join(" ", $fasttree, @params, $tmpin). "\n";
    248      SeedAware::system_with_redirect($fasttree, @params, $tmpin, { stdout => $tmptree, stderr => $tmplog });
    249  
    250      my $tree = gjonewicklib::read_newick_tree($tmptree);
    251      my $info = SeedAware::slurp_input($tmplog);
    252      my $stats;
    253  
    254      if ($info =~ /LogLk\s*=\s*(\S+)\s*(alpha|Time)/) {
    255          $stats->{logLk} = $1;
    256      }
    257      if ($info =~ /Total time: (\S+)/) {
```

## `lib/ffxtree.pm:2228`

```
   2222          my $fd0   = "$export_dir/$role.fasttree.AT/$role.delta";
   2223          my $lk0   = sprintf "%.3f", [split(/[\t\n]/, `head -n2 $fd0 | tail -n1`)]->[1];
   2224  
   2225          push @html, "  <tr>";
   2226          push @html, "  <td>$_</td>" for ($i, $role, $nseqs, $len, $lk0);
   2227          
>> 2228          for my $prog ("fasttree", "phyml") {
   2229              for my $ndel (@ndels) {
   2230                  my $nd = $ndel > 1 ? "N$ndel." : "";
   2231                  my $dir = "$export_dir/$role.$nd$prog.AT";
   2232                  my $fdelta = "$dir/$role.$nd"."delta";
   2233                  my $floglk = "$dir/$role.$nd"."logLk.txt";
   2234                  
   2235                  my $link1 = "http://bioseed.mcs.anl.gov/~fangfang/eval/$role.$nd$prog.AT";
   2236                  my $link2 = "$link1/$role.$nd" . "delta";
   2237  
   2238                  my $dmean = '-';
   2239                  $dmean = sprintf "%+.3f", [split(/\t/, `grep mean $fdelta`)]->[1] if -e $fdelta;
   2240                  $dmean = add_link($dmean, $link2) if -e $fdelta;
```

## `plbin/p3x-build-gene-tree.pl:7`

```
      1  #!/usr/bin/env perl
      2  =head1 Generate phylogenetic tree based on multiple sequence alignment in fasta format.
      3  
      4      p3x-build-gene-tree.pl [options] msaFile
      5  
      6  This script runs a phylogenetic tree-building program on the input alignment.
>>    7  Programs include RAxML, PhyML, and FastTree
      8  Output is a newick formatted tree as well as a log file.
      9  
     10  =head2 Parameters
     11  
     12  The one positional parameter is the path of the fasta-formatted MSA file.
     13  
     14  The command-line options are as follows.
     15  
     16  =over 4
     17  
     18  =item program
     19  
>>   20  raxml, phyml, or fasttree (case insensitive)
     21  
     22  =item model
     23  
     24  defaults to GTR for DNA and LG for protein, must be one recognized by program
     25  
     26  =item alphabet
     27  
     28  DNA or protein (inferred from sequences if missing)
     29  
     30  =item output_dir
     31  
     32  Directory where newick tree file and log file will be written. Defaults to current directory.
```

## `pybin/run_treesort.py:159`

```
    153  # Command-line script flags / optional arguments.
    154  class ScriptOption(str, Enum):
    155     CladesPath = "--clades"
    156     DescriptorPath = "-i"
    157     Deviation = "--dev"
    158     EqualRates = "--equal-rates"
>>  159     FastTree = "--fast"
    160     MatchOnEPI = "--match-on-epi"
    161     MatchOnRegex = "--match-on-regex"
    162     MatchOnStrain = "--match-on-strain"
    163     Method = "-m"
    164     NoCollapse = "--no-collapse"
    165     OutputFilename = "-o"
    166     PValue = "--pvalue"
    167     Segments = "--segments"
    168  
    169  
    170  # The reference segment inference method.
    171  class TreeInference(str, Enum):
>>  172     FastTree = "FastTree"
    173     IQTree = "IQ-Tree"
    174     # RAxML = "RAxML" # Not implemented yet
    175   
    176  
    177  #-----------------------------------------------------------------------------------------------------------------------------
    178  # Utility functions
    179  #-----------------------------------------------------------------------------------------------------------------------------
    180  
    181  # Trim a string that's possibly null and always return a trimmed, non-null value.
    182  def safe_trim(text: Optional[str]):
    183     if not text:
    184        return ""
```

## `lib/ffxtree.pm:2198`

```
   2192  sub export_eval {
   2193      my $html_dir   = $ENV{HOME}. "/public_html";
   2194      my $export_dir = "$html_dir/eval";
   2195      my $fhtml      = "$export_dir/index.html";
   2196      my $fexp       = "$export_dir/experiments";
   2197  
>> 2198      my @progs = ("fasttree", "phyml");
   2199      my @ndels = (1,2,4,8,16,32);
   2200  
   2201      my @html;
   2202      push @html, "<table border=1>";
   2203      push @html, "  <tr>";
   2204      push @html, "    <th>$_</th>" for ("&nbsp;", "Role", "#Seqs", "Length", "LogLk");
>> 2205      push @html, "    <th colspan=\"12\">$_</th>" for ("FastTree", "PhyML");
   2206      push @html, "  </tr>";
   2207  
   2208      push @html, "  <tr>";
   2209      push @html, "    <th colspan=\"5\">&nbsp;</th>";
   2210      for (@progs) {
   2211          push @html, "    <th colspan=\"2\" align=\"center\">$_</th>" for @ndels;
   2212      }
   2213      push @html, "  </tr>";
   2214  
   2215      my @lines = `cat $fexp`;
   2216      for (@lines) {
   2217          chomp;
```

## `lib/ffxtree.pm:2267`

```
   2261  sub eval_add_to_alignment {
   2262      my ($alignF, $opts) = @_;
   2263  
   2264      my $ndels   = $opts->{ndels}   || 1;
   2265      my $nruns   = $opts->{nruns}   || 10;
   2266      my $dir     = $opts->{dir}     || ".";
>> 2267      my $prog    = $opts->{program} || "fasttree";
   2268      my $realign = $opts->{realign};
   2269      
   2270  
   2271      my $name  = $alignF;
   2272      $name =~ s/\.(fa|mafft)$//i; $name =~ s/.*\///;
   2273      $name .= ".N$ndels" if $ndels > 1;
   2274  
   2275      my $atdir = "$dir/$name.$prog.AT";
   2276      -d $atdir || mkdir("$atdir", 0755) or die "Could not mkdir '$atdir'";
   2277      run("cp $alignF $atdir/");
   2278  
   2279      my $align = gjoseqlib::read_fasta($alignF);
```

## `lib/ffxtree.pm:2396`

```
   2390  sub eval_add_to_alignment_full {
   2391      my ($alignF, $opts) = @_;
   2392  
   2393      my $ndels = $opts->{ndels}   || 1;
   2394      my $nruns = $opts->{nruns}   || 10;
   2395      my $dir   = $opts->{dir}     || ".";
>> 2396      my $prog  = $opts->{program} || "fasttree";
   2397  
   2398      my $name  = $alignF;
   2399      $name =~ s/\.fa$//i; $name =~ s/.*\///;
   2400      $name .= ".N$ndels" if $ndels > 1;
   2401      $name .= ".full";
   2402  
   2403      my $atdir = "$dir/$name.$prog.AT";
   2404      -d $atdir || mkdir("$atdir", 0755) or die "Could not mkdir '$atdir'";
   2405      run("cp $alignF $atdir/");
   2406  
   2407      my $align = gjoseqlib::read_fasta($alignF);
   2408      my $nseqs = @$align; $nruns = $nseqs if $nseqs < $nruns;
```

## `plbin/App-GeneTree.pl:628`

```
    622      my $treeFile;
    623      my $bootstrap = $params->{bootstrap};
    624      if ($recipe eq 'raxml') {
    625          $treeFile = $tree_builder->build_raxml_tree($bootstrap);
    626      } elsif ($recipe eq 'phyml') {
    627          $treeFile = $tree_builder->build_phyml_tree($bootstrap);
>>  628      } elsif ($recipe eq 'fasttree') {
    629          $treeFile = $tree_builder->build_fasttree($bootstrap);
    630      } else {
    631          die "Unrecognized program: $recipe \n";
    632      }
    633      for my $index (0..$tree_builder->get_num_analysis_steps()-1) {
    634          my $step = $tree_builder->get_analysis_step($index);
    635          push @analysis_step, $step;
    636      }
    637      my $logFile = $tree_builder->get_log_file();
    638      push @outputs, ([$treeFile, "nwk"], [$logFile, "txt"]);
    639      # optionally re-write newick file with original sequence IDs if any were altered
    640      # not sure we want to do that as it could screw up downstream use of newick data i
```

## `plbin/p3-submit-gene-tree.pl:88`

```
     82  use List::Util;
     83  
     84  use constant SUB_MODELS => { "HKY85" => 1, "JC69" => 1, "K80" => 1, "F81" => 1, "F84" => 1, "TN93" => 1, "GTR" => 1, "LG" => 1,
     85          "WAG" => 1, "JTT" => 1, "MtREV" => 1, "Dayhoff" => 1, "DCMut" => 1, "RtREV" => 1, "CpREV" => 1, "VT" => 1,
     86          "AB" => 1, "Blosum62" => 1, "MtMam" => 1, "MtArt" => 1, "HIVw" => 1, "HIVb" => 1 };
     87  
>>   88  use constant RECIPES => { "RAxML" => 1, "PhyML" => 1, "FastTree" => 1 };
     89  
     90  # Insure we're logged in.
     91  my $p3token = P3AuthToken->new();
     92  if (! $p3token->token()) {
     93      die "You must be logged into BV-BRC to use this script.";
     94  }
     95  # Get a common-specification processor, an uploader, and a reads-processor.
     96  my $commoner = Bio::KBase::AppService::CommonSpec->new();
     97  my $uploader = Bio::KBase::AppService::UploadSpec->new($p3token);
     98  
     99  # Get the application service helper.
    100  my $app_service = Bio::KBase::AppService::Client->new();
```

## `plbin/p3-submit-influenza-treesort.pl:142`

```
    136  use List::Util;
    137  
    138  use constant SEGMENT_NAMES => { "PB2" => 1, "PB1" => 1, "PA" => 1, "HA" => 1, "NP" => 1, "NA" => 1, "MP" => 1, "NS" => 1 };
    139  
    140  use constant METHOD_NAMES => { local => 1, mincut => 1 };
    141  
>>  142  use constant INF_NAMES => { FastTree => 1, "IQTree" => 1 };
    143  
    144  # Insure we're logged in.
    145  my $p3token = P3AuthToken->new();
    146  if (! $p3token->token()) {
    147      die "You must be logged into BV-BRC to use this script.";
    148  }
    149  # Get a common-specification processor, an uploader, and a reads-processor.
    150  my $commoner = Bio::KBase::AppService::CommonSpec->new();
    151  my $uploader = Bio::KBase::AppService::UploadSpec->new($p3token);
    152  
    153  # Get the application service helper.
    154  my $app_service = Bio::KBase::AppService::Client->new();
    155  
    156  # Declare the option variables and their defaults.
    157  my $fasta;
    158  my $ref = "HA";
    159  my $names = "HA,NA";
    160  my $method = "local";
>>  161  my $inf = "FastTree";
    162  my $maxDev = 2.0;
    163  my $cutoff = 0.001;
    164  my $cladesFile = "";
    165  my $clock;
    166  my $noCollapse;
    167  # Now we parse the options.
    168  GetOptions($commoner->options(),
    169      "fasta=s" => \$fasta,
    170      "ref=s" => \$ref,
    171      "names=s" => \$names,
    172      "method=s" => \$method,
    173      "inf=s" => \$inf,
```

## `plbin/p3x-build-gene-tree.pl:98`

```
     92  $tree_builder->set_output_dir($output_dir);
     93  my $treeFile;
     94  if ($opt->program eq 'raxml') {
     95      $treeFile = $tree_builder->build_raxml_tree($opt->bootstrap);
     96  } elsif ($opt->program eq 'phyml') {
     97      $treeFile = $tree_builder->build_phyml_tree($opt->bootstrap);
>>   98  } elsif ($opt->program eq 'fasttree') {
     99      $treeFile = $tree_builder->build_fasttree($opt->bootstrap);
    100  } else {
    101      die "Unrecognized program: $opt->program \n";
    102  }
    103  my $logFile = $tree_builder->get_log_file();
    104  print "Output directory is $output_dir\n";
    105  print "Tree file is $treeFile\nLog file is $logFile\n";
    106  
```

## `lib/ffxtree.pm:168`

```
    162      }
    163      return $tree;
    164  }
    165  
    166  
    167  #-------------------------------------------------------------------------------
>>  168  #  Tree sequence with FastTree and return the tree. Tree is gjonewick format.
    169  #
    170  #     $tree           = tree_with_fasttree(\@ali, \%opts);
    171  #    ($tree, \%stats) = tree_with_fasttree(\@ali, \%opts);
    172  #   
    173  #    @ali is composed of triples: ($id, $defined, $sequence)
    174  #
    175  #  Optional:
    176  #
    177  #     treefile   => tree_file_name
    178  #     logfile    => log_file_name
    179  #     input      => input_tree
    180  #
```

## `lib/ffxtree.pm:2116`

```
   2110      wantarray() ? ($tree, $stats) : $tree;
   2111  }
   2112  
   2113  sub eval_tree_with_program {
   2114      my ($align, $treeF, $opts) = @_;
   2115      
>> 2116      my $defs = { program  => 'fasttree',
   2117                   optimize => 'eval',
   2118                   model    => 'JTT',
   2119                   rate     => 'Gamma',
   2120                   input    => $treeF,
   2121                   # nclasses => 4,
   2122                   treefile => "/tmp/eval_tree.$$.tree"
   2123                 };
   2124  
   2125      @$defs{ keys %$opts } = values %$opts if $opts;
   2126      
   2127      my ($tree, $stats) = tree_with_program($align, $defs);
   2128  
```

