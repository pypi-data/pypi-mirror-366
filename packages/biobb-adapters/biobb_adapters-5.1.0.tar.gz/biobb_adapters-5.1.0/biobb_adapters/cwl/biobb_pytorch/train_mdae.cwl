#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Train a Molecular Dynamics AutoEncoder (MDAE) PyTorch model.

doc: |-
  Train a Molecular Dynamics AutoEncoder (MDAE) PyTorch model, the resulting Auto-associative Neural Network (AANN) can be applied to reduce the dimensionality of molecular dynamics data and analyze the dynamic properties of the system.

baseCommand: train_mdae

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_pytorch:5.1.0--pyhad2cae4_0

inputs:
  input_train_npy_path:
    label: Path to the input train data file
    doc: |-
      Path to the input train data file
      Type: string
      File type: input
      Accepted formats: npy
      Example file: https://github.com/bioexcel/biobb_pytorch/raw/master/biobb_pytorch/test/data/mdae/train_mdae_traj.npy
    type: File
    format:
    - edam:format_4003
    inputBinding:
      position: 1
      prefix: --input_train_npy_path

  output_model_pth_path:
    label: Path to the output model file
    doc: |-
      Path to the output model file
      Type: string
      File type: output
      Accepted formats: pth
      Example file: https://github.com/bioexcel/biobb_pytorch/raw/master/biobb_pytorch/test/reference/mdae/ref_output_model.pth
    type: string
    format:
    - edam:format_2333
    inputBinding:
      position: 2
      prefix: --output_model_pth_path
    default: system.pth

  input_model_pth_path:
    label: Path to the input model file
    doc: |-
      Path to the input model file
      Type: string
      File type: input
      Accepted formats: pth
      Example file: https://github.com/bioexcel/biobb_pytorch/raw/master/biobb_pytorch/test/reference/mdae/ref_output_model.pth
    type: File?
    format:
    - edam:format_2333
    inputBinding:
      prefix: --input_model_pth_path

  output_train_data_npz_path:
    label: Path to the output train data file
    doc: |-
      Path to the output train data file
      Type: string
      File type: output
      Accepted formats: npz
      Example file: https://github.com/bioexcel/biobb_pytorch/raw/master/biobb_pytorch/test/reference/mdae/ref_output_train_data.npz
    type: string
    format:
    - edam:format_4003
    inputBinding:
      prefix: --output_train_data_npz_path
    default: system.npz

  output_performance_npz_path:
    label: Path to the output performance file
    doc: |-
      Path to the output performance file
      Type: string
      File type: output
      Accepted formats: npz
      Example file: https://github.com/bioexcel/biobb_pytorch/raw/master/biobb_pytorch/test/reference/mdae/ref_output_performance.npz
    type: string
    format:
    - edam:format_4003
    inputBinding:
      prefix: --output_performance_npz_path
    default: system.npz

  config:
    label: Advanced configuration options for biobb_pytorch TrainMDAE
    doc: |-
      Advanced configuration options for biobb_pytorch TrainMDAE. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pytorch TrainMDAE documentation: https://biobb-pytorch.readthedocs.io/en/latest/mdae.html#mdae.train_mdae.TrainMDAE
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_model_pth_path:
    label: Path to the output model file
    doc: |-
      Path to the output model file
    type: File
    outputBinding:
      glob: $(inputs.output_model_pth_path)
    format: edam:format_2333

  output_train_data_npz_path:
    label: Path to the output train data file
    doc: |-
      Path to the output train data file
    type: File?
    outputBinding:
      glob: $(inputs.output_train_data_npz_path)
    format: edam:format_4003

  output_performance_npz_path:
    label: Path to the output performance file
    doc: |-
      Path to the output performance file
    type: File?
    outputBinding:
      glob: $(inputs.output_performance_npz_path)
    format: edam:format_4003

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
