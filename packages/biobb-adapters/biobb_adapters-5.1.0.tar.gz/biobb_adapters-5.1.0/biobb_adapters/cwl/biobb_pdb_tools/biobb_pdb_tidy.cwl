#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Modifies the file to adhere (as much as possible) to the format specifications.

doc: |-
  This tool modifies the file to adhere (as much as possible) to the format specifications. It can be used to fix a PDB file that does not adhere to the format specifications.

baseCommand: biobb_pdb_tidy

hints:
  DockerRequirement:
    dockerPull: quay.io/repository/biocontainers/biobb_pdb_tools?tab=tags&tag=5.1.0--pyhdfd78af_0

inputs:
  input_file_path:
    label: PDB file
    doc: |-
      PDB file
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_pdb_tools/blob/master/biobb_pdb_tools/test/data/pdb_tools/1AKI.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --input_file_path

  output_file_path:
    label: PDB file modified according to the specifications
    doc: |-
      PDB file modified according to the specifications
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_pdb_tools/master/biobb_pdb_tools/test/reference/pdb_tools/ref_pdb_tidy.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      position: 2
      prefix: --output_file_path
    default: system.pdb

  config:
    label: Advanced configuration options for biobb_pdb_tools Pdbtidy
    doc: |-
      Advanced configuration options for biobb_pdb_tools Pdbtidy. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pdb_tools Pdbtidy documentation: https://biobb-pdb-tools.readthedocs.io/en/latest/pdb_tools.html#module-pdb_tools.biobb_pdb_tidy
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_file_path:
    label: PDB file modified according to the specifications
    doc: |-
      PDB file modified according to the specifications
    type: File
    outputBinding:
      glob: $(inputs.output_file_path)
    format: edam:format_1476

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
