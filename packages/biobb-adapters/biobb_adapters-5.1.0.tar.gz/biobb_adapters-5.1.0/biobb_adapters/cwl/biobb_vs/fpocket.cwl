#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the fpocket software.

doc: |-
  Finds the binding site of the input_pdb_path file via the fpocket software.

baseCommand: fpocket

hints:
  DockerRequirement:
    dockerPull: ''

inputs:
  input_pdb_path:
    label: Path to the PDB structure where the binding site is to be found
    doc: |-
      Path to the PDB structure where the binding site is to be found
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/fpocket/fpocket_input.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --input_pdb_path

  output_pockets_zip:
    label: Path to all the pockets found by fpocket in the input_pdb_path structure
    doc: |-
      Path to all the pockets found by fpocket in the input_pdb_path structure
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_pockets.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --output_pockets_zip
    default: system.zip

  output_summary:
    label: Path to the JSON summary file
    doc: |-
      Path to the JSON summary file
      Type: string
      File type: output
      Accepted formats: json
      Example file: https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_summary.json
    type: string
    format:
    - edam:format_3464
    inputBinding:
      position: 3
      prefix: --output_summary
    default: system.json

  config:
    label: Advanced configuration options for biobb_vs FPocket
    doc: |-
      Advanced configuration options for biobb_vs FPocket. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_vs FPocket documentation: https://biobb-vs.readthedocs.io/en/latest/fpocket.html#module-fpocket.fpocket
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_pockets_zip:
    label: Path to all the pockets found by fpocket in the input_pdb_path structure
    doc: |-
      Path to all the pockets found by fpocket in the input_pdb_path structure
    type: File
    outputBinding:
      glob: $(inputs.output_pockets_zip)
    format: edam:format_3987

  output_summary:
    label: Path to the JSON summary file
    doc: |-
      Path to the JSON summary file
    type: File
    outputBinding:
      glob: $(inputs.output_summary)
    format: edam:format_3464

$namespaces:
  edam: http://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
