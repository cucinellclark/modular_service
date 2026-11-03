# BV-BRC invocations of `mlst` (mlst)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 7 hunk(s) in 5 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/p3x-compute-cgmlst.pl`
- `plbin/p3x-compute-mlst.pl`
- `plbin/p3x-newick-to-phyloxml.pl`
- `plbin/rast_export_genome.pl`
- `plbin/update_local_mlstdb.pl`

## `plbin/p3x-compute-mlst.pl:29`

```
     23  				     
     24  print($usage->text), exit if $opt->help;
     25  print($usage->text), exit 1 if (@ARGV != 0);
     26  
     27  chomp(my $hostname = `hostname -f`);
     28  
>>   29  # mlst /vol/patric3/downloads/genomes/83332.12/83332.12.fna
     30  
     31  my $gto_in;
     32  
     33  if ($opt->in)
     34  {
     35      $gto_in = GenomeTypeObject->new({file => $opt->in});
     36      $gto_in or die "Error reading GTO from " . $opt->in . "\n";
     37  }
     38  else
     39  {
     40      $gto_in = GenomeTypeObject->new({file => \*STDIN});
     41      $gto_in or die "Error reading GTO from standard input\n";
     42  }
     43  
     44  my $in_file = File::Temp->new();
     45  
     46  $gto_in->write_contigs_to_file($in_file);
     47  
>>   48  my @cmd = ("mlst", $in_file);
     49  
     50  print STDERR "Invoke mlst: @cmd\n";
     51  
     52  my($stdout, $stderr);
     53  my $ok = run(\@cmd,
     54  	     ">", \$stdout,
     55  	     "2>", \$stderr);
     56  
     57  $ok or die "Error $? running @cmd\n";
     58  
     59  chomp $stdout;
     60  
```

## `plbin/p3x-newick-to-phyloxml.pl:55`

```
     49  
     50  #$| = 1;
     51  # Get the command-line options.
     52  
     53  my($opt, $usage) = P3Utils::script_opts('newickFile',
     54                  ['databaselink|link|l=s', 'Name of database field that tree identifiers map to (feature_id, genome_id, patric_id).'],
>>   55                  ['genomefields|g=s', 'Comma-separated list of genome fields to annotate each tree tip.', {default => 'species,strain,geographic_group,isolation_country,host_group,host_common_name,collection_year,genus,mlst'}],
     56                  ['featurefields|f=s', 'Comma-separated list of feature fields to annotate each tree tip.', {default => 'product,accession'}],
     57                  ['output_name=s', 'Output filename.'],
     58                  ['name_with_all_fields', 'Construct output file to include all fields.'],
     59                  ['overwrite|o', 'Overwrite existing files if any.'],
     60                  ['verbose|debug|v', 'Write status messages to STDERR.'],
     61                  ['name=s', 'Name for tree in phyloxml.'],
     62                  ['remove_substring|r=s', 'Substring to be removed from finalized data'],
     63                  ['description=s', 'Description of tree in phyloxml.'],
     64                  ['gtdb_bvbrc=s', 'Translation table from GTDB IDs to BVBRC genome IDs.'],
     65                  ['annotationtsv|a=s', 'TSV file containing annotation for tips on the tree (or comma-delimited list)'],
     66                  ['provenance|p=s', 'Provenance of annotation. (default: BVBRC)', { default => 'BVBRC' }],
     67          );
```

## `plbin/update_local_mlstdb.pl:133`

```
    127  		
    128  		#print "checking $profileId.\n";
    129  		
    130  		$total++;
    131  		
    132  		# update the metadata file with the new retrieval
>>  133  		my $newDate=$sp->{"mlst"}->{"database"}->{"retrieved"};
    134  		chomp $newDate;
>>  135  		my $newCount=$sp->{"mlst"}->{"database"}->{"profiles"}->{"count"};
    136  		chomp $newCount;
    137  		
    138  		if ($newCount==0) {
    139  			system("rm -f $prodir/$profileId.pro.txt");
    140  			system("rm -rf $seqdir/$profileId/");
    141  			next;
    142  		}
    143  		
    144  		# only update if the date and count are different
    145  		unless (doUpdate(\%metadata, $profileId, $newDate, $newCount)) {
    146  			print "$profileId is unchanged.\n";
    147  			next;
```

## `plbin/update_local_mlstdb.pl:156`

```
    150  		print "$profileId has been changed.\n";
    151  		print "  updating profile, loci, and blast data.\n";
    152  	
    153  		# get the profile list and save it locally
    154  		# tab-delim file, header is:
    155  		# ST	locus1..locusn	[clonal_complex|mlst_clade]
>>  156  		if (defined $sp->{'mlst'} and defined $sp->{'mlst'}->{'database'} and defined $sp->{'mlst'}->{'database'}->{'profiles'} and defined $sp->{'mlst'}->{'database'}->{'profiles'}->{'url'}) {
>>  157  			my $u = $sp->{'mlst'}->{'database'}->{'profiles'}->{'url'};
    158  			chomp $u;
    159  			system("curl -s -S $u -o $prodir/$profileId.pro.txt");
    160  		} else {
    161  			print STDERR "ERROR: unable to get profile for $profileId.\n";
    162  			next;
    163  		}
    164  		
>>  165  		unless (defined $sp->{"mlst"}->{"database"}->{"loci"} and defined $sp->{"mlst"}->{"database"}->{"loci"}->{"locus"}) {
    166  			print STDERR "ERROR: No locus information available for $profileId!\n";
    167  			next;
    168  		}
    169  		
>>  170  		my $count = scalar @{$sp->{"mlst"}->{"database"}->{"loci"}->{"locus"}};
    171  		if ($count<1) {
    172  			print STDERR "ERROR: No locus information available for $profileId!\n";
    173  			next;
    174  		}
    175  		
    176  		print "  updating $count loci.\n";
    177  		
    178  		# for each locus in this profile
    179  		mkdir "$seqdir/$profileId";
    180  		my @locusStats=();
    181  		
>>  182  		foreach my $locus (@{$sp->{"mlst"}->{"database"}->{"loci"}->{"locus"}}) {
    183  	
    184  			# download the latest seq file (fa format; header is locus_id)
    185  			my $locusName=$locus->{"content"};
    186  			chomp $locusName;
    187  			my $locusUrl=$locus->{"url"};
    188  			chomp $locusUrl;
    189  			system("curl -s -S $locusUrl -o $seqdir/$profileId/$locusName.fna");
    190  			
    191  			open my $testFH, "<", "$seqdir/$profileId/$locusName.fna";
    192  			unless (defined $testFH) {
    193  				print STDERR "ERROR: $profileId $locusName: No sequence file!\n";
    194  				next;
```

## `plbin/p3x-compute-cgmlst.pl:2`

```
      1  #
>>    2  # Compute genome MLST using https://github.com/tseemann/mlst
      3  #
      4  
      5  use Bio::KBase::AppService::AppConfig qw(application_backend_dir);
      6  use P3DataAPI;
      7  use strict;
      8  use Getopt::Long::Descriptive;  
      9  use File::Temp;
     10  use File::Copy;
     11  use File::Slurp;
     12  use GenomeTypeObject;
     13  use Cwd;
     14  use Data::Dumper;
```

## `plbin/p3x-compute-mlst.pl:2`

```
      1  #
>>    2  # Compute genome MLST using https://github.com/tseemann/mlst
      3  #
      4  
      5  use strict;
      6  use Getopt::Long::Descriptive;  
      7  use File::Temp;
      8  use File::Copy;
      9  use GenomeTypeObject;
     10  use Cwd;
     11  use Time::HiRes qw(gettimeofday);
     12  use File::Slurp;
     13  use JSON::XS;
     14  use Data::Dumper;
```

## `plbin/rast_export_genome.pl:848`

```
    842  
    843  sub export_patric_genome_metadata
    844  {
    845      my($genomeTO, $out_fh) = @_;
    846  
    847      my @headings = qw(genome_id genome_name organism_name taxon_id genome_status strain serovar biovar 
>>  848  		      pathovar mlst other_typing culture_collection type_strain 
    849  		      completion_date publication bioproject_accession biosample_accession 
    850  		      assembly_accession genbank_accessions refseq_accessions 
    851  		      sequencing_centers sequencing_status sequencing_platform sequencing_depth assembly_method 
    852  		      chromosomes plasmids contigs sequences genome_length gc_content patric_cds brc1_cds refseq_cds 
    853  		      isolation_site isolation_source isolation_comments collection_date isolation_country 
    854  		      geographic_location latitude longitude altitude depth other_environmental 
    855  		      host_name host_gender host_age host_health body_sample_site body_sample_subsite 
    856  		      other_clinical antimicrobial_resistance antimicrobial_resistance_evidence gram_stain 
    857  		      cell_shape motility sporulation temperature_range optimal_temperature salinity 
    858  		      oxygen_requirement habitat disease comments additional_metadata source source_id);
    859  
    860      print $out_fh join("\t", @headings), "\n";
```

