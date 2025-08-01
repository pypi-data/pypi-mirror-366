#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Downloads a structure in PDB format from the RCSB website.

doc: |-
  This tool downloads a structure in PDB format from the RCSB website. It can be used to download a structure in PDB format from the RCSB website.

baseCommand: biobb_pdb_fetch

hints:
  DockerRequirement:
    dockerPull: quay.io/repository/biocontainers/biobb_pdb_tools?tab=tags&tag=5.1.0--pyhdfd78af_0

inputs:
  output_file_path:
    label: PDB file of the protein selected
    doc: |-
      PDB file of the protein selected
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_pdb_tools/master/biobb_pdb_tools/test/reference/pdb_tools/ref_pdb_fetch.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --output_file_path
    default: system.pdb

  config:
    label: Advanced configuration options for biobb_pdb_tools Pdbfetch
    doc: |-
      Advanced configuration options for biobb_pdb_tools Pdbfetch. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pdb_tools Pdbfetch documentation: https://biobb-pdb-tools.readthedocs.io/en/latest/pdb_tools.html#module-pdb_tools.biobb_pdb_fetch
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_file_path:
    label: PDB file of the protein selected
    doc: |-
      PDB file of the protein selected
    type: File
    outputBinding:
      glob: $(inputs.output_file_path)
    format: edam:format_1476

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
