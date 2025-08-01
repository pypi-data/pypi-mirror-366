#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the TensorFlow Keras LSTM method for decoding.

doc: |-
  Decodes and predicts given a dataset and a model file compiled by an Autoencoder Neural Network. Visit the LSTM documentation page in the TensorFlow Keras official website for further information.

baseCommand: neural_network_decode

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
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/data/neural_networks/dataset_decoder.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 1
      prefix: --input_decode_path

  input_model_path:
    label: Path to the input model
    doc: |-
      Path to the input model
      Type: string
      File type: input
      Accepted formats: h5
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/data/neural_networks/input_model_decoder.h5
    type: File
    format:
    - edam:format_3590
    inputBinding:
      position: 2
      prefix: --input_model_path

  output_decode_path:
    label: Path to the output decode file
    doc: |-
      Path to the output decode file
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/neural_networks/ref_output_decode_decoder.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      position: 3
      prefix: --output_decode_path
    default: system.csv

  output_predict_path:
    label: Path to the output predict file
    doc: |-
      Path to the output predict file
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://github.com/bioexcel/biobb_ml/raw/master/biobb_ml/test/reference/neural_networks/ref_output_predict_decoder.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      prefix: --output_predict_path
    default: system.csv

  config:
    label: Advanced configuration options for biobb_ml DecodingNeuralNetwork
    doc: |-
      Advanced configuration options for biobb_ml DecodingNeuralNetwork. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_ml DecodingNeuralNetwork documentation: https://biobb-ml.readthedocs.io/en/latest/neural_networks.html#module-neural_networks.neural_network_decode
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_decode_path:
    label: Path to the output decode file
    doc: |-
      Path to the output decode file
    type: File
    outputBinding:
      glob: $(inputs.output_decode_path)
    format: edam:format_3752

  output_predict_path:
    label: Path to the output predict file
    doc: |-
      Path to the output predict file
    type: File?
    outputBinding:
      glob: $(inputs.output_predict_path)
    format: edam:format_3752

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
