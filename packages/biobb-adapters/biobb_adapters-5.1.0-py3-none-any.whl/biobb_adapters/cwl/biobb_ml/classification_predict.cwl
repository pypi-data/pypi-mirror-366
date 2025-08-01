#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Makes predictions from an input dataset and a given classification model.

doc: |-
  Makes predictions from an input dataset (provided either as a file or as a dictionary property) and a given classification model trained with DecisionTreeClassifier, KNeighborsClassifier, LogisticRegression, RandomForestClassifier, Support Vector Machine methods.

baseCommand: classification_predict

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_ml:4.1.0--pyhdfd78af_0

inputs:
  input_model_path:
    label: Path to the input model
    doc: |-
      Path to the input model
      Type: string
      File type: input
      Accepted formats: pkl
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/data/classification/model_classification_predict.pkl
    type: File
    format:
    - edam:format_3653
    inputBinding:
      position: 1
      prefix: --input_model_path

  output_results_path:
    label: Path to the output results file
    doc: |-
      Path to the output results file
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/classification/ref_output_classification_predict.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      position: 2
      prefix: --output_results_path
    default: system.csv

  input_dataset_path:
    label: Path to the dataset to predict
    doc: |-
      Path to the dataset to predict
      Type: string
      File type: input
      Accepted formats: csv
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/data/classification/input_classification_predict.csv
    type: File?
    format:
    - edam:format_3752
    inputBinding:
      prefix: --input_dataset_path

  config:
    label: Advanced configuration options for biobb_ml ClassificationPredict
    doc: |-
      Advanced configuration options for biobb_ml ClassificationPredict. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_ml ClassificationPredict documentation: https://biobb-ml.readthedocs.io/en/latest/classification.html#module-classification.classification_predict
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_results_path:
    label: Path to the output results file
    doc: |-
      Path to the output results file
    type: File
    outputBinding:
      glob: $(inputs.output_results_path)
    format: edam:format_3752

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
