#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the scikit-learn PCA method.

doc: |-
  Analyses a given dataset through Principal Component Analysis (PCA). Visit the PCA documentation page in the sklearn official website for further information.

baseCommand: principal_component

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
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/data/dimensionality_reduction/dataset_principal_component.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 1
      prefix: --input_dataset_path

  output_results_path:
    label: Path to the analysed dataset
    doc: |-
      Path to the analysed dataset
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/dimensionality_reduction/ref_output_results_principal_component.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      position: 2
      prefix: --output_results_path
    default: system.csv

  output_plot_path:
    label: Path to the Principal Component plot, only if number of components is 2
      or 3
    doc: |-
      Path to the Principal Component plot, only if number of components is 2 or 3
      Type: string
      File type: output
      Accepted formats: png
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/dimensionality_reduction/ref_output_plot_principal_component.png
    type: string
    format:
    - edam:format_3603
    inputBinding:
      prefix: --output_plot_path
    default: system.png

  config:
    label: Advanced configuration options for biobb_ml PrincipalComponentAnalysis
    doc: |-
      Advanced configuration options for biobb_ml PrincipalComponentAnalysis. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_ml PrincipalComponentAnalysis documentation: https://biobb-ml.readthedocs.io/en/latest/dimensionality_reduction.html#module-dimensionality_reduction.principal_component
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_results_path:
    label: Path to the analysed dataset
    doc: |-
      Path to the analysed dataset
    type: File
    outputBinding:
      glob: $(inputs.output_results_path)
    format: edam:format_3752

  output_plot_path:
    label: Path to the Principal Component plot, only if number of components is 2
      or 3
    doc: |-
      Path to the Principal Component plot, only if number of components is 2 or 3
    type: File?
    outputBinding:
      glob: $(inputs.output_plot_path)
    format: edam:format_3603

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
