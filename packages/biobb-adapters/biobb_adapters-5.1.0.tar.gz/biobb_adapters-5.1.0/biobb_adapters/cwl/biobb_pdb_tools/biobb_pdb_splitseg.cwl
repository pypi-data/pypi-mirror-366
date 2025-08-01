#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Splits a PDB file into several, each containing one segment.

doc: |-
  This tool splits a PDB file into several, each containing one segment. It can be used to split a PDB file into several, each containing one segment.

baseCommand: biobb_pdb_splitseg

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
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_pdb_tools/master/biobb_pdb_tools/test/data/pdb_tools/input_pdb_splitseg.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --input_file_path

  output_file_path:
    label: ZIP file containing all PDB files splited by protein segment
    doc: |-
      ZIP file containing all PDB files splited by protein segment
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_pdb_tools/blob/master/biobb_pdb_tools/test/reference/pdb_tools/ref_pdb_splitseg.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --output_file_path
    default: system.zip

  config:
    label: Advanced configuration options for biobb_pdb_tools Pdbsplitseg
    doc: |-
      Advanced configuration options for biobb_pdb_tools Pdbsplitseg. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pdb_tools Pdbsplitseg documentation: https://biobb-pdb-tools.readthedocs.io/en/latest/pdb_tools.html#pdb-tools-biobb-pdb-splitseg-module
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_file_path:
    label: ZIP file containing all PDB files splited by protein segment
    doc: |-
      ZIP file containing all PDB files splited by protein segment
    type: File
    outputBinding:
      glob: $(inputs.output_file_path)
    format: edam:format_3987

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
