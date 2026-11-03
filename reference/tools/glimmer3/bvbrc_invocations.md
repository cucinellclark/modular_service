# BV-BRC invocations of `glimmer3` (glimmer3)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 6 hunk(s) in 4 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/KBase/GenomeAnnotation/CmdHelper.pm`
- `lib/Bio/KBase/GenomeAnnotation/GenomeAnnotationImpl.pm`
- `lib/Bio/KBase/GenomeAnnotation/Glimmer.pm`
- `plbin/rast-call-features-CDS-glimmer3.pl`

## `lib/Bio/KBase/GenomeAnnotation/CmdHelper.pm:93`

```
     87  	    );
     88  	    
     89  }
     90  
     91  sub options_glimmer3
     92  {
>>   93      return (['min-training-len=i',  'Minimum size of a contig to be used for training glimmer3', { default => 2000 }],
     94  	    );
     95  	    
     96  }
     97  
     98  sub options_rrna_seed
     99  {
    100      return(['call-5S', 'Call 5S RNA features'],
    101  	   ['call-SSU', 'Call SSU RNA features'],
    102  	   ['call-LSU', 'Call LSU RNA features'],
    103  	   );
    104  }
    105  
```

## `lib/Bio/KBase/GenomeAnnotation/GenomeAnnotationImpl.pm:2615`

```
   2609  	
   2610  	unlink($sequences_file);
   2611  	
   2612  	my $trans_table = SeedUtils::genetic_code($genome_in->{genetic_code});
   2613  	
   2614  	my $event = {
>> 2615  	    tool_name => "glimmer3",
   2616  	    execution_time => scalar gettimeofday,
   2617  	    parameters => [ map { join("=", $_, $gparams->{$_}) } sort keys %$gparams ],
   2618  	    hostname => $self->{hostname},
   2619  	};
   2620  	
   2621  	my $idc = IDclient->new($genome_in);
   2622  	
   2623  	my $event_id = $genome_in->add_analysis_event($event);
   2624  	my $type = 'CDS';
   2625  	my $id_type = $self->{cds_id_type};
   2626  	
   2627  	my $id_prefix = $genome_in->{id};
```

## `lib/Bio/KBase/GenomeAnnotation/GenomeAnnotationImpl.pm:2676`

```
   2670  	    
   2671  	    $genome_in->add_feature({
   2672  		-id		     => $id,
   2673  		-type 	     => $type,
   2674  		-location 	     => $loc,
   2675  		-analysis_event_id 	     => $event_id,
>> 2676  		-annotator => 'glimmer3',
   2677  		-protein_translation => $trans,
   2678  	    });
   2679  	}
   2680      }
   2681  				
   2682      $return = $genome_in;
   2683      $return = $return->prepare_for_return();
   2684  
   2685      
   2686      #END call_features_CDS_glimmer3
   2687      my @_bad_returns;
   2688      (ref($return) eq 'HASH') or push(@_bad_returns, "Invalid type for return variable \"return\" (value was \"$return\")");
```

## `lib/Bio/KBase/GenomeAnnotation/Glimmer.pm:206`

```
    200      
    201      
    202      #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    203      #... First GLIMMER pass
    204      #-----------------------------------------------------------------------
    205      print STDERR "Running first GLIMMER pass\n" if $verbose;
>>  206      run($verbose, "glimmer3 $glimmeropts $genetic_code_switch $contigs_file $tmp_model $tmp_prefix.pass_1");
    207      
    208      
    209      
    210      #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    211      #... Extract upstream regions and START codon counts
    212      #-----------------------------------------------------------------------
    213      my $tmp_predictions_pass_1 = "$tmp_prefix.pass_1.predict";
    214      print STDERR "\nExtracting upstream regions and START counts from $tmp_predictions_pass_1\n"
    215  	if $verbose;
    216      
    217      open(PREDICT,  "<$tmp_predictions_pass_1")
    218  	|| die "Could not read-open $tmp_predictions_pass_1";
```

## `lib/Bio/KBase/GenomeAnnotation/Glimmer.pm:324`

```
    318      
    319      #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    320      #... Re-call PEGs using ICM and PWM
    321      #-----------------------------------------------------------------------
    322      print STDERR "Re-calling PEGs using trained ICM\n" if $verbose;
    323      
>>  324      run($verbose, "glimmer3 $glimmeropts $genetic_code_switch -b $tmp_matrix -P $start_freqs $contigs_file $tmp_model $tmp_prefix");
    325      
    326      #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    327      #... Parse and write final predictions
    328      #    NOTE: Does not yet handle '-skip' option
    329      #-----------------------------------------------------------------------
    330      my $tmp_predictions = "$tmp_prefix.predict";
    331      print STDERR "\nParsing $tmp_predictions\n"
    332  	if $verbose;
    333      
    334      open(PREDICT,  "<$tmp_predictions")
    335  	|| die "Could not read-open $tmp_predictions";
    336      
```

## `plbin/rast-call-features-CDS-glimmer3.pl:26`

```
     20  rast-call-features-CDS-glimmer3 [-io] [long options...] < input > output
     21  	-i --input              file from which the input is to be read
     22  	-o --output             file to which the output is to be written
     23  	--help                  print usage message and exit
     24  	--url                   URL for the genome annotation service
     25  	--min-training-len      Minimum size of a contig to be used for
>>   26  	                        training glimmer3
     27  =cut
     28  
     29  my @options = (options_common(), options_glimmer3());
     30  
     31  
     32  my($opt, $usage) = describe_options("rast-call-features-CDS-glimmer3 %o < input > output",
     33  				    @options);
     34  
     35  print($usage->text), exit if $opt->help;
     36  
     37  my $genome_in = load_input($opt);
     38  
```

