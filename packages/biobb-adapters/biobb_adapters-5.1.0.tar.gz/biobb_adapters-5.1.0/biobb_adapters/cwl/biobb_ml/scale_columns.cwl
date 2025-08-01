#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Scales columns from a given dataset.

doc: |-
  None

baseCommand: scale_columns

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_ml:4.1.0--pyhdfd78af_0

inputs:
  input_dataset_path:
    label: Path to the input dataset
    doc: |-
      Path to the input dataset
      Type: string
      File type: input
      Accepted formats: csv
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/data/utils/dataset_scale.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 1
      prefix: --input_dataset_path

  output_dataset_path:
    label: Path to the output dataset
    doc: |-
      Path to the output dataset
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/utils/ref_output_scale.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      position: 2
      prefix: --output_dataset_path
    default: system.csv

  config:
    label: Advanced configuration options for biobb_ml ScaleColumns
    doc: |-
      Advanced configuration options for biobb_ml ScaleColumns. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_ml ScaleColumns documentation: https://biobb-ml.readthedocs.io/en/latest/utils.html#module-utils.scale_columns
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_dataset_path:
    label: Path to the output dataset
    doc: |-
      Path to the output dataset
    type: File
    outputBinding:
      glob: $(inputs.output_dataset_path)
    format: edam:format_3752

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
