cwlVersion: v1.2
class: Workflow
label: "fastp -> minimap2 -> samtools coverage (hand-written preview of modpipe compile)"
requirements:
  StepInputExpressionRequirement: {}
  InlineJavascriptRequirement: {}
inputs:
  reads: Any
  reference: Any
  output_path: string
  run_name: string
outputs:
  coverage: {type: "Directory?", outputSource: cov/coverage}
  alignment: {type: "Directory?", outputSource: map/alignment}
steps:
  trim:
    run: ../../cwl/tools/fastp.cwl
    in:
      reads: reads
      output_path: output_path
      output_file: {source: run_name, valueFrom: $(self + "_fastp")}
    out: [trimmed_reads]
  map:
    run: ../../cwl/tools/minimap2.cwl
    in:
      reads: trim/trimmed_reads
      reference: reference
      input_types: {valueFrom: '$({"reference": "sequences.dna.contigs"})'}
      output_path: output_path
      output_file: {source: run_name, valueFrom: $(self + "_minimap2")}
    out: [alignment]
  cov:
    run: ../../cwl/tools/samtools_coverage.cwl
    in:
      alignment: map/alignment
      output_path: output_path
      output_file: {source: run_name, valueFrom: $(self + "_coverage")}
    out: [coverage]
