# BV-BRC invocations of `tRNAscan-SE` (trnascan)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 4 hunk(s) in 2 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/rast_call_tRNAs_trnascan.pl`
- `plbin/run-one-pipeline-step.pl`

## `plbin/rast_call_tRNAs_trnascan.pl:138`

```
    132  close($scan_out);
    133  my $scan_log = File::Temp->new();
    134  close($scan_log);
    135  my $scan_stats = File::Temp->new();
    136  close($scan_stats);
    137  
>>  138  my @cmd = ("tRNAscan-SE", $dflag,
    139  	   "-o", "$scan_out",
    140  	   "-m", "$scan_stats",
    141  	   "-l", "$scan_log",
    142  	   "-Q",
    143  	   "--brief",
    144  	   "$contigs_tmp");
    145  
    146  my $hostname = `hostname`;
    147  chomp $hostname;
    148  
    149  my $event = {
>>  150      tool_name => 'tRNAscan-SE',
    151      execute_time => scalar gettimeofday,
    152      parameters => \@cmd,
    153      hostname => $hostname,
    154  };
    155  my $event_id = $genomeTO->add_analysis_event($event);
    156  
    157  print STDERR "@cmd\n";
    158  $rc = system(@cmd);
    159  print STDERR "==============================\ntRNAscan-SE stats:\n==============================\n";
    160  copy("$scan_stats", \*STDERR);
    161  print STDERR "==============================\ntRNAscan-SE log:\n==============================\n";
    162  copy("$scan_log", \*STDERR);
    163  
    164  if ($rc != 0)
    165  {
>>  166      die "tRNAscan-SE failed with $rc\n";
    167  }
    168  
    169  open(RES, "<", "$scan_out") or die "Cannot open output file $scan_out: $!";
    170  
    171  while (<RES>)
    172  {
    173      chomp;
    174      my($contig, $idx, $beg, $end, $type, $anti, $intro_beg, $intron_end, $cove_score) = split(/\t/);
    175      $contig =~ s/^\s*//;
    176      $contig =~ s/\s*$//;
    177  
    178      $beg += 0;
```

## `plbin/rast_call_tRNAs_trnascan.pl:30`

```
     24  =head1 SYNOPSIS
     25  
     26  rast_call_RNAs [--input genome_file] [--output genome_file] [--url service-url] [< genome-file] [> genome-file]   
     27  
     28  =head1 DESCRIPTION
     29  
>>   30  Find instances of tRNAs in a genome-type object. Uses tRNAscan-SE directly
     31  
     32  Example:
     33  
     34      rast_call_tRNAs < input_genome > output_genome_with_tRNAs_called
     35  
     36  =head1 COMMAND-LINE OPTIONS
     37  
     38  Usage: rast_call_tRNAs  < input_genome_object  > output_genome_object
     39  Usage: rast_call_tRNAs  --input input_genome_object --output output_genome_object
     40  
     41      --input      --- Read input genome-typed object from file instead of STDIN
     42  
```

## `plbin/rast_call_tRNAs_trnascan.pl:192`

```
    186      $genomeTO->add_feature({ -id_client  => $id_client,
    187  						-id_prefix  => $id_prefix,
    188  						-type       => 'rna',
    189  						-location   => [[ $contig, $beg, $strand, $length ]],
    190  						-function   => $func,
    191  						-annotator  => 'search_for_rnas',
>>  192  						-annotation => "Add feature called by tRNAscan-SE with score $cove_score",
    193  						-analysis_event_id => $event_id,
    194  					    }
    195  				   );
    196  }
    197  
    198  $genomeTO->destroy_to_file($out_fh);
    199  close($out_fh);
    200  
    201  __DATA__
```

## `plbin/run-one-pipeline-step.pl:84`

```
     78      'assign_functions_to_CDSs'          => { params => undef, desc => 'Assign functions to CDS features' },
     79      'call_selenoproteins'               => { params => undef, desc => 'Call selenoprotein features' },
     80      'call_pyrrolysoproteins'            => { params => undef, desc => 'Call pyrrolysine protein features' },
     81      'call_features_selenoprotein'       => { params => undef, desc => 'Call selenoprotein features (alias)' },
     82      'call_features_pyrrolysoprotein'    => { params => undef, desc => 'Call pyrrolysine features (alias)' },
     83      'call_features_insertion_sequences' => { params => undef, desc => 'Call insertion sequence features' },
>>   84      'call_features_tRNA_trnascan'       => { params => undef, desc => 'Call tRNA features using tRNAscan-SE' },
     85      'call_RNAs'                         => { params => undef, desc => 'Call all RNA features' },
     86      'call_features_CDS_prodigal'        => { params => undef, desc => 'Call CDS features using Prodigal' },
     87      'call_features_CDS_genemark'        => { params => undef, desc => 'Call CDS features using GeneMarkS' },
     88      'call_features_CDS_phanotate'       => { params => undef, desc => 'Call CDS features using PHANOTATE (phage)' },
     89      'call_features_CDS_FragGeneScan'    => { params => undef, desc => 'Call CDS features using FragGeneScan' },
     90      'call_features_prophage_phispy'     => { params => undef, desc => 'Call prophage features using PhiSpy' },
     91      'call_features_strep_suis_repeat'   => { params => undef, desc => 'Call Streptococcus suis repeat features' },
     92      'call_features_strep_pneumo_repeat' => { params => undef, desc => 'Call Streptococcus pneumoniae repeat features' },
     93      'call_features_crispr'              => { params => undef, desc => 'Call CRISPR features' },
     94      'translate_untranslated_proteins'   => { params => undef, desc => 'Generate protein translations for untranslated CDS' },
     95      'annotate_special_proteins'         => { params => undef, desc => 'Annotate special proteins (AMR, virulence, etc.)' },
     96      'annotate_special_proteins_v2'      => { params => undef, desc => 'Annotate special proteins v2' },
```

