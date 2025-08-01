#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper class for the Haddock-Restraints active_passive_to_ambig module.

doc: |-
  Haddock-Restraints active_passive_to_ambig generates a corresponding ambig.tbl file to be used by HADDOCK from two given files containing active (in the first line) and passive (second line) residues.

baseCommand: haddock3_actpass_to_ambig

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_haddock:5.1.0--pyhdfd78af_0

inputs:
  input_actpass1_path:
    label: Path to the first input HADDOCK active-passive file containing active (in
      the first line) and passive (second line) residues
    doc: |-
      Path to the first input HADDOCK active-passive file containing active (in the first line) and passive (second line) residues
      Type: string
      File type: input
      Accepted formats: txt, dat, in, pass
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/data/haddock/haddock_actpass1.txt
    type: File
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_actpass1_path

  input_actpass2_path:
    label: Path to the second input HADDOCK active-passive file containing active
      (in the first line) and passive (second line) residues
    doc: |-
      Path to the second input HADDOCK active-passive file containing active (in the first line) and passive (second line) residues
      Type: string
      File type: input
      Accepted formats: txt, dat, in, pass
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/data/haddock/haddock_actpass2.txt
    type: File
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --input_actpass2_path

  output_tbl_path:
    label: Path to the output HADDOCK tbl file with Ambiguous Interaction Restraints
      (AIR) information
    doc: |-
      Path to the output HADDOCK tbl file with Ambiguous Interaction Restraints (AIR) information
      Type: string
      File type: output
      Accepted formats: tbl, txt, out
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/reference/haddock_restraints/haddock_actpass.tbl
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      position: 3
      prefix: --output_tbl_path
    default: system.tbl

  config:
    label: Advanced configuration options for biobb_haddock Haddock3ActpassToAmbig
    doc: |-
      Advanced configuration options for biobb_haddock Haddock3ActpassToAmbig. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_haddock Haddock3ActpassToAmbig documentation: https://biobb-haddock.readthedocs.io/en/latest/haddock_restraints.html#module-haddock_restraints.haddock3_actpass_to_ambig
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
