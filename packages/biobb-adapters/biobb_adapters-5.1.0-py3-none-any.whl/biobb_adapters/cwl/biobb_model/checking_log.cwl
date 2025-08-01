#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Class to check the errors of a PDB structure.

doc: |-
  Check the errors of a PDB structure and create a report log file.

baseCommand: checking_log

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_model:5.1.0--pyhdfd78af_0

inputs:
  input_pdb_path:
    label: Input PDB file path
    doc: |-
      Input PDB file path
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_model/raw/master/biobb_model/test/data/model/2ki5.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --input_pdb_path

  output_log_path:
    label: Output report log file path
    doc: |-
      Output report log file path
      Type: string
      File type: output
      Accepted formats: log
      Example file: https://github.com/bioexcel/biobb_model/raw/master/biobb_model/test/reference/model/checking.log
    type: string
    format:
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --output_log_path
    default: system.log

  config:
    label: Advanced configuration options for biobb_model CheckingLog
    doc: |-
      Advanced configuration options for biobb_model CheckingLog. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_model CheckingLog documentation: https://biobb-model.readthedocs.io/en/latest/model.html#module-model.checking_log
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_log_path:
    label: Output report log file path
    doc: |-
      Output report log file path
    type: File
    outputBinding:
      glob: $(inputs.output_log_path)
    format: edam:format_2330

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
