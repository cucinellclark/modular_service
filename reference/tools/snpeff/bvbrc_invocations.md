# BV-BRC invocations of `snpEff.sh` (snpeff)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 2 hunk(s) in 1 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/App-Variation.pl`

## `plbin/App-Variation.pl:35`

```
     29      $ENV{PATH} = "$path_prefix:$ENV{PATH}";
     30  }
     31  
     32  #
     33  # Find right snpeff name to use
     34  #
>>   35  my @snpEffOptions = qw(snpEff.sh snpEff);
     36  my $snpEffPath;
     37  for my $snpEffTest (@snpEffOptions)
     38  {
     39      my $vers;
     40      print "Try '$snpEffTest'\n";
     41      my $ok = eval { run([$snpEffTest, "-version"], ">", \$vers); };
     42      if ($ok)
     43      {
     44  	my($path) = File::Which::which($snpEffTest);
     45  	warn "Using $path version $vers\n";
     46  	$snpEffPath = $path;;
     47  	last;
     48      }
     49  }
>>   50  $snpEffPath or die "Cannot find snpEff in $ENV{PATH}; options are @snpEffOptions\n";
     51  
     52  use Bio::KBase::AppService::AppConfig;
     53  use Bio::KBase::AppService::AppScript;
     54  use Bio::KBase::AppService::ReadSet;
     55  
     56  my $data_url = Bio::KBase::AppService::AppConfig->data_api_url;
     57  my $script = Bio::KBase::AppService::AppScript->new(\&process_variation_data, \&preflight);
     58  
     59  my $rc = $script->run(\@ARGV);
     60  exit $rc;
     61  
     62  our $global_ws;
```

## `plbin/App-Variation.pl:582`

```
    576      $summary .= "\n\nOutput summary:\n";
    577      $summary .= "all.var.tsv             - combined sheet of annotated variants from all libraries\n";
    578      $summary .= "all.var.html            - sortable HTML table of all annotated variants\n";
    579      $summary .= "libs.txt                - mapping from read library to file(s)\n";
    580      $summary .= "<LIB>.aln.bam           - $mapper aligned reads for a read library\n";
    581      $summary .= "<LIB>.var.vcf           - $caller generated high quality variants for a read library\n";
>>  582      $summary .= "<LIB>.var.snpEff.vcf    - snpEff augmented VCF with variant effect prediction\n";
    583      $summary .= "<LIB>.var.annotated.tsv - PATRIC annotated variants in a spreadsheet\n";
    584      $summary .= "<LIB> denotes the name of a read library (e.g., PE1 for paired end 1, SE3 for single end 3).\n";
    585      $summary .= "\nResults by read library:\n";
    586  
    587      my $lib_txt = "$tmpdir/libs.txt";
    588      my @lines = `tail -n $n_libs $lib_txt`;
    589      my $i;
    590      for (@$libs) {
    591          my ($lib, $reads) = split(/\t/, $lines[$i]); chomp($reads);
    592          $i++;
    593          $summary .= "\n[$i] $lib ($reads)\n\n";
    594          my $sumfile = "$tmpdir/$lib/summary.txt";
```

