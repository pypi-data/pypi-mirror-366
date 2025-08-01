#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of most of the imblearn.under_sampling methods.

doc: |-
  Remove samples from the majority class of a given dataset, with or without replacement. If regression is specified as type, the data will be resampled to classes in order to apply the undersampling model. Visit the imbalanced-learn official website for the different methods accepted in this wrapper: RandomUnderSampler, NearMiss, CondensedNearestNeighbour, TomekLinks, EditedNearestNeighbours, NeighbourhoodCleaningRule, ClusterCentroids.

baseCommand: undersampling

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
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/data/resampling/dataset_resampling.csv
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
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/resampling/ref_output_undersampling.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      position: 2
      prefix: --output_dataset_path
    default: system.csv

  config:
    label: Advanced configuration options for biobb_ml Undersampling
    doc: |-
      Advanced configuration options for biobb_ml Undersampling. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_ml Undersampling documentation: https://biobb-ml.readthedocs.io/en/latest/resampling.html#module-resampling.undersampling
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
