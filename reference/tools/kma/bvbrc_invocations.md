# BV-BRC invocations of `kma` (kma)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 3 hunk(s) in 3 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/MetagenomicReadMapping/MetagenomicReadMappingReport.tt`
- `lib/Bio/P3/MetagenomicReadMapping/Report.pm`
- `plbin/App-MetagenomicReadMapping.pl`

## `plbin/App-MetagenomicReadMapping.pl:190`

```
    184        my $db_path = kma_db . "/$db_dir";
    185        my $kma_identity = 70;
    186  
    187        -f "$db_dir.name" or die "Database file for $db_dir not found\n";
    188  
    189        my @input_params = stage_input($app, $params, $staging_dir);
>>  190        my $output_base = "$output_dir/kma";
>>  191        @cmd = ("kma");
    192        push(@cmd,
    193            "-ID", $kma_identity,
    194            "-t_db", $db_dir,
    195            "-ef",
    196            @input_params,
    197            "-o", $output_base);
    198      #
    199      # If we are running under Slurm, pick up our memory and CPU limits.
    200      #
    201      my $mem = $ENV{P3_ALLOCATED_MEMORY};
    202      my $cpu = $ENV{P3_ALLOCATED_CPU};
    203  
```

## `lib/Bio/P3/MetagenomicReadMapping/MetagenomicReadMappingReport.tt:42`

```
     36  
     37  The table below shows results from read mapping
     38  [% IF params.gene_set_type == "predefined_list" -%]
     39  against the selected template database [% params.gene_set_name %]
     40  [% END -%]
     41  using
>>   42  <a target="_blank" href="https://bitbucket.org/genomicepidemiology/kma">KMA</a>
     43  (<a target="_blank" href="https://www.ncbi.nlm.nih.gov/pubmed/30157759">reference</a>).
     44  The matching
     45  reference genes are shown as <i>Template</i> and the input reads are shown
     46  as <i>Query</i>. The table provides a summary of the most common statistics for
     47  each mapped template.
     48  <p>
     49  
     50  
     51  <table border="1">
     52  <tr>
     53  [% FOR h IN results_header -%]
     54  <th>[% h %]</th>
```

## `lib/Bio/P3/MetagenomicReadMapping/Report.pm:17`

```
     11  use base qw(Exporter);
     12  our @EXPORT_OK = qw(write_report);
     13  
     14  #
     15  # Write the read mapping report
     16  #
>>   17  # $output_base is the path including output prefix to which the kma output is written.
     18  #
     19  # Thus we have output files $output_base.fsa, $output_base.res, etc.
     20  #
     21  
     22  sub write_report
     23  {
     24      my($task_id, $params, $output_base, $output_fh) = @_;
     25  
     26      my $templ = Template->new(ABSOLUTE => 1);
     27      my $tax_base = 'https://www.bv-brc.org/view/Taxonomy';
     28      #my $genome_base = 'https://www.bv-brc.org/view/GenomeList';
     29  	my $genome_base;
```

