
# Application specification: GenomeComparison

This is the application specification for service with identifier GenomeComparison.

The backend script implementing the application is [App-GenomeComparison.pl](../service-scripts/App-GenomeComparison.pl).

The raw JSON file for this specification is [GenomeComparison.json](GenomeComparison.json).

This service performs the following task:   Compare the proteome sets from multiple genomes using Blast

It takes the following parameters:

| id | label | type | required | default value |
| -- | ----- | ---- | :------: | ------------ |
| genome_ids | Genome IDs | string  |  |  |
| user_genomes | Genome protein sequence files | WS: feature_protein_fasta  |  |  |
| user_feature_groups | User feature groups | WS: feature_group  |  |  |
| reference_genome_index | Index of genome to be used as reference | int  |  | 1 |
| min_seq_cov | Minimum coverage of query and subject | float  |  | 0.3 |
| max_e_val | Maximum E-value | float  |  | 1e-05 |
| min_ident | Minimum fraction identity | float  |  | 0.1 |
| min_positives | Minimum fraction positive-scoring positions | float  |  | 0.2 |
| output_path | Output Folder | folder  | :heavy_check_mark: |  |
| output_file | File Basename | wsid  | :heavy_check_mark: |  |

