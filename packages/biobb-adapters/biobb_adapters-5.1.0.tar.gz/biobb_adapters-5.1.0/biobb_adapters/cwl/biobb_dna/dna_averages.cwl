#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Load .ser file for a given helical parameter and read each column corresponding
  to a base calculating average over each one.

doc: |-
  Calculate average values for each base pair and save them in a .csv file.

baseCommand: dna_averages

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_dna:5.1.0--pyhdfd78af_0

inputs:
  input_ser_path:
    label: Path to .ser file for helical parameter. File is expected to be a table,
      with the first column being an index and the rest the helical parameter values
      for each base/basepair
    doc: |-
      Path to .ser file for helical parameter. File is expected to be a table, with the first column being an index and the rest the helical parameter values for each base/basepair
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/dna/canal_output_shift.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_ser_path

  output_csv_path:
    label: Path to .csv file where output is saved
    doc: |-
      Path to .csv file where output is saved
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/dna/shift_avg.csv
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
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/dna/shift_avg.jpg
    type: string
    format:
    - edam:format_3579
    inputBinding:
      position: 3
      prefix: --output_jpg_path
    default: system.jpg

  config:
    label: Advanced configuration options for biobb_dna HelParAverages
    doc: |-
      Advanced configuration options for biobb_dna HelParAverages. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna HelParAverages documentation: https://biobb-dna.readthedocs.io/en/latest/dna.html#module-dna.dna_averages
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
