#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the CP2K QM tool module.

doc: |-
  Runs atomistic simulations of solid state, liquid, molecular, periodic, material, crystal, and biological systems using CP2K QM tool.

baseCommand: cp2k_run

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_cp2k:5.1.0--pyhdfd78af_0

inputs:
  input_inp_path:
    label: Input configuration file (CP2K run options)
    doc: |-
      Input configuration file (CP2K run options)
      Type: string
      File type: input
      Accepted formats: inp, in, txt, wfn
      Example file: https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/data/cp2k/cp2k_energy.inp
    type: File
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    - edam:format_2333
    inputBinding:
      position: 1
      prefix: --input_inp_path

  output_log_path:
    label: Output log file
    doc: |-
      Output log file
      Type: string
      File type: output
      Accepted formats: log, out, txt, o
      Example file: https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/reference/cp2k/cp2k_run_out.log
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --output_log_path
    default: system.log

  output_outzip_path:
    label: Output files
    doc: |-
      Output files
      Type: string
      File type: output
      Accepted formats: zip, gzip, gz
      Example file: https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/reference/cp2k/cp2k_run_out.zip
    type: string
    format:
    - edam:format_3987
    - edam:format_3987
    - edam:format_3987
    inputBinding:
      position: 3
      prefix: --output_outzip_path
    default: system.zip

  output_rst_path:
    label: Output restart file
    doc: |-
      Output restart file
      Type: string
      File type: output
      Accepted formats: wfn
      Example file: https://github.com/bioexcel/biobb_cp2k/raw/master/biobb_cp2k/test/reference/cp2k/cp2k_run_out.wfn
    type: string
    format:
    - edam:format_2333
    inputBinding:
      position: 4
      prefix: --output_rst_path
    default: system.wfn

  config:
    label: Advanced configuration options for biobb_cp2k Cp2kRun
    doc: |-
      Advanced configuration options for biobb_cp2k Cp2kRun. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_cp2k Cp2kRun documentation: https://biobb-cp2k.readthedocs.io/en/latest/cp2k.html#module-cp2k.cp2k_run
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_log_path:
    label: Output log file
    doc: |-
      Output log file
    type: File
    outputBinding:
      glob: $(inputs.output_log_path)
    format: edam:format_2330

  output_outzip_path:
    label: Output files
    doc: |-
      Output files
    type: File
    outputBinding:
      glob: $(inputs.output_outzip_path)
    format: edam:format_3987

  output_rst_path:
    label: Output restart file
    doc: |-
      Output restart file
    type: File
    outputBinding:
      glob: $(inputs.output_rst_path)
    format: edam:format_2333

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
