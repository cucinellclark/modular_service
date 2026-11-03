
# Application specification: MetagenomicReadMapping

This is the application specification for service with identifier MetagenomicReadMapping.

The backend script implementing the application is [App-MetagenomicReadMapping.pl](../service-scripts/App-MetagenomicReadMapping.pl).

The raw JSON file for this specification is [MetagenomicReadMapping.json](MetagenomicReadMapping.json).

This service performs the following task:   Map metagenomic reads to a defined gene set

It takes the following parameters:

| id | label | type | required | default value |
| -- | ----- | ---- | :------: | ------------ |
| gene_set_type | Input Type | enum  | :heavy_check_mark: |  |
| gene_set_name | Gene set name | enum  |  |  |
| gene_set_fasta | Gene set FASTA data | WS: feature_protein_fasta  |  |  |
| gene_set_feature_group | Gene set feature group | string  |  |  |
| paired_end_libs |  | group  |  |  |
| single_end_libs |  | group  |  |  |
| srr_ids | SRR ID | string  |  |  |
| output_path | Output Folder | folder  | :heavy_check_mark: |  |
| output_file | File Basename | wsid  | :heavy_check_mark: |  |

