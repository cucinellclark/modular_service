
# Application specification: ModelReconstruction

This is the application specification for service with identifier ModelReconstruction.

The backend script implementing the application is [App-ModelReconstruction.pl](../service-scripts/App-ModelReconstruction.pl).

The raw JSON file for this specification is [ModelReconstruction.json](ModelReconstruction.json).

This service performs the following task:   Reconstructs a metabolic model from an annotated genome.

It takes the following parameters:

| id | label | type | required | default value |
| -- | ----- | ---- | :------: | ------------ |
| genome | Genome object | WS: genome  | :heavy_check_mark: |  |
| media | Gapfilling media | WS: media  |  |  |
| template_model | Template model | WS: template_model  |  |  |
| fulldb | Full DB model | bool  | :heavy_check_mark: | 0 |
| output_path | Output Folder | folder  |  |  |
| output_file | File Basename | wsid  |  |  |

