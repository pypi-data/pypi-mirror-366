#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the TensorFlow Keras LSTM method for encoding.

doc: |-
  Fits and tests a given dataset and save the compiled model for an Autoencoder Neural Network. Visit the LSTM documentation page in the TensorFlow Keras official website for further information.

baseCommand: autoencoder_neural_network

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_ml:4.1.0--pyhdfd78af_0

inputs:
  input_decode_path:
    label: Path to the input decode dataset
    doc: |-
      Path to the input decode dataset
      Type: string
      File type: input
      Accepted formats: csv
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/data/neural_networks/dataset_autoencoder_decode.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 1
      prefix: --input_decode_path

  output_model_path:
    label: Path to the output model file
    doc: |-
      Path to the output model file
      Type: string
      File type: output
      Accepted formats: h5
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/neural_networks/ref_output_model_autoencoder.h5
    type: string
    format:
    - edam:format_3590
    inputBinding:
      position: 2
      prefix: --output_model_path
    default: system.h5

  input_predict_path:
    label: Path to the input predict dataset
    doc: |-
      Path to the input predict dataset
      Type: string
      File type: input
      Accepted formats: csv
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/data/neural_networks/dataset_autoencoder_predict.csv
    type: File?
    format:
    - edam:format_3752
    inputBinding:
      prefix: --input_predict_path

  output_test_decode_path:
    label: Path to the test decode table file
    doc: |-
      Path to the test decode table file
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/neural_networks/ref_output_test_decode_autoencoder.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      prefix: --output_test_decode_path
    default: system.csv

  output_test_predict_path:
    label: Path to the test predict table file
    doc: |-
      Path to the test predict table file
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/neural_networks/ref_output_test_predict_autoencoder.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      prefix: --output_test_predict_path
    default: system.csv

  config:
    label: Advanced configuration options for biobb_ml AutoencoderNeuralNetwork
    doc: |-
      Advanced configuration options for biobb_ml AutoencoderNeuralNetwork. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_ml AutoencoderNeuralNetwork documentation: https://biobb-ml.readthedocs.io/en/latest/neural_networks.html#module-neural_networks.autoencoder_neural_network
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_model_path:
    label: Path to the output model file
    doc: |-
      Path to the output model file
    type: File
    outputBinding:
      glob: $(inputs.output_model_path)
    format: edam:format_3590

  output_test_decode_path:
    label: Path to the test decode table file
    doc: |-
      Path to the test decode table file
    type: File?
    outputBinding:
      glob: $(inputs.output_test_decode_path)
    format: edam:format_3752

  output_test_predict_path:
    label: Path to the test predict table file
    doc: |-
      Path to the test predict table file
    type: File?
    outputBinding:
      glob: $(inputs.output_test_predict_path)
    format: edam:format_3752

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
