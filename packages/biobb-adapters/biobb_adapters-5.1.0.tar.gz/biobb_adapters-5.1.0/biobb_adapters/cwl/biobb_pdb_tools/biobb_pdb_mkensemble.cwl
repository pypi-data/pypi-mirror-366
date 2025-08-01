#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Merges several PDB files into one multi-model (ensemble) file.

doc: |-
  This tool merges several PDB files into one multi-model (ensemble) file. It can be used to merge several PDB files into one multi-model (ensemble) file.

baseCommand: biobb_pdb_mkensemble

hints:
  DockerRequirement:
    dockerPull: quay.io/repository/biocontainers/biobb_pdb_tools?tab=tags&tag=5.1.0--pyhdfd78af_0

inputs:
  input_file_path:
    label: ZIP file of selected proteins
    doc: |-
      ZIP file of selected proteins
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_pdb_tools/master/biobb_pdb_tools/test/data/pdb_tools/input_pdb_mkensemble.pdb
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 1
      prefix: --input_file_path

  output_file_path:
    label: Multi-model (ensemble) PDB file with input PDBs merged
    doc: |-
      Multi-model (ensemble) PDB file with input PDBs merged
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_pdb_tools/master/biobb_pdb_tools/test/reference/pdb_tools/ref_pdb_mkensemble.pdb
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --output_file_path
    default: system.pdb

  config:
    label: Advanced configuration options for biobb_pdb_tools Mkensemble
    doc: |-
      Advanced configuration options for biobb_pdb_tools Mkensemble. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pdb_tools Mkensemble documentation: https://biobb-pdb-tools.readthedocs.io/en/latest/pdb_tools.html#pdb-tools-biobb-pdb-mkensemble-module
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_file_path:
    label: Multi-model (ensemble) PDB file with input PDBs merged
    doc: |-
      Multi-model (ensemble) PDB file with input PDBs merged
    type: File
    outputBinding:
      glob: $(inputs.output_file_path)
    format: edam:format_3987

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
