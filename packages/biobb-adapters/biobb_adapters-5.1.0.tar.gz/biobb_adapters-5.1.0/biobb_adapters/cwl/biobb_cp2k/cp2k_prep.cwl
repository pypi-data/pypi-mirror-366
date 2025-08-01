#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Helper bb to prepare inputs for the CP2K QM tool module.

doc: |-
  Prepares input files for the CP2K QM tool.

baseCommand: cp2k_prep

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_cp2k:5.1.0--pyhdfd78af_0

inputs:
  output_inp_path:
    label: Output CP2K input configuration file
    doc: |-
      Output CP2K input configuration file
      Type: string
      File type: output
      Accepted formats: inp, in, txt
      Example file: https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/reference/cp2k/cp2k_prep_out.inp
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --output_inp_path
    default: system.inp

  input_inp_path:
    label: Input configuration file (CP2K run options)
    doc: |-
      Input configuration file (CP2K run options)
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/cp2k_energy.inp
    type: File?
    format:
    - edam:format_1476
    inputBinding:
      prefix: --input_inp_path

  input_pdb_path:
    label: Input PDB file
    doc: |-
      Input PDB file
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/H2O_box.pdb
    type: File?
    format:
    - edam:format_1476
    inputBinding:
      prefix: --input_pdb_path

  input_rst_path:
    label: Input restart file (WFN)
    doc: |-
      Input restart file (WFN)
      Type: string
      File type: input
      Accepted formats: wfn
      Example file: https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/cp2k.wfn
    type: File?
    format:
    - edam:format_2333
    inputBinding:
      prefix: --input_rst_path

  config:
    label: Advanced configuration options for biobb_cp2k Cp2kPrep
    doc: |-
      Advanced configuration options for biobb_cp2k Cp2kPrep. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_cp2k Cp2kPrep documentation: https://biobb-cp2k.readthedocs.io/en/latest/cp2k.html#module-cp2k.cp2k_prep
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_inp_path:
    label: Output CP2K input configuration file
    doc: |-
      Output CP2K input configuration file
    type: File
    outputBinding:
      glob: $(inputs.output_inp_path)
    format: edam:format_2330

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
