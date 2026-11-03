
# Application specification: GapfillModel

This is the application specification for service with identifier GapfillModel.

The backend script implementing the application is [App-GapfillModel.pl](../service-scripts/App-GapfillModel.pl).

The raw JSON file for this specification is [GapfillModel.json](GapfillModel.json).

This service performs the following task:   Run gapfilling on model.

It takes the following parameters:

| id | label | type | required | default value |
| -- | ----- | ---- | :------: | ------------ |
| model | Model object | WS: model  | :heavy_check_mark: |  |
| media | FBA media | WS: media  |  |  |
| probanno | Probabilistic annotation | WS: probanno  |  |  |
| alpha | Comprehensive gapfilling priority | float  |  | 0 |
| allreversible | Make all reactions reversible | bool  |  | 0 |
| allowunbalanced | Allow unbalanced reactions in gapfilling | bool  |  | 0 |
| integrate_solution | Integrate first gapfilling solution | bool  |  | 0 |
| thermo_const_type | Thermodynamic constraints | enum  |  |  |
| media_supplement | Media supplements | string  |  |  |
| geneko | Gene knockouts | string  |  |  |
| rxnko | Reaction knockouts | string  |  |  |
| target_reactions | Target reactions | string  |  |  |
| objective_fraction | Objective fraction | float  |  | 0.001 |
| low_expression_theshold | Threshold of expression for gene to be consider inactive | float  |  | 1 |
| high_expression_theshold | Threshold of expression for gene to be consider active | float  |  | 1 |
| output_file | File Basename | wsid  |  |  |
| uptake_limit |  | group  |  |  |
| custom_bounds |  | group  |  |  |
| objective |  | group  |  |  |

