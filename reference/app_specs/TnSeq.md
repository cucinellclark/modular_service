
# Application specification: TnSeq

This is the application specification for service with identifier TnSeq.

The backend script implementing the application is [App-TnSeq.pl](../service-scripts/App-TnSeq.pl).

The raw JSON file for this specification is [TnSeq.json](TnSeq.json).

This service performs the following task:   Use TRANSIT to analyze TnSeq data

It takes the following parameters:

| id | label | type | required | default value |
| -- | ----- | ---- | :------: | ------------ |
| experimental_conditions | Experimental conditions | list  |  | ARRAY(0x55be19a74038) |
| contrasts | Contrasts | list  |  | ARRAY(0x55be199acf08) |
| read_files |  | group  |  |  |
| reference_genome_id | Reference genome ID | string  | :heavy_check_mark: |  |
| recipe | TnSeq recipe | enum  |  | gumbel |
| protocol | TnSeq protocol | enum  |  | sassetti |
| primer | Primer DNA string. | string  |  |  |
| output_path | Output Folder | folder  | :heavy_check_mark: |  |
| output_file | File Basename | wsid  | :heavy_check_mark: |  |

