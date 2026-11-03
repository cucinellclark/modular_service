# BV-BRC invocations of `blastp` (blastp)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 54 hunk(s) in 22 file(s); showing top 25.
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/KBase/HomologyService/HomologyServiceImpl.pm`
- `lib/Bio/KBase/HomologyService/Util.pm`
- `lib/Bio/P3/HomologySearch/HomologySearch.pm`
- `lib/BlastInterface.pm`
- `lib/BlastUtils.pm`
- `lib/P3DataAPI.pm`
- `lib/ProtSims.pm`
- `lib/alignment.pm`
- `lib/bidir_best_hits.pm`
- `lib/gjoalignandtree.pm`
- `lib/gjoalignment.pm`
- `lib/representative_sequences.pm`
- `lib/rota-a-genotyper/VIGOR3/prod3/VIGOR3.pm`
- `lib/rota-a-genotyper/VIGOR3/prod3/dbutils/transferAnnotation.pl`
- `plbin/App-GenomeComparison.pl`
- `plbin/blast_against_genomes.pl`
- `plbin/p3-blast.pl`
- `plbin/p3-submit-BLAST.pl`
- `plbin/p3x-compute-specialty-blast.pl`
- `plbin/rast_compute_specialty_genes.pl`
- `plbin/sars2-get-blast-variants.pl`
- `pybin/run_ha_subtype_numbering_conversion.py`

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

## `lib/Bio/P3/HomologySearch/HomologySearch.pm:224`

```
    218  
    219  #
    220  # $search_type_map{input-type}->{db-type} = valid-blast-programs
    221  #
    222  our %search_type_map =
    223      (aa => {
>>  224  	faa => ['blastp'],
    225  	ffn => ['tblastn'],
    226  	frn => ['tblastn'],
    227  	fna => ['tblastn'],
    228      },
    229       dna => {
    230  	 faa => ['blastx'],
    231  	 ffn => ['blastn', 'tblastx'],
    232  	 frn => ['blastn', 'tblastx'],
    233  	 fna => ['blastn', 'tblastx'],
    234       });
    235  				    
    236  our %makeblastdb_dbtype = (faa => "prot",
```

## `lib/ProtSims.pm:246`

```
    240  	    {
    241  		@par = ("-a", 4);
    242  	    }
    243  	}
    244  	
    245  	
>>  246  	# my $cmd = "$blastall_cmd -m 8 -i $tmpQ -d $dbF -FF -p blastp -e 1e-5";
>>  247  	my @cmd = ($blastall_cmd,  '-m', 8, '-i', $tmpQ, '-d', $dbF, '-FF', '-p', 'blastp', '-e', '1e-5', @par);
    248  	#print STDERR "$cmd\n";
    249  	#open(BL, "$cmd|") or die "ProtSims::blastP: pipe to blast failed with $!: $cmd\n";
    250  	
    251  	#
    252  	# It'd be nice to do this but windows doesn't support it.
    253  	#
    254  	#open(BL, "-|", @cmd) or die "ProtSims::blastP: pipe to blast failed with $!: @cmd\n";
    255  	my $out_tmp = "$tmp_dir/blast_out.$tmp_suffix";
    256  	push(@cmd, "-o", $out_tmp);
    257  	#print STDERR "@cmd\n";
    258  	my $rc = system(@cmd);
    259  	if ($rc != 0)
```

## `lib/gjoalignment.pm:1573`

```
   1567  
   1568      gjoseqlib::write_fasta( $blastfile, scalar gjoseqlib::pack_sequences( $clnali ) );
   1569      gjoseqlib::write_fasta( $seqfile,   scalar gjoseqlib::pack_sequences( $clnseq ) );
   1570  
   1571      $type = gjoseqlib::guess_seq_type( $clnseq->[2] ) if ! $type;
   1572      my ( $is_prot, $prog, @opt ) = ( $type =~ m/^n/i ) ? qw( f blastn -r 1 -q -1 )
>> 1573                                                         : qw( t blastp );
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
   1585  
```

## `plbin/p3x-compute-specialty-blast.pl:163`

```
    157  
    158      print STDERR "Compute $db\n";
    159  
    160      my @cmd;
    161      if ($opt->program eq 'blast')
    162      {
>>  163  	@cmd = ("blastp", "-query", $in_file, "-db", "$db_file.faa",
    164  		   "-num_threads", $opt->parallel,
    165  		   "-num_alignments", 1,
    166  		   "-num_descriptions", 1,
    167  		   "-evalue", $opt->evalue,
    168  		   "-outfmt", 0);
    169      }
    170      elsif ($opt->program eq 'diamond')
    171      {
>>  172  	@cmd = ("diamond", "blastp",
    173  		"--query", $in_file,
    174  		"--db", "$db_file.faa.dmnd",
    175  		"--outfmt", "0",
    176  		"--evalue", $opt->evalue,
    177  		"--id", $min_iden,
    178  		"--sensitive",
    179  		"--threads", $opt->parallel);
    180      }
    181      else
    182      {
    183  	@cmd = ("blat", "-prot", "$db_file.faa", $in_file, "-out=blast", "/dev/fd/1");
    184      }
```

## `pybin/run_ha_subtype_numbering_conversion.py:268`

```
    262              subtype = values["header"].split("|")[2].split()[0]
    263              reference_sequences[subtype] = values["data"]
    264  
    265      blast_output_file = output_dir / "blast.out"
    266      # Run BLAST
    267      try:
>>  268          blast_cmd = ["blastall", "-d", str(REFERENCE_SEQUENCE), "-i", str(blast_input_file), "-p", "blastp",
    269                       "-G", "10", "-E", "1", "-m", "7", "-o", str(blast_output_file)]
    270          subprocess.check_call(blast_cmd, shell=False)
    271      except Exception as e:
    272          print(f"Error running blast for {input_file}: {e}")
    273          sys.exit(1)
    274  
    275      # Parse blast result and create sequence annotation file
    276      qresults = SearchIO.parse(str(blast_output_file), "blast-xml")
    277  
    278      sequence_annotation_file_path = output_dir / BLAST_SEQ_ANNOTATION_NAME
    279      with open(sequence_annotation_file_path, "w") as sequence_annotation_file:
    280          sequence_annotation_writer = csv.DictWriter(sequence_annotation_file, delimiter="\t",
```

## `lib/BlastInterface.pm:2874`

```
   2868                || ( $blast_prog eq 'tblastn'  &&   $opts->{in_pssm} )
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

## `lib/alignment.pm:1440`

```
   1434  
   1435      gjoseqlib::write_fasta( $blastfile, scalar gjoseqlib::pack_sequences( $clnali ) );
   1436      gjoseqlib::write_fasta( $seqfile,   scalar gjoseqlib::pack_sequences( $clnseq ) );
   1437  
   1438      $type = guess_seq_type( $clnseq->[2] ) if ! $type;
   1439      my ( $is_prot, $prog, @opt ) = ( $type =~ m/^n/i ) ? qw( f blastn -r 1 -q -1 )
>> 1440                                                         : qw( t blastp );
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
   1452      my @params = ( '-p', $prog,
```

## `plbin/rast_compute_specialty_genes.pl:238`

```
    232  #    print "\t", join(" ", map { keys %{$md5{$_}}} keys %to_compute), "\n";
    233  
    234      if ($do)
    235      {
    236  	if ($opt->program eq 'blast')
    237  	{
>>  238  	    my @cmd = ("blastp", "-query", $tmp, "-db", $db_file,
    239  		    "-num_threads", $opt->parallel,
    240  		    "-num_alignments", 1,
    241  		    "-num_descriptions", 1,
    242  		    "-evalue", $opt->evalue,
    243  		    "-outfmt", 0);
    244  	    my $ok = run(\@cmd, '>>', $raw_blast_fh);
    245  	    
    246  	    if (!$ok)
    247  	    {
    248  		die "Blast failed with $?: $@cmd\n";
    249  	    }
    250  	}
```

## `lib/Bio/KBase/HomologyService/Util.pm:439`

```
    433      # if we have short sequences, use the tasks optimized for that.
    434      #
    435      if ($program eq 'blastn' && $is_short)
    436      {
    437  	push(@cmd, "-task", "blastn-short");
    438      }
>>  439      elsif ($program eq 'blastp' && $is_short)
    440      {
    441  	push(@cmd, "-task", "blastp-short");
    442      }
    443         
    444      return @cmd;
    445  }
    446  
    447  sub blast_fasta_to_taxon
    448  {
    449      my ($self, $fasta_data, $program, $taxon_id, $subj_type, $evalue_cutoff, $max_hits, $min_coverage) = @_;
    450  
    451      #
```

## `lib/Bio/P3/HomologySearch/HomologySearch.pm:960`

```
    954  	);
    955  
    956      if ($blast_program eq 'blastn' && $is_short)
    957      {
    958  	push(@opts, "-task", "blastn-short");
    959      }
>>  960      elsif ($blast_program eq 'blastp' && $is_short)
    961      {
    962  	push(@opts, "-task", "blastp-short");
    963      }
    964  
    965  
    966      if (exists $params->{blast_evalue_cutoff})
    967      {
    968  	push(@opts, "-evalue", $params->{blast_evalue_cutoff});
    969      }
    970  
    971      if (exists $params->{blast_max_hits})
    972      {
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

## `plbin/App-GenomeComparison.pl:25`

```
     19  
     20  use Bio::KBase::AppService::AppConfig;
     21  use Bio::KBase::AppService::AppScript;
     22  
     23  use bidir_best_hits;
     24  
>>   25  my $blastp  = "blastp";
     26  my $circos  = "circos";
     27  my $openssl = "openssl";
     28  
     29  verify_cmd($blastp) and verify_cmd($circos) and verify_cmd($openssl);
     30  
     31  my $data_api = Bio::KBase::AppService::AppConfig->data_api_url;
     32  # my $data_api = 'http://www.alpha.patricbrc.org/api';
     33  
     34  my $script = Bio::KBase::AppService::AppScript->new(\&process_proteomes, \&preflight_cb);
     35  my $rc = $script->run(\@ARGV);
     36  exit $rc;
     37  
```

## `lib/Bio/KBase/HomologyService/Util.pm:19`

```
     13  use DB_File;
     14  use LWP::UserAgent;
     15  use gjoseqlib;
     16  
     17  __PACKAGE__->mk_accessors(qw(blast_db_genomes blast_db_private_genomes impl json));
     18  
>>   19  my %blast_command_subject_type = (blastp => 'a',
     20  				  blastn => 'd',
     21  				  blastx => 'a',
     22  				  tblastn => 'd',
     23  				  tblastx => 'd');
>>   24  my %blast_command_exe_name = (blastp => 'blastp',
     25  			      blastn => 'blastn',
     26  			      blastx => 'blastx',
     27  			      tblastn => 'tblastn',
     28  			      tblastx => 'tblastx');
     29  
     30  sub new
     31  {
     32      my($class, $impl) = @_;
     33  
     34      my $self = {
     35  	impl => $impl,
     36  	blast_db_genomes => $impl->{_blast_db_genomes},
```

## `lib/BlastUtils.pm:1859`

```
   1853  
   1854  sub form_blast_command
   1855  {
   1856      my( $queryF, $dbF, $blast_prog, $parms ) = @_;
   1857      $parms ||= {};
   1858  
>> 1859      my %prog_ok = map { $_ => 1 } qw( blastn blastp blastx tblastn tblastx psiblast rpsblast rpstblastn);
   1860      $queryF && $dbF && $blast_prog && $prog_ok{ $blast_prog }
   1861          or return wantarray ? () : [];
   1862  
   1863      my $prog = SeedTkRun::executable_for( $blast_prog );
   1864  
   1865      $prog
   1866          or return wantarray ? () : [];
   1867  
   1868      my $threads          = $parms->{ threads }          || $parms->{ numThreads }       || $parms->{ num_threads };
   1869  
   1870      my $dbCode           = $parms->{ dbCode }           || $parms->{ dbGenCode }        || $parms->{ db_gen_code };
   1871      my $giList           = $parms->{ giList }           || $parms->{ gilist };
```

## `lib/rota-a-genotyper/VIGOR3/prod3/VIGOR3.pm:6857`

```
   6851   #    system
   6852   #"cd $vigorspace; $myBin/formatdb -i $mpsbj -l $vigorspace/formatdb_mpsbj.log";
   6853  
   6854      my $mpxml = "$vigorspace/xml";
   6855      unlink $mpxml;
   6856  
>> 6857      &runCmd($vigorspace, "$myBin/blastall -p blastp -e 10 -W 1 -C 0 -F \"\" -v 0 -b 2000 -m 7 -d $matpepdb -i $mpsbj > $mpxml 2> /dev/null");
   6858  
>> 6859  #"cd $vigorspace; $myBin/blastall -p blastp -e 10 -M BLOSUM45 -g F -F \"\" -v 0 -b 1 -m 7 -i $mpqry -d $mpsbj > $mpxml";
   6860      my @tmp = parse_blastxml( $mpxml, 0 );
   6861  
   6862      #    if ($verbose) {
   6863      #        print "SUBJECT HSPS\n";
   6864      #        print_blasthits( 0, @tmp );
   6865      #    }
   6866  
   6867      #    {
   6868      #        my %best;
   6869      #        for my $hit ( sort { $$a{evalue} <=> $$b{evalue} } @tmp ) {
   6870      #            if ( !exists $best{ $$hit{subject_id} } ) {
   6871      #                $best{ $$hit{subject_id} } = $hit;
```

## `lib/rota-a-genotyper/VIGOR3/prod3/dbutils/transferAnnotation.pl:124`

```
    118  my $blastXML = "$vigorspace/blast.xml";
    119  for my $rawSeq ( sort { $$a{id} cmp $$b{id} } values %rawSeqs ) {
    120      $$rawSeq{defline} = cleanDefline( $$rawSeq{defline} );
    121      unlink $queryFasta;
    122      unlink $blastXML;
    123      writeFasta( $queryFasta, $rawSeq );
>>  124      $cmd = "blastall -p blastp -b 5 -e 0.01 -F \"\" -i $queryFasta -d $tmpRef -m 7 -o $blastXML";
    125      runCmd($vigorspace, $cmd);
    126      my @hsps = parse_blastxml( $blastXML, 0 );
    127      my @hits = sort { $$b{vigor_matchwgt} <=> $$a{vigor_matchwgt} } best_subject_hits( undef, \@hsps );
    128  
    129  #print "\n> $$rawSeq{defline}\n";
    130  #print "\n     HSPS\n";
    131  #print_blasthits( 5, @hsps ); 
    132  #print "\n     HITS\n";
    133  #print_blasthits( 5, @hits );
    134  
    135      my %original;
    136      for my $tag ( @transferTags ) {
```

## `lib/Bio/P3/HomologySearch/HomologySearch.pm:181`

```
    175  
    176  use File::Slurp;
    177  
    178  #
    179  # Configure PATH to point at the correct location for BLAST binaries.
    180  #
>>  181  # If we have $KB_TOP/services/homology_service/bin/blastp, that is our
    182  # deployed path and use that.
    183  #
    184  # Otherwise, assume we are in a dev container where we will look in
    185  # $KB_TOP/modules/homology_service/blast.bin.
    186  #
    187  
    188  
    189  {
    190      my @blast_paths = ("$ENV{KB_TOP}/services/homology_service/bin",
    191  		       "$ENV{KB_TOP}/modules/homology_service/blast.bin");
>>  192      my @found = grep { -x "$_/blastp" } @blast_paths;
    193      if (@found)
    194      {
    195  	print STDERR "Initializing BLAST path to $found[0]\n";
    196  	$ENV{PATH} = "$found[0]:$ENV{PATH}";
    197      }
    198      else
    199      {
    200  	print STDERR "No internal BLAST found, using default path $ENV{PATH}\n";
    201      }
    202      my $out;
>>  203      run(["blastp", "-version-full"], ">", \$out);
    204      print STDERR "BLAST version: $out\n";
    205  }
    206  
    207  __PACKAGE__->mk_accessors(qw(app app_def params token task_id
    208  			     blast_program blast_params
    209  			     blast_sqlite_db
    210  			     work_dir stage_dir
    211  			     output_base output_folder 
    212  			     contigs app_params  api
    213  			     database_path
    214  			     blastdbs
    215  			     json
```

## `lib/P3DataAPI.pm:3081`

```
   3075  
   3076          my $rc = system("formatdb", "-p", "t", "-i", "$tmp_db");
   3077          $rc == 0 or die "formatdb failed with $rc\n";
   3078  
   3079          my $evalue = "1e-5";
   3080  
>> 3081          open(my $blast, "-|", "blastall", "-p", "blastp", "-i", "$tmp_qry", "-d", "$tmp_db", "-m", 8, "-e", $evalue,
   3082               ($n_genomes ? ("-b", $n_genomes) : ()))
   3083              or die "cannot run blastall: $!";
   3084          my %seen;
   3085          while (<$blast>)
   3086          {
   3087              print STDERR $_;
   3088              chomp;
   3089              my($id1, $id2, $iden, undef, undef, undef, $b1, $e1, $b2, $e2) = split(/\t/);
   3090              next if $seen{$id1, $id2}++;
   3091  
   3092              if (!defined($me->{blast_shift}))
   3093              {
```

## `lib/P3DataAPI.pm:3180`

```
   3174          my $rc = system("formatdb", "-p", "t", "-i", $tmp);
   3175          $rc == 0 or die "formatdb failed with $rc\n";
   3176  
   3177          my $evalue = "1e-5";
   3178  
   3179          my $blast;
>> 3180          open($blast, "-|", "blastall", "-p", "blastp", "-i", "$tmp2", "-d", "$tmp", "-m", 8, "-e", $evalue,
   3181               ($max_size ? ("-b", $max_size) : ()))
   3182              or die "cannot run blastall: $!";
   3183          my %seen;
   3184          #
   3185          # We are blasting against the unique sequences. For now,
   3186          # just remap the blast output. We may be able to be more
   3187          # clever moving forward.
   3188          #
   3189          my @hits;
   3190      my %found = map { $_->{patric_id} => 1 } @pin;
   3191          while (<$blast>)
   3192          {
```

## `lib/bidir_best_hits.pm:295`

```
    289  #  \@matches = best_merged_blast_hit( $query_file, $subject_file, \%options )
    290  #  \@matches = best_merged_blast_hit( $query_file, $subject_file,  %options )
    291  #
    292  #      options:
    293  #      -------------------------------------------
    294  #      e_value => max_e_value         # D = 10e-5
>>  295  #      program => blast_program       # D = blastp
    296  #      options => blast_command_opts  # D = ''
    297  #      -------------------------------------------
    298  #
    299  #
    300  #  Matches are:
    301  #
    302  #    [ qid, qdef, qlen, sid, sdef, slen,
    303  #      score, e_val, n_seq, p_n,
    304  #      aln_len, aln_id, aln_pos, aln_gap, aln_dir
    305  #      q_start, q_end, q_aln, s_start, s_end, s_aln,
    306  #      [ @hsps ]
    307  #    ]
```

## `plbin/App-GenomeComparison.pl:121`

```
    115      my $nproc = $ENV{P3_ALLOCATED_CPU} // 2;
    116  
    117      my $opts = { min_cover     => $params->{min_seq_cov},
    118                   min_positives => $params->{min_positives},
    119                   min_ident     => $params->{min_ident},
    120                   max_e_val     => $params->{max_e_val},
>>  121                   program       => 'blastp',
    122                   blast_opts    => "-a $nproc",
    123                   verbose       => 1
    124                 };
    125      print STDERR "BBH options: ", Dumper($opts);
    126  
    127      my @orgs = @$genomes;
    128      my ($circos_ref, @circos_comps);
    129      my @fids;
    130      my %hits;
    131  
    132      my @ref_fields  = qw(contig gene aa_length patric_id locus_tag gene_name plfam_id pgfam_id function start end strand);
    133      my @comp_fields = qw(hit contig gene aa_length patric_id locus_tag gene_name function percent_identity seq_coverage); # e_value not directly available for Gary's tool
```

## `plbin/p3-submit-BLAST.pl:127`

```
    121  
    122  use constant DB_TYPE => { 'fna' => 'n', 'ffn' => 'n', 'frn' => 'n', 'faa' => 'p' };
    123  
    124  use constant DB_FILE_TYPE => { 'fna' => 'contigs', 'ffn' => 'feature_dna_fasta', 'frn' => 'feature_dna_fasta',
    125      'faa' => 'feature_protein_fasta' };
    126  
>>  127  use constant BLAST_PROGRAM => { 'nn' => 'blastn', 'np' => 'blastx', 'pn' => 'tblastn', 'pp' => 'blastp' };
    128  
    129  use constant DB_NAME => { 'BV-BRC' => 1, 'REFSEQ' => 1, 'Plasmids' => 1, 'Phages' => 1 };
    130  
    131  # Insure we're logged in.
    132  my $p3token = P3AuthToken->new();
    133  if (! $p3token->token()) {
    134      die "You must be logged into BV-BRC to use this script.";
    135  }
    136  # Get a common-specification processor, an uploader, and a reads-processor.
    137  my $commoner = Bio::KBase::AppService::CommonSpec->new();
    138  my $uploader = Bio::KBase::AppService::UploadSpec->new($p3token);
    139  
```

## `plbin/sars2-get-blast-variants.pl:14`

```
      8  use Getopt::Long;
      9  use gjoseqlib;
     10  
     11  my $usage = 'get-blast-variants.pl -s subject_seqs.dna -q spike_protein.aa
     12  
     13  
>>   14          -b blast program  [chose tblastn, blastp, blastn, or blastx], required                
     15          -q query sequence  required
     16          -s subject sequence for blasting against, required
     17          
     18          -l min hsp length (d = 50)
     19          -p min hsp percent identity d = (0.85)
     20          -t [file name] print table of blast match statistics
     21          -c [file name] print a consensus sequence of the recovered protein
     22          -g "gap character" d = "X", this is the character that gets inserted when
     23              multiple HSPS are spliced together. Blast fills in gaps in a match with 
     24              the X character.  
     25          -k keep the bastdb files [default = remove]
     26          -f strip fasta header after the first white space, default keeps whole string. 
```

