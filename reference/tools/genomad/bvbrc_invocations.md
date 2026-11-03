# BV-BRC invocations of `genomad` (genomad)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 9 hunk(s) in 3 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/MobileElementDetection.pm`
- `plbin/App-Genomad.pl`
- `plbin/App-MobileElementDetection.pl`

## `plbin/App-Genomad.pl:93`

```
     87  	close $fh;	
     88  	die "Input File is not fasta format.\n" unless $lines[0] =~ /^>/; 
     89  	die "Input file is likley FASTQ format. Assembled contigs are required.\n" if grep { /^\+/ } @lines;  
     90  	die "Not DNA FASTA\n" if grep { !/^>/ && /[^ACGTRYKMSWBDHVN\s]/i } @lines;
     91  	
     92  	
>>   93  	# Usage: genomad end-to-end [OPTIONS] INPUT OUTPUT DATABASE                                                                   
     94  	my @command;
     95  	my $of = $params->{'output_file'};
>>   96  	push @command, ("genomad", "end-to-end", "--threads", "$threads"); 
     97  	if ($params->{'cleanup'}){push @command, "--cleanup";}
     98  	if ($params->{'restart'}){push @command, "--restart";}
     99  	if ($params->{'verbose'}){push @command, "--verbose";}
    100  	if ($params->{'lenient-taxonomy'}){push @command, "--lenient-taxonomy";}
    101  	if ($params->{'full-ictv-lineage'}){push @command, "--full-ictv-lineage";}
    102  	if ($params->{'force-auto'}){push @command, "--force-auto";}
    103      if ($params->{'filtering-preset'}){push @command, "--$params->{'filtering-preset'}";}
    104      if ($params->{'composition'})
    105      {	push @command, "--composition";
    106      	push @command, $params->{'composition'};
    107      }
    108  	push @command, $input_file;
    109  	push @command, $of;
    110  	push @command, $db;
    111  	
    112      my $rc = system(@command);   
>>  113      die "Failure running genomad" if $rc != 0;
    114  	
    115  	#I want to concatenate the log files into a single file in the right order so 
    116  	#that it can be kept.  It has some useful info on the run with versions, etc.
    117  
    118  	my $cat = "cat $of/${prefix}_annotate.log $of/${prefix}_find_proviruses.log $of/${prefix}_marker_classification.log $of/${prefix}_nn_classification.log $of/${prefix}_aggregated_classification.log $of/${prefix}_summary.log > $of/geNomad_run.stderr";
    119  
    120  	my $rc = system($cat);   
    121      die "Failure concatenating log file" if $rc != 0;
    122  	
    123  	my $folder = $app->result_folder();
    124  
    125  	my @to_move = 	opendir (DIR, "$of/${prefix}_summary/");
```

## `lib/MobileElementDetection.pm:501`

```
    495  {
    496      my($params, $input_file, $threads) = @_;
    497      
    498      my @command;
    499      my $of = $params->{'output_file'};
    500      
>>  501      push @command, ("genomad", "end-to-end", "--threads", "$threads"); 
    502      if ($params->{'cleanup'}){push @command, "--cleanup";}
    503      if ($params->{'restart'}){push @command, "--restart";}
    504      if ($params->{'verbose'}){push @command, "--verbose";}
    505      if ($params->{'lenient-taxonomy'}){push @command, "--lenient-taxonomy";}
    506      if ($params->{'full-ictv-lineage'}){push @command, "--full-ictv-lineage";}
    507      if ($params->{'force-auto'}){push @command, "--force-auto";}
    508      if ($params->{'filtering-preset'}){push @command, "--$params->{'filtering-preset'}";}
    509      if ($params->{'composition'}) 
    510      {    
    511          push @command, "--composition";
    512          push @command, $params->{'composition'};
    513      }
    514      push @command, $input_file;
    515      push @command, $of;
    516      push @command, $DB_PATH;
    517      
    518      my $genomad_rc = system(@command);   
>>  519      die "Failure running genomad" if $genomad_rc != 0;
    520      
    521      return 1;
    522  }
    523  
    524  #-----------------------------------------------------------------------------------------
    525  # Results processing - viral contigs
    526  #-----------------------------------------------------------------------------------------
    527  
    528  sub process_viral_contigs 
    529  {
    530      my($app, $params, $seqH, $folder, $prefix) = @_;
    531      
```

## `lib/MobileElementDetection.pm:195`

```
    189      print "App-Genomad: ", Dumper($app_def, $raw_params, $params);
    190      my $threads = $ENV{P3_ALLOCATED_CPU} // 16;
    191      
    192      # Step 1: Process and validate input
    193      my ($input_file, $prefix, $contigs_ws_path) = process_input_and_validate($app, $params);
    194      
>>  195      # Step 2: Execute genomad analysis
    196      execute_genomad_analysis($params, $input_file, $threads);
    197      
    198      # Step 3: Read input sequences for processing
    199      open (IN, "<$input_file") or warn "could not open fasta file of contigs\n";
    200      my @seqs = &gjoseqlib::read_fasta(\*IN);
    201      close IN; 
    202      my $seqH = {};
    203      for my $i (0..$#seqs) 
    204      {
    205          $seqH->{$seqs[$i][0]}->{SEQ} = $seqs[$i][2];
    206          $seqH->{$seqs[$i][0]}->{ANN} = $seqs[$i][1];
    207      }
```

## `plbin/App-Genomad.pl:5`

```
      1  #! /usr/bin/env perl
      2  
      3  #
      4  # The BVBRC App wrapper for Genomad
>>    5  # https://github.com/apcamargo/genomad
      6  #
      7  
      8  use Carp::Always;
      9  use Bio::KBase::AppService::AppScript;
     10  use File::Slurp;
     11  use strict;
     12  use Data::Dumper;
     13  
     14  my $db = "/vol/bvbrc/production/application-backend/genomad/genomad_db"; 
     15  my $script = Bio::KBase::AppService::AppScript->new(\&genomad, \&preflight);
     16  $script->run(\@ARGV);
     17  
```

## `plbin/App-Genomad.pl:66`

```
     60  	{
     61  		$runtime = (3600 * 72); # 3 day wall time for job > 1GB
     62  	}
     63      return { cpu => 16, memory => '32G', runtime => $runtime };
     64  }
     65  
>>   66  sub genomad
     67  {
     68      my($app, $app_def, $raw_params, $params) = @_;
     69  
     70      print "App-Genomad: ", Dumper($app_def, $raw_params, $params);
     71  	my $threads = $ENV{P3_ALLOCATED_CPU} // 16;
     72  	
     73      my $input_path = $params->{'input_file'};
     74      my $input_file = $input_path;
     75  	$input_file =~ s/.+\///g;
     76  	my $prefix = $input_file;
     77  	$prefix =~ s/\..+//g; 
     78  
```

## `plbin/App-MobileElementDetection.pl:7`

```
      1  #!/usr/bin/env perl
      2  
      3  #
      4  # The BVBRC App wrapper for Genomad with integrated GenomeAssembly2
      5  # and plasmid and viral (LowVan) annotation.
      6  
>>    7  # https://github.com/apcamargo/genomad
      8  #
      9  
     10  use strict;
     11  use warnings;
     12  use Carp::Always;
     13  use Bio::KBase::AppService::AppScript;
     14  
     15  # Import the functions we need from our module
     16  use MobileElementDetection qw(run preflight);
     17  
     18  # Create the AppScript with references to our imported subroutines
     19  my $script = Bio::KBase::AppService::AppScript->new(\&run, \&preflight);
```

## `lib/MobileElementDetection.pm:134`

```
    128          }
    129  
    130          # Modern assemblers are more complex - multiply by 10 
    131          $est_time *= 10;
    132          $est_time = 3600 if $est_time < 3600;  # Minimum 1 hour
    133  
>>  134          # Add 4 hours for genomad, this is janky but there is no easy way to estimate 
    135          # contig number and assembly file size from reads.  This should cover any assembly
    136          # < 100MB
    137          $runtime = $est_time + 14400;  #
    138  
    139          # Estimated compressed storage based on input compressed size
    140          my $est_storage = int(1.3e6 * $est_comp / 0.75);
    141  
    142          $cpu = 32;  # More CPUs for assembly
    143          $memory = "128G";  # More memory for assembly
    144          
    145          # Adjust CPU/memory based on estimated time like GenomeAssembly2
    146          if ($est_time < 6*60*60) # Less than 6 hours
```

## `lib/MobileElementDetection.pm:154`

```
    148              $cpu = 16;
    149              $memory = "48G";
    150          }
    151      }
    152      else 
    153      {
>>  154          # Contigs: input requirements based on genomad runs
    155          my $ctg = $params->{input_file};
    156          $ctg or die "Assembled contigs must be specified\n";
    157          my $res = $app->workspace->stat($ctg);
    158          my $size = $res->size;
    159          $size > 0 or die "Contigs not found\n";
    160          
    161          # Runtime estimates based on contigs size
    162          if ($size < 10_000_000) {
    163              $runtime = 3600; #1hr wall time for jobs < 10MB
    164          }
    165          elsif (($size >= 10_000_000) && ($size < 100_000_000)) {
    166              $runtime = (3600 * 4); # 4 hr wall time for job < 100MB
```

## `lib/MobileElementDetection.pm:251`

```
    245      
    246      if ($params->{input_type} eq 'reads') 
    247      {
    248          # Perform assembly using GenomeAssembly2 app
    249          $contigs_ws_path = assemble_reads_with_app($app, $params);
    250          
>>  251          # Download the assembled contigs for genomad processing
    252          $input_file = "assembly_contigs.fasta";
    253          $app->workspace->download_file($contigs_ws_path, $input_file, 1);
    254          
    255          # Extract prefix from the actual filename
    256          $prefix = $input_file;
    257          $prefix =~ s/\..+//g;  # Remove extension, so "assembly_contigs.fasta" -> "assembly_contigs"
    258      }
    259      else 
    260      {
    261          # Use provided contigs
    262          my $input_path = $params->{'input_file'};
    263          $input_file = $input_path;
```

