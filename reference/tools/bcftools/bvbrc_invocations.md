# BV-BRC invocations of `bcftools` (bcftools)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 12 hunk(s) in 6 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/Bio/P3/CmdRunner.pm`
- `plbin/App-Variation.pl`
- `plbin/sars2-cdc-illumina.pl`
- `plbin/var-map.pl`
- `pybin/reference_guided_assembly.py`
- `pybin/run_viral_assembly.py`

## `plbin/var-map.pl:113`

```
    107      my $r2 = $r1;
    108      $r2 =~ s/R1\./R2\./;
    109      return $r2 if -s $r2 && $r2 ne $r1;
    110  }
    111  
    112  sub call_variant_with_bcftools {
>>  113      verify_cmd(qw(bcftools));
>>  114      -s "mpileup"        or run("bcftools mpileup -Ou -f ref.fa aln.bam >mpileup");
>>  115      -s "var.sam.vcf"    or run("bcftools call -Ov -mv mpileup >var.sam.vcf");
    116      -s "var.sam.q.vcf"  or run("vcffilter -f 'QUAL > 10 & DP > 5' var.sam.vcf > var.sam.q.vcf");
    117      -s "var.sam.count"  or run("grep -v '^#' var.sam.vcf |cut -f4 |grep -v 'N' |wc -l > var.sam.count");
    118      -s "var.vcf"        or run("ln -s -f var.sam.q.vcf var.vcf");
    119  }
    120  
    121  sub call_variant_with_freebayes {
    122      verify_cmd(qw(freebayes-parallel fasta_generate_regions.py vcffilter vcffirstheader vcfuniq vcfstreamsort));
    123      -s "var.fb.vcf"     or run("bash -c 'freebayes-parallel <(fasta_generate_regions.py ref.fa.fai 100000) $nthread -p 1 -f ref.fa aln.bam >var.fb.vcf'");
    124      -s "var.fb.q10.vcf" or run("vcffilter -f 'QUAL > 10 & DP > 5' var.fb.vcf > var.fb.q10.vcf");
    125      -s "var.fb.q1.vcf"  or run("vcffilter -f 'QUAL > 1' var.fb.vcf > var.fb.q1.vcf");
    126      -s "var.fb.count"   or run("grep -v '^#' var.fb.vcf |cut -f4 |grep -v 'N' |wc -l > var.fb.count");
    127      -s "var.vcf"        or run("ln -s -f var.fb.q10.vcf var.vcf");
```

## `plbin/var-map.pl:136`

```
    130  sub call_variant_with_snippy {
    131      -s "var.snp.count"  or run("grep -v '^#' snippy_out/snps.raw.vcf |cut -f4 |grep -v 'N' |wc -l > var.snp.count");
    132      -s "var.vcf"        or run("ln -s -f snippy_out/snps.vcf var.vcf");
    133  }
    134  
    135  sub compute_consensus {
>>  136      verify_cmd(qw(bgzip tabix bcftools));
    137      my $consensus_error = '';
    138      -s "var.vcf.gz"     or run("bgzip -c var.vcf > var.vcf.gz");
    139      -s "var.vcf.gz.tbi" or run("tabix var.vcf.gz");
>>  140      -s "consensus"      or $consensus_error = run_with_error_msg("bcftools consensus -c chain -f ref.fa var.vcf.gz", 'consensus');
    141      # handle the case "The fasta sequence does not match the REF allele" 
    142      print "compute_consensus: $consensus_error\n";
    143      
    144      if ($consensus_error =~ /The fasta sequence does not match the REF allele/) {
    145        print "revise and index ref.fa\n";
    146        run("sed -E '/^>/! s/[^ACGTacgt]/N/g' ref.fa > modified_ref.fa");
    147        run("samtools faidx modified_ref.fa");
>>  148        print "run bcftools norm\n";
>>  149        run("bcftools norm -f modified_ref.fa var.vcf.gz -o var.norm.vcf");
    150        run("bgzip -c var.norm.vcf > var.norm.vcf.gz");
>>  151        run("bcftools index var.norm.vcf.gz");
>>  152        run("bcftools consensus -c chain -f modified_ref.fa var.norm.vcf.gz > consensus");
    153        print "compute_consensus ended\n";
    154      }
    155  }
    156  
    157  sub compute_stats {
    158      verify_cmd(qw(samtools bedtools));
    159      -s "ref.fa.fai"     or run("samtools faidx ref.fa");
    160      if (-s "aln.raw.sam") {
    161        -s "raw.flagstat" or run("samtools flagstat aln.raw.sam > raw.flagstat");
    162      }
    163      if (-s "aln.bam") {
    164        -s "flagstat"       or run("samtools flagstat aln.bam > flagstat");
```

## `pybin/reference_guided_assembly.py:277`

```
    271          return items or None
    272      return None
    273  
    274  
    275  def _bcftools_consensus_supports_regions() -> bool:
    276      """
>>  277      Detect whether `bcftools consensus` supports -r/--regions.
    278      We avoid shell grep for portability and tool restrictions.
    279      """
    280      try:
    281          p = subprocess.run(
>>  282              ["bcftools", "consensus", "-h"],
    283              stdout=subprocess.PIPE,
    284              stderr=subprocess.STDOUT,
    285              text=True,
    286              check=False,
    287          )
    288          out = p.stdout or ""
>>  289          # Older bcftools builds don't support -r/--regions at all.
    290          # To avoid false positives (e.g. "-r" inside other text), require
    291          # an option line that starts with the short flag.
    292          for line in out.splitlines():
    293              stripped = line.lstrip()
    294              if stripped.startswith("-r ") or stripped.startswith("-r,") or stripped.startswith("--regions"):
    295                  return True
    296          return False
    297      except Exception:
    298          return False
    299  
    300  
    301  def run_reference_guided_resolved(
```

## `pybin/reference_guided_assembly.py:508`

```
    502      run_command(
    503          f"samtools view -Sb {sam} | samtools sort -o {bam_sorted}",
    504          f"Sort BAM {sample_name}",
    505      )
    506      run_command(f"samtools index {bam_sorted}", f"Index BAM {sample_name}")
    507  
>>  508      # Variant calling with bcftools
    509      vcf_gz = outdir / f"{sample_name}.vcf.gz"
    510      region_opt = f"-r {region} " if region else ""
    511      run_command(
>>  512          f"bcftools mpileup -Ou -f {multi_ref} {region_opt}{bam_sorted} | "
>>  513          f"bcftools call -mv -Oz -o {vcf_gz}",
    514          f"Variant calling {sample_name}",
    515      )
>>  516      run_command(f"bcftools index {vcf_gz}", f"Index VCF {sample_name}")
    517  
    518      # Low-coverage mask BED (depth-based masking similar to original pipeline)
    519      mask_bed = None
    520      if depth_cutoff > 0:
    521          mask_bed = outdir / f"{sample_name}.lowcov_dp{depth_cutoff}.bed"
    522          depth_bytes = run_command(
    523              f"samtools depth -a {bam_sorted}",
    524              f"Depth {sample_name}",
    525              capture_stdout=True,
    526          ) or b""
    527          write_lowcov_bed_from_depth(depth_bytes, depth_cutoff, mask_bed)
    528          mask_opt = f"-m {mask_bed}"
```

## `pybin/reference_guided_assembly.py:563`

```
    557          if consensus_multi != consensus_primary:
    558              shutil.copyfile(consensus_primary, consensus_multi)
    559      else:
    560          consensus_primary = outdir / f"{sample_name}.consensus.multi.fasta"
    561          if single_multi_input and not emit_per_segment:
    562              run_command(
>>  563                  f"bcftools consensus -f {multi_ref} {mask_opt} {vcf_gz} > {consensus_primary}",
    564                  f"Consensus {sample_name} (combined)",
    565              )
    566          else:
    567              supports_r = _bcftools_consensus_supports_regions()
    568              run_command(f"samtools faidx {multi_ref}", f"samtools faidx {multi_ref.name}")
    569              with open(consensus_primary, "w") as all_out:
    570                  for seg in contigs:
    571                      safe_seg = _safe_segment_name(seg)
    572                      seg_cons = outdir / f"{sample_name}.consensus.{safe_seg}.fasta"
    573                      if supports_r:
    574                          try:
    575                              run_command(
>>  576                                  f"bcftools consensus -f {multi_ref} -r {seg} {mask_opt} {vcf_gz} > {seg_cons}",
    577                                  f"Consensus {sample_name}:{seg}",
    578                              )
    579                          except subprocess.CalledProcessError:
>>  580                              # Some bcftools builds print -r in help but don't accept it.
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

## `plbin/App-Variation.pl:114`

```
    108  
    109  
    110  sub process_variation_data {
    111      my ($app, $app_def, $raw_params, $params) = @_;
    112  
    113      system("samtools", "--version") == 0 or die "samtools --version failed";
>>  114      system("bcftools", "--version") == 0 or die "bcftools --version failed";
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
    126      if ($file_count > 4 && -d $bigtmp)
```

## `plbin/sars2-cdc-illumina.pl:295`

```
    289      {
    290  	$runner->run(["tabix", $v]);
    291      }
    292  }
    293  
    294  my $filter_params = "N_ALT == 0";
>>  295  my @con1 = ( "bcftools", "filter", "-e", $filter_params, "$vcf.gz");
    296  my @con2 = ("bgzip","-c");
    297  $runner->run(\@con1, '|',
    298  	\@con2, '>', "$vcf2.gz");
    299  
    300  #
    301  # Create coverage plot
    302  #
    303  
    304  $runner->run(["samtools", "depth", $bamfile], '>', "$out_dir/$base.depth");
    305  
    306  if (-s "$out_dir/$base.depth")
    307  {
```

## `plbin/sars2-cdc-illumina.pl:255`

```
    249  # Create consensus
    250  #
    251  my $use_bcftools_mpileup = 1;
    252  my @con1;
    253  if ($use_bcftools_mpileup)
    254  {
>>  255      @con1 = (qw(bcftools mpileup -f), $reference, $bamfile);
    256  }
    257  else
    258  {
    259      @con1 = ( qw(samtools mpileup -aa -d 8000 -uf), $reference, $bamfile);
    260  }
>>  261  my @con2 = qw(bcftools call -Mc);
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
    272  	 \@con4, '|',
    273  	 \@con5, '|',
```

## `pybin/run_viral_assembly.py:582`

```
    576        report_details["errors"].append("Reference-guided assembly failed.")
    577  
    578      # Retrieve software versions for reference-guided tools
    579      report_details["tools"] = {
    580        "bwa": get_software_version("bwa"),
    581        "samtools": get_software_version("samtools"),
>>  582        "bcftools": get_software_version("bcftools"),
    583        "fastp": get_software_version("fastp"),
    584        "quast": get_software_version("quast.py"),
    585      }
    586  
    587    else:
    588      # IRMA-based assembly
    589      assembly_output_dir = os.path.join(output_dir, strategy)
    590      lowqc_output_dir = os.path.join(output_dir, f"{strategy}_lowQC")
    591  
    592      if paired_end_lib:
    593        read1 = paired_end_lib.get("read1")
    594        read2 = paired_end_lib.get("read2")
```

## `pybin/reference_guided_assembly.py:542`

```
    536      consensus_segments: List[str] = []
    537      legacy_consensus_files: List[Path] = []
    538      root_consensus_alias: Optional[Path] = None
    539      if not is_segmented:
    540          consensus_primary = outdir / f"{sample_name}.consensus.fasta"
    541          run_command(
>>  542              f"bcftools consensus -f {multi_ref} {mask_opt} {vcf_gz} > {consensus_primary}",
    543              f"Consensus {sample_name}",
    544          )
    545          # For backward-compatibility with the original pipeline, also emit a
    546          # contig-named consensus when there is exactly one contig and no
    547          # explicit segment_names override, e.g.
    548          #   <sample>.consensus.NC_001474.2.fasta
    549          if len(contigs) == 1:
    550              only = contigs[0]
    551              legacy_name = outdir / f"{sample_name}.consensus.{only}.fasta"
    552              if legacy_name != consensus_primary:
    553                  shutil.copyfile(consensus_primary, legacy_name)
    554                  legacy_consensus_files.append(legacy_name)
```

## `lib/Bio/P3/CmdRunner.pm:131`

```
    125  	return undef;
    126      }
    127      elsif ($base eq 'seqtk' ||
    128  	   $base eq 'samtools' ||
    129  	   $base eq 'tabix' ||
    130  	   $base eq 'bgzip' ||
>>  131  	   $base eq 'bcftools' ||
    132  	   $base eq 'bamclipper.sh')
    133      {
    134  	my $v;
    135  	IPC::Run::run([$cmd], '2>', \$v, '<', '/dev/null');
    136  	if ($v =~ /Version:\s+(\S+)/)
    137  	{
    138  	    return $1;
    139  	}
    140  	return undef;
    141      }
    142      elsif ($base eq 'cutadapt')
    143      {
```

## `plbin/var-map.pl:3`

```
      1  #! /usr/bin/env perl
      2  
>>    3  # requires: samtools v1.17, bcftools v1.17
      4  
      5  use strict;
      6  use Carp;
      7  use Cwd 'abs_path';
      8  use Data::Dumper;
      9  use File::Path qw(make_path);
     10  use File::Basename;
     11  use File::Which;
     12  use Getopt::Long;
     13  
     14  my $usage = <<"End_of_Usage";
     15  
     16  usage: $0 [options] ref.fq reads_1.fq [reads_2.fq]
     17  
     18         -a algo          - alignment algorithm [bwa_mem bwa_mem_strict bowtie2 mosaik last] (D = bwa_mem)
     19         -o dir           - output directory (D = ref_reads_[algo])
     20         -t int           - number of threads (D = 8)
     21         -m size          - max memory per thread; suffix K/M/G recognized (D = 2G)
>>   22         --vc tool        - variant calling [bcftools freebayes] (D = freebayes)
     23  
     24  End_of_Usage
     25  
     26  my ($help, $algo, $memory, $nthread, $outdir, $paired, $vc, $path_prefix);
     27  
     28  GetOptions("h|help"        => \$help,
     29         "path-prefix=s" => \$path_prefix,
     30             "a|algo=s"      => \$algo,
     31             "m|memory=s"    => \$memory,
     32             "o|outdir=s"    => \$outdir,
     33             "p|paired"      => \$paired,
     34             "t|threads=i"   => \$nthread,
```

