#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Determine binormality/bimodality from a helical parameter series dataset.

doc: |-
  Determine binormality/bimodality from a helical parameter series dataset.

baseCommand: dna_bimodality

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_dna:5.1.0--pyhdfd78af_0

inputs:
  input_csv_file:
    label: Path to .csv file with helical parameter series. If `input_zip_file` is
      passed, this should be just the filename of the .csv file inside .zip
    doc: |-
      Path to .csv file with helical parameter series. If `input_zip_file` is passed, this should be just the filename of the .csv file inside .zip
      Type: string
      File type: input
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/dna/series_shift_AT.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 1
      prefix: --input_csv_file

  output_csv_path:
    label: Path to .csv file where output is saved
    doc: |-
      Path to .csv file where output is saved
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/dna/AT_shift_bimod.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      position: 2
      prefix: --output_csv_path
    default: system.csv

  output_jpg_path:
    label: Path to .jpg file where output is saved
    doc: |-
      Path to .jpg file where output is saved
      Type: string
      File type: output
      Accepted formats: jpg
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/dna/AT_shift_bimod.jpg
    type: string
    format:
    - edam:format_3579
    inputBinding:
      position: 3
      prefix: --output_jpg_path
    default: system.jpg

  input_zip_file:
    label: .zip file containing the `input_csv_file` .csv file
    doc: |-
      .zip file containing the `input_csv_file` .csv file
      Type: string
      File type: input
      Accepted formats: zip
      Example file: null
    type: File?
    format:
    - edam:format_3987
    inputBinding:
      prefix: --input_zip_file

  config:
    label: Advanced configuration options for biobb_dna HelParBimodality
    doc: |-
      Advanced configuration options for biobb_dna HelParBimodality. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna HelParBimodality documentation: https://biobb-dna.readthedocs.io/en/latest/dna.html#module-dna.dna_bimodality
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
