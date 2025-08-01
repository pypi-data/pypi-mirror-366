#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Class to sort the selected residues from a GRO 3D structure.

doc: |-
  Sorts the selected residues from a GRO 3D structure.

baseCommand: sort_gro_residues

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_structure_utils:5.1.0--pyhdfd78af_0

inputs:
  input_gro_path:
    label: Input GRO file path
    doc: |-
      Input GRO file path
      Type: string
      File type: input
      Accepted formats: gro
      Example file: https://github.com/bioexcel/biobb_structure_utils/raw/master/biobb_structure_utils/test/data/utils/WT_aq4_md_1.gro
    type: File
    format:
    - edam:format_2033
    inputBinding:
      position: 1
      prefix: --input_gro_path

  output_gro_path:
    label: Output sorted GRO file path
    doc: |-
      Output sorted GRO file path
      Type: string
      File type: output
      Accepted formats: gro
      Example file: https://github.com/bioexcel/biobb_structure_utils/raw/master/biobb_structure_utils/test/reference/utils/WT_aq4_md_sorted.gro
    type: string
    format:
    - edam:format_2033
    inputBinding:
      position: 2
      prefix: --output_gro_path
    default: system.gro

  config:
    label: Advanced configuration options for biobb_structure_utils SortGroResidues
    doc: |-
      Advanced configuration options for biobb_structure_utils SortGroResidues. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_structure_utils SortGroResidues documentation: https://biobb-structure-utils.readthedocs.io/en/latest/utils.html#module-utils.sort_gro_residues
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_gro_path:
    label: Output sorted GRO file path
    doc: |-
      Output sorted GRO file path
    type: File
    outputBinding:
      glob: $(inputs.output_gro_path)
    format: edam:format_2033

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
