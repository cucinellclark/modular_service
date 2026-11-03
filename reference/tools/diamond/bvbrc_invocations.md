# BV-BRC invocations of `diamond` (diamond)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 7 hunk(s) in 6 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/KBase/GenomeAnnotation/GenomeAnnotationImpl.pm`
- `lib/Bio/KBase/KIDL/sapling_spec.tt`
- `plbin/build_blast_dbs.pl`
- `plbin/compile_dbd_to_typespec.pl`
- `plbin/dbd_to_iplant.pl`
- `plbin/p3x-compute-specialty-blast.pl`

## `lib/Bio/KBase/GenomeAnnotation/GenomeAnnotationImpl.pm:5225`

```
   5219  		   "--parallel", $threads);
   5220      
   5221      my @cmd_blast = ("p3x-compute-specialty-blast",
   5222  		     "--tabular", "specialty-blast.txt",
   5223  		     "--report", "specialty-blast-alignments.txt",
   5224  		     "--db-dir", $self->{specialty_genes_blast},
>> 5225  		     "--program", "diamond",
   5226  		     "--parallel", $threads);
   5227  
   5228      #
   5229      # We set this up as a pipeline to avoid writing intermediate files.
   5230      #
   5231  
   5232      my $enc = encode_json($genome_in);
   5233  
   5234      my $out;
   5235      my $ok = run(\@cmd_amr, "<", \$enc,
   5236  		 "|",
   5237  		 \@cmd_rgi,
```

## `plbin/build_blast_dbs.pl:140`

```
    134  
    135  	}
    136  
    137  	close FAA; 
    138  
    139  	makeBlastDB($faa_file, "prot") if grep {$_ eq "blast"} @db_type;
>>  140  	makeDiamondDB($faa_file) if grep {$_ eq "diamond"} @db_type;
    141  
    142  }
    143  
    144  sub makeBlastDB {
    145  
    146  	my ($fasta_file, $db_type) = @_;
    147  
    148  	`makeblastdb -in "$fasta_file" -dbtype $db_type`;
    149  
    150  }
    151  
    152  
    153  sub makeDiamondDB {
    154  
    155  	my ($fasta_file) = @_;
    156  
>>  157  	`diamond makedb --in "$fasta_file" --db "$fasta_file"`;
    158  
    159  }
```

## `plbin/p3x-compute-specialty-blast.pl:170`

```
    164  		   "-num_threads", $opt->parallel,
    165  		   "-num_alignments", 1,
    166  		   "-num_descriptions", 1,
    167  		   "-evalue", $opt->evalue,
    168  		   "-outfmt", 0);
    169      }
>>  170      elsif ($opt->program eq 'diamond')
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

## `plbin/p3x-compute-specialty-blast.pl:58`

```
     52  # Since we don't use human homologs any more, the required parameters are as follows.
     53  #
     54  my $min_qcov = 80;
     55  my $min_scov = 80;
     56  my $min_iden = 80;
     57  
>>   58  if ($opt->program ne 'blast' && $opt->program ne 'blat' && $opt->program ne 'diamond')
     59  {
>>   60      die "Invalid value for --program option (must be either 'blast', 'blat', or 'diamond')\n";
     61  }
     62  
     63  my $db_dir = $opt->db_dir;
     64  
     65  $db_dir or die "Database directory must be specified.\n";
     66  -d $db_dir or die "Database directory $db_dir not found.\n";
     67  
     68  chomp(my $hostname = `hostname -f`);
     69  
     70  my $orig_dir = getcwd();
     71  my $work_dir = File::Temp->newdir();
     72  
```

## `plbin/compile_dbd_to_typespec.pl:71`

```
     65  my %type_map = (boolean	    => 'int',
     66  		'semi-boolean'	=> 'string',
     67  		char	    => 'string',
     68  		countVector => 'countVector',
     69  		counter	    => 'int',
     70  		date	    => 'string',
>>   71  		diamond	    => 'diamond',
     72  		dna	    => 'string',
     73  		float	    => 'float',
     74  		image	    => 'string',
     75  		int	    => 'int',
     76  		link	    => 'string',
     77  		rectangle   => 'rectangle',
     78  		string	    => 'string',
     79  		'long-string'	    => 'string',
     80  		text	    => 'string',
     81  		);
     82  
     83  
```

## `plbin/dbd_to_iplant.pl:93`

```
     87  my %type_map = (boolean	    => 'xs:boolean',
     88  		'semi-boolean'	=> 'xs:string',
     89  		char	    => 'xs:string',
     90  		countVector => 'xs:string',
     91  		counter	    => 'xs:integer',
     92  		date	    => 'xsstring',
>>   93  		diamond	    => 'xs:string',
     94  		dna	    => 'xs:string',
     95  		float	    => 'xs:float',
     96  		image	    => 'xs:string',
     97  		int	    => 'xs:integer',
     98  		link	    => 'xs:string',
     99  		rectangle   => 'xs:string',
    100  		string	    => 'xs:string',
    101  		'long-string'	    => 'xs:string',
    102  		text	    => 'xs:string',
    103  		);
    104  
    105  my %kids;
```

## `lib/Bio/KBase/KIDL/sapling_spec.tt:2`

```
      1  module [% service %] : [% module %] {
>>    2      typedef string diamond;
      3      typedef string countVector;
      4      typedef string rectangle;
      5  
      6      /*
      7      Wrapper for the GetAll function documented L<here|http://pubseed.theseed.org/sapling/server.cgi?pod=ERDB#GetAll>.
      8      Note that the object_names and fields arguments must be strings; array references are not allowed.
      9      */
     10      funcdef get_all(string object_names,
     11  		    string filter_clause,
     12  		    list<string> parameters,
     13  		    string fields,
     14  		    int count) returns(list<list<string>> result_set);
```

