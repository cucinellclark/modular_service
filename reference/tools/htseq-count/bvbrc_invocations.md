# BV-BRC invocations of `htseq-count` (htseq-count)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 1 hunk(s) in 1 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/process.py`

## `lib/process.py:526`

```
    520          quant_cmd_list = []
    521          annotation_file = self.genome.get_genome_data("annotation")
    522          sample_details_list = []
    523          for sample in sample_list:
    524              bam_file = sample.get_sample_data("bam")
    525              quant_cmd = [
>>  526                  "htseq-count",
    527                  "-n",
    528                  str(threads),
    529                  "-t",
    530                  "gene",
    531                  "-f",
    532                  "bam",
    533                  "-r",
    534                  "pos",
    535                  "-i",
    536                  "ID",
    537                  bam_file,
    538                  annotation_file,
```

