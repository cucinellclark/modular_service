# BV-BRC invocations of `mmseqs` (mmseqs)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 5 hunk(s) in 3 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/FCP_Main_Utils.pm`
- `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/FCP_Nterm_Utils.pm`
- `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/fasta-cluster-pssm.pl`

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/FCP_Nterm_Utils.pm:232`

```
    226          print STDERR "  Running MMSeqs on N-terminal region (first ", NTERM_LENGTH, " amino acids)...\n";
    227          my $mmseqs_prefix = "$nterm_dir/nterm";
    228          
    229          # Use the n_term_cluster_id parameter with a default of 0.7
    230          my $n_term_cluster_id = defined($options->{n_term_cluster_id}) ? $options->{n_term_cluster_id} : 0.7;
    231          my $mmc = $options->{mmc};
>>  232          my $cmd = "mmseqs easy-cluster $nterm_dir/nterm.fasta $mmseqs_prefix tmp --min-seq-id $n_term_cluster_id -c $mmc --cov-mode 0 >/dev/null";
    233          print STDERR "  Command: $cmd\n";
    234          
    235          my $ret = system $cmd;
    236          if ($ret != 0) 
    237          {
    238              print STDERR "  Warning: MMSeqs execution failed with return code $ret: $!\n";
    239              print $log_fh "$ali_file\t0\t0\t0\n";
    240              next;
    241          }
    242          
    243          # Read the all_seqs fasta file
    244          print STDERR "  Reading $mmseqs_prefix\_all_seqs.fasta...\n";
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/FCP_Main_Utils.pm:255`

```
    249      my ($seq_data, $options) = @_;
    250      my $tmp = $seq_data->{tmp};
    251      
    252      my $mmi = $options->{mmi};
    253      my $mmc = $options->{mmc};
    254      
>>  255      print STDERR "Running mmseqs with parameters: min-seq-id=$mmi, coverage=$mmc\n";
    256      
>>  257      # Run mmseqs easy-cluster
>>  258      print STDERR "Command: mmseqs easy-cluster $tmp.fasta $tmp.mmseq tmp --min-seq-id $mmi -c $mmc --cov-mode 0\n";
>>  259      my $ret = system "mmseqs easy-cluster $tmp.fasta $tmp.mmseq tmp --min-seq-id $mmi -c $mmc --cov-mode 0 >/dev/null";
    260      
    261      if ($ret != 0) 
    262      {
    263          die "MMSeqs execution failed with return code $ret: $!\n";
    264      }
    265      
    266      print STDERR "MMSeqs clustering completed successfully\n";
    267      
    268      # Process the clusters
    269      process_mmseqs_clusters($seq_data, $options);
    270      
    271      return 1;
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/fasta-cluster-pssm.pl:138`

```
    132  		&gjoseqlib::print_alignment_as_fasta(\*OUT, ([$id, $prots2[$i][1], $prots2[$i][2]]));
    133  	}
    134  }
    135  
    136  
    137  print STDERR "Running mmseqs\n"; 
>>  138  # Run mmseqs
>>  139  system "mmseqs easy-cluster $tmp.fasta $tmp.mmseq tmp --min-seq-id $mmi -c $mmc --cov-mode 0 >/dev/null";
    140  
    141  
    142  
    143  
    144  #Process the clusters into individual fasta files.
    145   
    146  open (IN, "<$tmp.mmseq_all_seqs.fasta"), or die "cannot open all_seqs fasta file from mmseqs\n"; 
    147  my $seqH = {};
    148  my @seqs = &gjoseqlib::read_fasta(\*IN); # garys read program ignores fasta identifiers with out sequence.
    149  close IN;
    150  for my $i (0..$#seqs)
    151  {
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/FCP_Main_Utils.pm:32`

```
     26  			-e cutoff for the number of dashes at the end of a sequence to be seen 
     27  			   before throwing away sequence with a gap at the end [d = 3]
     28  			-efo end fraction occupancy, this goes with -e.  This dictates the fraction of dashes in the -e 
     29  			     end columns in order to allow cutting [d = 0.15] (if the fraction is too high, you might 
     30  			     be cutting something that is conserved)
     31  			-fd maximum fraction of dashes allowable for keeping a sequence (d = 0.20)
>>   32  			-mi mmseqs identity [d = 0.8]
>>   33  			-mc mmseqs coverage [d = 0.8]
     34  			-k keep temp fasta (pre-aligned)
     35  			-p "pssm prefix" (default = nothing).
     36  			-tmp name temp fasta file 
     37  			-p_nterm percent identity minimum for reclustering the columns in the first 25aas (default = 65%)
     38  			-n_nterm number of bad columns required for the n-terminal reclustering procedure (default = 3)
     39  			-nterm_eval_length number of N-terminal columns to check for poor conservation (default = 10)
     40  			-nterm-mmseq-id identity threshold for N-terminal reclustering (default = 0.7)
     41  			-no_nterm_eval disable N-terminal evaluation and reclustering
     42  ';
     43  
     44      my ($help, $keep_x, $keep_i, $keep_tmp, $start_dash, $annotation, $pssm_prefix, $no_nterm_eval);
     45  
```

## `services/bvbrc_lowvan/Viral_Annotation/Other_Scripts/fasta-cluster-pssm.pl:30`

```
     24  			-e cutoff for the number of dashes at the end of a sequence to be seen 
     25  			   before order to throw away a sequence with a gap at the end [d = 3]
     26  			-efo end fraction occupancy, this goes with -e.  This dictates the fraction of dashes in the -e 
     27  			     end columns in order to allow cutting [d = 0.15] (if the fraction is too high, you might 
     28  			     be cutting something that is conserved)
     29  			-fd maximum fraction of dashes allowable for keeping a sequence (d = 0.20)
>>   30  			-mi mmseqs identity [d = 0.8]
>>   31  			-mc mmseqs coverage [d = 0.8]
     32  			-k keep temp fasta (pre-aligned)
     33  			-p "pssm prefix" (default = nothing).
     34  			-tmp name temp fasta file 
     35  ';
     36  
     37  my ($help, $tmp, $keep_x, $keep_i, $keep_tmp, $tmp, $start_dash, $annotation, $pssm_prefix);
     38  
     39  my $end_frac_occ = 0.15;
     40  my $end_dash = 3;
     41  my $min_seqs = 5;
     42  my $f_insert = 0.33;
     43  my $frac_n_term = 0.75;
```

