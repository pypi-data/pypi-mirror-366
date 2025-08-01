#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Class to renumber atomic indexes from a 3D structure.

doc: |-
  Renumber atomic indexes from a 3D structure.

baseCommand: renumber_structure

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_structure_utils:5.1.0--pyhdfd78af_0

inputs:
  input_structure_path:
    label: Input structure file path
    doc: |-
      Input structure file path
      Type: string
      File type: input
      Accepted formats: pdb, gro
      Example file: https://github.com/bioexcel/biobb_structure_utils/raw/master/biobb_structure_utils/test/data/utils/cl3.noH.pdb
    type: File
    format:
    - edam:format_1476
    - edam:format_2033
    inputBinding:
      position: 1
      prefix: --input_structure_path

  output_structure_path:
    label: Output structure file path
    doc: |-
      Output structure file path
      Type: string
      File type: output
      Accepted formats: pdb, gro
      Example file: https://github.com/bioexcel/biobb_structure_utils/raw/master/biobb_structure_utils/test/reference/utils/renum_cl3_noH.pdb
    type: string
    format:
    - edam:format_1476
    - edam:format_2033
    inputBinding:
      position: 2
      prefix: --output_structure_path
    default: system.pdb

  output_mapping_json_path:
    label: Output mapping json file path
    doc: |-
      Output mapping json file path
      Type: string
      File type: output
      Accepted formats: json
      Example file: https://github.com/bioexcel/biobb_structure_utils/raw/master/biobb_structure_utils/test/reference/utils/cl3_output_mapping_json_path.json
    type: string
    format:
    - edam:format_3464
    inputBinding:
      position: 3
      prefix: --output_mapping_json_path
    default: system.json

  config:
    label: Advanced configuration options for biobb_structure_utils RenumberStructure
    doc: |-
      Advanced configuration options for biobb_structure_utils RenumberStructure. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_structure_utils RenumberStructure documentation: https://biobb-structure-utils.readthedocs.io/en/latest/utils.html#module-utils.renumber_structure
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_structure_path:
    label: Output structure file path
    doc: |-
      Output structure file path
    type: File
    outputBinding:
      glob: $(inputs.output_structure_path)
    format: edam:format_1476

  output_mapping_json_path:
    label: Output mapping json file path
    doc: |-
      Output mapping json file path
    type: File
    outputBinding:
      glob: $(inputs.output_mapping_json_path)
    format: edam:format_3464

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
