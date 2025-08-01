#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the scikit-learn SpectralClustering method.

doc: |-
  Clusters a given dataset and calculates best K coefficient. Visit the SpectralClustering documentation page in the sklearn official website for further information.

baseCommand: spectral_coefficient

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
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/data/clustering/dataset_spectral_coefficient.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 1
      prefix: --input_dataset_path

  output_results_path:
    label: Table with WCSS (elbow method), Gap and Silhouette coefficients for each
      cluster
    doc: |-
      Table with WCSS (elbow method), Gap and Silhouette coefficients for each cluster
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/clustering/ref_output_results_spectral_coefficient.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      position: 2
      prefix: --output_results_path
    default: system.csv

  output_plot_path:
    label: Path to the elbow method and gap statistics plot
    doc: |-
      Path to the elbow method and gap statistics plot
      Type: string
      File type: output
      Accepted formats: png
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/clustering/ref_output_plot_spectral_coefficient.png
    type: string
    format:
    - edam:format_3603
    inputBinding:
      prefix: --output_plot_path
    default: system.png

  config:
    label: Advanced configuration options for biobb_ml SpectralCoefficient
    doc: |-
      Advanced configuration options for biobb_ml SpectralCoefficient. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_ml SpectralCoefficient documentation: https://biobb-ml.readthedocs.io/en/latest/clustering.html#module-clustering.spectral_coefficient
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_results_path:
    label: Table with WCSS (elbow method), Gap and Silhouette coefficients for each
      cluster
    doc: |-
      Table with WCSS (elbow method), Gap and Silhouette coefficients for each cluster
    type: File
    outputBinding:
      glob: $(inputs.output_results_path)
    format: edam:format_3752

  output_plot_path:
    label: Path to the elbow method and gap statistics plot
    doc: |-
      Path to the elbow method and gap statistics plot
    type: File?
    outputBinding:
      glob: $(inputs.output_plot_path)
    format: edam:format_3603

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
