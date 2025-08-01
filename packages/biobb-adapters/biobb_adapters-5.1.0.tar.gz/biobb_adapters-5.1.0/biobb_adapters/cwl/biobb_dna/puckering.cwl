#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Calculate Puckering from phase parameters.

doc: |-
  Calculate North/East/West/South distribution of sugar puckering backbone torsions.

baseCommand: puckering

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_dna:5.1.0--pyhdfd78af_0

inputs:
  input_phaseC_path:
    label: Path to .ser file for helical parameter 'phaseC'
    doc: |-
      Path to .ser file for helical parameter 'phaseC'
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/backbone/canal_output_phaseC.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_phaseC_path

  input_phaseW_path:
    label: Path to .ser file for helical parameter 'phaseW'
    doc: |-
      Path to .ser file for helical parameter 'phaseW'
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/backbone/canal_output_phaseW.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --input_phaseW_path

  output_csv_path:
    label: Path to .csv file where output is saved
    doc: |-
      Path to .csv file where output is saved
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/backbone/puckering_ref.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      position: 3
      prefix: --output_csv_path
    default: system.csv

  output_jpg_path:
    label: Path to .jpg file where output is saved
    doc: |-
      Path to .jpg file where output is saved
      Type: string
      File type: output
      Accepted formats: jpg
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/backbone/puckering_ref.jpg
    type: string
    format:
    - edam:format_3579
    inputBinding:
      position: 4
      prefix: --output_jpg_path
    default: system.jpg

  config:
    label: Advanced configuration options for biobb_dna Puckering
    doc: |-
      Advanced configuration options for biobb_dna Puckering. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna Puckering documentation: https://biobb-dna.readthedocs.io/en/latest/backbone.html#module-backbone.puckering
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_csv_path:
    label: Path to .csv file where output is saved
    doc: |-
      Path to .csv file where output is saved
    type: File
    outputBinding:
      glob: $(inputs.output_csv_path)
    format: edam:format_3752

  output_jpg_path:
    label: Path to .jpg file where output is saved
    doc: |-
      Path to .jpg file where output is saved
    type: File
    outputBinding:
      glob: $(inputs.output_jpg_path)
    format: edam:format_3579

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
