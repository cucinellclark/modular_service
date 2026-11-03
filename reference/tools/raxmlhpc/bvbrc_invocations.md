# BV-BRC invocations of `raxmlHPC-PTHREADS-SSE3` (raxmlhpc)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 11 hunk(s) in 6 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/GenomeAnnotationApp/ComprehensiveGenomeAnalysis.pm`
- `lib/Bio/P3/SARS2Assembly/ComprehensiveAnalysis.pm`
- `lib/Tree_Builder.pm`
- `lib/ffxtree.pm`
- `plbin/App-CodonTree.pl`
- `plbin/App-GeneTree.pl`

## `plbin/App-GeneTree.pl:824`

```
    818      }
    819      else {
    820          $model = 'LG' if $model !~ /DAYHOFF|DCMUT|JTT|MTREV|WAG|RTREV|CPREV|VT|BLOSUM62|MTMAM|LG|MTART|MTZOA|PMB|HIVB|HIVW|JTTDCMUT|FLU|STMTREV|DUMMY|DUMMY2|AUTO|LG4M|LG4X|PROT_FILE|GTR_UNLINKED|GTR/i;
    821          $model = "PROTCAT". $model;
    822      }
    823  
>>  824      my @cmd = ("raxmlHPC-PTHREADS-SSE3");
    825      push @cmd, ("-T", $parallel);
    826      push @cmd, ("-p", "12345");
    827      push @cmd, ("-m", $model);
    828      push @cmd, ("-s", basename($alignment_file));
    829      push @cmd, ("-n", $output_name);
    830      my $support_trees;
    831      if ($bootstrap) {
    832          push @cmd, ("-f",  "d"); # just do ML search (generate bootstrap trees separately later)
    833          $support_trees = "RAxML_bootstrap." . $output_name . "_bootstrap";
    834      }
    835      else {
    836          push @cmd, ("-f", "D"); # generate RELL replicate trees
```

## `plbin/App-GeneTree.pl:853`

```
    847      #$step_info->{details} = $out;
    848  
    849      if ($bootstrap) {
    850          if ($alphabet eq 'DNA') {
    851              $model = 'GTRCAT'
    852          }
>>  853          @cmd = ("raxmlHPC-PTHREADS-SSE3");
    854          push @cmd, ("-T", $parallel);
    855          push @cmd, ("-m", $model);
    856          push @cmd, ("-s", basename($alignment_file));
    857          push @cmd, ("-n", $output_name . "_bootstrap");
    858          push @cmd, ("-b",  "12345", "-#", $bootstrap, "-p", "12345");
    859          ($out, $err) = run_cmd(\@cmd);
    860      }
    861      # now map replicate support numbers onto ML tree (from either bootstrap or RELL output)
>>  862      @cmd = ("raxmlHPC-PTHREADS-SSE3", "-f", "b", "-m", "GTRCAT"); #to map RELL bootstrap support onto ML tree
    863      push @cmd, ("-t", "RAxML_bestTree.".$output_name);
    864      push @cmd, ("-z", $support_trees);
    865      push @cmd, ("-n", $output_name . "_support");
    866      print STDERR "Map support values onto ML tree:\n", join(" ", @cmd), "\n";
    867      my ($out, $err) = run_cmd(\@cmd);
    868      print STDERR "STDOUT:\n$out\n";
    869      print STDERR "STDERR:\n$err\n";
    870      #$step_info->{details} .= $out;
    871      
    872      my @outputs;
    873      my $treeFile = $output_name . "_raxml_tree.nwk";
    874      move("RAxML_bipartitions.".$output_name. "_support", $treeFile);
```

## `plbin/App-GeneTree.pl:970`

```
    964      print STDERR "STDERR:\n$err\n";
    965  
    966      if ($bootstrap) {
    967          # use raxml to generate 100 data matrices
    968          # use fasttree to analyze them
    969          # use compareToBootstrap to count the per-branch support (as proportion)
>>  970          @cmd = "raxmlHPC-PTHREADS-SSE3  -f j -b 123 -# $bootstrap -s $alignment_file -n boot_matrix -m GTRCAT";
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
    982          @cmd = ("FastTree", "-n", $bootstrap, "-out", $multi_tree_file);
```

## `lib/Tree_Builder.pm:177`

```
    171          $model = 'LG' if $model !~ /DAYHOFF|DCMUT|JTT|MTREV|WAG|RTREV|CPREV|VT|BLOSUM62|MTMAM|LG|MTART|MTZOA|PMB|HIVB|HIVW|JTTDCMUT|FLU|STMTREV|DUMMY|DUMMY2|AUTO|LG4M|LG4X|PROT_FILE/i;
    172          $model = "PROTCAT". $model;
    173      }
    174      #$self->{_model} = $model;
    175  
    176      my $analysis_descriptor = "Build maximum-likelihood tree using RAxML";
>>  177      my @cmd = ("raxmlHPC-PTHREADS-SSE3");
    178      push @cmd, ("-T", $self->{_parallel});
    179      push @cmd, ("-p", "12345");
    180      push @cmd, ("-m", $model);
    181      push @cmd, ("-s", $self->{_alignment_file});
    182      push @cmd, ("-n", $output_base);
    183      my $support_trees;
    184      my $comment;
    185      my $tree_with_support_name = "${output_base}_raxml";
    186      if ($bootstrap) {
    187          push @cmd, ("-f",  "d"); # just do ML search (generate bootstrap trees separately later)
    188          $tree_with_support_name .= "_bootstrap_tree.nwk";
    189      }
```

## `lib/Tree_Builder.pm:213`

```
    207          if ($self->{_alphabet} eq 'DNA') {
    208              $model = 'GTRCAT'
    209          }
    210          my $bootstrap_name = "Tree_Builder_bootstrap";
    211          $analysis_descriptor = "Generate bootstrap trees";
    212          $support_trees = "RAxML_bootstrap." . $bootstrap_name;
>>  213          @cmd = ("raxmlHPC-PTHREADS-SSE3");
    214          push @cmd, ("-T", $self->{_parallel});
    215          push @cmd, ("-m", $model);
    216          push @cmd, ("-s", $self->{_alignment_file});
    217          push @cmd, ("-n", $bootstrap_name);
    218          push @cmd, ("-b",  "12345", "-#", $bootstrap, "-p", "12345");
    219          $self->add_analysis_step($analysis_descriptor, join(" ", @cmd));
    220          print STDOUT "run command: ". join(" ", @cmd)."\n" if $debug;
    221          ($out, $err) = run_cmd(\@cmd);
    222          $self->add_analysis_out_err($out, $err);
    223          $self->add_analysis_tree($support_trees);
    224          $self->add_analysis_comment("Number of bootstrap replicates = $bootstrap.");
    225          open CAT, ">>$logFile";
```

## `lib/Tree_Builder.pm:233`

```
    227          print CAT <IN>;
    228          close CAT;
    229          $self->add_analysis_log($logFile);
    230      }
    231      # now map replicate support numbers onto ML tree (from either bootstrap or RELL output)
    232      $analysis_descriptor = "Map replicate support numbers onto ML tree";
>>  233      @cmd = ("raxmlHPC-PTHREADS-SSE3", "-f", "b", "-m", "GTRCAT"); #to map RELL bootstrap support onto ML tree
    234      push @cmd, ("-t", "RAxML_bestTree.".$output_base);
    235      push @cmd, ("-z", $support_trees);
    236      push @cmd, ("-n", $tree_with_support_name);
    237      push @cmd, ("-T", $self->{_parallel}, "-p", "12345");
    238      $self->add_analysis_step($analysis_descriptor, join(" ", @cmd));
    239      print STDOUT "run command: ". join(" ", @cmd)."\n" if $debug;
    240      ($out, $err) = run_cmd(\@cmd);
    241      $self->add_analysis_out_err($out, $err);
    242      move("RAxML_bipartitions.$tree_with_support_name", "$self->{_output_dir}/$tree_with_support_name");
    243      $self->add_analysis_tree($tree_with_support_name);
    244      open CAT, ">>$logFile";
    245      open IN, "RAxML_info.$tree_with_support_name";
```

## `lib/Tree_Builder.pm:342`

```
    336          # use raxml to generate 100 data matrices
    337          # use fasttree to analyze them
    338          # use compareToBootstrap to count the per-branch support (as proportion)
    339          my $model = "GTRCAT";
    340          $model =  "PROTCATLG" if $self->{_alphabet} =~ /protein/i;
    341          print STDERR "alphabet = $self->{_alphabet} , model = $model\n" if $debug;
>>  342          @cmd = ('raxmlHPC-PTHREADS-SSE3',  '-f', 'j', '-b', '123', '-#', $bootstrap, '-s', $self->{_alignment_file}, '-n', 'boot_matrix', '-m', $model);
    343          $analysis_descriptor = "Generate bootstrap matrices";
    344          $self->add_analysis_step($analysis_descriptor, join(" ", @cmd));
    345          print STDOUT "run command: ". join(" ", @cmd)."\n" if $debug;
    346          my ($out, $err) = run_cmd(\@cmd);
    347          $self->add_analysis_out_err($out, $err);
    348          die "raxml failed to produce BS1" unless -f "$self->{_alignment_file}.BS1";
    349          my $multi_alignment_file = $self->{_alignment_file};
    350          $multi_alignment_file =~ s/\.{3,7}$//;
    351          $multi_alignment_file .= "_${bootstrap}BS.phy";
    352          @cmd = ("cat", "$self->{_alignment_file}.BS*", ">", $multi_alignment_file);
    353          print STDERR "Concatenate into one file:\n" . join(" ", @cmd) . "\n";
    354          system(join(" ", @cmd)); # requires shell interpolation
```

## `lib/Bio/P3/GenomeAnnotationApp/ComprehensiveGenomeAnalysis.pm:668`

```
    662      my $max_genes = 5;
    663      my $max_allowed_dups = 1;
    664      my $max_genomes_missing = 2;
    665      my $bootstrap_reps = 100;
    666      my $n_threads = $ENV{P3_ALLOCATED_CPU} // 2;
    667  
>>  668      my $exe = "raxmlHPC-PTHREADS-SSE3";
    669      
    670      @cmd = ("p3x-build-codon-tree",
    671  	    "--maxGenes", $max_genes,
    672  	    "--maxAllowedDups", $max_allowed_dups,
    673  	    "--maxGenomesMissing", $max_genomes_missing,
    674  	    "--bootstrapReps", $bootstrap_reps,
    675  	    "--threads", $n_threads,
    676  	    "--outputDirectory", $tree_dir,
    677  	    "--raxmlExecutable", $exe,
    678  	    "--genomeObjectFile", $annotated_file,
    679  	    "--genomeIdsFile", $ingroup_file);
    680      print "@cmd\n";
```

## `lib/Bio/P3/SARS2Assembly/ComprehensiveAnalysis.pm:659`

```
    653      my $max_genes = 5;
    654      my $max_allowed_dups = 1;
    655      my $max_genomes_missing = 2;
    656      my $bootstrap_reps = 100;
    657      my $n_threads = $ENV{P3_ALLOCATED_CPU} // 2;
    658  
>>  659      my $exe = "raxmlHPC-PTHREADS-SSE3";
    660      
    661      @cmd = ("p3x-build-codon-tree",
    662  	    "--maxGenes", $max_genes,
    663  	    "--maxAllowedDups", $max_allowed_dups,
    664  	    "--maxGenomesMissing", $max_genomes_missing,
    665  	    "--bootstrapReps", $bootstrap_reps,
    666  	    "--threads", $n_threads,
    667  	    "--outputDirectory", $tree_dir,
    668  	    "--raxmlExecutable", $exe,
    669  	    "--genomeObjectFile", $annotated_file,
    670  	    "--genomeIdsFile", $ingroup_file);
    671      print "@cmd\n";
```

## `lib/ffxtree.pm:490`

```
    484          $vals->{t} = $tmptr2;
    485          $vals->{f} = 'e';
    486      }
    487  
    488      my @params = make_params_from_vals_and_flags($vals, $flags);
    489  
>>  490      my $raxml = SeedAware::executable_for($opts->{raxml} || $opts->{program} || 'raxmlHPC-PTHREADS-SSE3');
    491      
    492      SeedAware::system_with_redirect($raxml, @params, { stdout => $tmplog, stderr => '/dev/null' });
    493      # print STDERR join(" ", $raxml, @params). "\n";
    494  
    495      my $tree  = gjonewicklib::read_newick_tree($tmptree);
    496      my $info  = SeedAware::slurp_input($tmplog);
    497      my $info2 = SeedAware::slurp_input($tmplog2);
    498      my $stats;
    499  
    500      if ($info =~ /Overall Time for \d+ Inference\s*(\S+)/) {
    501          $stats->{time}  = $1;
    502      } elsif ($info =~ /Overall Time for Tree Evaluation\s*(\S+)/) {
```

## `plbin/App-CodonTree.pl:73`

```
     67  
     68      my $n_genes = $params->{number_of_genes};
     69      my $bootstraps = $params->{bootstraps};
     70      my $max_missing = $params->{max_genomes_missing};
     71      my $max_allowed_dups = $params->{max_allowed_dups};
     72      
>>   73      my $raxml = "raxmlHPC-PTHREADS-SSE3";
     74      
     75      my $out_dir = "$here/output";
     76      make_path($out_dir);
     77      
     78      my @figtrees = grep { -f $_ } sort { $b <=> $a }  <$ENV{KB_RUNTIME}/FigTree*/lib/figtree.jar>;
     79      my @figtree_jar;
     80      if (@figtrees)
     81      {
     82  	@figtree_jar = ("--pathToFigtreeJar", $figtrees[0]);
     83      }
     84      else
     85      {
```

