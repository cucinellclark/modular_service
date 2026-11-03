
# Application specification: Variation

This is the application specification for service with identifier Variation.

The backend script implementing the application is [App-Variation.pl](../service-scripts/App-Variation.pl).

The raw JSON file for this specification is [Variation.json](Variation.json).

This service performs the following task:   Identify and annotate small nucleotide variations relative to a reference genome

It takes the following parameters:

| id | label | type | required | default value |
| -- | ----- | ---- | :------: | ------------ |
| reference_genome_id | Reference genome ID | string  | :heavy_check_mark: |  |
| paired_end_libs |  | group  |  |  |
| single_end_libs |  | group  |  |  |
| srr_ids | SRR ID | string  |  |  |
| reference_genome_id | Reference genome ID | string  |  |  |
| mapper | Short read mapper | enum  |  | BWA-mem |
| caller | SNP caller | enum  |  | FreeBayes |
| output_path | Output Folder | folder  | :heavy_check_mark: |  |
| output_file | File Basename | wsid  | :heavy_check_mark: |  |
| debug | Run job in debug mode | bool  |  | 0 |

