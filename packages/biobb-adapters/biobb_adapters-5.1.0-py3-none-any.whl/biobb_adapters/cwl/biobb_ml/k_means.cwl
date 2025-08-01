#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the scikit-learn KMeans method.

doc: |-
  Clusters a given dataset and saves the model and scaler. Visit the KMeans documentation page in the sklearn official website for further information.

baseCommand: k_means

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
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/data/clustering/dataset_k_means.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 1
      prefix: --input_dataset_path

  output_results_path:
    label: Path to the clustered dataset
    doc: |-
      Path to the clustered dataset
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/clustering/ref_output_results_k_means.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      position: 2
      prefix: --output_results_path
    default: system.csv

  output_model_path:
    label: Path to the output model file
    doc: |-
      Path to the output model file
      Type: string
      File type: output
      Accepted formats: pkl
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/clustering/ref_output_model_k_means.pkl
    type: string
    format:
    - edam:format_3653
    inputBinding:
      position: 3
      prefix: --output_model_path
    default: system.pkl

  output_plot_path:
    label: Path to the clustering plot
    doc: |-
      Path to the clustering plot
      Type: string
      File type: output
      Accepted formats: png
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/clustering/ref_output_plot_k_means.png
    type: string
    format:
    - edam:format_3603
    inputBinding:
      prefix: --output_plot_path
    default: system.png

  config:
    label: Advanced configuration options for biobb_ml KMeansClustering
    doc: |-
      Advanced configuration options for biobb_ml KMeansClustering. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_ml KMeansClustering documentation: https://biobb-ml.readthedocs.io/en/latest/clustering.html#module-clustering.k_means
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_results_path:
    label: Path to the clustered dataset
    doc: |-
      Path to the clustered dataset
    type: File
    outputBinding:
      glob: $(inputs.output_results_path)
    format: edam:format_3752

  output_model_path:
    label: Path to the output model file
    doc: |-
      Path to the output model file
    type: File
    outputBinding:
      glob: $(inputs.output_model_path)
    format: edam:format_3653

  output_plot_path:
    label: Path to the clustering plot
    doc: |-
      Path to the clustering plot
    type: File?
    outputBinding:
      glob: $(inputs.output_plot_path)
    format: edam:format_3603

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
