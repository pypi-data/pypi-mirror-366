#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Merges several PDB files into one.

doc: |-
  This tool merges several PDB files into one. It can be used to merge several PDB files into one.

baseCommand: biobb_pdb_merge

hints:
  DockerRequirement:
    dockerPull: quay.io/repository/biocontainers/biobb_pdb_tools?tab=tags&tag=5.1.0--pyhdfd78af_0

inputs:
  input_file_path:
    label: ZIP file of selected protein
    doc: |-
      ZIP file of selected protein
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_pdb_tools/master/biobb_pdb_tools/test/data/pdb_tools/input_pdb_merge.pdb
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 1
      prefix: --input_file_path

  output_file_path:
    label: PDB file with input PDBs merged
    doc: |-
      PDB file with input PDBs merged
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_pdb_tools/master/biobb_pdb_tools/test/reference/pdb_tools/ref_pdb_merge.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      position: 2
      prefix: --output_file_path
    default: system.pdb

  config:
    label: Advanced configuration options for biobb_pdb_tools Pdbmerge
    doc: |-
      Advanced configuration options for biobb_pdb_tools Pdbmerge. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pdb_tools Pdbmerge documentation: https://biobb-pdb-tools.readthedocs.io/en/latest/pdb_tools.html#module-pdb_tools.biobb_pdb_merge
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_file_path:
    label: PDB file with input PDBs merged
    doc: |-
      PDB file with input PDBs merged
    type: File
    outputBinding:
      glob: $(inputs.output_file_path)
    format: edam:format_1476

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
