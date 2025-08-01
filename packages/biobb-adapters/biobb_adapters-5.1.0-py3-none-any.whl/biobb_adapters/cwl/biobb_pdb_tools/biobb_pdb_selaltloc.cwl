#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Selects alternative locations from a PDB file.

doc: |-
  By default, selects the label with the highest occupancy value for each atom, but the user can define a specific altloc label to select. Selecting by highest occupancy removes all altloc labels for all atoms. If the user provides an option (e.g. -A), only atoms with conformers with an altloc A are processed by the script.

baseCommand: biobb_pdb_selaltloc

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
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_pdb_tools/master/biobb_pdb_tools/test/data/pdb_tools/9INS.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --input_file_path

  output_file_path:
    label: PDB file with selected alternative locations
    doc: |-
      PDB file with selected alternative locations
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_pdb_tools/master/biobb_pdb_tools/test/reference/pdb_tools/ref_pdb_selaltloc.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      position: 2
      prefix: --output_file_path
    default: system.pdb

  config:
    label: Advanced configuration options for biobb_pdb_tools Pdbselaltloc
    doc: |-
      Advanced configuration options for biobb_pdb_tools Pdbselaltloc. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pdb_tools Pdbselaltloc documentation: https://biobb-pdb-tools.readthedocs.io/en/latest/pdb_tools.html#module-pdb_tools.biobb_pdb_selaltloc
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_file_path:
    label: PDB file with selected alternative locations
    doc: |-
      PDB file with selected alternative locations
    type: File
    outputBinding:
      glob: $(inputs.output_file_path)
    format: edam:format_1476

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
