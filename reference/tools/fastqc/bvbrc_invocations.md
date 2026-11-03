# BV-BRC invocations of `fastqc` (fastqc)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 28 hunk(s) in 12 file(s); showing top 25.
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/fastq_utils.py`
- `lib/process.py`
- `lib/report.py`
- `plbin/App-FastqUtils.pl`
- `plbin/p3-submit-fastqutils.pl`
- `pybin/fastq_utils.py`
- `workflows/bvbrc_SARS2Wastewater/snakefile/pe_freyja_snakefile`
- `workflows/bvbrc_SARS2Wastewater/snakefile/se_freyja_snakefile`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing_16s`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing`
- `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing_16s`

## `pybin/fastq_utils.py:49`

```
     43          return tool_params[program][feature]
     44      return None
     45  
     46  
     47  def run_fastqc(read_list, output_dir, job_data, tool_params):
     48      rcount = 0
>>   49      threads = get_param("fastqc", "-p", tool_params)
>>   50      fastqc_base_cmd = ["fastqc", "--memory", "4096", "-t", str(threads) if threads else "8"]
     51      for r in read_list:
     52          rcount += 1
>>   53          if len(r.get("fastqc", [])) == 0:
     54              fastqc_cmd = fastqc_base_cmd + ["--outdir", output_dir]
     55              if "read2" in r:
     56                  fastqc_cmd += [r["read1"], r["read2"]]
>>   57                  r["fastqc"].append(
     58                      os.path.join(
     59                          output_dir, os.path.basename(r["read1"]) + ".fastqc.html"
     60                      )
     61                  )
>>   62                  r["fastqc"].append(
     63                      os.path.join(
     64                          output_dir, os.path.basename(r["read2"]) + ".fastqc.html"
     65                      )
     66                  )
     67              else:
     68                  fastqc_cmd += [r["read1"]]
>>   69                  r["fastqc"].append(
     70                      os.path.join(
     71                          output_dir, os.path.basename(r["read1"]) + ".fastqc.html"
     72                      )
     73                  )
     74              print((" ".join(fastqc_cmd)))
     75              subprocess.run(fastqc_cmd, check=True)
     76  
     77  
     78  def find_prefix(filename):
     79      r1_parts = filename.split(".")
     80      prefix_pos = (
     81          -2
```

## `pybin/fastq_utils.py:100`

```
     94      rcount = 0
     95      trimmed_reads = []
     96      threads = get_param("trim_galore", "-p", tool_params)
     97      trim_base_cmd = ["trim_galore", "-j", str(threads) if threads else "1"]
     98      for r in read_list:
     99          tr = copy.deepcopy(r)
>>  100          tr["fastqc"] = []
    101          cur_check = []
    102          rename_files = {}
    103          rcount += 1
    104          # trim_galore --gzip --paired -o ../fonsynbiothr/trimmed_reads/ ../fonsynbiothr/fastq_files/926M_RNA_S8_L001_R1_001.fastq ../fonsynbiothr/fastq_files/926M_RNA_S8_L001_R2_001.fastq
    105          trim_cmd = trim_base_cmd + ["--gzip", "-o", output_dir]
    106          if "read2" in r:
    107              trim_cmd += ["--paired", r["read1"], r["read2"]]
    108              pre_pos = find_prefix(r["read1"])
    109              old_name = os.path.join(
    110                  output_dir,
    111                  ".".join(os.path.basename(r["read1"]).split(".")[0:pre_pos])
    112                  + "_val_1.fq.gz",
```

## `pybin/fastq_utils.py:632`

```
    626                              r["read2"] = os.path.join(target_dir, f)
    627                          elif f.endswith("_1.fastq"):
    628                              r["read1"] = os.path.join(target_dir, f)
    629                          elif f.endswith(".fastq"):
    630                              r["read1"] = os.path.join(target_dir, f)
    631                          elif f.endswith("fastqc.html"):
>>  632                              r["fastqc"].append(os.path.join(target_dir, f))
    633      recipe = job_data.get("recipe", [])
    634      new_read_list = []
    635      for r in read_list:
    636          if "read1" in r and "read2" not in r and os.path.exists(r["read1"]):
    637              r["read1"] = moveRead(r["read1"])
    638              new_read_list.append(r)
    639          if (
    640              "read1" in r
    641              and "read2" in r
    642              and os.path.exists(r["read1"])
    643              and os.path.exists(r["read2"])
    644          ):
```

## `lib/fastq_utils.py:49`

```
     43          return tool_params[program][feature]
     44      return None
     45  
     46  
     47  def run_fastqc(read_list, output_dir, job_data, tool_params):
     48      rcount = 0
>>   49      threads = get_param("fastqc", "-p", tool_params)
>>   50      fastqc_base_cmd = ["fastqc", "--memory", "4096", "-t", str(threads) if threads else "8"]
     51      for r in read_list:
     52          rcount += 1
>>   53          if len(r.get("fastqc", [])) == 0:
     54              fastqc_cmd = fastqc_base_cmd + ["--outdir", output_dir]
     55              if "read2" in r:
     56                  fastqc_cmd += [r["read1"], r["read2"]]
>>   57                  r["fastqc"].append(
     58                      os.path.join(
     59                          output_dir, os.path.basename(r["read1"]) + ".fastqc.html"
     60                      )
     61                  )
>>   62                  r["fastqc"].append(
     63                      os.path.join(
     64                          output_dir, os.path.basename(r["read2"]) + ".fastqc.html"
     65                      )
     66                  )
     67              else:
     68                  fastqc_cmd += [r["read1"]]
>>   69                  r["fastqc"].append(
     70                      os.path.join(
     71                          output_dir, os.path.basename(r["read1"]) + ".fastqc.html"
     72                      )
     73                  )
     74              print((" ".join(fastqc_cmd)))
     75              subprocess.run(fastqc_cmd, check=True)
     76  
     77  
     78  def find_prefix(filename):
     79      r1_parts = filename.split(".")
     80      prefix_pos = (
     81          -2
```

## `lib/fastq_utils.py:100`

```
     94      rcount = 0
     95      trimmed_reads = []
     96      threads = get_param("trim_galore", "-p", tool_params)
     97      trim_base_cmd = ["trim_galore", "-j", str(threads) if threads else "1"]
     98      for r in read_list:
     99          tr = copy.deepcopy(r)
>>  100          tr["fastqc"] = []
    101          cur_check = []
    102          rename_files = {}
    103          rcount += 1
    104          # trim_galore --gzip --paired -o ../fonsynbiothr/trimmed_reads/ ../fonsynbiothr/fastq_files/926M_RNA_S8_L001_R1_001.fastq ../fonsynbiothr/fastq_files/926M_RNA_S8_L001_R2_001.fastq
    105          trim_cmd = trim_base_cmd + ["--gzip", "-o", output_dir]
    106          if "read2" in r:
    107              trim_cmd += ["--paired", r["read1"], r["read2"]]
    108              pre_pos = find_prefix(r["read1"])
    109              old_name = os.path.join(
    110                  output_dir,
    111                  ".".join(os.path.basename(r["read1"]).split(".")[0:pre_pos])
    112                  + "_val_1.fq.gz",
```

## `lib/fastq_utils.py:632`

```
    626                              r["read2"] = os.path.join(target_dir, f)
    627                          elif f.endswith("_1.fastq"):
    628                              r["read1"] = os.path.join(target_dir, f)
    629                          elif f.endswith(".fastq"):
    630                              r["read1"] = os.path.join(target_dir, f)
    631                          elif f.endswith("fastqc.html"):
>>  632                              r["fastqc"].append(os.path.join(target_dir, f))
    633      recipe = job_data.get("recipe", [])
    634      new_read_list = []
    635      for r in read_list:
    636          if "read1" in r and "read2" not in r and os.path.exists(r["read1"]):
    637              r["read1"] = moveRead(r["read1"])
    638              new_read_list.append(r)
    639          if (
    640              "read1" in r
    641              and "read2" in r
    642              and os.path.exists(r["read1"])
    643              and os.path.exists(r["read2"])
    644          ):
```

## `lib/process.py:1718`

```
   1712                  reads_results.append(future.result())
   1713          return all(reads_results)
   1714  
   1715      def run_fastqc(self, sample):
   1716          sample_dir = sample.get_path()
   1717          reads = sample.get_reads_as_list()
>> 1718          fastqc_cmd = ["fastqc", "--outdir", sample_dir]
   1719          fastqc_cmd += reads
>> 1720          sample.add_command("fastqc", fastqc_cmd, "running")
   1721          print("Running command:\n {0}".format(" ".join(fastqc_cmd)))
   1722          try:
   1723              # TODO: ENABLE
   1724              subprocess.check_call(fastqc_cmd)
>> 1725              sample.set_command_status("fastqc", "finished")
   1726          except Exception as e:
   1727              sys.stderr.write(
   1728                  "FastQC encountered an error in Sample {0}:\ncheck error log file".format(
   1729                      sample.get_id()
   1730                  )
   1731              )
>> 1732              sample.set_command_status("fastqc", e)
   1733              return False
   1734  
   1735      # runs trim_galore on samples
   1736      # TODO: option for rerunning fastqc?
   1737      # TODO: option for adapter specification
   1738      def run_trimming(self, sample, threads):
   1739          sample_dir = sample.get_path()
   1740          reads = sample.get_reads_as_list()
   1741          trimmed_reads = []
   1742          trim_cmd = [
   1743              "trim_galore",
   1744              "--output_dir",
```

## `pybin/fastq_utils.py:601`

```
    595          + job_data.get("single_end_libs", [])
    596          + job_data.get("srr_libs", [])
    597      ):
    598          if "read" in r:
    599              r["read1"] = r.pop("read")
    600          read_list.append(r)
>>  601          r["fastqc"] = []
    602          target_dir = output_dir
    603          rcount += 1
    604          if "srr_accession" in r:
    605              srr_id = r["srr_accession"]
    606              meta_file = os.path.join(target_dir, srr_id + "_meta.txt")
    607              sra_cmd = [
    608                  "p3-sra",
    609                  "--out",
    610                  target_dir,
    611                  "--metadata-file",
    612                  meta_file,
    613                  "--id",
```

## `workflows/bvbrc_SARS2Wastewater/snakefile/pe_freyja_snakefile:155`

```
    149          fastqc_html = "output/{zpd_sample}/fastqc_results/{zpd_sample}_R{unzpd_read_num}_fastqc.html",
    150      shell:
    151          """
    152          mkdir -p {params.fastqc_dir}
    153          mkdir -p {params.clean_up}
    154  
>>  155          fastqc --version
    156  
>>  157          fastqc {input.raw_read} \
    158          -o {params.fastqc_dir} -q
    159          """
    160  
    161  rule fastqc_unzpd_reads:
    162      input:
    163          raw_read = "staging/pe_reads/{unzpd_sample}_R{unzpd_read_num}.fastq",
    164      params:
    165          fastqc_dir = directory("output/{unzpd_sample}/fastqc_results"),
    166          clean_up = directory("clean_up"),
    167      output:
    168          fastqc_html = "output/{unzpd_sample}/fastqc_results/{unzpd_sample}_R{unzpd_read_num}_fastqc.html",
    169      shell:
    170          """
    171          mkdir -p {params.fastqc_dir}
    172          mkdir -p {params.clean_up}
    173  
>>  174          fastqc --version
    175  
>>  176          fastqc {input.raw_read} \
    177          -o {params.fastqc_dir} -q
    178          """
    179  
    180  rule fastqc_ivar:
    181      input:
    182          ivar_bam = "output/{sample}/assembly/{sample}.ivar.bam",
    183          ivar_sorted_bam = "output/{sample}/assembly/{sample}.sorted.bam"
    184      params:
    185          fastqc_dir = "output/{sample}/fastqc_results",
    186          clean_up = "clean_up",
    187      output:
    188          ivar_html = "output/{sample}/fastqc_results/{sample}.ivar_fastqc.html",
    189          ivar_sorted_html = "output/{sample}/fastqc_results/{sample}.sorted_fastqc.html",
    190      shell:
    191          """
    192          mkdir -p {params.fastqc_dir}
    193          mkdir -p {params.clean_up}
    194  
>>  195          fastqc --version
    196  
>>  197          fastqc {input.ivar_bam} \
    198          -o {params.fastqc_dir} -q
    199  
>>  200          fastqc {input.ivar_sorted_bam} \
    201          -o {params.fastqc_dir} -q
    202          """
    203  
    204  rule samtools_flagstat:
    205      input:
    206          ivar_sorted_bam = "output/{sample}/assembly/{sample}.sorted.bam"
    207      output:
    208          flagstat_txt = "output/{sample}/assembly/{sample}_flagstat.txt"
    209      shell:
    210          """
    211          samtools flagstat {input.ivar_sorted_bam} > {output.flagstat_txt}
    212          """
```

## `workflows/bvbrc_SARS2Wastewater/snakefile/se_freyja_snakefile:148`

```
    142          fastqc_html = 'output/{zpd_sample}/fastqc_results/{zpd_sample}_fastqc.html',
    143      shell:
    144          '''
    145          mkdir -p {params.fastqc_dir}
    146          mkdir -p {params.clean_up}
    147  
>>  148          fastqc --version
    149  
>>  150          fastqc {input.raw_read} \
    151          -o {params.fastqc_dir} -q
    152          '''
    153  
    154  rule fastqc_unzpd_reads:
    155      input:
    156          raw_read = 'staging/se_reads/{unzpd_sample}.fastq',
    157      params:
    158          fastqc_dir = 'output/{unzpd_sample}/fastqc_results',
    159          clean_up = 'clean_up',
    160      output:
    161          fastqc_html = 'output/{unzpd_sample}/fastqc_results/{unzpd_sample}_fastqc.html',
    162      shell:
    163          '''
    164          mkdir -p {params.fastqc_dir}
    165          mkdir -p {params.clean_up}
    166  
>>  167          fastqc --version
    168  
>>  169          fastqc {input.raw_read} \
    170          -o {params.fastqc_dir} -q
    171          '''
    172  
    173  rule fastqc_ivar:
    174      input:
    175          ivar_bam = 'output/{sample}/assembly/{sample}.ivar.bam',
    176          ivar_sorted_bam = 'output/{sample}/assembly/{sample}.sorted.bam'
    177      params:
    178          fastqc_dir = 'output/{sample}/fastqc_results',
    179          clean_up = 'clean_up',
    180      output:
    181          ivar_html = 'output/{sample}/fastqc_results/{sample}.ivar_fastqc.html',
    182          ivar_sorted_html = 'output/{sample}/fastqc_results/{sample}.sorted_fastqc.html',
    183      shell:
    184          '''
    185          mkdir -p {params.fastqc_dir}
    186          mkdir -p {params.clean_up}
    187  
>>  188          fastqc --version
    189  
>>  190          fastqc {input.ivar_bam} \
    191          -o {params.fastqc_dir} -q
    192  
>>  193          fastqc {input.ivar_sorted_bam} \
    194          -o {params.fastqc_dir} -q
    195          '''
    196  
    197  rule samtools_flagstat:
    198      input:
    199          ivar_sorted_bam = "output/{sample}/assembly/{sample}.sorted.bam"
    200      output:
    201          flagstat_txt = "output/{sample}/assembly/{sample}_flagstat.txt"
    202      shell:
    203          """
    204          samtools flagstat {input.ivar_sorted_bam} > {output.flagstat_txt}
    205          """
```

## `lib/fastq_utils.py:601`

```
    595          + job_data.get("single_end_libs", [])
    596          + job_data.get("srr_libs", [])
    597      ):
    598          if "read" in r:
    599              r["read1"] = r.pop("read")
    600          read_list.append(r)
>>  601          r["fastqc"] = []
    602          target_dir = output_dir
    603          rcount += 1
    604          if "srr_accession" in r:
    605              srr_id = r["srr_accession"]
    606              meta_file = os.path.join(target_dir, srr_id + "_meta.txt")
    607              sra_cmd = [
    608                  "p3-sra",
    609                  "--out",
    610                  target_dir,
    611                  "--metadata-file",
    612                  meta_file,
    613                  "--id",
```

## `plbin/App-FastqUtils.pl:170`

```
    164      open(JDESC, ">", $jdesc) or die "Cannot write $jdesc: $!";
    165      print JDESC JSON::XS->new->pretty(1)->encode($params_to_app);
    166      close(JDESC);
    167  
    168      my $parallel = $ENV{P3_ALLOCATED_CPU};
    169      my $override = {
>>  170  	fastqc => { -p => $parallel},
    171  	trim_galore => {-p => $parallel},
    172  	bowtie2 => {-p => $parallel},
    173  	hisat2 => {-p => $parallel},
    174  	samtools_view => {-p => $parallel},
    175  	samtools_index => {-p => $parallel},
    176      samtools_sort => {-p => $parallel}
    177      };
    178  
    179      my @cmd = ("p3-fqutils",
    180  	       "--jfile", $jdesc,
    181  	       "--sstring", $sstring,
    182  	       "-p", encode_json($override),
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing:108`

```
    102          fastqc_zip = 'output/{sample}/fastqc_results/raw_reads/raw_{sample}_R{read_num}_fastqc.zip'
    103      threads: 4
    104      shell:
    105          '''
    106          mkdir -p {params.fastqc_dir}
    107  
>>  108          fastqc --version
    109          
>>  110          fastqc {input.raw_read} \
    111          -t {threads} \
    112          -o {params.fastqc_dir} -q
    113  
    114          echo {params.fastqc_dir}/{wildcards.sample}_{wildcards.read_num}_fastqc.html
    115          echo {wildcards.sample}
    116          echo {wildcards.read_num}
    117  
    118          mv {params.fastqc_dir}/{wildcards.sample}_R{wildcards.read_num}_fastqc.html {output.fastqc_html}
    119          mv {params.fastqc_dir}/{wildcards.sample}_R{wildcards.read_num}_fastqc.zip {output.fastqc_zip}
    120          '''
    121  
    122  rule hisat2_remove_host_dna:
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing:169`

```
    163          fastqc_zip = 'output/{sample}/fastqc_results/host_removed_reads/{sample}_host_removed_R{read_num}_fastqc.zip'
    164      threads: 4
    165      shell:
    166          '''
    167          mkdir -p {params.fastqc_dir}
    168  
>>  169          fastqc --version
    170          
>>  171          fastqc {input.clean_read} \
    172          -t {threads} \
    173          -o {params.fastqc_dir} -q
    174          '''
    175  
    176  rule classify_with_kraken:
    177      input:
    178          kraken2_input_r1 = k_r1,
    179          kraken2_input_r2 = k_r2
    180      params: 
    181          database = database_path,
    182          kraken_dir = 'output/{sample}/kraken_output',
    183          classified_flag = cf,
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing_16s:80`

```
     74          fastqc_zip = 'output/{sample}/fastqc_results/raw_reads/raw_{sample}_R{read_num}_fastqc.zip'
     75      threads: 4
     76      shell:
     77          '''
     78          mkdir -p {params.fastqc_dir}
     79  
>>   80          fastqc --version
     81          
>>   82          fastqc {input.raw_read} \
     83          -t {threads} \
     84          -o {params.fastqc_dir} -q
     85  
     86          mv {params.fastqc_dir}/{wildcards.sample}_R{wildcards.read_num}_fastqc.html {output.fastqc_html}
     87          mv {params.fastqc_dir}/{wildcards.sample}_R{wildcards.read_num}_fastqc.zip {output.fastqc_zip}
     88          '''
     89  
     90  rule trim_adapters:
     91      input:
     92          r1 ='staging/pe_reads/{sample}_R1.fastq.gz',
     93          r2 = 'staging/pe_reads/{sample}_R2.fastq.gz'
     94      params:
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing_16s:122`

```
    116          fastqc_zip = 'output/{sample}/fastqc_results/trimmed_reads/{sample}_R{read_num}_trimmed_fastqc.zip'
    117      threads: 4
    118      shell:
    119          '''
    120          mkdir -p {params.fastqc_dir}
    121  
>>  122          fastqc --version
    123          
>>  124          fastqc {input.trimmed_read} \
    125          -t {threads} \
    126          -o {params.fastqc_dir} -q
    127          '''
    128  
    129  rule classify_with_kraken:
    130      input:
    131          kraken2_input_r1 = 'output/{sample}/trimmed_reads/{sample}_R1_trimmed.fastq.gz',
    132          kraken2_input_r2 = 'output/{sample}/trimmed_reads/{sample}_R2_trimmed.fastq.gz'
    133      params: 
    134          database = database_path,
    135          kraken_dir = 'output/{sample}/kraken_output',
    136          classified_flag = cf,
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing:95`

```
     89          fastqc_zip = 'output/{sample}/fastqc_results/raw_reads/raw_{sample}_fastqc.zip'
     90      threads: 4
     91      shell:
     92          '''
     93          mkdir -p {params.fastqc_dir}
     94  
>>   95          fastqc --version
     96          
>>   97          fastqc {input.raw_read} \
     98          -t {threads} \
     99          -o {params.fastqc_dir} -q
    100  
    101          mv {params.fastqc_dir}/{wildcards.sample}_fastqc.html {output.fastqc_html}
    102          mv {params.fastqc_dir}/{wildcards.sample}_fastqc.zip {output.fastqc_zip}
    103          '''
    104  
    105  
    106  rule hisat2_remove_host_dna:
    107      input:
    108          raw_read = 'staging/se_reads/{sample}.fastq.gz',
    109      params:
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing:147`

```
    141          fastqc_zip = 'output/{sample}/fastqc_results/host_removed_reads/{sample}_host_removed_fastqc.zip'
    142      threads: 4
    143      shell:
    144          '''
    145          mkdir -p {params.fastqc_dir}
    146  
>>  147          fastqc --version
    148          
>>  149          fastqc {input.clean_read} \
    150          -t {threads} \
    151          -o {params.fastqc_dir} -q
    152          '''
    153  
    154  rule classify_with_kraken:
    155      input:
    156          kraken2_input = k_input
    157      params:
    158          database = database_path,
    159          kraken_dir = 'output/{sample}/kraken_output',
    160          classified_flag = cf,
    161          classified_fq = co,
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing_16s:65`

```
     59          fastqc_zip = 'output/{sample}/fastqc_results/raw_read/raw_{sample}_fastqc.zip'
     60      threads: 4
     61      shell:
     62          '''
     63          mkdir -p {params.fastqc_dir}
     64  
>>   65          fastqc --version
     66          
>>   67          fastqc {input.raw_read} \
     68          -t {threads} \
     69          -o {params.fastqc_dir} -q
     70  
     71          mv {params.fastqc_dir}/{wildcards.sample}_fastqc.html {output.fastqc_html}
     72          mv {params.fastqc_dir}/{wildcards.sample}_fastqc.zip {output.fastqc_zip}
     73          '''
     74  
     75  rule trim_adapters:
     76      input:
     77          raw_read = 'staging/se_reads/{sample}.fastq.gz',
     78      params:
     79          out_dir = 'output/{sample}/trimmed_read/',
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing_16s:105`

```
     99          fastqc_zip = 'output/{sample}/fastqc_results/trimmed_read/{sample}_trimmed_fastqc.zip'
    100      threads: 4
    101      shell:
    102          '''
    103          mkdir -p {params.fastqc_dir}
    104  
>>  105          fastqc --version
    106          
>>  107          fastqc {input.trimmed_read} \
    108          -t {threads} \
    109          -o {params.fastqc_dir} -q
    110          '''
    111  
    112  
    113  rule classify_with_kraken:
    114      input:
    115          kraken2_input = 'output/{sample}/trimmed_read/{sample}_trimmed.fastq.gz',
    116      params:
    117          database = database_path,
    118          kraken_dir = 'output/{sample}/kraken_output',
    119          classified_flag = cf,
```

## `plbin/App-FastqUtils.pl:29`

```
     23  exit $rc;
     24  
     25  sub preflight
     26  {
     27      my($app, $app_def, $raw_params, $params) = @_;
     28  
>>   29      print STDERR "preflight fastqc ", Dumper($params, $app);
     30  
     31      my $token = $app->token();
     32      my $ws = $app->workspace();
     33  
     34      my $readset;
     35      eval {
     36  	$readset = Bio::KBase::AppService::ReadSet->create_from_asssembly_params($params);
     37      };
     38      if ($@)
     39      {
     40  	die "Error parsing assembly parameters: $@";
     41      }
```

## `plbin/p3-submit-fastqutils.pl:105`

```
     99  my $align = 0;
    100  my $referenceGenomeId;
    101  # Now we parse the options.
    102  GetOptions($commoner->options(), $reader->lib_options(),
    103          'trim' => \$trim,
    104          'paired-filter' => \$pairedFilter,
>>  105          'fastqc' => \$fastqc,
    106          'reference-genome-id|ref|genome=s' => \$referenceGenomeId
    107          );
    108  # Verify the argument count.
    109  if (! $ARGV[0] || ! $ARGV[1]) {
    110      die "Too few parameters-- output path and output name are required.";
    111  } elsif (scalar @ARGV > 2) {
    112      die "Too many parameters-- only output path and output name should be specified.  Found : \"" . join('", "', @ARGV) . '"';
    113  }
    114  # Handle the output path and name.
    115  my ($outputPath, $outputFile) = $uploader->output_spec(@ARGV);
    116  # We will build the recipe list here.
    117  my $recipes = [];
    118  if ($pairedFilter) { push @$recipes, 'paired_filter'; }
    119  if ($trim) { push @$recipes, 'trim'; }
>>  120  if ($fastqc) { push @$recipes, 'fastqc' }
    121  if ($referenceGenomeId) {
    122      if (! Bio::KBase::AppService::GenomeIdSpec::validate_genome('--reference-genome-id' => $referenceGenomeId)) {
    123          die "Invalid reference genome ID.";
    124      }
    125      push @$recipes, 'align';
    126  }
    127  if (! @$recipes) {
    128      die "No service specified.";
    129  }
    130  # Build the parameter structure.
    131  my $params = {
    132      recipe => $recipes,
```

## `pybin/fastq_utils.py:677`

```
    671  
    672  def run_fq_util(job_data, output_dir, tool_params={}):
    673      # arguments:
    674      # list of genomes [{"genome":somefile,"annotation":somefile}]
    675      # dictionary of library dictionaries structured as {libraryname:{library:libraryname, replicates:[{read1:read1file, read2:read2file}]}}
    676      # parametrs_file is a json keyed parameters list.
>>  677      # Example tool_params: '{"fastqc":{"-p":"2"},"trim_galore":{"-p":"2"},"bowtie2":{"-p":"2"},"hisat2":{"-p":"2"},"samtools_view":{"-p":"2"},"samtools_index":{"-p":"2"}}'
    678      output_dir = os.path.abspath(output_dir)
    679      if not os.path.isdir(output_dir):
    680          os.makedirs(output_dir)
    681      genome_list, read_list, recipe = setup(job_data, output_dir, tool_params)
    682      # print("genome_list: {}\nread_list: {}\nrecipe: {}".format(genome_list, read_list, recipe), file=sys.stdout)
    683      # sys.stdout.flush()
    684      for step in recipe:
    685          step = step.upper()
    686          if step == "TRIM":
    687              trimmed_reads = run_trim(read_list, output_dir, job_data, tool_params)
    688              read_list = trimmed_reads
    689          elif step == "PAIRED_FILTER":
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/pe_fastq_processing:73`

```
     67      "mustela_putorius_furo" : "GCF_000215625.1_MusPutFur1.0_genomic",
     68      "sus_scrofa" : "GCF_000003025.6_Sscrofa11.1_genomic"}
     69  
     70  # setting rules according to host 
     71  if host_genome == "no_host":
     72      hisat_indices = None
>>   73      msg = 'No host selected. SKIPPING Hisat2 to remove host dna and fastqc on host removed reads.  \n'
     74      # set kraken input to raw reads as default
     75      k_r1 ='staging/pe_reads/{sample}_R1.fastq.gz'
     76      k_r2 = 'staging/pe_reads/{sample}_R2.fastq.gz'
     77  else:
     78      # append to rule all list 
     79      rule_all_list.append(expand('output/{sample}/hisat2_results/{sample}_host_removed_R{read_num}.fastq.gz', sample=samples, read_num=read_nums)),
     80      rule_all_list.append(expand('output/{sample}/fastqc_results/host_removed_reads/{sample}_host_removed_R{read_num}_fastqc.html', sample=samples, read_num=read_nums)),
     81      # update kraken input to include host removed reads 
     82      k_r1 = 'output/{sample}/hisat2_results/{sample}_host_removed_R1.fastq.gz'
     83      k_r2 = 'output/{sample}/hisat2_results/{sample}_host_removed_R2.fastq.gz'
     84      # update rule order
     85      ruleorder: fastqc_raw_reads > hisat2_remove_host_dna > fastqc_on_host_removed_reads > classify_with_kraken
     86      # select the correct indices
     87      hisat_indices = host_dict[host_genome]
>>   88      msg = f'Host genome {host_genome} selected. ADDING Hisat2 to remove host dna and fastqc on host removed reads. \n'
     89  sys.stderr.write(msg)
     90  
     91  rule all:
     92      input:
     93          rule_all_list
     94  
     95  rule fastqc_raw_reads:
     96      input:
     97          raw_read = 'staging/pe_reads/{sample}_R{read_num}.fastq.gz',
     98      params:
     99          fastqc_dir = 'output/{sample}/fastqc_results/raw_reads',
    100      output:
```

## `workflows/bvbrc_taxonomic_classification_2/snakefile/se_fastq_processing:62`

```
     56  
     57  # setting rules according to host
     58  if host_genome == "no_host":
     59      hisat_indices = None
     60      # set kraken input to trimmed reads as default
     61      k_input = "staging/se_reads/{sample}.fastq.gz"
>>   62      msg = 'No host selected. SKIPPING Hisat2 to remove host dna and fastqc on host removed reads \n'
     63  else:
     64      # append to rule all list
     65      # update kraken input to include host removed reads 
     66      rule_all_list.append(expand('output/{sample}/hisat2_results/{sample}_host_removed.fastq.gz', sample=samples)),
     67      rule_all_list.append(expand('output/{sample}/fastqc_results/host_removed_reads/{sample}_host_removed_fastqc.html', sample=samples)),
     68      # update rule order
     69      ruleorder: fastqc_raw_reads > hisat2_remove_host_dna > fastqc_on_host_removed_reads > classify_with_kraken
     70      # select the correct indicies
     71      hisat_indices = host_dict[host_genome]
     72      k_input = "output/{sample}/hisat2_results/{sample}_host_removed.fastq.gz"
>>   73      msg = f'Host genome {host_genome} selected. ADDING Hisat2 to remove host dna and fastqc on host removed reads \n'
     74  
     75  sys.stderr.write(msg)
     76  
     77  rule all:
     78      input:
     79          rule_all_list
     80  
     81  rule fastqc_raw_reads:
     82      input:
     83          raw_read = 'staging/se_reads/{sample}.fastq.gz',
     84      params:
     85          fastqc_dir = 'output/{sample}/fastqc_results/raw_reads',
```

