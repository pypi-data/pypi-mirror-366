#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Calculate BI/BII populations from epsilon and zeta parameters.

doc: |-
  Calculate BI/BII populations from epsilon and zeta parameters.

baseCommand: bipopulations

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_dna:5.1.0--pyhdfd78af_0

inputs:
  input_epsilC_path:
    label: Path to .ser file for helical parameter 'epsilC'
    doc: |-
      Path to .ser file for helical parameter 'epsilC'
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/backbone/canal_output_epsilC.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_epsilC_path

  input_epsilW_path:
    label: Path to .ser file for helical parameter 'epsilW'
    doc: |-
      Path to .ser file for helical parameter 'epsilW'
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/backbone/canal_output_epsilW.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --input_epsilW_path

  input_zetaC_path:
    label: Path to .ser file for helical parameter 'zetaC'
    doc: |-
      Path to .ser file for helical parameter 'zetaC'
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/backbone/canal_output_zetaC.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 3
      prefix: --input_zetaC_path

  input_zetaW_path:
    label: Path to .ser file for helical parameter 'zetaW'
    doc: |-
      Path to .ser file for helical parameter 'zetaW'
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/backbone/canal_output_zetaW.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 4
      prefix: --input_zetaW_path

  output_csv_path:
    label: Path to .csv file where output is saved
    doc: |-
      Path to .csv file where output is saved
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/backbone/bipop_ref.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      position: 5
      prefix: --output_csv_path
    default: system.csv

  output_jpg_path:
    label: Path to .jpg file where output is saved
    doc: |-
      Path to .jpg file where output is saved
      Type: string
      File type: output
      Accepted formats: jpg
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/backbone/bipop_ref.jpg
    type: string
    format:
    - edam:format_3579
    inputBinding:
      position: 6
      prefix: --output_jpg_path
    default: system.jpg

  config:
    label: Advanced configuration options for biobb_dna BIPopulations
    doc: |-
      Advanced configuration options for biobb_dna BIPopulations. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna BIPopulations documentation: https://biobb-dna.readthedocs.io/en/latest/backbone.html#module-backbone.bipopulations
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
