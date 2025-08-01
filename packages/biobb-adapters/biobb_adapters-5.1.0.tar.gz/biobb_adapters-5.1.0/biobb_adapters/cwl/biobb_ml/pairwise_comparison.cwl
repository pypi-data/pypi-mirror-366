#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Generates a pairwise comparison from a given dataset.

doc: |-
  None

baseCommand: pairwise_comparison

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
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/data/utils/dataset_pairwise_comparison.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 1
      prefix: --input_dataset_path

  output_plot_path:
    label: Path to the pairwise comparison plot
    doc: |-
      Path to the pairwise comparison plot
      Type: string
      File type: output
      Accepted formats: png
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/utils/ref_output_plot_pairwise_comparison.png
    type: string
    format:
    - edam:format_3603
    inputBinding:
      position: 2
      prefix: --output_plot_path
    default: system.png

  config:
    label: Advanced configuration options for biobb_ml PairwiseComparison
    doc: |-
      Advanced configuration options for biobb_ml PairwiseComparison. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_ml PairwiseComparison documentation: https://biobb-ml.readthedocs.io/en/latest/utils.html#module-utils.pairwise_comparison
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_plot_path:
    label: Path to the pairwise comparison plot
    doc: |-
      Path to the pairwise comparison plot
    type: File
    outputBinding:
      glob: $(inputs.output_plot_path)
    format: edam:format_3603

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
