#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Apply a Molecular Dynamics AutoEncoder (MDAE) PyTorch model.

doc: |-
  Apply a Molecular Dynamics AutoEncoder (MDAE) PyTorch model, the resulting denoised molecular dynamics or the reduced the dimensionality of molecular dynamics data can be used to analyze the dynamic properties of the system.

baseCommand: apply_mdae

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_pytorch:5.1.0--pyhad2cae4_0

inputs:
  input_data_npy_path:
    label: Path to the input data file
    doc: |-
      Path to the input data file
      Type: string
      File type: input
      Accepted formats: npy
      Example file: https://github.com/bioexcel/biobb_pytorch/raw/master/biobb_pytorch/test/data/mdae/train_mdae_traj.npy
    type: File
    format:
    - edam:format_4003
    inputBinding:
      position: 1
      prefix: --input_data_npy_path

  input_model_pth_path:
    label: Path to the input model file
    doc: |-
      Path to the input model file
      Type: string
      File type: input
      Accepted formats: pth
      Example file: https://github.com/bioexcel/biobb_pytorch/raw/master/biobb_pytorch/test/reference/mdae/ref_output_model.pth
    type: File
    format:
    - edam:format_2333
    inputBinding:
      position: 2
      prefix: --input_model_pth_path

  output_reconstructed_data_npy_path:
    label: Path to the output reconstructed data file
    doc: |-
      Path to the output reconstructed data file
      Type: string
      File type: output
      Accepted formats: npy
      Example file: https://github.com/bioexcel/biobb_pytorch/raw/master/biobb_pytorch/test/reference/mdae/ref_output_reconstructed_data.npy
    type: string
    format:
    - edam:format_4003
    inputBinding:
      position: 3
      prefix: --output_reconstructed_data_npy_path
    default: system.npy

  output_latent_space_npy_path:
    label: Path to the reduced dimensionality file
    doc: |-
      Path to the reduced dimensionality file
      Type: string
      File type: output
      Accepted formats: npy
      Example file: https://github.com/bioexcel/biobb_pytorch/raw/master/biobb_pytorch/test/reference/mdae/ref_output_latent_space.npy
    type: string
    format:
    - edam:format_4003
    inputBinding:
      prefix: --output_latent_space_npy_path
    default: system.npy

  config:
    label: Advanced configuration options for biobb_pytorch ApplyMDAE
    doc: |-
      Advanced configuration options for biobb_pytorch ApplyMDAE. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pytorch ApplyMDAE documentation: https://biobb-pytorch.readthedocs.io/en/latest/mdae.html#module-mdae.apply_mdae
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_reconstructed_data_npy_path:
    label: Path to the output reconstructed data file
    doc: |-
      Path to the output reconstructed data file
    type: File
    outputBinding:
      glob: $(inputs.output_reconstructed_data_npy_path)
    format: edam:format_4003

  output_latent_space_npy_path:
    label: Path to the reduced dimensionality file
    doc: |-
      Path to the reduced dimensionality file
    type: File?
    outputBinding:
      glob: $(inputs.output_latent_space_npy_path)
    format: edam:format_4003

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
