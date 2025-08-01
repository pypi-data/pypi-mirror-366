#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper class for the Haddock3-Restraints passive_from_active module.

doc: "Haddock3-Restraints passive_from_active given a list of active_residues and\
  \ a PDB structure, it will return a list of surface exposed passive residues within\

  \ a radius (6.5\xC5 by default) from the active residues."

baseCommand: haddock3_passive_from_active

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_haddock:5.1.0--pyhdfd78af_0

inputs:
  input_pdb_path:
    label: Path to the input PDB structure file
    doc: |-
      Path to the input PDB structure file
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/data/haddock_restraints/1A2P_ch.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --input_pdb_path

  output_actpass_path:
    label: Path to the output file with list of passive residues
    doc: |-
      Path to the output file with list of passive residues
      Type: string
      File type: output
      Accepted formats: txt, dat, list, out
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/reference/haddock_restraints/1A2P_manual_actpass.txt
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --output_actpass_path
    default: system.txt

  input_active_list_path:
    label: Path to the input file with list of active residues
    doc: |-
      Path to the input file with list of active residues
      Type: string
      File type: input
      Accepted formats: txt, dat, list
      Example file: null
    type: File?
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      prefix: --input_active_list_path

  config:
    label: Advanced configuration options for biobb_haddock Haddock3PassiveFromActive
    doc: |-
      Advanced configuration options for biobb_haddock Haddock3PassiveFromActive. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_haddock Haddock3PassiveFromActive documentation: https://biobb-haddock.readthedocs.io/en/latest/haddock_restraints.html#module-haddock_restraints.haddock3_passive_from_active
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_actpass_path:
    label: Path to the output file with list of passive residues
    doc: |-
      Path to the output file with list of passive residues
    type: File
    outputBinding:
      glob: $(inputs.output_actpass_path)
    format: edam:format_2330

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
