#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Generates a correlation matrix from a given dataset.

doc: |-
  None

baseCommand: correlation_matrix

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
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/data/utils/dataset_correlation_matrix.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 1
      prefix: --input_dataset_path

  output_plot_path:
    label: Path to the correlation matrix plot
    doc: |-
      Path to the correlation matrix plot
      Type: string
      File type: output
      Accepted formats: png
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/utils/ref_output_plot_correlation_matrix.png
    type: string
    format:
    - edam:format_3603
    inputBinding:
      position: 2
      prefix: --output_plot_path
    default: system.png

  config:
    label: Advanced configuration options for biobb_ml CorrelationMatrix
    doc: |-
      Advanced configuration options for biobb_ml CorrelationMatrix. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_ml CorrelationMatrix documentation: https://biobb-ml.readthedocs.io/en/latest/utils.html#module-utils.correlation_matrix
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_plot_path:
    label: Path to the correlation matrix plot
    doc: |-
      Path to the correlation matrix plot
    type: File
    outputBinding:
      glob: $(inputs.output_plot_path)
    format: edam:format_3603

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
