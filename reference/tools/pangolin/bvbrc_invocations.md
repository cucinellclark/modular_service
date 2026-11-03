# BV-BRC invocations of `pangolin` (pangolin)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 4 hunk(s) in 2 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/SARS2Assembly/report.tt`
- `plbin/sars2-compute-variation.pl`

## `plbin/sars2-compute-variation.pl:55`

```
     49  }
     50  
     51  unlink($contigs);
     52  
     53  $genome_in->destroy_to_file($opt->output, { canonical => 1 });
     54  
>>   55  sub pangolin
     56  {
     57      my($gto, $contigs_file) = @_;
     58  
     59      my $out = File::Temp->new();
     60      close($out);
     61      my $threads = $ENV{P3_ALLOCATED_CPU} // 1;
>>   62      my @cmd = ("pangolin", "--outfile", $out, "--threads", $threads, $contigs_file);
     63      my $ok = run(\@cmd);
     64      if (!$ok)
     65      {
     66  	warn "Pangolin run failed with $?\n";
     67  	return;
     68      }
     69  
     70      my $lin_fh;
     71      if (!open($lin_fh, "<", $out))
     72      {
>>   73  	warn "Cannot open pangolin lineage output $out: $!";
     74  	return;
     75      }
     76  
     77      my $res = csv(in => $lin_fh, headers => 'auto');
     78      if (@$res == 0)
     79      {
     80  	warn "Could not read headers from $out\n";
     81  	return;
     82      }
     83  
     84      my $lin = $res->[0];
     85  
     86      #
>>   87      # look up pangolin version
     88      #
     89      my $p_vers;
     90      if (!$lin->{pangolin_version})
     91      {
>>   92  	my $ok = run(["pangolin", "-v"], ">", \$p_vers);
     93  	if ($ok)
     94  	{
     95  	    chomp $p_vers;
     96  	    $p_vers =~ s/^pang\S+\s+//;
     97  	}
     98      }
     99  
    100      my $tool_md = {};
    101      for my $vkey (grep { /version/ } keys %$lin)
    102      {
    103  	$tool_md->{$vkey} = $lin->{$vkey};
    104      }
    105  
    106      my $var = {
>>  107  	tool => 'pangolin',
    108  	tool_output => $lin,
    109  	tool_metadata => $tool_md,
    110  	variants => [],
    111  	lineage => $lin->{lineage},
    112  	probability => $lin->{probability},
    113  	conflict => $lin->{conflict},
    114  	status => $lin->{status},
    115  	notes => $lin->{note},
    116      };
    117  
    118      push(@{$gto->{computed_variants}}, $var);
    119  }
```

## `lib/Bio/P3/SARS2Assembly/report.tt:141`

```
    135  <body id="patric-homepage">
    136  
    137  
    138  <h1>SARS2 Analysis Report for [% gto.scientific_name %]</h1>
    139  
    140  [% FOREACH vset IN gto.computed_variants -%]
>>  141  [% IF vset.tool == "pangolin" -%]
    142  <h2>Pangolin Lineage</h2><p>
    143  We analyzed this genome with Pangolin version [% vset.tool_metadata.pangolin_version %].
    144  [% IF vset.linage == "None" -%]
    145  No lineage was able to be computed.
    146  [% ELSE -%]
    147  Pangolin determined the
    148  lineage for this assembly to be <em><b>[% vset.lineage %]</b></em>
    149  [% IF  vset.probability.defined -%]
    150  with a probability of [% vset.probability %].
    151  [% ELSIF  vset.conflict.defined -%]
    152  with a conflict of [% vset.conflict %].
    153  [% END -%]
```

## `lib/Bio/P3/SARS2Assembly/report.tt:171`

```
    165  [% END -%]
    166  Version information:<br>
    167  [% FOR k IN vset.tool_metadata.keys.sort  %]
    168  [% k %]: [% vset.tool_metadata.$k %]<br> 
    169  [% END -%]
    170  <p>You can read more about the Pangolin output data at 
>>  171  <a href="https://cov-lineages.org/resources/pangolin/output.html">the pangolin documentation site</a>.
    172  [% END -%]
    173  [% END -%]
    174  
    175  [% FOREACH vset IN gto.computed_variants -%]
    176  [% IF vset.tool == "assembly pipeline" -%]
    177  <h2>Protein SNPs from assembly</h2><p>
    178  
    179  <table border=1>
    180  <tr><th>Gene</th><th>SNPs</th></tr>
    181  [% FOREACH var IN vset.variants -%]
    182  [% IF var.gene == "S"  && var.snps.size() > 0 -%]
    183  <tr><td>[% var.gene %]</td>
```

## `lib/Bio/P3/SARS2Assembly/report.tt:310`

```
    304  [% END -%]
    305  [% END -%]
    306  </table>
    307  [% END -%]
    308  
    309  [% FOREACH vset IN gto.computed_variants -%]
>>  310  [% IF vset.tool == "pangolin" -%]
    311  <h2>All Pangolin output data</h2>
    312  [% FOR k IN vset.tool_output.keys.sort -%]
    313  [% k %]: [% vset.tool_output.$k %]<br> 
    314  [% END -%]
    315  [% END -%]
    316  [% END -%]
    317  
    318  </body>
    319  </html>
```

