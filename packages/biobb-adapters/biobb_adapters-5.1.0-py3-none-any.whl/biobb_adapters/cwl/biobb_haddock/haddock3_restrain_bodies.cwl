#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper class for the Haddock-Restraints restrain_bodies module.

doc: |-
  Haddock-Restraints restrain_bodies creates distance restraints to lock several chains together. Useful to avoid unnatural flexibility or movement due to sequence/numbering gaps.

baseCommand: haddock3_restrain_bodies

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_haddock:5.1.0--pyhdfd78af_0

inputs:
  input_structure_path:
    label: Path to the input PDB structure to be restrained
    doc: |-
      Path to the input PDB structure to be restrained
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/data/haddock_restraints/4G6K_clean.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --input_structure_path

  output_tbl_path:
    label: Path to the output HADDOCK tbl file with Ambiguous Interaction Restraints
      (AIR) information
    doc: |-
      Path to the output HADDOCK tbl file with Ambiguous Interaction Restraints (AIR) information
      Type: string
      File type: output
      Accepted formats: tbl, txt, out
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/reference/haddock_restraints/antibody-unambig.tbl
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --output_tbl_path
    default: system.tbl

  config:
    label: Advanced configuration options for biobb_haddock Haddock3RestrainBodies
    doc: |-
      Advanced configuration options for biobb_haddock Haddock3RestrainBodies. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_haddock Haddock3RestrainBodies documentation: https://biobb-haddock.readthedocs.io/en/latest/haddock_restraints.html#module-haddock_restraints.haddock3_restrain_bodies
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_tbl_path:
    label: Path to the output HADDOCK tbl file with Ambiguous Interaction Restraints
      (AIR) information
    doc: |-
      Path to the output HADDOCK tbl file with Ambiguous Interaction Restraints (AIR) information
    type: File
    outputBinding:
      glob: $(inputs.output_tbl_path)
    format: edam:format_2330

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
