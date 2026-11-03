# BV-BRC invocations of `blastn` (blastn)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 117 hunk(s) in 35 file(s); showing top 25.
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bin/Blast.pm`
- `lib/Bio/KBase/HomologyService/Util.pm`
- `lib/Bio/P3/HomologySearch/HomologySearch.pm`
- `lib/BlastInterface.pm`
- `lib/BlastUtils.pm`
- `lib/VASTR/MLST/LocalMLST.pm`
- `lib/alignment.pm`
- `lib/find_homologs.pm`
- `lib/find_special_proteins.pm`
- `lib/gjoalignandtree.pm`
- `lib/gjoalignment.pm`
- `lib/representative_sequences.pm`
- `lib/rota-a-genotyper/VIGOR3/prod3/VIGOR3.pl`
- `lib/rota-a-genotyper/VIGOR3/prod3/VIGOR3.pm`
- `lib/rota-a-genotyper/VIGOR3/prod3/rna_finder.pl`
- `lib/rota-a-genotyper/VIGOR3/prod3/tblUTR.pl`
- `plbin/annotate_by_viral_pssm.pl`
- `plbin/assign_st_to_genome.pl`
- `plbin/blast_against_genomes.pl`
- `plbin/build_blast_dbs.pl`
- `plbin/get_splice_variant_features.pl`
- `plbin/get_transcript_edited_features.pl`
- `plbin/hs-p3-update-blast-databases.pl`
- `plbin/p3-blast.pl`
- `plbin/p3-make-genome-list-blast-database.pl`
- `plbin/p3-submit-BLAST.pl`
- `plbin/p3x-create-blast-db.pl`
- `plbin/p3x-update-blast-dbs.pl`
- `plbin/sars2-compute-variation.pl`
- `plbin/sars2-get-blast-variants.pl`
- `plbin/svr_big_repeats.pl`
- `plbin/update_local_mlstdb.pl`
- `services/bvbrc_lowvan/Viral_Annotation/annotate_by_viral_pssm.pl`
- `services/bvbrc_lowvan/Viral_Annotation/get_splice_variant_features.pl`
- `services/bvbrc_lowvan/Viral_Annotation/get_transcript_edited_features.pl`

## `plbin/blast_against_genomes.pl:8`

```
      2  use Data::Dumper;
      3  use strict;
      4  use File::Slurp;
      5  use Getopt::Long::Descriptive;
      6  
      7  my($opt, $usage) = describe_options("%c %o genome-id [genome-id...] [< input]",
>>    8  				    ["program|p=s", "blast program (blastp / blastn / blastx / tblastx / tblastn)", { default => 'blastp' }],
      9  				    ["contigs", "blast against contigs, not features"],
     10  				    ["evalue|e=s", "evalue cutoff"],
     11  				    ["max-hits|n=s", "max hits"],
     12  				    ["coverage=s", "coverage"],
     13  				    ["url|u=s", "URL to homology service"],
     14  				    ["input|i=s", "Input file (if not specified, use stdin)"],
     15  				    ["help|h", "Show this help message"]);
     16  print($usage->text), exit 0 if $opt->help;
     17  die($usage->text) if @ARGV == 0;
     18  
     19  my @genomes = @ARGV;
     20  
```

## `plbin/p3-blast.pl:98`

```
     92  
     93  =back
     94  
     95  =cut
     96  
     97  # map each blast tool name to the type of blast database required
>>   98  use constant BLAST_TOOL => { blastp => 'prot', blastn => 'dna', blastx => 'prot', tblastn => 'dna' };
     99  
    100  $| = 1;
    101  # Get the command-line parameters.
    102  my $opt = P3Utils::script_opts('type blastdb',
    103          P3Utils::ih_options(),
    104          ['output' => hidden => { one_of => [ [ 'hsp' => 'produce HSP output'], ['sim' => 'produce similarity output'], ['tbl' => 'produce table output']]}],
    105          ['maxE|e=f', 'maximum e-value', { default => 1e-10 }],
    106          ['maxHSP|b', 'if specified, the maximum number of returned results (before filtering)'],
    107          ['minScr=f', 'if specified, the minimum permissible bit score'],
    108          ['percIdentity=f', 'if specified, the minimum permissible percent identity'],
    109          ['minLen|l=i', 'if specified, the minimum permissible match lengt (for filtering)'],
    110          ['best', 'only output best match for each query sequence']
```

## `plbin/p3-make-genome-list-blast-database.pl:83`

```
     77  
     78      my $tmp = $api->retrieve_protein_features_in_genomes_to_temp($genome_ids);
     79      my @params = ("-dbtype" => "prot",
     80  		  "-in", "$tmp",
     81  		  "-out", $db_file);
     82  
>>   83      my $rc = system("makeblastdb", @params);
     84      if ($rc != 0)
     85      {
>>   86  	die "makeblastdb @params failed with rc=$rc\n";
     87      }
     88  }
     89  
     90  sub build_dna_db
     91  {
     92      my($genome_ids, $db_file) = @_;
     93  
     94      my $tmp = $api->retrieve_dna_features_in_genomes_to_temp($genome_ids);
     95      my @params = ("-dbtype" => "nucl",
     96  		  "-in", "$tmp",
     97  		  "-out", $db_file);
     98  
>>   99      my $rc = system("makeblastdb", @params);
    100      if ($rc != 0)
    101      {
>>  102  	die "makeblastdb @params failed with rc=$rc\n";
    103      }
    104  }
    105  
    106  sub build_rna_db
    107  {
    108      my($genome_ids, $db_file) = @_;
    109  
    110      my $tmp = $api->retrieve_rna_features_in_genomes_to_temp($genome_ids);
    111      system("cat $tmp");
    112      my @params = ("-dbtype" => "nucl",
    113  		  "-in", "$tmp",
    114  		  "-out", $db_file);
    115  
>>  116      my $rc = system("makeblastdb", @params);
    117      if ($rc != 0)
    118      {
>>  119  	die "makeblastdb @params failed with rc=$rc\n";
    120      }
    121  }
    122  
    123  sub build_contig_db
    124  {
    125      my($genome_ids, $db_file) = @_;
    126  
    127      my $tmp = $api->retrieve_contigs_in_genomes_to_temp($genome_ids);
    128      my @params = ("-dbtype" => "nucl",
    129  		  "-in", "$tmp",
    130  		  "-out", $db_file);
    131  
>>  132      my $rc = system("makeblastdb", @params);
    133      if ($rc != 0)
    134      {
>>  135  	die "makeblastdb @params failed with rc=$rc\n";
    136      }
    137  }
    138  
```

## `lib/Bio/P3/HomologySearch/HomologySearch.pm:225`

```
    219  #
    220  # $search_type_map{input-type}->{db-type} = valid-blast-programs
    221  #
    222  our %search_type_map =
    223      (aa => {
    224  	faa => ['blastp'],
>>  225  	ffn => ['tblastn'],
>>  226  	frn => ['tblastn'],
>>  227  	fna => ['tblastn'],
    228      },
    229       dna => {
>>  230  	 faa => ['blastx'],
>>  231  	 ffn => ['blastn', 'tblastx'],
>>  232  	 frn => ['blastn', 'tblastx'],
>>  233  	 fna => ['blastn', 'tblastx'],
    234       });
    235  				    
    236  our %makeblastdb_dbtype = (faa => "prot",
    237  			   ffn => "nucl",
    238  			   frn => "nucl",
    239  			   fna => "nucl");
    240  
    241  sub new
    242  {
    243      my($class) = @_;
    244  
    245      my $api = P3DataAPI->new(data_api_url);
```

## `lib/BlastInterface.pm:2866`

```
   2860  #-------------------------------------------------------------------------------
   2861  sub form_blast_command
   2862  {
   2863      my( $queryF, $dbF, $blast_prog, $opts ) = @_;
   2864      $opts ||= {};
   2865  
>> 2866      #  There are different ways for psiblast and tblastn to get a query, so
   2867      ( $queryF || ( $blast_prog eq 'psiblast' && ( $opts->{in_pssm} || $opts->{in_msa} ) )
>> 2868                || ( $blast_prog eq 'tblastn'  &&   $opts->{in_pssm} )
   2869          )
   2870          or return wantarray ? () : [];
   2871  
   2872      $dbF or return wantarray ? () : [];
   2873  
>> 2874      my %prog_ok = map { $_ => 1 } qw( blastn blastp blastx tblastn tblastx psiblast rpsblast rpstblastn );
   2875      $blast_prog && $prog_ok{ $blast_prog }
   2876          or return wantarray ? () : [];
   2877  
   2878      #  Find an executable to perform the requested function:
   2879  
   2880      my $blastall;
   2881      my $blastplus;
>> 2882      my %all_ok  = map { $_ => 1 } qw( blastn blastp blastx tblastn tblastx );
   2883      my $try_all = $opts->{ blastall } && $all_ok{ $blast_prog };
   2884  
   2885      #  If the user asks for it, look for blastall.
   2886      if    ( $try_all && ( $blastall = SeedAware::executable_for( 'blastall' ) ) ) {}
   2887  
   2888      #  If blastall was not explicitly requested, or we cannot find it, try the
   2889      #  blast+ program.
   2890      elsif ( $blastplus = SeedAware::executable_for( $blast_prog ) ) {}
   2891  
   2892      #  If we could not find the blast+ program, and we did not try for blastall,
   2893      #  try looking for it now.
   2894      elsif ( ( ! $try_all ) && $all_ok{ $blast_prog } && ( $blastall = SeedAware::executable_for( 'blastall' ) ) ) {}
```

## `lib/BlastInterface.pm:2983`

```
   2977          push @cmd, -b => $maxHSP                  if $maxHSP;
   2978          push @cmd, -z => $dbLen                   if $dbLen;
   2979          push @cmd, -Y => $searchSp                if $searchSp;
   2980  
   2981          push @cmd, -W => $wordSz                  if $wordSz;
   2982          push @cmd, -M => $matrix                  if $matrix;
>> 2983          push @cmd, -r => $nucIdenScr ||  1        if $blast_prog eq 'blastn';
>> 2984          push @cmd, -q => $nucMisScr  || -1        if $blast_prog eq 'blastn';
   2985          push @cmd, -G => $gapOpen                 if $gapOpen;
   2986          push @cmd, -E => $gapExtend               if $gapExtend;
   2987          push @cmd, -f => $threshold               if $threshold;
   2988          push @cmd, -X => $xDropGap                if $xDropGap;
   2989          push @cmd, -y => $xDropUngap              if $xDropUngap;
   2990          push @cmd, -Z => $xDropFinal              if $xDropFinal;
   2991          push @cmd, -s => $useSwTback ? 'T' : 'F'  if defined $useSwTback;
   2992          push @cmd, -g => $ungapped   ? 'T' : 'F'  if defined $ungapped;
   2993          push @cmd, -t => $maxIntronLength         if $maxIntronLength;
   2994  
   2995          push @cmd, -I => $showGIs    ? 'T' : 'F'  if defined $showGIs;
   2996  
   2997          #  blastall does not have a percent identity option, so we must set the
   2998          #  filter.
   2999  
>> 3000          $opts->{minIden} ||= 0.01 * $percentIdentity if $blast_prog eq 'blastn';
   3001      }
   3002  
   3003      #  We are using a blast+ program
   3004      else
   3005      {
   3006          if ( defined $lcFilter )
   3007          {
>> 3008              my %seg_prog = map { $_ => 1 } qw( blastp blastx tblastn );
   3009              $seg  = $lcFilter ? 'yes' : 'no' if ! defined $seg  && $seg_prog{ $blast_prog };
>> 3010              $dust = $lcFilter ? 'yes' : 'no' if ! defined $dust && $blast_prog eq 'blastn';
   3011          }
   3012  
   3013          my $alignF;
   3014          if ( $blast_prog eq 'psiblast' )
   3015          {
   3016              $alignF   = valid_fasta( $inMSA, $opts ) if defined $inMSA;
   3017              $alignF ||= $queryF if ! defined $inPSSM ;
   3018  
   3019              # queryIndex is 1-based
   3020              if ( ! $queryIndex && ! defined $inPSSM )
   3021              {
   3022                  my @align = gjoseqlib::read_fasta( $alignF );
```

## `lib/BlastInterface.pm:3065`

```
   3059          push @cmd, -searchsp            => $searchSp          if $searchSp;
   3060          push @cmd, -best_hit_overhang   => $bestHitOverhang   if $bestHitOverhang;
   3061          push @cmd, -best_hit_score_edge => $bestHitScoreEdge  if $bestHitScoreEdge;
   3062  
   3063          push @cmd, -word_size           => $wordSz            if $wordSz;
   3064          push @cmd, -matrix              => $matrix            if $matrix;
>> 3065          push @cmd, -reward              => $nucIdenScr ||  1  if $blast_prog eq 'blastn';
>> 3066          push @cmd, -penalty             => $nucMisScr  || -1  if $blast_prog eq 'blastn';
   3067          push @cmd, -gapopen             => $gapOpen           if $gapOpen;
   3068          push @cmd, -gapextend           => $gapExtend         if $gapExtend;
   3069          push @cmd, -threshold           => $threshold         if $threshold;
   3070          push @cmd, -xdrop_gap           => $xDropGap          if $xDropGap;
   3071          push @cmd, -xdrop_ungap         => $xDropUngap        if $xDropUngap;
   3072          push @cmd, -xdrop_final         => $xDropFinal        if $xDropFinal;
   3073          push @cmd, -use_sw_tback        => ()                 if $useSwTback;
   3074          push @cmd, -ungapped            => ()                 if $ungapped;
   3075          push @cmd, -max_intron_length   => $maxIntronLength   if $maxIntronLength;
   3076  
   3077          push @cmd, -show_gis            => ()                 if $showGIs;
   3078  
```

## `lib/BlastUtils.pm:1987`

```
   1981      push @cmd, '-searchsp'          => $searchSp          if $searchSp;
   1982      push @cmd, -best_hit_overhang   => $bestHitOverhang   if $bestHitOverhang;
   1983      push @cmd, -best_hit_score_edge => $bestHitScoreEdge  if $bestHitScoreEdge;
   1984  
   1985      push @cmd, -word_size           => $wordSz            if $wordSz;
   1986      push @cmd, -matrix              => $matrix            if $matrix;
>> 1987      push @cmd, -reward              => $nucIdenScr ||  1  if $blast_prog eq 'blastn';
>> 1988      push @cmd, -penalty             => $nucMisScr  || -1  if $blast_prog eq 'blastn';
   1989      push @cmd, -gapopen             => $gapOpen           if $gapOpen;
   1990      push @cmd, -gapextend           => $gapExtend         if $gapExtend;
   1991      push @cmd, -threshold           => $threshold         if $threshold;
   1992      push @cmd, -xdrop_gap           => $xDropGap          if $xDropGap;
   1993      push @cmd, -xdrop_ungap         => $xDropUngap        if $xDropUngap;
   1994      push @cmd, -xdrop_final         => $xDropFinal        if $xDropFinal;
   1995      push @cmd, -use_sw_tback        => ()                 if $useSwTback;
   1996      push @cmd, -ungapped            => ()                 if $ungapped;
   1997      push @cmd, -max_intron_length   => $maxIntronLength   if $maxIntronLength;
   1998      push @cmd, -max_target_seqs		=> $maxHitsPerQuery	  if $maxHitsPerQuery;
   1999  
   2000      push @cmd, '-show_gis'          => ()                 if $showGIs;
```

## `lib/gjoalignment.pm:1572`

```
   1566      my $seqfile   = SeedAware::tmp_file_name( "trim_query",   $tmpdir );
   1567  
   1568      gjoseqlib::write_fasta( $blastfile, scalar gjoseqlib::pack_sequences( $clnali ) );
   1569      gjoseqlib::write_fasta( $seqfile,   scalar gjoseqlib::pack_sequences( $clnseq ) );
   1570  
   1571      $type = gjoseqlib::guess_seq_type( $clnseq->[2] ) if ! $type;
>> 1572      my ( $is_prot, $prog, @opt ) = ( $type =~ m/^n/i ) ? qw( f blastn -r 1 -q -1 )
   1573                                                         : qw( t blastp );
   1574      my $formatdb = SeedAware::executable_for( 'formatdb' )
   1575          or print STDERR "Could not locate executable file for 'formatdb'.\n"
   1576              and return undef;
   1577  
   1578      my $blastall = SeedAware::executable_for( 'blastall' )
   1579          or print STDERR "Could not locate executable file for 'blastall'.\n"
   1580              and return undef;
   1581  
   1582      my @fmt_params = ( '-i', $blastfile, '-p', $is_prot );
   1583      my $fmt_redirects = { stderr => '/dev/null' };
   1584      SeedAware::system_with_redirect( $formatdb, @fmt_params, $fmt_redirects );
```

## `plbin/hs-p3-update-blast-databases.pl:46`

```
     40  my $n = @work;
     41  print "$n items\n";
     42  
     43  pareach \@work, sub {
     44      my($item) = @_;
     45      my($type, $in, $out) = @$item;
>>   46      my @cmd = ("/homes/olson/P3/blast/deployment/services/homology_service/bin/makeblastdb",
     47  	       "-in", $in,
     48  	       "-out", $out,
     49  	       "-dbtype", $type);
     50      print "@cmd\n";
     51      my $rc = system(@cmd);
     52      if ($rc != 0)
     53      {
     54  	die "Error $rc processing $type $in $out: @cmd\n";
     55      }
     56  }, { Max_Workers => $par };
```

## `plbin/sars2-get-blast-variants.pl:96`

```
     90  my $max = scalar @subseqs;
     91  print STDERR "\n BLASTing $max subject sequences\n\n"; 
     92  close IN; 
     93  
     94  
     95  
>>   96  my $ok = run(["makeblastdb", "-dbtype", $dbtype, "-in", $s_file, "-max_file_sz", $dbsize],
     97  	     '>', '/dev/null');
     98     
>>   99  $ok or die "Failure $? running makeblastdb";
    100  
    101  my @cmd = ($program,
    102  	   "-outfmt", "15",
    103  	   "-subject", $s_file,
    104  	   "-max_target_seqs", $max);
    105  
    106  
>>  107  if (($program eq "blastn") || ($program eq "blastx"))
    108  {
    109      push(@cmd, 
    110  	 "-dust", "no",);
    111  }
    112  else
    113  {
    114      push(@cmd,
    115  	 '-seg', 'no');
    116  }
    117  
    118  my($out, $err);
    119  
```

## `lib/Bio/KBase/HomologyService/Util.pm:435`

```
    429  	push(@cmd, "-num_threads", $self->impl->{_blast_threads});
    430      }
    431  
    432      #
    433      # if we have short sequences, use the tasks optimized for that.
    434      #
>>  435      if ($program eq 'blastn' && $is_short)
    436      {
    437  	push(@cmd, "-task", "blastn-short");
    438      }
    439      elsif ($program eq 'blastp' && $is_short)
    440      {
    441  	push(@cmd, "-task", "blastp-short");
    442      }
    443         
    444      return @cmd;
    445  }
    446  
    447  sub blast_fasta_to_taxon
```

## `lib/alignment.pm:1439`

```
   1433      my $seqfile   = SeedTkRun::tmp_file_name( "trim_query",   $tmpdir );
   1434  
   1435      gjoseqlib::write_fasta( $blastfile, scalar gjoseqlib::pack_sequences( $clnali ) );
   1436      gjoseqlib::write_fasta( $seqfile,   scalar gjoseqlib::pack_sequences( $clnseq ) );
   1437  
   1438      $type = guess_seq_type( $clnseq->[2] ) if ! $type;
>> 1439      my ( $is_prot, $prog, @opt ) = ( $type =~ m/^n/i ) ? qw( f blastn -r 1 -q -1 )
   1440                                                         : qw( t blastp );
   1441      my $formatdb = SeedTkRun::executable_for( 'formatdb' )
   1442          or print STDERR "Could not locate executable file for 'formatdb'.\n"
   1443              and return undef;
   1444  
   1445      my $blastall = SeedTkRun::executable_for( 'blastall' )
   1446          or print STDERR "Could not locate executable file for 'blastall'.\n"
   1447              and return undef;
   1448  
   1449      my @fmt_params = ( '-i', $blastfile, '-p', $is_prot );
   1450      SeedTkRun::run_redirected( $formatdb, @fmt_params );
   1451  
```

## `lib/find_special_proteins.pm:167`

```
    161                      and return ();
    162  
    163      #  Search the contigs for the reference sequences:
    164  
    165      my $blastall = $params->{ blastall };
    166      $blastall ||= $ext_bin ? "$ext_bin/blastall" : 'blastall';
>>  167      my $blastcmd = "$blastall -p tblastn -d '$contig_file' -i '$ref_file' "
    168                   . "-e 1e-10 -F f -b 200 -v 200 -a 2 |";
    169      open( BLAST, $blastcmd )
    170          or print STDERR "Could not open pipe '$blastcmd'.\n"
    171             and return ();
    172      my @hsps = gjoparseblast::blast_hsp_list( \*BLAST );
    173      close BLAST;
    174  
    175      #  Delete the temporary directory unless it already existed:
    176  
    177      system "/bin/rm -r $tmp_dir" if ! $save_tmp;
    178  
    179  #
```

## `lib/find_special_proteins.pm:400`

```
    394                      and return ();
    395  
    396      #  Search the contigs for the reference sequences:
    397  
    398      my $blastall = $params->{ blastall };
    399      $blastall ||= $ext_bin ? "$ext_bin/blastall" : 'blastall';
>>  400      my $blastcmd = "$blastall -p tblastn -d '$contig_file' -i '$ref_file' "
    401                   . "-e $expect -F f -b 200 -v 200 -a 2 |";
    402      open( BLAST, $blastcmd )
    403          or print STDERR "Could not open pipe '$blastcmd'.\n"
    404             and return ();
    405      my @hsps = gjoparseblast::blast_hsp_list( \*BLAST );
    406      close BLAST;
    407  
    408      #  Delete the temporary directory unless it already existed:
    409  
    410      system "/bin/rm -r $tmp_dir" if ! $save_tmp;
    411  
    412  #
```

## `lib/find_special_proteins.pm:730`

```
    724                      and return ();
    725  
    726      #  Search the contigs for the reference sequences:
    727  
    728      my $blastall = $params->{ blastall };
    729      $blastall ||= $ext_bin ? "$ext_bin/blastall" : 'blastall';
>>  730      my $blastcmd = "$blastall -p tblastn -d '$contig_file' -i '$ref_file' "
    731                   . "-e 1e-10 -F f -b 200 -v 200 -a 2 |";
    732      open( BLAST, $blastcmd )
    733          or print STDERR "Could not open pipe '$blastcmd'.\n"
    734             and return ();
    735      my @hsps = gjoparseblast::blast_hsp_list( \*BLAST );
    736      close BLAST;
    737  
    738      #  Delete the temporary directory unless it already existed:
    739  
    740      system "/bin/rm -r $tmp_dir" if ! $save_tmp;
    741  
    742  #
```

## `lib/rota-a-genotyper/VIGOR3/prod3/VIGOR3.pm:12208`

```
  12202      my $seq = $$genome{sequence};
  12203      $seq =~ s/(.{1,60})/$1\n/g;
  12204      print TMP ">$$genome{id}\n$seq";
  12205      close TMP;
  12206  
  12207  #    my $blastcmd =
>>12208  #"$myBin/blastall -p blastx -i $tmpfile -d $virusdb -e 1e-5 -M BLOSUM45 -X 5 -Z 12 -f 14 -F \"\" -v 0 -b 100 -m 7 1> $xmlfile 2> $logfile";
>>12209      my $blastcmd = "$myBin/blastall -p blastx -i $tmpfile -d $virusdb -e 1e-5 -M BLOSUM45 -g F -F \"\" -z 3000000 -v 0 -b 100 -m 7 1> $xmlfile 2> $logfile";
  12210      &runCmd($vigorspace, $blastcmd);
  12211      #print "cd $vigorspace; $blastcmd\n";
  12212      #    my @hsps = parse_blastxml( $xmlfile, 0 );
  12213      my @hsps = parse_blastxml( $xmlfile, 0 );
  12214  
  12215      #print "\nDATABASE HAPS\n";
  12216      #print_blasthits( 0, @hsps );
  12217      unlink $tmpfile;
  12218      unlink $xmlfile;
  12219      unlink $logfile;
  12220      if ( !@hsps ) {
  12221          my $db = get_parameter("reference_db");
```

## `plbin/sars2-compute-variation.pl:134`

```
    128      my($ref_id) = read_next_fasta_seq(\*R);
    129      close(R);
    130  
    131      my($out, $err);
    132      
    133      my @cmd = ("sars2-get-blast-variants",
>>  134  	       "-b", "tblastn",
    135  	       "-r",
    136  	       "-q", $spike,
    137  	       "-s", $contigs_file);
    138      print STDERR "@cmd\n";
    139      my $ok = run(\@cmd, ">", \$out, '2>', \$err);
    140      my $nohits;
    141      if (!$ok)
    142      {
    143  	my $rc = ($? >> 8);
    144  	if ($rc == 2)
    145  	{
    146  	    warn "No hits found\n";
```

## `lib/Bio/KBase/HomologyService/Util.pm:196`

```
    190  
    191      if ($sequence_count == 0)
    192      {
    193  	die "Error creating BLAST FAA database for $genome (owned by $owner): No protein sequences found in genome\n";
    194      }
    195  
>>  196      my $exe = "makeblastdb";
    197      my $suffix = $self->impl->{_blast_program_suffix};
    198      $exe .= $suffix if $suffix;
    199      my $prefix = $self->impl->{_blast_program_prefix};
    200      $exe = $prefix . $exe if $prefix;
    201  
    202      my @cmd = ($exe, "-in", $fasta_file, "-dbtype", "prot");
    203      my $rc = system(@cmd);
    204      $rc == 0 or die "Error $rc creating blastdb for $genome $owner: @cmd\n";
    205  }
    206  
    207  sub create_private_fna_db
    208  {
```

## `lib/Bio/KBase/HomologyService/Util.pm:242`

```
    236  
    237      if ($sequence_count == 0)
    238      {
    239  	die "Error creating BLAST FNA database for $genome (owned by $owner): No contig sequences found in genome\n";
    240      }
    241  
>>  242      my $exe = "makeblastdb";
    243      my $suffix = $self->impl->{_blast_program_suffix};
    244      $exe .= $suffix if $suffix;
    245      my $prefix = $self->impl->{_blast_program_prefix};
    246      $exe = $prefix . $exe if $prefix;
    247  
    248      my @cmd = ($exe, "-in", $fasta_file, "-dbtype", "nucl");
    249      my $rc = system(@cmd);
    250      $rc == 0 or die "Error $rc creating blastdb for $genome $owner: @cmd\n";
    251  }
    252  
    253  sub create_private_ffn_db
    254  {
```

## `lib/Bio/KBase/HomologyService/Util.pm:292`

```
    286  
    287      if ($sequence_count == 0)
    288      {
    289  	die "Error creating BLAST FFN database for $genome (owned by $owner): No feature sequences found in genome\n";
    290      }
    291  
>>  292      my $exe = "makeblastdb";
    293      my $suffix = $self->impl->{_blast_program_suffix};
    294      $exe .= $suffix if $suffix;
    295      my $prefix = $self->impl->{_blast_program_prefix};
    296      $exe = $prefix . $exe if $prefix;
    297  
    298      my @cmd = ($exe, "-in", $fasta_file, "-dbtype", "nucl");
    299      my $rc = system(@cmd);
    300      $rc == 0 or die "Error $rc creating blastdb for $genome $owner: @cmd\n";
    301  }
    302  
    303  
    304  #
```

## `lib/Bio/P3/HomologySearch/HomologySearch.pm:956`

```
    950  	 "-query", $input_file,
    951  	 "-db", $db_file,
    952  	 "-outfmt", 11,
    953  	 "-out", $out_file,
    954  	);
    955  
>>  956      if ($blast_program eq 'blastn' && $is_short)
    957      {
    958  	push(@opts, "-task", "blastn-short");
    959      }
    960      elsif ($blast_program eq 'blastp' && $is_short)
    961      {
    962  	push(@opts, "-task", "blastp-short");
    963      }
    964  
    965  
    966      if (exists $params->{blast_evalue_cutoff})
    967      {
    968  	push(@opts, "-evalue", $params->{blast_evalue_cutoff});
```

## `lib/BlastInterface.pm:2772`

```
   2766      }
   2767  
   2768      my $cmd = &form_blast_command( $queryF, $dbF, $blast_prog, $opts )
   2769          or warn "BlastInterface::run_blast: Failed to create a blast command."
   2770              and return wantarray ? () : [];
   2771  
>> 2772      if ( $opts->{ maxOffset } && $blast_prog ne 'blastp' && $blast_prog ne 'blastn' )
   2773      {
   2774          delete $opts->{ maxOffset };
   2775          print STDERR "Warning: maxOffset option deleted for program '$blast_prog'.\n";
   2776      }
   2777  
   2778      my $redir = { $opts->{ warnings } ? () : ( stderr => "/dev/null" ) };
   2779      my $fh    = &SeedAware::read_from_pipe_with_redirect( $cmd, $redir )
   2780          or return wantarray ? () : [];
   2781  
   2782      my $includeSelf = defined( $opts->{ includeSelf } ) ?   $opts->{ includeSelf }
   2783                      : defined( $opts->{ excludeSelf } ) ? ! $opts->{ excludeSelf }
   2784                      :                                       $queryF ne $dbF;
```

## `lib/VASTR/MLST/LocalMLST.pm:170`

```
    164  	my ($self,$databaseId,$locus,$seq,$max)=@_;
    165  	
    166  	$max=1 unless defined $max;
    167  	my @matches=();
    168  	
    169  	my $asnfile="$self->{TMPDIR}/${databaseId}-${locus}.asn";
>>  170  	system("echo \"$seq\" | blastn -task megablast -evalue 0.001 -max_target_seqs $max -outfmt 11 -db $self->{CONN}/blastdb/$databaseId/$locus -query - -out $asnfile");
    171  		
    172  	my $blastResult = capture{ system("blast_formatter -archive $asnfile -outfmt \"6 sseqid mismatch gaps length sseq\"") };
    173  	system("rm $asnfile");
    174  	
    175  	for my $result (split /\n/, $blastResult) {
    176  		my ($aid, $mismatches, $gaps, $length, $aseq) = split /\t/, $result;
    177  
    178  		# extract the id from the fasta header
    179  		$aid =~ s/^.+?_(\d+)$/$1/g;
    180  
    181  		my $match={
    182  			"database"	 => $databaseId,
```

## `lib/VASTR/MLST/LocalMLST.pm:204`

```
    198  sub matchToAllele {
    199  	my ($self,$databaseId,$locus,$seq)=@_;
    200  	
    201  	my @alleles=();	# the return object
    202  
    203  	my $asnfile="$self->{TMPDIR}/${databaseId}-${locus}.asn";
>>  204  	system("echo \"$seq\" | blastn -task megablast -evalue 0.000001 -max_target_seqs 25 -outfmt 11 -db $self->{CONN}/blastdb/$databaseId/$locus -query - -out $asnfile");
    205  	
    206  	my $blastResult = capture{ system("blast_formatter -archive $asnfile -outfmt \"6 sseqid mismatch gaps length sseq btop sstart send qstart qend bitscore slen\"") };
    207  	return \@alleles unless defined $blastResult && $blastResult ne '';
    208  	
    209  	# get the alignments and store them keyed by allele id (locus_allele)
    210  	my $blastAlign = capture{ system("blast_formatter -archive $asnfile -num_alignments 25") };
    211  	my @raw_alignments = split /\n{3}/, $blastAlign;
    212  	my %alignments=();
    213  	foreach my $align (@raw_alignments) {
    214  		my $key = $1 if $align =~ />\s*([A-Za-z0-9_\-]+)/i;
    215  		next unless defined $key;
    216  		next if defined $alignments{$key};
```

