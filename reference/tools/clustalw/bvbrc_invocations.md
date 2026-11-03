# BV-BRC invocations of `clustalw` (clustalw)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 16 hunk(s) in 7 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/alignment.pm`
- `lib/clustaltree.pm`
- `lib/gjoalignment.pm`
- `lib/rota-a-genotyper/VIGOR3/prod3/VIGOR3.pm`
- `lib/rota-a-genotyper/VIGOR3/prod3/dbutils/findClusters.pl`
- `plbin/p3x-annotate-mat-peptide.pl`
- `plbin/snp_analysis.pl`

## `lib/gjoalignment.pm:1425`

```
   1419      gjoseqlib::write_fasta( $inFH, [ [ "s1", "", $s1 ], [ "s2", "", $s2 ] ] );
   1420  
   1421      close( $inFH );
   1422      close( $outFH );
   1423      close( $dndFH );
   1424  
>> 1425      my $clustalw = SeedAware::executable_for( 'clustalw' )
>> 1426          or print STDERR "Could not locate executable file for 'clustalw'.\n"
   1427              and return undef;
   1428  
   1429      my @params = ( "-infile=$infile",
   1430                     "-outfile=$outfile",
   1431                     "-newtree=$dndfile",
   1432                     '-maxdiv=0',
   1433                     '-align'
   1434                   );
   1435      my $redirects = { stdout => '/dev/null' };
   1436      SeedAware::system_with_redirect( $clustalw, @params, $redirects );
   1437  
   1438      ( $s1, $s2 ) = map { $_->[2] } gjoseqlib::read_clustal_file( $outfile );  # just seqs
```

## `lib/rota-a-genotyper/VIGOR3/prod3/VIGOR3.pm:7868`

```
   7862        || die "Could not write to the tmp_align_fasta file\.\n";
   7863      print TMP ">$pepid\n$tmppepseq\n>$refid\n$refseq\n";
   7864  
   7865  #if ( getlogin() eq "jhoover" ) { print ">$tmppepid\n$tmppepseq\n>$tmprefid\n$refseq\n" }
   7866      close TMP;
   7867  
>> 7868      my $cmd = "$myBin/clustalw -align -GAPOPEN=6.0 -GAPEXT=0.3 -infile=$vigorspace/tmp_align_fasta > $vigorspace/tmp_align_fasta.log 2>&1";
   7869  
   7870  #"muscle -in $vigorspace/tmp_align_fasta -out $vigorspace/tmp_align_fasta.aln -clwstrict &> $vigorspace/tmp_align_fasta.log";
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
```

## `lib/alignment.pm:1322`

```
   1316      $s1 = $seq1->[2];
   1317      $s1 =~ s/[^A-Za-z]+//g;
   1318      $s2 = $seq2->[2];
   1319      $s2 =~ s/[^A-Za-z]+//g;
   1320      gjoseqlib::write_fasta( $infile, [ [ "s1", "", $s1 ], [ "s2", "", $s2 ] ] );
   1321  
>> 1322      my $clustalw = SeedTkRun::executable_for( 'clustalw' )
>> 1323          or print STDERR "Could not locate executable file for 'clustalw'.\n"
   1324              and return undef;
   1325  
   1326      my @params = ( "-infile=$infile",
   1327                     "-outfile=$outfile",
   1328                     "-newtree=$dndfile",
   1329                     '-maxdiv=0',
   1330                     '-align'
   1331                   );
   1332      SeedTkRun::run_redirected( $clustalw, @params );
   1333  
   1334      ( $s1, $s2 ) = map { $_->[2] } gjoseqlib::read_clustal_file( $outfile );  # just seqs
   1335  
```

## `lib/gjoalignment.pm:637`

```
    631      gjoseqlib::write_fasta( $seqFH, \@seqs2 );
    632  
    633      close( $seqFH );
    634      close( $outFH );
    635      close( $dndFH );
    636  
>>  637      my $clustalw = SeedAware::executable_for( $opts->{ clustalw } || $opts->{ program } || 'clustalw' )
>>  638          or print STDERR "Could not locate executable file for 'clustalw'.\n"
    639              and return undef;
    640  
    641      my @params = ( "-infile=$seqfile",
    642                     "-outfile=$outfile",
    643                     "-newtree=$dndfile",
    644                     '-outorder=aligned',
    645                     '-maxdiv=0',
    646                     '-align'
    647                   );
    648      my $redirects = { stdout => '/dev/null' };
    649      SeedAware::system_with_redirect( $clustalw, @params, $redirects );
    650  
```

## `lib/gjoalignment.pm:772`

```
    766      #
    767      #  I would have thought that the profile tree file should be -newtree1, but
    768      #  that fails.  -newtree works fine at putting the file where we want it.
    769      #  Perhaps it would have made more sense to do a cd to the desired directory
    770      #  first.
    771      #
>>  772      my $clustalw = SeedAware::executable_for( 'clustalw' )
>>  773          or print STDERR "Could not locate executable file for 'clustalw'.\n"
    774              and return undef;
    775  
    776      my @params = ( "-profile1=$profile",
    777                     "-profile2=$seqfile",
    778                     "-outfile=$outfile",
    779                     "-newtree=$dndfile",
    780                     '-outorder=input',
    781                     '-maxdiv=0',
    782                     '-profile'
    783                   );
    784      my $redirects = { stdout => '/dev/null' };
    785      SeedAware::system_with_redirect( $clustalw, @params, $redirects );
```

## `lib/gjoalignment.pm:1338`

```
   1332      gjoseqlib::write_fasta( $seqFH, $seqs2 );
   1333  
   1334      close( $proFH );
   1335      close( $seqFH );
   1336      close( $outFH );
   1337  
>> 1338      my $clustalw = SeedAware::executable_for( 'clustalw' )
>> 1339          or print STDERR "Could not locate executable file for 'clustalw'.\n"
   1340              and return undef;
   1341  
   1342      my @params = ( "-profile1=$profile",
   1343                     "-profile2=$seqfile",
   1344                     "-outfile=$outfile",
   1345                     "-newtree=$dndfile",
   1346                     '-outorder=input',
   1347                     '-maxdiv=0',
   1348                     '-profile'
   1349                   );
   1350      my $redirects = { stdout => '/dev/null' };
   1351      SeedAware::system_with_redirect( $clustalw, @params, $redirects );
   1352  
>> 1353      #  2010-09-08: clustalw profile align can have columns of all gaps; so pack it
   1354  
   1355      my @aligned = gjoseqlib::pack_alignment( gjoseqlib::read_clustal_file( $outfile ) );
   1356  
   1357      unlink( $dndfile );   #  The others go away on their own
   1358  
   1359      wantarray ? @aligned : \@aligned;
   1360  }
   1361  
   1362  
   1363  #-------------------------------------------------------------------------------
   1364  #
   1365  #  remove dangling ends from $id
```

## `lib/rota-a-genotyper/VIGOR3/prod3/dbutils/findClusters.pl:88`

```
     82  print "working directory: $workdir\n";
     83  
     84  # use cd-hit to reduce redundancy ( 95% identity 95 %coverage)
     85  my $cmd = "$myBin/cd-hit -i $infasta -o $workdir/nr -aL $coverage -aS $coverage -G 0 -c $similarity -g 1 -B 1 -t 5 2>&1 | tee $workdir/cluster.log";
     86  print "clustering: $cmd\n";
     87  runCmd('.', $cmd);
>>   88  print "flushing clustalw buffers...\n";
     89  sleep 60;    # give cd-hit time to flush buffers to disk
     90  
     91  # find clusters
     92  print "loading cluster definitions\n";
     93  my %multiclusters;
     94  open( CL, "<$workdir/nr.clstr" ) || die "\nCannot read cluster deflines\n";
     95  my $cluster_id = 0;
     96  my %clusters;
     97  while ( my $member = <CL> ) {
     98      chomp $member;
     99      if ( $member =~ /^>Cluster (.*)$/ ) {        
    100          $cluster_id = $1;
```

## `lib/alignment.pm:545`

```
    539      my $seqfile = SeedTkRun::tmp_file_name( "align_fasta",  'fasta', $tmpdir );
    540      my $outfile = SeedTkRun::tmp_file_name( "align_fasta",  'aln',   $tmpdir );
    541      my $dndfile = SeedTkRun::tmp_file_name( "align_fasta",  'dnd',   $tmpdir );
    542  
    543      gjoseqlib::write_fasta( $seqfile, \@seqs2 );
    544  
>>  545      my $clustalw = SeedTkRun::executable_for( $opts->{ clustalw } || $opts->{ program } || 'clustalw' )
>>  546          or print STDERR "Could not locate executable file for 'clustalw'.\n"
    547              and return undef;
    548  
    549      my @params = ( "-infile=$seqfile",
    550                     "-outfile=$outfile",
    551                     "-newtree=$dndfile",
    552                     '-outorder=aligned',
    553                     '-maxdiv=0',
    554                     '-align'
    555                   );
    556      SeedTkRun::run_redirected( $clustalw, @params);
    557  
    558      my @aligned = gjoseqlib::read_clustal_file( $outfile );
```

## `lib/alignment.pm:673`

```
    667      #
    668      #  I would have thought that the profile tree file should be -newtree1, but
    669      #  that fails.  -newtree works fine at putting the file where we want it.
    670      #  Perhaps it would have made more sense to do a cd to the desired directory
    671      #  first.
    672      #
>>  673      my $clustalw = SeedTkRun::executable_for( 'clustalw' )
>>  674          or print STDERR "Could not locate executable file for 'clustalw'.\n"
    675              and return undef;
    676  
    677      my @params = ( "-profile1=$profile",
    678                     "-profile2=$seqfile",
    679                     "-outfile=$outfile",
    680                     "-newtree=$dndfile",
    681                     '-outorder=input',
    682                     '-maxdiv=0',
    683                     '-profile'
    684                   );
    685      SeedTkRun::run_redirected( $clustalw, @params );
    686  
```

## `lib/alignment.pm:1240`

```
   1234      ( my $dndfile = $profile ) =~ s/fasta$/dnd/;  # The program ignores our name
   1235  
   1236      $seqs2 = [ $seqs2 ] if ! ( ref $seqs2->[0] );
   1237      gjoseqlib::write_fasta( $profile, $seqs1 );
   1238      gjoseqlib::write_fasta( $seqfile, $seqs2 );
   1239  
>> 1240      my $clustalw = SeedTkRun::executable_for( 'clustalw' )
>> 1241          or print STDERR "Could not locate executable file for 'clustalw'.\n"
   1242              and return undef;
   1243  
   1244      my @params = ( "-profile1=$profile",
   1245                     "-profile2=$seqfile",
   1246                     "-outfile=$outfile",
   1247                     "-newtree=$dndfile",
   1248                     '-outorder=input',
   1249                     '-maxdiv=0',
   1250                     '-profile'
   1251                   );
   1252      SeedTkRun::run_redirected( $clustalw, @params );
   1253  
>> 1254      #  2010-09-08: clustalw profile align can columns of all gaps; so pack it
   1255  
   1256      my @aligned = gjoseqlib::pack_alignment( gjoseqlib::read_clustal_file( $outfile ) );
   1257  
   1258      unlink( $profile, $seqfile, $outfile, $dndfile );
   1259  
   1260      wantarray ? @aligned : \@aligned;
   1261  }
   1262  
   1263  
   1264  =pod
   1265  
   1266    remove dangling ends from $id
```

## `lib/clustaltree.pm:89`

```
     83      open( SEQ, ">$seqfile" ) || return undef;
     84      foreach ( @seqs2 ) { print SEQ ">$_->[0]\n$_->[2]\n" }
     85      close SEQ;
     86  
     87      #  Do the tree:
     88  
>>   89      my $clustalw = $ext_bin ? "$ext_bin/clustalw" : 'clustalw';
     90      &run( "$clustalw -infile='$seqfile' -newtree='$treefile' -tree > /dev/null" );
     91  
     92      my $tree = &gjonewicklib::read_newick_tree( $treefile );
     93      $tree || return undef;
     94  
     95      #  Clean up:
     96  
     97      unlink( $seqfile, $treefile );
     98  
     99      #  Restore the ids:
    100  
    101      &gjonewicklib::newick_relabel_tips( $tree, \%ori_id );
```

## `plbin/p3x-annotate-mat-peptide.pl:37`

```
     31  
     32  my $tempdir = File::Temp->newdir(CLEANUP => ($opt->debug ? 0 : 1));
     33  
     34  print STDERR "Tempdir=$tempdir\n" if $opt->debug;
     35  
     36  #
>>   37  # Ugh. Need to set up a bindir with clustalw pointing at clustalw2.
     38  #
     39  mkdir("$tempdir/bin") or die "mkdir $tempdir/bin failed: $!";
     40  my @p = searchpath("clustalw2");
     41  if (@p)
     42  {
>>   43      symlink($p[0], "$tempdir/bin/clustalw");
     44  }
     45  
     46  $ENV{PATH} = "$tempdir/bin:$ENV{PATH}";
     47  
     48  #
     49  # We copy our input gto to disk if it arrived from
     50  # stdin since we need to both write a genbank from it
     51  # as well as load it to add features later.
     52  #
     53  
     54  my $input_gto;
     55  if ($opt->input)
```

## `plbin/snp_analysis.pl:29`

```
     23  	-a aa seq only
     24  	-x snp only
     25  	-t subtype
     26  	-o host
     27  	-g segment
     28  	-m protein (eg. PB1)
>>   29  	-c run clustalw for na sequence alignment
     30  	-h help
     31  	-d debug flag
     32  	-z min size
     33  	-e reverse
     34  	-f flu sequence
     35  ";
     36  
     37  if($opt_h) { die $usage; }
     38  
     39  print "\t\tSTART: " . localtime(time) . "\n";
     40  
     41  my $pwd = cwd();
```

## `lib/alignment.pm:498`

```
    492      return wantarray ? ( \@ali, $treestr ) : \@ali;
    493  }
    494  
    495  
    496  =pod
    497  
>>  498    Align sequence with clustalw and return the alignment
    499  
    500      @align = align_with_clustal(  @sequences )
    501      @align = align_with_clustal( \@sequences )
    502      @align = align_with_clustal( \@sequences, \%opts )
    503     \@align = align_with_clustal(  @sequences )
    504     \@align = align_with_clustal( \@sequences )
    505     \@align = align_with_clustal( \@sequences, \%opts )
    506  
    507  =cut
    508  sub align_with_clustal
    509  {
    510      return wantarray ? [] : () if ! @_;        #  No input
```

## `lib/clustaltree.pm:53`

```
     47  our @EXPORT = qw(
     48          tree_with_clustal
     49          );
     50  
     51  
     52  #===============================================================================
>>   53  #  Tree sequence with clustalw and return the tree.  Tree is gjonewick format.
     54  #
     55  #    $tree = tree_with_clustal(  @alignment )
     56  #    $tree = tree_with_clustal( \@alignment )
     57  #
     58  #  Currently very pedantic:
     59  #     $tree is gjonewick format.
     60  #     @alignment is composed of triples: ( $id, $definition, $sequence )
     61  #===============================================================================
     62  sub tree_with_clustal
     63  {
     64      @_ and ref( $_[0] ) eq 'ARRAY' or return undef;
     65      my @seqs = ref( $_[0]->[0] ) eq 'ARRAY' ? @{ $_[0] } : @_;
```

## `lib/gjoalignment.pm:586`

```
    580  
    581      return wantarray ? ( \@ali, $treestr ) : \@ali;
    582  }
    583  
    584  
    585  #===============================================================================
>>  586  #  Align sequence with clustalw and return the alignment
    587  #
    588  #    @align = align_with_clustal(  @sequences )
    589  #    @align = align_with_clustal( \@sequences )
    590  #    @align = align_with_clustal( \@sequences, \%opts )
    591  #   \@align = align_with_clustal(  @sequences )
    592  #   \@align = align_with_clustal( \@sequences )
    593  #   \@align = align_with_clustal( \@sequences, \%opts )
    594  #
    595  #===============================================================================
    596  sub align_with_clustal
    597  {
    598      return wantarray ? [] : () if ! @_;        #  No input
```

