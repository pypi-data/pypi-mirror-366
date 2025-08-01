#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Extracts the residue sequence in a PDB file to FASTA format.

doc: |-
  This tool extracts the residue sequence in a PDB file to FASTA format. It can be used to extract the sequence of a PDB file to FASTA format.

baseCommand: biobb_pdb_tofasta

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
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_pdb_tools/master/biobb_pdb_tools/test/data/pdb_tools/1AKI.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --input_file_path

  output_file_path:
    label: FASTA file containing the aminoacids sequence
    doc: |-
      FASTA file containing the aminoacids sequence
      Type: string
      File type: output
      Accepted formats: fasta, fa
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_pdb_tools/master/biobb_pdb_tools/test/reference/pdb_tools/ref_pdb_tofasta.pdb
    type: string
    format:
    - edam:format_1929
    - edam:format_1929
    inputBinding:
      position: 2
      prefix: --output_file_path
    default: system.fasta

  config:
    label: Advanced configuration options for biobb_pdb_tofasta Pdbtofasta
    doc: |-
      Advanced configuration options for biobb_pdb_tofasta Pdbtofasta. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pdb_tofasta Pdbtofasta documentation: https://biobb-pdb-tools.readthedocs.io/en/latest/pdb_tools.html#pdb-tools-biobb-pdb-tofasta-module
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_file_path:
    label: FASTA file containing the aminoacids sequence
    doc: |-
      FASTA file containing the aminoacids sequence
    type: File
    outputBinding:
      glob: $(inputs.output_file_path)
    format: edam:format_1929

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
