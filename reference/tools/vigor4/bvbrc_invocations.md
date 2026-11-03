# BV-BRC invocations of `vigor4` (vigor4)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 10 hunk(s) in 5 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/MetagenomeBinning/MetagenomeBinning.pm`
- `plbin/p3-submit-genome-annotation.pl`
- `plbin/p3x-annotate-mat-peptide.pl`
- `plbin/p3x-annotate-vigor4.pl`
- `pybin/run_sequence_submission.py`

## `plbin/p3-submit-genome-annotation.pl:142`

```
    136  		     ["overwrite|f", "If a file to be uploaded already exists in the workspace, overwrite it on upload. Otherwise we will not continue the service submission."],
    137  		     ["genbank-file=s", "A genbank file to be annotated."],
    138  		     ["contigs-file=s", "A file of DNA contigs to be annotated."],
    139  		     ["phage", "Set defaults for phage annotation."],
    140  		     ["recipe=s", "Use the given non-default recipe for this annotation"],
    141  		     ["reference-genome=s", "The BV-BRC identifier of a reference genome whose annotations will be propagated as part of this annotation."],
>>  142  		     ["reference-virus=s", "The name of a virus from the VIGOR_DB collection to use as the reference for a vigor4 viral annotation."],
    143  		     [],
    144  		     ["The following options describe the genome to be annotated."],
    145  		     ["In each case where the value for the specified option may be drawn"],
    146  		     ["from a submitted genbank file it is optional to supply the value."],
    147  		     ["If a value is supplied, it will override the value in the genbank file."],
    148  		     [],
    149  		     ["scientific-name|n=s", "Scientific name for this genome."],
    150  		     ["taxonomy-id|t=i", "Numeric NCBI taxonomy ID for this genome. If not specified an estimate will be computed, and if that is not possible the catchall taxonomy ID 6666666 will be used."],
    151  		     ["genetic-code|g=i", "Genetic code for this genome; either 11 or 4. If not specified defaults to 11 unless it can be determined from the declared or computed taxonomy ID."],
    152  		     ["domain|d=s", "Domain for this genome (Bacteria or Archaea)"],
    153  		     [],
    154  		     ["Advanced options:"],
```

## `plbin/p3x-annotate-vigor4.pl:25`

```
     19  
     20  use Cwd;
     21  
     22  my($opt, $usage) = describe_options("%c %o",
     23  				    ["reference=s" => "Vigor4 reference name"],
     24  				    ["taxon=i" => "Taxon identifier"],
>>   25  				    ["remove-existing" => "Remove existing CDS and mat_peptide features if vigor4 run is successful"],	
     26  				    ["input|i=s" => "Input file"],
     27  				    ["output|o=s" => "Output file"],
     28  				    ["threads|j=i" => "Limit vigor to this many threads", { default => 1 }],
     29  				    ["debug|d" => "Enable debugging"],
     30  				    ["help|h" => "Show this help message"]);
     31  print($usage->text), exit 0 if $opt->help;
     32  die($usage->text) if @ARGV != 0;
     33  
     34  chomp(my $hostname = `hostname`);
     35  
     36  my $tempdir = File::Temp->newdir(CLEANUP => ($opt->debug ? 0 : 1));
     37  
```

## `plbin/p3x-annotate-vigor4.pl:102`

```
     96  my @vigor_params = ("-i", $sequences_file,
     97  		    "--reference-database-path", $ref_dir,
     98  		    "-d", $reference_name,
     99  		    "-o", "$here/vigor_out");
    100  
    101  print STDERR Dumper(\@vigor_params);
>>  102  my $ok = run(["vigor4", @vigor_params],
    103  	     init => sub {
    104  		 chdir $tempdir;
    105  		 $ENV{JAVA_OPTS} = "-XX:ActiveProcessorCount=" . $opt->threads;
    106  	     },
    107  	     ">", "$here/vigor4.stdout.txt",
    108  	     "2>", "$here/vigor4.stderr.txt");
    109  if (!$ok)
    110  {
    111      print STDERR "Vigor run failed with rc=$?. Stdout:\n";
    112      copy("$here/vigor4.stdout.txt", \*STDERR);
    113      print STDERR "Stderr:\n";
    114      copy("$here/vigor4.stderr.txt", \*STDERR);
    115  }
    116      
    117  my $event = {
>>  118      tool_name => "vigor4",
    119      execution_time => scalar gettimeofday,
    120      parameters => \@vigor_params,
    121      hostname => $hostname,
    122  };
    123  
    124  my $event_id = $genome_in->add_analysis_event($event);
    125  
    126  #
    127  # Parse the generated peptide file. We collect the CDS and mature_peptides, then
    128  # add features so that we can register the counts.
    129  #
    130  if (open(my $pep_fh, "<", "$here/vigor_out.pep"))
```

## `pybin/run_sequence_submission.py:173`

```
    167  def runVIGOR4(fasta_file, organism):
    168    fasta_file_name = os.path.splitext(os.path.basename(fasta_file))[0] 
    169    database = DATABASE_MAP[organism.lower()]
    170  
    171    #Run VIGOR4 for the database
    172    try:
>>  173      vigor4_cmd = ["vigor4", "-i", fasta_file, "-o", fasta_file_name, "-d", database] 
    174      subprocess.check_call(vigor4_cmd, shell=False)
    175    except Exception as e:
    176      print("Error running VIGOR4 for %s using database %s:\n %s" %(fasta_file, database, e))
    177      return False
    178  
    179    return True
    180  
    181  def parseCDSFile(cds_file_path):
    182    result = {}
    183  
    184    if os.path.isfile(cds_file_path):
    185      cf = open(cds_file_path)
```

## `plbin/p3x-annotate-vigor4.pl:2`

```
      1  #
>>    2  # Use vigor4 to annotate the given genome.
      3  #
      4  
      5  
      6  use strict;
      7  use Data::Dumper;
      8  use Time::HiRes 'gettimeofday';
      9  use gjogenbank;
     10  use gjoseqlib;
     11  use GenomeTypeObject;
     12  use Getopt::Long::Descriptive;
     13  use File::Copy;
     14  use IPC::Run qw(run);
```

## `plbin/p3-submit-genome-annotation.pl:43`

```
     37  	--reference-genome STR                The BV-BRC identifier of a
     38  	                                      reference genome whose
     39  	                                      annotations will be propagated
     40  	                                      as part of this annotation.
     41  	--reference-virus STR                 The name of a virus from the
     42  	                                      VIGOR_DB collection to use as
>>   43  	                                      the reference for a vigor4
     44  	                                      viral annotation.
     45  	                                    
     46  	The following options describe the genome to be annotated.
     47  	In each case where the value for the specified option may be drawn
     48  	from a submitted genbank file it is optional to supply the value.
     49  	If a value is supplied, it will override the value in the genbank file.
     50  	                                    
     51  	-n STR --scientific-name STR          Scientific name for this genome.
     52  	-t INT --taxonomy-id INT              Numeric NCBI taxonomy ID for
     53  	                                      this genome. If not specified
     54  	                                      an estimate will be computed,
     55  	                                      and if that is not possible the
```

## `plbin/p3x-annotate-mat-peptide.pl:78`

```
     72  
     73  {
     74      my $gto_for_gb = GenomeTypeObject->create_from_file($input_gto);
     75      $gto_for_gb or die "Could not parse input gto\n";
     76  
     77      #
>>   78      # Check for vigor4 features.
     79      #
     80      my $vigor_ae;
     81      for my $ae ($gto_for_gb->analysis_events)
     82      {
>>   83  	if ($ae->{tool_name} eq 'vigor4')
     84  	{
     85  	    $vigor_ae = $ae;
     86  	    last;
     87  	}
     88      }
     89  
     90      my @to_del;
     91  
     92      for my $f ($gto_for_gb->features)
     93      {
     94  	if ($f->{type} eq 'mat_peptide')
     95  	{
```

## `plbin/p3x-annotate-vigor4.pl:77`

```
     71      warn "No reference found\n";
     72      $genome_in->destroy_to_file($opt->output);
     73      exit 0;
     74  }
     75  
     76  #
>>   77  # Invoke vigor4 to annotate viral genome.
     78  #
     79  # Write contigs as fasta file.
>>   80  # Invoke vigor4, using the reference that was passed in as the reference_name parameter;
     81  # We parse the .pep file that is generated. It contains two feature types.
     82  # This is a CDS:
     83  # >NC_045512.1 location=266..13468,13471..21555 codon_start=1 gene="orf1ab" ref_db="covid19" ref_id="YP_009724389.1"
     84  # This is a mature peptide:
     85  # >NC_045512.1.1 mat_peptide location=266..805 gene="orf1ab" product="leader protein" ref_db="covid19_orf1ab_mp" ref_id="YP_009725297.1"
     86  #
     87  # We create features of type CDS and mat_peptide.
     88  #
     89  
     90  my $sequences_file = $genome_in->extract_contig_sequences_to_temp_file();
     91  
     92  my $ref_dir = vigor_reference_db_directory;
```

## `plbin/p3x-annotate-vigor4.pl:238`

```
    232  	{
    233  	    my $p = {
    234  		-id	     => $genome_in->new_feature_id($id_type),
    235  		-type 	     => $type,
    236  		-location 	     => $feature->{location},
    237  		-analysis_event_id 	     => $event_id,
>>  238  		-annotator => 'vigor4',
    239  		-protein_translation => $feature->{aa_sequence},
    240  		-alias_pairs => [[gene => $feature->{gene}]],
    241  		-function => $feature->{product},
    242  		-quality_measure => $feature->{quality},
    243  		-genbank_feature => $feature->{genbank_feature},
    244  	    };
    245  	    #die Dumper($p);
    246  	    
    247  	    $genome_in->add_feature($p);
    248  	}
    249      }
    250      
```

## `lib/Bio/P3/MetagenomeBinning/MetagenomeBinning.pm:929`

```
    923      # Lenarviricota 2732407
    924      # unclassified bacterial viruses 12333
    925      # Cystoviridae 10877
    926      # unclassified dsDNA phages 79205
    927  
    928      #
>>  929      # We also look up the taxon IDs of the bins in the vigor4 taxonomy map.
    930      #
    931  
    932      my @annotated_bins;
    933      my @unannotated_bins;
    934  
    935      my $api = P3DataAPI->new(data_api_url);
    936      my $app_spec = $self->find_app_spec("GenomeAnnotation");
    937  
    938      my $sub_time = time;
    939      my $n = 1;
    940      my $recipe = $self->params->{viral_recipe} // "viral";
    941      for my $bin (@$bins)
```

