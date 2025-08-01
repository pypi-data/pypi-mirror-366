#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Calculate correlation between helical parameters for a single intra-base pair.

doc: |-
  Calculate correlation between helical parameters for a single intra-base pair.

baseCommand: intrahpcorr

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_dna:5.1.0--pyhdfd78af_0

inputs:
  input_filename_shear:
    label: Path to .csv file with data for helical parameter 'shear'
    doc: |-
      Path to .csv file with data for helical parameter 'shear'
      Type: string
      File type: input
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/correlation/series_shear_A.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 1
      prefix: --input_filename_shear

  input_filename_stretch:
    label: Path to .csv file with data for helical parameter 'stretch'
    doc: |-
      Path to .csv file with data for helical parameter 'stretch'
      Type: string
      File type: input
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/correlation/series_stretch_A.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 2
      prefix: --input_filename_stretch

  input_filename_stagger:
    label: Path to .csv file with data for helical parameter 'stagger'
    doc: |-
      Path to .csv file with data for helical parameter 'stagger'
      Type: string
      File type: input
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/correlation/series_stagger_A.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 3
      prefix: --input_filename_stagger

  input_filename_buckle:
    label: Path to .csv file with data for helical parameter 'buckle'
    doc: |-
      Path to .csv file with data for helical parameter 'buckle'
      Type: string
      File type: input
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/correlation/series_buckle_A.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 4
      prefix: --input_filename_buckle

  input_filename_propel:
    label: Path to .csv file with data for helical parameter 'propeller'
    doc: |-
      Path to .csv file with data for helical parameter 'propeller'
      Type: string
      File type: input
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/correlation/series_propel_A.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 5
      prefix: --input_filename_propel

  input_filename_opening:
    label: Path to .csv file with data for helical parameter 'opening'
    doc: |-
      Path to .csv file with data for helical parameter 'opening'
      Type: string
      File type: input
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/correlation/series_opening_A.csv
    type: File
    format:
    - edam:format_3752
    inputBinding:
      position: 6
      prefix: --input_filename_opening

  output_csv_path:
    label: Path to directory where output is saved
    doc: |-
      Path to directory where output is saved
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/correlation/intra_hpcorr_ref.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      position: 7
      prefix: --output_csv_path
    default: system.csv

  output_jpg_path:
    label: Path to .jpg file where output is saved
    doc: |-
      Path to .jpg file where output is saved
      Type: string
      File type: output
      Accepted formats: jpg
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/correlation/intra_hpcorr_ref.jpg
    type: string
    format:
    - edam:format_3579
    inputBinding:
      position: 8
      prefix: --output_jpg_path
    default: system.jpg

  config:
    label: Advanced configuration options for biobb_dna IntraHelParCorrelation
    doc: |-
      Advanced configuration options for biobb_dna IntraHelParCorrelation. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna IntraHelParCorrelation documentation: https://biobb-dna.readthedocs.io/en/latest/intrabp_correlations.html#intrabp-correlations-intrahpcorr-module
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_csv_path:
    label: Path to directory where output is saved
    doc: |-
      Path to directory where output is saved
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
