#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper class for the Haddock-Restraints Accessibility module.

doc: |-
  Haddock-Restraints Accessibility computes residues accessibility using freesasa included in the Haddock3 package.

baseCommand: haddock3_accessibility

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_haddock:5.1.0--pyhdfd78af_0

inputs:
  input_pdb_path:
    label: Path to the input PDB file
    doc: |-
      Path to the input PDB file
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/data/haddock/e2aP_1F3G_noH.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --input_pdb_path

  output_accessibility_path:
    label: Path to the output file with accessibility information
    doc: |-
      Path to the output file with accessibility information
      Type: string
      File type: output
      Accepted formats: txt, dat, out
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/reference/haddock_restraints/mol1_sasa.txt
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --output_accessibility_path
    default: system.txt

  output_actpass_path:
    label: Path to the output file with active/passive residues to be used as haddock3
      restraint information
    doc: |-
      Path to the output file with active/passive residues to be used as haddock3 restraint information
      Type: string
      File type: output
      Accepted formats: txt, dat, out
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/reference/haddock_restraints/mol1_haddock_actpass.txt
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      prefix: --output_actpass_path
    default: system.txt

  config:
    label: Advanced configuration options for biobb_haddock Haddock3Accessibility
    doc: |-
      Advanced configuration options for biobb_haddock Haddock3Accessibility. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_haddock Haddock3Accessibility documentation: https://biobb-haddock.readthedocs.io/en/latest/haddock_restraints.html#module-haddock_restraints.haddock3_accessibility
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_accessibility_path:
    label: Path to the output file with accessibility information
    doc: |-
      Path to the output file with accessibility information
    type: File
    outputBinding:
      glob: $(inputs.output_accessibility_path)
    format: edam:format_2330

  output_actpass_path:
    label: Path to the output file with active/passive residues to be used as haddock3
      restraint information
    doc: |-
      Path to the output file with active/passive residues to be used as haddock3 restraint information
    type: File?
    outputBinding:
      glob: $(inputs.output_actpass_path)
    format: edam:format_2330

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
