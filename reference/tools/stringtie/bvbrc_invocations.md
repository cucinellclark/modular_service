# BV-BRC invocations of `stringtie` (stringtie)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 6 hunk(s) in 4 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/process.py`
- `lib/report.py`
- `plbin/App-RNASeq.pl`
- `pybin/rnaseqPrepDE.py`

## `lib/process.py:901`

```
    895  
    896              gene_output = os.path.join(sample_dir, "gene_abund.tab")
    897              gtf_output = os.path.join(sample_dir, "transcripts.gtf")
    898              gtf_list.append(gtf_output)
    899              # not including -e (included below), including restricts novel feature prediction
    900              quant_cmd = [
>>  901                  "stringtie",
    902                  bam_file,
    903                  "-p",
    904                  str(threads),
    905                  "-A",
    906                  gene_output,
    907                  "-G",
    908                  annotation_file,
    909                  "-o",
    910                  gtf_output,
    911              ]
    912              sample.add_command(
    913                  "stringtie_" + self.genome.get_id(), quant_cmd, "running"
```

## `lib/process.py:939`

```
    933                  )
    934                  return False
    935          # merge reconstructed transcriptomes
    936          merge_file = os.path.join(self.genome.get_genome_dir(), "merged.gtf")
    937          if not os.path.exists(merge_file):
    938              merge_cmd = [
>>  939                  "stringtie",
    940                  "--merge",
    941                  "-G",
    942                  annotation_file,
    943                  "-o",
    944                  merge_file,
    945              ] + gtf_list
    946              try:
    947                  print("Running command:\n{0}\n".format(" ".join(merge_cmd)))
    948                  subprocess.check_call(merge_cmd)
    949              except Exception as e:
    950                  sys.stderr.write(
    951                      "ERROR running stringtie-merge:\n{0}".format(e)
```

## `lib/process.py:965`

```
    959  
    960              gene_output = os.path.join(sample_dir, "merged_gene_abund.tab")
    961              gtf_output = os.path.join(sample_dir, "merged_transcripts.gtf")
    962              # -e requires using trancripts found in -G
    963              # (turns off novel feature prediction)
    964              quant_cmd = [
>>  965                  "stringtie",
    966                  "-e",
    967                  bam_file,
    968                  "-p",
    969                  str(threads),
    970                  "-A",
    971                  gene_output,
    972                  "-G",
    973                  merge_file,
    974                  "-o",
    975                  gtf_output,
    976              ]
    977              sample.add_command(
```

## `pybin/rnaseqPrepDE.py:14`

```
      8  import itertools
      9  from math import ceil
     10  from optparse import OptionParser
     11  from operator import itemgetter
     12  
     13  parser = OptionParser(
>>   14      description="Generates two CSV files containing the count matrices for genes and transcripts, using the coverage values found in the output of `stringtie -e`"
     15  )
     16  parser.add_option(
     17      "-i",
     18      "--input",
     19      "--in",
     20      default=".",
     21      help="a folder containing all sample sub-directories, or a text file with sample ID and path to its GTF file on each line [default: %default/]",
     22  )
     23  parser.add_option(
     24      "-g",
     25      default="gene_count_matrix.csv",
     26      help="where to output the gene count matrix [default: %default",
```

## `plbin/App-RNASeq.pl:293`

```
    287      my $override = {
    288  	cufflinks => { -p => $parallel},
    289  	cuffdiff => {-p => $parallel},
    290  	cuffmerge => {-p => $parallel},
    291  	hisat2 => {-p => $parallel},
    292  	bowtie2 => {-p => $parallel},
>>  293  	stringtie => {-p => $parallel},
    294      htseq => {-p => $parallel}
    295      };
    296      #
    297      # no pretty, ensure it's on one line
    298      #i
    299      my $pstring = encode_json($override);
    300      my $sstring = encode_json($dat);
    301      
    302      my $outdir = "$tmpdir";
    303      
    304      my $exps     = params_to_exps($params);
    305      my $labels   = $params->{experimental_conditions};
```

## `lib/report.py:323`

```
    317          reference_list.append("<li>" + samtools_ref + "</li>")
    318          # bowtie/hisat
    319          bowtie_ref = "Langmead B, Salzberg SL. Fast gapped-read alignment with Bowtie 2. Nat Methods. 2012 Mar 4;9(4):357-9. doi: 10.1038/nmeth.1923. PMID: 22388286; PMCID: PMC3322381."
    320          hisat_ref = "Kim, D., Paggi, J.M., Park, C. et al. Graph-based genome alignment and genotyping with HISAT2 and HISAT-genotype. Nat Biotechnol 37, 907–915 (2019). https://doi.org/10.1038/s41587-019-0201-4"
    321          reference_list.append("<li>" + bowtie_ref + "</li>")
    322          reference_list.append("<li>" + hisat_ref + "</li>")
>>  323          # stringtie
    324          stringtie_ref = "Pertea M, Pertea GM, Antonescu CM, Chang TC, Mendell JT, Salzberg SL. StringTie enables improved reconstruction of a transcriptome from RNA-seq reads. \
    325                          Nat Biotechnol. 2015 Mar;33(3):290-5. doi: 10.1038/nbt.3122. Epub 2015 Feb 18. PMID: 25690850; PMCID: PMC4643835."
    326          reference_list.append("<li>" + stringtie_ref + "</li>")
    327          # htseq
    328          htseq_ref = "Anders S, Pyl PT, Huber W. HTSeq--a Python framework to work with high-throughput sequencing data. Bioinformatics. \
    329                      2015 Jan 15;31(2):166-9. doi: 10.1093/bioinformatics/btu638. Epub 2014 Sep 25. PMID: 25260700; PMCID: PMC4287950."
    330          reference_list.append("<li>" + htseq_ref + "</li>")
    331          # tpmcalculator
    332          tpmcalculator_ref = "Roberto Vera Alvarez, Lorinc Sandor Pongor, Leonardo Mariño-Ramírez, David Landsman, TPMCalculator: \
    333                              one-step software to quantify mRNA abundance of genomic features, Bioinformatics, Volume 35, Issue 11, \
    334                              1 June 2019, Pages 1960–1962, https://doi.org/10.1093/bioinformatics/bty896"
    335          reference_list.append("<li>" + tpmcalculator_ref + "</li>")
```

