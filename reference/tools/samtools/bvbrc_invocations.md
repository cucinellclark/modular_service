# BV-BRC invocations of `samtools` (samtools)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 38 hunk(s) in 21 file(s); showing top 25.
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/CmdRunner.pm`
- `lib/Bio/P3/SARS2Assembly/primer_schemes/import-varskip`
- `lib/fastq_utils.py`
- `lib/process.py`
- `lib/report.py`
- `plbin/App-RNASeq.pl`
- `plbin/App-Variation.pl`
- `plbin/sars2-cdc-illumina.pl`
- `plbin/sars2-cdc-nanopore.pl`
- `plbin/sars2-onecodex.pl`
- `plbin/var-map.pl`
- `pybin/fastq_utils.py`
- `pybin/p3_tnseq.py`
- `pybin/p3x-assembly.py`
- `pybin/reference_guided_assembly.py`
- `pybin/run_rnaseq.py`
- `pybin/run_viral_assembly.py`
- `workflows/bvbrc_SARS2Wastewater/scripts/prep_results.py`
- `workflows/bvbrc_SARS2Wastewater/snakefile/pe_freyja_snakefile`
- `workflows/bvbrc_SARS2Wastewater/snakefile/se_freyja_snakefile`
- `workflows/bvbrc_SARS2Wastewater/snakefile/stats_snakefile`

## `plbin/App-RNASeq.pl:561`

```
    555      for my $f (@sams) {
    556          my $sam = basename($f);
    557          my $bam = $sam;
    558          $bam =~ s/_R[12]\.sam$/.sam/;
    559          $bam =~ s/\.sam$/.bam/;
    560          $bam = "$dir/$bam";
>>  561          # my @cmd = ("samtools", "view", "-bS", $f, "-o", $bam);
>>  562          my @cmd = ("samtools", "sort", "-T", "$f.temp", "-O", "bam","-o", $bam, $f);
    563          run_cmd(\@cmd);
    564          push @outputs, [ $bam, 'bam' ];
>>  565          @cmd = ("samtools", "index", $bam);       
    566          run_cmd(\@cmd);
    567          push @outputs, [ "$bam.bai", 'bai' ];
    568      }
    569      push @outputs, ["$dir/summary.txt", 'txt'];
    570      
    571      return @outputs;
    572  }
    573  
    574  sub prepare_ref_data_rocket {
    575      my ($gid, $basedir, $host, $host_ftp) = @_;
    576      $gid or die "Missing reference genome id\n";
    577      
```

## `plbin/sars2-cdc-illumina.pl:242`

```
    236  }
    237     
    238  #
    239  # Create bam format output
    240  #
    241  
>>  242  $runner->run(["samtools", "view", "-b", $samfile],
    243  	 "|",
>>  244  	 ["samtools", "sort", "-", "--threads", $threads, "-o", $bamfile]);
    245  
>>  246  $runner->run(["samtools", "index", $bamfile]);
    247  
    248  #
    249  # Create consensus
    250  #
    251  my $use_bcftools_mpileup = 1;
    252  my @con1;
    253  if ($use_bcftools_mpileup)
    254  {
    255      @con1 = (qw(bcftools mpileup -f), $reference, $bamfile);
    256  }
    257  else
    258  {
>>  259      @con1 = ( qw(samtools mpileup -aa -d 8000 -uf), $reference, $bamfile);
    260  }
    261  my @con2 = qw(bcftools call -Mc);
    262  my @con3 = ("tee", "-a", $vcf );
    263  my @con4 = qw(vcfutils.pl vcf2fq -D 100000000);
    264  push(@con4, "-d", $opt->min_depth);
    265  my @con5 = qw(seqtk seq -A -);
    266  my @con6 = qw(sed 2~2s/[actg]/N/g);
    267  my @con7 = qw(seqtk seq -l 60 -);
    268  
    269  $runner->run(\@con1, '|',
    270  	 \@con2, '|',
    271  	 \@con3, '|',
```

## `plbin/sars2-onecodex.pl:67`

```
     61  				    ["primers=s" => "Use these primers. Choices are @primer_names"],
     62  				    ["primer-version=s" => "Use the specfiied version of the chosen primers. Default is the latest available version"],
     63  				    ["length-threshold|l=i" => "Max length to be considered short read sequencing", { default => 600 }],
     64  				    ["nanopore" => "Force use of nanopore mapping method"],
     65  				    ["keep-intermediates|k" => "Save all intermediate files"],
     66  				    ["delete-reads" => "Delete reads when they have been processed"],
>>   67  				    ["samtools-sort-timeout=i" => "Timeout for samtools sort", { default => 960 }],
     68  				    ["help|h"      => "Show this help message"],
     69  				    );
     70  
     71  
     72  print($usage->text), exit 0 if $opt->help;
     73  die($usage->text) unless @ARGV == 2;
     74  
     75  $opt->primers or die "Primers must be defined using the --primers flag. Available primers are @primer_names\n";
     76  
     77  my($reference, $bed_file);
     78  if ($opt->bed_file || $opt->reference)
     79  {
```

## `plbin/var-map.pl:147`

```
    141      # handle the case "The fasta sequence does not match the REF allele" 
    142      print "compute_consensus: $consensus_error\n";
    143      
    144      if ($consensus_error =~ /The fasta sequence does not match the REF allele/) {
    145        print "revise and index ref.fa\n";
    146        run("sed -E '/^>/! s/[^ACGTacgt]/N/g' ref.fa > modified_ref.fa");
>>  147        run("samtools faidx modified_ref.fa");
    148        print "run bcftools norm\n";
    149        run("bcftools norm -f modified_ref.fa var.vcf.gz -o var.norm.vcf");
    150        run("bgzip -c var.norm.vcf > var.norm.vcf.gz");
    151        run("bcftools index var.norm.vcf.gz");
    152        run("bcftools consensus -c chain -f modified_ref.fa var.norm.vcf.gz > consensus");
    153        print "compute_consensus ended\n";
    154      }
    155  }
    156  
    157  sub compute_stats {
>>  158      verify_cmd(qw(samtools bedtools));
>>  159      -s "ref.fa.fai"     or run("samtools faidx ref.fa");
    160      if (-s "aln.raw.sam") {
>>  161        -s "raw.flagstat" or run("samtools flagstat aln.raw.sam > raw.flagstat");
    162      }
    163      if (-s "aln.bam") {
>>  164        -s "flagstat"       or run("samtools flagstat aln.bam > flagstat");
>>  165        -s "stats"          or run("samtools stats aln.bam -c 1,8000,1 > stats");
>>  166        # -s "depth"          or run("samtools depth aln.bam > depth");
    167        -s "depth"          or run("bedtools genomecov -ibam aln.bam -d > depth");
    168        -s "depth.hist"     or run("bedtools genomecov -ibam aln.bam > depth.hist");
    169        -s "cov.bedgraph"   or run("bedtools genomecov -ibam aln.bam -bga > cov.bedgraph");
    170        -s "uncov.10"       or run("bedtools genomecov -ibam aln.bam -bga | perl -ne 'chomp; \@c=split/\t/; \$ln=\$c[2]-\$c[1]; print join(\"\\t\", \@c, \$ln).\"\\n\" if \$c[3]<10;' > uncov.10" );
>>  171        -s "ref.fa.fai"     or run ("samtools faidx ref.fa");
    172        -s "chrom.sizes"     or run ("cut -f1,2 ref.fa.fai > chrom.sizes");
    173        -s "cov.bigwig"     or run ("bedGraphToBigWig cov.bedgraph chrom.sizes cov.bigwig");
    174        # BED start position 0-based and the end position 1-based (Example: NC_000962,1987085,1987701,0,616; the 0 coverage base really starts at 1987086)
    175      }
    176  }
    177  
    178  sub map_with_bwa_mem {
>>  179      verify_cmd(qw(bwa samtools));
    180      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    181      -s "read_1.fq"      or run_symlink($read1, "read_1.fq");
    182      -s "read_2.fq"      or run_symlink($read2, "read_2.fq");
    183      -s "ref.fa.bwt"     or run("bwa index ref.fa");
    184      -s "aln-pe.sam"     or run("bwa mem -t $nthread ref.fa read_1.fq read_2.fq > aln-pe.sam 2>mem.log");
    185      -s "aln.raw.sam"    or run("ln -s -f aln-pe.sam aln.raw.sam");
>>  186      -s "aln.keep.bam"   or run("samtools view -@ $nthread -f 0x2 -bS aln.raw.sam > aln.keep.bam"); # keep only properly paired reads
>>  187      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
>>  188      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
>>  189    # -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread aln.keep.bam aln.sorted"); # v1.1
>>  190      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    191      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
    192    # -s "aln.bam"        or run("ln -s -f aln.sorted.bam aln.bam");
>>  193    # -s "aln.bam.bai"    or run("samtools index aln.bam"); # v1.1
>>  194      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    195  }
    196  
    197  sub map_with_bwa_mem_se {
>>  198      verify_cmd(qw(bwa samtools));
    199      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    200      -s "read.fq"        or run_symlink($read1, "read.fq");
    201      -s "ref.fa.bwt"     or run("bwa index ref.fa");
    202      -s "aln-se.sam"     or run("bwa mem -t $nthread ref.fa read.fq > aln-se.sam 2>mem.log");
    203      -s "aln.raw.sam"    or run("ln -s -f aln-se.sam aln.raw.sam");
>>  204      -s "aln.keep.bam"   or run("samtools view -@ $nthread -bS aln.raw.sam > aln.keep.bam");
>>  205      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
>>  206      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
>>  207      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    208      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
>>  209      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    210  }
    211  
    212  sub map_with_bwa_mem_strict {
>>  213      verify_cmd(qw(bwa samtools));
    214      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    215      -s "read_1.fq"      or run_symlink($read1, "read_1.fq");
    216      -s "read_2.fq"      or run_symlink($read2, "read_2.fq");
    217      -s "ref.fa.bwt"     or run("bwa index ref.fa");
    218      -s "aln-pe.sam"     or run("bwa mem -B9 -O16 -E1 -L5 -t $nthread ref.fa read_1.fq read_2.fq > aln-pe.sam 2>mem.log");
    219      -s "aln.raw.sam"    or run("ln -s -f aln-pe.sam aln.raw.sam");
>>  220      -s "aln.keep.bam"   or run("samtools view -@ $nthread -f 0x2 -q 10 -bS aln.raw.sam > aln.keep.bam"); # keep only properly paired reads
>>  221      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
>>  222      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
>>  223      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    224      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
>>  225      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    226  }
    227  
    228  sub map_with_bwa_mem_strict_se {
>>  229      verify_cmd(qw(bwa samtools));
    230      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    231      -s "read.fq"        or run_symlink($read1, "read.fq");
    232      -s "ref.fa.bwt"     or run("bwa index ref.fa");
    233      -s "aln-se.sam"     or run("bwa mem -B9 -O16 -E1 -L5 -t $nthread ref.fa read.fq > aln-se.sam 2>mem.log");
    234      -s "aln.raw.sam"    or run("ln -s -f aln-se.sam aln.raw.sam");
>>  235      -s "aln.keep.bam"   or run("samtools view -@ $nthread -bS -q 10 aln.raw.sam > aln.keep.bam");
>>  236      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
>>  237      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
>>  238      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    239      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
>>  240      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    241  }
    242  
    243  sub map_with_bowtie2 {
>>  244      verify_cmd(qw(bowtie2-build bowtie2 samtools));
    245      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    246      -s "read_1.fq"      or run_symlink($read1, "read_1.fq");
    247      -s "read_2.fq"      or run_symlink($read2, "read_2.fq");
    248      -s "ref.1.bt2"      or run("bowtie2-build ref.fa ref");
    249      -s "aln.raw.sam"    or run("bowtie2 -p $nthread -x ref -1 $read1 -2 $read2 -S aln.raw.sam");
>>  250      -s "aln.keep.bam"   or run("samtools view -@ $nthread -f 0x2 -q 10 -bS aln.raw.sam > aln.keep.bam"); # keep only properly paired reads
>>  251      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
>>  252      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
>>  253      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    254      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
>>  255      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    256  }
    257  
    258  sub map_with_bowtie2_se {
>>  259      verify_cmd(qw(bowtie2-build bowtie2 samtools));
    260      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    261      -s "read.fq"        or run_symlink($read1, "read.fq");
    262      -s "ref.1.bt2"      or run("bowtie2-build ref.fa ref");
    263      -s "aln.raw.sam"    or run("bowtie2 -p $nthread -x ref -U $read1 -S aln.raw.sam");
>>  264      -s "aln.keep.bam"   or run("samtools view -@ $nthread -bS -q 10 aln.raw.sam > aln.keep.bam");
>>  265      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
>>  266      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
>>  267      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    268      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
>>  269      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    270  }
    271  
    272  sub map_with_mosaik {
    273      # https://github.com/wanpinglee/MOSAIK/wiki/QuickStart
>>  274      verify_cmd(qw(MosaikBuild MosaikAligner samtools));
    275      my $bin_dir = dirname(which('MosaikAligner'));
    276      verify_file("$bin_dir/2.1.78.se.ann", "$bin_dir/2.1.78.pe.ann");
    277      -s "se.ann"         or run("ln -s -f $bin_dir/2.1.78.se.ann se.ann");
    278      -s "pe.ann"         or run("ln -s -f $bin_dir/2.1.78.pe.ann pe.ann");
    279      -s "ref.fa"         or run("ln -s -f $ref ref.fa");
    280      -s "read_1.fq"      or run("ln -s -f $read1 read_1.fq");
    281      -s "read_2.fq"      or run("ln -s -f $read2 read_2.fq");
    282      -s "ref.dat"        or run("MosaikBuild -fr ref.fa -oa ref.dat");
    283      -s "reads.mkb"      or run("MosaikBuild -q read_1.fq -q2 read_2.fq -out reads.mkb -st illumina -mfl 500");
    284      system("ls -l reads.mkb");
    285      sleep 5;
    286      system("ls -l reads.mkb");
    287      -s "reads.mka.bam"  or run("MosaikAligner -in reads.mkb -out reads.mka -ia ref.dat -p $nthread -annpe pe.ann -annse se.ann");
    288      -s "aln.raw.sam"    or run("ln -s -f reads.mka.bam aln.raw.sam");
>>  289      -s "aln.keep.bam"   or run("samtools view -@ $nthread -f 0x2 -bS reads.mka.bam > aln.keep.bam"); # keep only properly paired reads
>>  290      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS reads.mka.bam > unmapped.bam");
>>  291      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
>>  292      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    293      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
>>  294      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    295  }
    296  
    297  sub map_with_mosaik_se {
>>  298      verify_cmd(qw(MosaikBuild MosaikAligner samtools));
    299      my $bin_dir = dirname(which('MosaikAligner'));
    300      verify_file("$bin_dir/2.1.78.se.ann", "$bin_dir/2.1.78.pe.ann");
    301      -s "se.ann"         or run("ln -s -f $bin_dir/2.1.78.se.ann se.ann");
    302      -s "pe.ann"         or run("ln -s -f $bin_dir/2.1.78.pe.ann pe.ann");
    303      -s "ref.fa"         or run("ln -s -f $ref ref.fa");
    304      -s "read.fq"        or run("ln -s -f $read1 read.fq");
    305      -s "ref.dat"        or run("MosaikBuild -fr ref.fa -oa ref.dat");
    306      -s "reads.mkb"      or run("MosaikBuild -q read.fq -out reads.mkb -st illumina");
    307      -s "reads.mka.bam"  or run("MosaikAligner -in reads.mkb -out reads.mka -ia ref.dat -p $nthread -annpe pe.ann -annse se.ann");
    308      -s "aln.raw.sam"    or run("ln -s -f reads.mka.bam aln.raw.sam");
    309      -s "aln.keep.bam"   or run("ln -s -f reads.mka.bam aln.keep.bam");
>>  310      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS reads.mka.bam > unmapped.bam");
>>  311      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
>>  312      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    313      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
>>  314      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    315  }
    316  
    317  sub map_with_last {
>>  318      verify_cmd(qw(lastdb lastal parallel last-pair-probs maf-convert samtools));
    319      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    320      -s "read_1.fq"      or run_symlink($read1, "read_1.fq");
    321      -s "read_2.fq"      or run_symlink($read2, "read_2.fq");
    322      -s "index.suf"      or run("lastdb -m1111110 index ref.fa");
    323      -s "out1.maf"       or run("parallel --gnu --pipe -L8 -j $nthread -k 'lastal -Q fastx -d108 -e120 -i1 index' < read_1.fq > out1.maf");
    324      -s "out2.maf"       or run("parallel --gnu --pipe -L8 -j $nthread -k 'lastal -Q fastx -d108 -e120 -i1 index' < read_2.fq > out2.maf");
    325    # -s "out1.maf"       or run("lastal -Q1 -d108 -e120 -i1 index read_1.fq > out1.maf"); # sequential
    326    # -s "out2.maf"       or run("lastal -Q1 -d108 -e120 -i1 index read_2.fq > out2.maf"); # sequential
    327      -s "aln-pe.maf"     or run("last-pair-probs -m 0.1 out1.maf out2.maf > aln-pe.maf");
>>  328      -s "ref.fa.fai"     or run("samtools faidx ref.fa");
    329      -s "sam.header"     or run("awk '{ print \"\@SQ\\tSN:\"\$1\"\\tLN:\"\$2 }' ref.fa.fai > sam.header");
    330      -s "aln.raw.sam"    or run("bash -c 'cat sam.header <(maf-convert sam aln-pe.maf) > aln.raw.sam'");
    331      remove_extra_pg_headers('aln.raw.sam');
>>  332      -s "aln.keep.bam"   or run("samtools view -@ $nthread -bS aln.raw.sam > aln.keep.bam");
>>  333      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
>>  334      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
>>  335      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    336      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
>>  337      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    338  }
    339  
    340  sub map_with_last_se {
>>  341      verify_cmd(qw(lastdb parallel last-pair-probs samtools));
    342      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    343      -s "read.fq"        or run_symlink($read1, "read.fq");
    344      -s "index.suf"      or run("lastdb -m1111110 index ref.fa");
    345      -s "out.maf"        or run("parallel --gnu --pipe -L8 -j $nthread -k 'lastal -Q fastx -d108 -e120 -i1 index' < read.fq > out.maf");
    346    # -s "out.maf"        or run("lastal -Q1 -d108 -e120 -i1 index read.fq > out.maf"); # sequential
    347      -s "aln-se.maf"     or run("ln -s -f out.maf aln-se.maf");
>>  348      -s "ref.fa.fai"     or run("samtools faidx ref.fa");
    349      -s "sam.header"     or run("awk '{ print \"\@SQ\\tSN:\"\$1\"\\tLN:\"\$2 }' ref.fa.fai > sam.header");
    350      -s "aln.raw.sam"    or run("bash -c 'cat sam.header <(maf-convert sam aln-se.maf) > aln.raw.sam'");
    351      remove_extra_pg_headers('aln.raw.sam');
>>  352      -s "aln.keep.bam"   or run("samtools view -@ $nthread -bS aln.raw.sam > aln.keep.bam");
>>  353      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
>>  354      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
>>  355      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    356      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
>>  357      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    358  }
    359  
    360  sub map_with_minimap2 {
>>  361      verify_cmd(qw(minimap2 samtools));
    362      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    363      -s "read_1.fq"      or run_symlink($read1, "read_1.fq");
    364      -s "read_2.fq"      or run_symlink($read2, "read_2.fq");
    365      -s "aln-pe.sam"     or run("minimap2 -t $nthread -a ref.fa read_1.fq read_2.fq -o aln-pe.sam");
    366      -s "aln.raw.sam"    or run("ln -s -f aln-pe.sam aln.raw.sam");
>>  367      -s "aln.keep.bam"   or run("samtools view -@ $nthread -bS aln.raw.sam > aln.keep.bam");
>>  368      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
>>  369      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
>>  370      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    371      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
>>  372      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    373  }
    374  
    375  sub map_with_minimap2_se {
>>  376      verify_cmd(qw(minimap2 samtools));
    377      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    378      -s "read.fq"        or run_symlink($read1, "read.fq");
    379      -s "aln-se.sam"     or run("minimap2 -t $nthread -a ref.fa read.fq -o aln-se.sam");
    380      -s "aln.raw.sam"    or run("ln -s -f aln-se.sam aln.raw.sam");
>>  381      -s "aln.keep.bam"   or run("samtools view -@ $nthread -bS aln.raw.sam > aln.keep.bam");
>>  382      -s "unmapped.bam"   or run("samtools view -@ $nthread -f 4 -bS aln.raw.sam > unmapped.bam");
>>  383      -s "aln.sorted.bam" or run("samtools sort -m $memory -@ $nthread -o aln.sorted.bam aln.keep.bam");
>>  384      -s "aln.dedup.bam"  or run("samtools rmdup aln.sorted.bam aln.dedup.bam");  # rmdup broken in samtools v1.0 and v1.1
    385      -s "aln.bam"        or run("ln -s -f aln.dedup.bam aln.bam");
>>  386      -s "aln.bam.bai"    or run("samtools index aln.bam aln.bam.bai");
    387  }
    388  
    389  sub map_with_snippy {
    390      verify_cmd(qw(snippy));
    391      -s "ref.fa"         or run_symlink($ref, "ref.fa");
    392      -s "read_1.fq"      or run_symlink($read1, "read_1.fq");
    393      -s "read_2.fq"      or run_symlink($read2, "read_2.fq");
    394      -s "snps.vcf"       or run("snippy --cpus $nthread --outdir snippy_out --ref ref.fa --R1 read_1.fq --R2 read_2.fq");
    395      -s "aln.bam"        or run("ln -s -f snippy_out/snps.bam aln.bam");
    396      -s "aln.bam.bai"    or run("ln -s -f snippy_out/snps.bam.bai aln.bam.bai");
    397  }
    398  
```

## `pybin/fastq_utils.py:283`

```
    277                  )
    278              else:
    279                  subprocess.run(cur_cmd, check=True)  # call mapping tool
    280                  view_threads = parameters.get("samtools_view", {}).get("-p", SAM_THREADS)
    281                  with open(bam_file_all, "w") as outstream:
    282                      samtools_view = subprocess.Popen(
>>  283                          ["samtools", "view", "-@", str(view_threads), "-Su", str(sam_path)],
    284                          stdout=subprocess.PIPE,
    285                      )
    286                      samtools_sort = subprocess.Popen(
>>  287                          ["samtools", "sort", "-o", "-", "-"],
    288                          stdin=samtools_view.stdout,
    289                          stdout=outstream,
    290                      )
    291                      samtools_sort.communicate()
    292  
    293                  # minimap2 can't write the unmapped reads like bowtie2 and hisat2
    294                  if not (read2 or hisat2_used): # minimap2
    295                      with unmapped_fq_gz_path.open('w') as un_fq_gz_hdl:
    296                          subprocess.run(
    297                              [
>>  298                                  "samtools", "fastq",
    299                                  "--threads", str(view_threads),
    300                                  "-n", "-f", "4",
    301                                  bam_file_all
    302                              ],
    303                              check=True,
    304                              stdout=un_fq_gz_hdl,
    305                          )
    306  
    307                  with open(bam_file_aligned, "w") as outstream:
    308                      subprocess.run(
    309                          [
>>  310                              "samtools",
    311                              "view",
    312                              "-@",
    313                              str(view_threads),
    314                              "-b",
    315                              "-F",
    316                              "4",
    317                              bam_file_all,
    318                          ],
    319                          check=True,
    320                          stdout=outstream,
    321                      )
    322                  sam_sort = parameters.get("samtools_sort", {}).get("-p", "1")
    323                  if not sam_sort:
    324                      sam_sort = SAM_THREADS
    325                  sort_name_cmd = [
>>  326                      "samtools",
    327                      "sort",
    328                      "-n",
    329                      "-@",
    330                      str(sam_sort),
    331                      bam_file_aligned,
    332                  ]
    333                  bam2fq_cmd = [
    334                      "bedtools",
    335                      "bamtofastq",
    336                      "-i",
    337                      bam_file_sort_name,
    338                      "-fq",
```

## `pybin/fastq_utils.py:346`

```
    340                  ]
    341                  bam2fqgz_cmd = ["gzip", fastq_file_aligned]
    342                  if read2:  # paired end
    343                      bam2fq_cmd += ["-fq2", fastq_file_aligned2]
    344                      bam2fqgz_cmd += [fastq_file_aligned2]
    345                  print(" ".join(sort_name_cmd))
>>  346                  # Need to sort by name to convert to fastq: samtools sort -n myBamFile.bam myBamFile.sortedByName
    347                  subprocess.run(
    348                      sort_name_cmd, check=True, stdout=open(bam_file_sort_name, "w")
    349                  )
    350                  cur_cleanup.append(bam_file_sort_name)
    351                  print((" ".join(bam2fq_cmd)))
    352                  with open(os.path.join(target_dir, "bedtools.log.txt"), "a") as fd:
    353                      print("Redirecting bedtools stderr to a log.", file=sys.stderr)
    354                      print(bam_file_sort_name, file=fd)
    355                      fd.flush()
    356                      subprocess.run(bam2fq_cmd, check=True, stderr=fd)
    357                  subprocess.run(bam2fqgz_cmd, check=True)
    358                  samtools_index_threads = parameters.get("samtools_index", {}).get(
    359                      "-p", "1"
    360                  )
    361                  if not samtools_index_threads:
    362                      samtools_index_threads = SAM_THREADS
    363                  subprocess.run(
    364                      [
>>  365                          "samtools",
    366                          "index",
    367                          "-@",
    368                          str(samtools_index_threads),
    369                          bam_file_aligned,
    370                      ],
    371                      check=True,
    372                  )
    373                  print((" ".join(samstat_cmd)))
    374                  try:
    375                      subprocess.run(samstat_cmd, check=True)
    376                  except subprocess.CalledProcessError as cpe:
    377                      with open(bam_file_all + ".samstat.html", "w") as samstat_html:
```

## `pybin/p3_tnseq.py:375`

```
    369                  #                         cat_cmd = ["cat"] + [r[genome["genome"]]["wig"][contig] for contig in contig_ids]
    370                  #                         # cat_cmd += [">", wig_file]
    371                  #                         with open(wig_file, "w") as wig_fd:
    372                  #                             subprocess.run(cat_cmd, stdout=wig_fd)
    373                  #                 r[genome["genome"]]["wig"] = wig_file
    374                  if not os.path.exists(bam_file):
>>  375                      # subprocess.check_call("samtools view -Su "+sam_file+" | samtools sort -o - - > "+bam_file, shell=True)#convert to bam
    376                      bam_out = open(bam_file, "w")
    377                      p1 = subprocess.Popen(
>>  378                          ["samtools", "view", "-Su", sam_file], stdout=subprocess.PIPE
    379                      )
    380                      p2 = subprocess.Popen(
>>  381                          ["samtools", "sort", "-o", "-", "-"],
    382                          stdout=bam_out,
    383                          stdin=p1.stdout,
    384                      )
    385                      p1.stdout.close()
    386                      output = p2.communicate()
    387                      bam_out.close()
    388                      print("pipeline done " + str(output))
    389                      p1_stat = p1.wait()
    390                      p2_stat = p2.wait()
    391                      print("view status = %d" % p1_stat)
    392                      print("sort status = %d" % p2_stat)
>>  393                      subprocess.check_call(["samtools", "index", bam_file])
>>  394                      # subprocess.check_call('samtools view -S -b %s > %s' % (sam_file, bam_file+".tmp"), shell=True)
>>  395                      # subprocess.check_call('samtools sort %s %s' % (bam_file+".tmp", bam_file), shell=True)
    396                  for garbage in cur_cleanup:
    397                      if os.path.exists(garbage):
    398                          subprocess.call(["rm", garbage])
    399          key_handle.close()
    400          for garbage in final_cleanup:
    401              subprocess.call(["rm", garbage])
    402  
    403  
    404  def main(server_setup, job_data):
    405      required_data = [
    406          "experimental_conditions",
    407          "read_files",
```

## `pybin/p3x-assembly.py:637`

```
    631      return report
    632  
    633  def convertSamToBam(samFile, num_threads, save_sam=False):
    634      #convert format to bam and index
    635      LOG.write("convertSamToBam(%s, %s)\n"%(samFile, str(num_threads)))
    636      tempTime = time()
>>  637      command = ["samtools"]
    638      proc = subprocess.Popen(command, shell=False, stderr=subprocess.PIPE)
    639      proc.wait()
    640      version_text = proc.stderr.read().decode()
    641      samtools_version = ''
    642      for line in version_text.splitlines():
    643          if 'Version' in line:
    644              samtools_version = line.strip()
    645  
    646      sortThreads = max(int(num_threads/2), 1)
    647      samFilePrefix = re.sub(".sam", "", samFile, re.IGNORECASE)
>>  648      command = ["samtools", "view", "-bS", "-@", str(sortThreads), "-o", samFilePrefix+"_unsorted.bam", samFile]
    649      LOG.write(" ".join(command)+"\n")
    650      return_code = subprocess.call(command, shell=False, stderr=LOG)
    651      #os.remove(samFile) #save a little space
    652      if return_code != 0:
>>  653          comment = "samtools view returned %d"%return_code
    654          LOG.write(comment+"\n")
    655          return None
    656      if not save_sam:
    657          os.unlink(samFile)
    658  
    659      LOG.flush()
    660  
    661      bamFileSorted = samFilePrefix+".bam" 
>>  662      command = ["samtools", "sort", "-@", str(sortThreads), "-o", bamFileSorted, samFilePrefix+"_unsorted.bam"]
    663      if "Version: 0.1.19" in samtools_version:
    664          # different invocation for this older version
>>  665          command = ["samtools", "sort", "-@", str(sortThreads), samFilePrefix+"_unsorted.bam", samFilePrefix]
    666      return_code = subprocess.check_call(command, shell=False, stderr=LOG)
    667  
    668      if return_code != 0:
>>  669          comment = "samtools sort returned %d, convertSamToBam failed"%return_code
    670          LOG.write(comment+"\n")
    671          return None
    672      LOG.write("bamFileSorted = "+bamFileSorted+"\n")
    673      os.remove(samFilePrefix+"_unsorted.bam")
    674      if not os.path.exists(bamFileSorted):
    675          comment = "{0} not found, sorting bamfile failed, convertSamToBam failed\n".format(bamFileSorted)
    676          LOG.write(comment+"\n")
    677          return None
    678      if not os.path.getsize(bamFileSorted):
    679          comment = "{0} of size zero, sorting bamfile failed, convertSamToBam failed\n".format(bamFileSorted)
    680          LOG.write(comment+"\n")
    681          return None
>>  682      LOG.write("samtools sort return code=%d, time=%d, size of %s is %d\n"%(return_code, time()-tempTime, bamFileSorted, os.path.getsize(bamFileSorted)))
    683  
>>  684      command = ["samtools", "index", bamFileSorted]
    685      LOG.write("executing: "+" ".join(command)+"\n")
    686      return_code = subprocess.call(command, shell=False, stderr=LOG)
>>  687      #LOG.write("samtools index return code = %d\n"%return_code)
    688      return (bamFileSorted, samtools_version)
    689  
    690  def runRacon(contigFile, read_set, num_threads, save_intermediate=False):
    691      """
    692      Polish (correct) sequence of assembled contigs by comparing to the original long-read sequences
    693      Run racon on reads, read-to-contig-sam, contigs. Generate polished contigs.
    694      Return name of polished contigs.
    695      """
    696      LOG.write('runRacon(%s, %s, %s)\n'%(contigFile, read_set.files[0], str(num_threads)))
    697      report = {"input_contigs":contigFile, "reads": read_set.files[0], "program": "racon"}
    698      command = ["racon", "--version"]
    699      proc = subprocess.Popen(command, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
```

## `pybin/p3x-assembly.py:830`

```
    824      return report 
    825  
    826  def calcReadDepth(bamfiles):
    827      """ Return dict of contig_ids to tuple of (coverage, normalized_coverage) """
    828      LOG.write("calcReadDepth(%s)\n"%" ".join(bamfiles))
    829      readDepth = {}
>>  830      command = ["samtools", "depth"]
    831      if type(bamfiles) is str:
    832          command.append(bamfiles)
    833      else:
    834          command.extend(bamfiles)
    835      LOG.write("command = "+" ".join(command)+"\n")
    836      proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    837      depthData = proc.communicate()[0].decode()
    838      if 0:
    839          LOG.write("length of depthData string = %d\n"%len(depthData))
    840      depthSum = 0
    841      totalDepthSum = 0
    842      totalLength = 0
```

## `pybin/p3x-assembly.py:1025`

```
   1019                      HTML.write("<tr><td>%s:</td><td>%s</td></tr>\n"%(key, value))
   1020                  HTML.write("<tr></tr>\n") # blank row
   1021                  program_version[info['program']] = info["version"]
   1022                  if 'bowtie2_version' in info:
   1023                      program_version['bowtie2'] = info['bowtie2_version']
   1024                  if 'samtools_version' in info:
>> 1025                      program_version['samtools'] = info['samtools_version']
   1026          HTML.write("</tbody></table>\n")
   1027          HTML.write("</section>\n")
   1028  
   1029      if "quast" in assembly_data:
   1030          HTML.write("<section><h2>Quast Report</h2>\n")
   1031          if 'report_text' in assembly_data["quast"]:
   1032              HTML.write("<pre>\n")
   1033              HTML.write(assembly_data["quast"]["report_text"])
   1034              HTML.write("\n</pre>\n")
   1035          HTML.write("</section>\n")
   1036          program_version['quast'] = assembly_data['quast']["version"]
   1037      
```

## `pybin/p3x-assembly.py:1053`

```
   1047              HTML.write("<tr><td>{}:</td><td>{}</td></tr>\n".format(key, assembly_data['contig_filtering'][key])) 
   1048          HTML.write("</tbody></table>\n")
   1049          HTML.write("</section>\n")
   1050          if 'bowtie2_version' in assembly_data['contig_filtering']:
   1051              program_version['bowtie2'] = assembly_data['contig_filtering']['bowtie2_version']
   1052          if 'samtools_version' in assembly_data['contig_filtering']:
>> 1053              program_version['samtools'] = assembly_data['contig_filtering']['samtools_version']
   1054  
   1055      HTML.write('<div>\n<h2>Preprocessing of Reads</h2>\n')
   1056      for read_set in read_list:
   1057          read_set.writeHtml(HTML)
   1058      HTML.write("</div>\n")
   1059  
   1060      HTML.write("<section><h2>Tools Used:</h2>\n")
   1061      HTML.write("""
   1062          <table class="med-table kv-table">
   1063              <thead class="table-header">
   1064              <tr> <th > Tool </th><th> Version</th></tr></thead>
   1065              <tbody>
```

## `pybin/reference_guided_assembly.py:503`

```
    497              f"bwa mem {bwa_thr_opt} {multi_ref} {trim_single} > {sam}",
    498              f"Align {sample_name} (SE)",
    499          )
    500  
    501      bam_sorted = outdir / f"{sample_name}.sorted.bam"
    502      run_command(
>>  503          f"samtools view -Sb {sam} | samtools sort -o {bam_sorted}",
    504          f"Sort BAM {sample_name}",
    505      )
>>  506      run_command(f"samtools index {bam_sorted}", f"Index BAM {sample_name}")
    507  
    508      # Variant calling with bcftools
    509      vcf_gz = outdir / f"{sample_name}.vcf.gz"
    510      region_opt = f"-r {region} " if region else ""
    511      run_command(
    512          f"bcftools mpileup -Ou -f {multi_ref} {region_opt}{bam_sorted} | "
    513          f"bcftools call -mv -Oz -o {vcf_gz}",
    514          f"Variant calling {sample_name}",
    515      )
    516      run_command(f"bcftools index {vcf_gz}", f"Index VCF {sample_name}")
    517  
    518      # Low-coverage mask BED (depth-based masking similar to original pipeline)
    519      mask_bed = None
    520      if depth_cutoff > 0:
    521          mask_bed = outdir / f"{sample_name}.lowcov_dp{depth_cutoff}.bed"
    522          depth_bytes = run_command(
>>  523              f"samtools depth -a {bam_sorted}",
    524              f"Depth {sample_name}",
    525              capture_stdout=True,
    526          ) or b""
    527          write_lowcov_bed_from_depth(depth_bytes, depth_cutoff, mask_bed)
    528          mask_opt = f"-m {mask_bed}"
    529      else:
    530          mask_opt = ""
    531  
    532      # Consensus
    533      is_segmented = len(contigs) > 1
    534      emit_per_segment = bool(per_segment_consensus) if single_multi_input else True
    535  
```

## `pybin/reference_guided_assembly.py:568`

```
    562              run_command(
    563                  f"bcftools consensus -f {multi_ref} {mask_opt} {vcf_gz} > {consensus_primary}",
    564                  f"Consensus {sample_name} (combined)",
    565              )
    566          else:
    567              supports_r = _bcftools_consensus_supports_regions()
>>  568              run_command(f"samtools faidx {multi_ref}", f"samtools faidx {multi_ref.name}")
    569              with open(consensus_primary, "w") as all_out:
    570                  for seg in contigs:
    571                      safe_seg = _safe_segment_name(seg)
    572                      seg_cons = outdir / f"{sample_name}.consensus.{safe_seg}.fasta"
    573                      if supports_r:
    574                          try:
    575                              run_command(
    576                                  f"bcftools consensus -f {multi_ref} -r {seg} {mask_opt} {vcf_gz} > {seg_cons}",
    577                                  f"Consensus {sample_name}:{seg}",
    578                              )
    579                          except subprocess.CalledProcessError:
    580                              # Some bcftools builds print -r in help but don't accept it.
    581                              # Fall back to the streamed approach for this and remaining segments.
    582                              supports_r = False
    583                              run_command(
>>  584                                  f"samtools faidx {multi_ref} {seg} | bcftools consensus {mask_opt} {vcf_gz} > {seg_cons}",
    585                                  f"Consensus {sample_name}:{seg} (streamed)",
    586                              )
    587                      else:
    588                          run_command(
>>  589                              f"samtools faidx {multi_ref} {seg} | bcftools consensus {mask_opt} {vcf_gz} > {seg_cons}",
    590                              f"Consensus {sample_name}:{seg} (streamed)",
    591                          )
    592                      consensus_segments.append(str(seg_cons))
    593                      with open(seg_cons) as fh:
    594                          all_out.write(fh.read())
    595  
    596      # QUAST on consensus
    597      quast_dir = outdir / "quast_reference_guided"
    598      ensure_dir(quast_dir)
    599      quast_cmd = (
    600          f"quast.py -o {quast_dir} -t 4 --min-contig 200 {consensus_primary}"
    601      )
```

## `lib/fastq_utils.py:283`

```
    277                  )
    278              else:
    279                  subprocess.run(cur_cmd, check=True)  # call mapping tool
    280                  view_threads = parameters.get("samtools_view", {}).get("-p", SAM_THREADS)
    281                  with open(bam_file_all, "w") as outstream:
    282                      samtools_view = subprocess.Popen(
>>  283                          ["samtools", "view", "-@", str(view_threads), "-Su", str(sam_path)],
    284                          stdout=subprocess.PIPE,
    285                      )
    286                      samtools_sort = subprocess.Popen(
>>  287                          ["samtools", "sort", "-o", "-", "-"],
    288                          stdin=samtools_view.stdout,
    289                          stdout=outstream,
    290                      )
    291                      samtools_sort.communicate()
    292  
    293                  # minimap2 can't write the unmapped reads like bowtie2 and hisat2
    294                  if not (read2 or hisat2_used): # minimap2
    295                      with unmapped_fq_gz_path.open('w') as un_fq_gz_hdl:
    296                          subprocess.run(
    297                              [
>>  298                                  "samtools", "fastq",
    299                                  "--threads", str(view_threads),
    300                                  "-n", "-f", "4",
    301                                  bam_file_all
    302                              ],
    303                              check=True,
    304                              stdout=un_fq_gz_hdl,
    305                          )
    306  
    307                  with open(bam_file_aligned, "w") as outstream:
    308                      subprocess.run(
    309                          [
>>  310                              "samtools",
    311                              "view",
    312                              "-@",
    313                              str(view_threads),
    314                              "-b",
    315                              "-F",
    316                              "4",
    317                              bam_file_all,
    318                          ],
    319                          check=True,
    320                          stdout=outstream,
    321                      )
    322                  sam_sort = parameters.get("samtools_sort", {}).get("-p", "1")
    323                  if not sam_sort:
    324                      sam_sort = SAM_THREADS
    325                  sort_name_cmd = [
>>  326                      "samtools",
    327                      "sort",
    328                      "-n",
    329                      "-@",
    330                      str(sam_sort),
    331                      bam_file_aligned,
    332                  ]
    333                  bam2fq_cmd = [
    334                      "bedtools",
    335                      "bamtofastq",
    336                      "-i",
    337                      bam_file_sort_name,
    338                      "-fq",
```

## `lib/fastq_utils.py:346`

```
    340                  ]
    341                  bam2fqgz_cmd = ["gzip", fastq_file_aligned]
    342                  if read2:  # paired end
    343                      bam2fq_cmd += ["-fq2", fastq_file_aligned2]
    344                      bam2fqgz_cmd += [fastq_file_aligned2]
    345                  print(" ".join(sort_name_cmd))
>>  346                  # Need to sort by name to convert to fastq: samtools sort -n myBamFile.bam myBamFile.sortedByName
    347                  subprocess.run(
    348                      sort_name_cmd, check=True, stdout=open(bam_file_sort_name, "w")
    349                  )
    350                  cur_cleanup.append(bam_file_sort_name)
    351                  print((" ".join(bam2fq_cmd)))
    352                  with open(os.path.join(target_dir, "bedtools.log.txt"), "a") as fd:
    353                      print("Redirecting bedtools stderr to a log.", file=sys.stderr)
    354                      print(bam_file_sort_name, file=fd)
    355                      fd.flush()
    356                      subprocess.run(bam2fq_cmd, check=True, stderr=fd)
    357                  subprocess.run(bam2fqgz_cmd, check=True)
    358                  samtools_index_threads = parameters.get("samtools_index", {}).get(
    359                      "-p", "1"
    360                  )
    361                  if not samtools_index_threads:
    362                      samtools_index_threads = SAM_THREADS
    363                  subprocess.run(
    364                      [
>>  365                          "samtools",
    366                          "index",
    367                          "-@",
    368                          str(samtools_index_threads),
    369                          bam_file_aligned,
    370                      ],
    371                      check=True,
    372                  )
    373                  print((" ".join(samstat_cmd)))
    374                  try:
    375                      subprocess.run(samstat_cmd, check=True)
    376                  except subprocess.CalledProcessError as cpe:
    377                      with open(bam_file_all + ".samstat.html", "w") as samstat_html:
```

## `lib/process.py:1216`

```
   1210              sample.set_alignment_check(False)
   1211              return True
   1212  
   1213      def run_alignment_stats(self, sample, threads):
   1214          sample_dir = self.genome.get_sample_path(sample.get_id())
   1215          sample_bam = sample.get_sample_data("bam")
>> 1216          # samtools stats
>> 1217          stats_cmd = ["samtools", "stats", "--threads", str(threads), sample_bam]
   1218          stats_output = os.path.join(
   1219              sample_dir, sample.get_id() + ".samtools_stats"
   1220          )
   1221          sample.add_command(
   1222              "samtools_stats_" + self.genome.get_id(), stats_cmd, "running"
   1223          )
   1224          try:
   1225              # TODO: ENABLE
   1226              print("Running command:\n{0}".format(" ".join(stats_cmd)))
   1227              with open(stats_output, "w") as so:
   1228                  subprocess.check_call(stats_cmd, stdout=so)
   1229              sample.set_command_status(
```

## `lib/process.py:1405`

```
   1399          return True
   1400  
   1401      def convert_sam_to_bam(self, sam_file, threads):
   1402          bam_file = sam_file.replace(".sam", ".bam")
   1403          print("bam_file = {0}".format(bam_file))
   1404          sam_to_bam_cmd = (
>> 1405              "samtools view -Su "
   1406              + sam_file
>> 1407              + " | samtools sort -o - - -@ "
   1408              + str(threads)
   1409              + " > "
   1410              + bam_file
   1411          )
   1412          try:
   1413              print("Running command:\n{0}".format(sam_to_bam_cmd))
   1414              # TODO: ENABLE
   1415              subprocess.check_call(sam_to_bam_cmd, shell=True)
   1416          except Exception as e:
   1417              sys.stderr.write(
   1418                  "Error in converting sam to bam file:\n{0}\n".format(e)
   1419              )
   1420              return None
>> 1421          index_cmd = "samtools index " + bam_file
   1422          try:
   1423              print("Running command:\n{0}".format(index_cmd))
   1424              # TODO: ENABLE
   1425              subprocess.check_call(index_cmd, shell=True)
   1426          except Exception as e:
   1427              sys.stderr.write("Error indexing bam file:\n{0}\n".format(e))
   1428              return None
   1429          return bam_file
   1430  
   1431      def infer_strand_from_file(self, infer_file):
   1432          strand = None
   1433          with open(infer_file, "r") as handle:
```

## `plbin/App-Variation.pl:113`

```
    107  
    108  
    109  
    110  sub process_variation_data {
    111      my ($app, $app_def, $raw_params, $params) = @_;
    112  
>>  113      system("samtools", "--version") == 0 or die "samtools --version failed";
    114      system("bcftools", "--version") == 0 or die "bcftools --version failed";
    115      system("freebayes", "--version") == 0 or die "freebayes --version failed";
    116      system("snippy", "--version") == 0 or die "snippy --version failed";
    117  
    118      #
    119      # Redirect tmp to large NFS if more than 4 input files.
    120      # (HACK)
    121      #
    122  
    123      my $file_count = count_params_files($params);
    124      print STDERR "File count: $file_count\n";
    125      my $bigtmp = "/vol/patric3/tmp";
```

## `plbin/sars2-cdc-nanopore.pl:156`

```
    150  $runner->run(\@minimap, ">", $samfile);
    151  
    152  #
    153  # Create bam format output
    154  #
    155  
>>  156  $runner->run(["samtools", "view", "-b", $samfile],
    157  	 "|",
>>  158  	 ["samtools", "sort", "-", "--threads", $threads, "-o", $bamfile]);
    159  
>>  160  $runner->run(["samtools", "index", $bamfile]);
    161  
    162  #
    163  # Primer clipping
    164  #
    165  
    166  my @clip = ("bamclipper.sh",
    167  	    "-b", $bamfile,
    168  	    "-p", $primer,
    169  	    "-n", $threads,
    170  	    "-o", $out_dir,
    171  	    "-u", 80,
    172  	    "-d", 80);
```

## `plbin/sars2-onecodex.pl:274`

```
    268  if ($opt->delete_reads)
    269  {
    270      print STDERR "Deleting inputs @inputs\n";
    271      unlink(@inputs);
    272  }
    273  
>>  274  $runner->run_with_timeout(960, ["samtools",
    275  			    "view",
    276  			    "-u",
    277  			    "-h",
    278  			    "-q", $opt->min_quality,
    279  			    "-F", 4,
    280  			    "$int_dir/minimap.out"],
    281  		      '|',
>>  282  		      ["samtools",
    283  		       "sort",
    284  		       "--threads", $opt->threads,
    285  		       "-o", "$int_dir/$base.sorted.bam",
    286  		       "-"]
    287  		     );
    288  unlink("$int_dir/minimap.out");
>>  289  $runner->run(["samtools", "index", "$int_dir/$base.sorted.bam"]);
    290  
    291  my $ivar_file = "$int_dir/$base.ivar";
    292  
    293  $runner->run(["ivar",
    294  	  "trim",
    295  	  "-e",
    296  	  "-q", 0,
    297  	  "-i", "$int_dir/$base.sorted.bam",
    298  	  "-b", "$bed_tmp",
    299  	  "-p", $ivar_file],
    300  	    '>', "$out_dir/$base.primer-trim.txt");
    301  
```

## `plbin/sars2-onecodex.pl:356`

```
    350  #
    351  # We are hitting seemingly random timeouts on Bebop with this sort.
    352  #
    353  # Work around it with a timeout and rerun attempt.
    354  #
    355  
>>  356  $runner->run_with_timeout($opt->samtools_sort_timeout, ["samtools",
    357  						    "sort",
    358  						    "$ivar_file.bam",
    359  						    "--threads", $opt->threads,
    360  						    "-o", "$int_dir/$base.isorted.bam"]);
    361  
>>  362  $runner->run(["samtools", "index", "$int_dir/$base.isorted.bam"]);
    363  
>>  364  $runner->run(["samtools",
    365  	  "mpileup",
    366  	  "--fasta-ref", $reference,
    367  	  "--max-depth", $opt->max_depth,
    368  	  "--count-orphans",
    369  	  "--no-BAQ",
    370  	  "--min-BQ", 0,
    371  	  "$int_dir/${base}.isorted.bam"],
    372  	 '>',
    373  	 "$int_dir/$base.pileup");
    374  
    375  my $pileup_compress_handle = start(["gzip", "-c", "$int_dir/$base.pileup"],
    376  				   '>',
```

## `pybin/run_rnaseq.py:348`

```
    342      # parameters as input json file OR inline
    343      # unit testing parameters
    344  
    345      map_args = parser.parse_args()
    346      print("map_args:\n{0}".format(map_args))
    347  
>>  348      # set path to use correct version of samtools
    349      os.environ["PATH"] = (
    350          "/disks/patric-common/runtime/samtools-1.9/bin:" + os.environ["PATH"]
    351      )
    352      os.environ["R_LIBS"] = (
    353          "/disks/patric-common/runtime/lib/R/library:" + os.environ.get("R_LIBS", "")
    354      )
    355      print("R_LIBS path = {0}".format(os.environ["R_LIBS"]))
    356  
    357      # output directory
    358      output_dir = map_args.o
    359      output_dir = os.path.abspath(output_dir)
    360      if not os.path.exists(output_dir):
```

## `workflows/bvbrc_SARS2Wastewater/scripts/prep_results.py:60`

```
     54          if os.path.exists(f'output/{sample_id}/freyja/{sample_id}_freyja_result.tsv'):
     55              df_samples['Freyja - Analysis'][idx] = "Complete"
     56          if os.path.exists(f'plots/lineages_plot.html'):
     57              df_samples['Freyja - Visualization'][idx] = "Complete"
     58          # clean up primer path only show the bed file and remove the path
     59          df_samples['primers'][idx] = get_last_segment(df_samples['primers'][idx])
>>   60          # TO DO:parse samtools flagstats file
     61          # parse_samtools_flagstats(f'output/{sample_id}/assembly/{sample_id}_flagstat.txt')
     62  
     63      # the reference col shows an internal path - dropping because it does not help user
     64      df_samples = df_samples.drop(['reference'], axis='columns')
     65  
     66      # reorder columns
     67  
     68      df_samples = df_samples[[
     69      "sampleID",
     70      "Assembly",
     71      "Freyja - Analysis",
     72      "Freyja - Visualization",
```

## `pybin/reference_guided_assembly.py:134`

```
    128  def bwa_index_present(ref_fa: Path) -> bool:
    129      suffixes = [".amb", ".ann", ".bwt", ".pac", ".sa"]
    130      return all((ref_fa.with_suffix(ref_fa.suffix + s)).exists() for s in suffixes)
    131  
    132  
    133  def write_lowcov_bed_from_depth(depth_bytes: bytes, cutoff: int, bed_path: Path) -> None:
>>  134      """Convert `samtools depth -a` output (bytes) to merged BED regions where depth < cutoff."""
    135      with open(bed_path, "w") as bed:
    136          last_ctg = None
    137          start = None
    138          last_pos = None
    139          for line in depth_bytes.decode().splitlines():
    140              if not line:
    141                  continue
    142              ctg, pos_s, dp_s = line.split()[:3]
    143              pos = int(pos_s)
    144              dp = int(dp_s)
    145              if dp < cutoff:
    146                  if ctg == last_ctg and last_pos is not None and pos == last_pos + 1:
```

## `pybin/run_viral_assembly.py:333`

```
    327          [software, "--version"],
    328          stdout=subprocess.PIPE,
    329          stderr=subprocess.PIPE,
    330        )
    331        output = result.stdout or result.stderr
    332  
>>  333      # Decode tolerantly — some tools (e.g. samtools) include non-UTF-8 chars like ©
    334      text = output.decode("utf-8", errors="replace")
    335  
    336      # bwa embeds version as "Version: X.X.X" inside the usage block; strip the label
    337      if software in _VERSION_STDERR_TOOLS:
    338        for line in text.splitlines():
    339          if "version:" in line.lower():
    340            # Extract just the version string after the colon, e.g. "0.7.17-r1188"
    341            version = line.split(":", 1)[-1].strip()
    342            print(f"{software} version: {version}")
    343            return version
    344        return "Unknown"
    345  
```

