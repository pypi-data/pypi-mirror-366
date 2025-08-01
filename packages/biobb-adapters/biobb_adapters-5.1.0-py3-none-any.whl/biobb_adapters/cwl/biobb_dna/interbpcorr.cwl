#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Calculate correlation between all base pairs of a single sequence and for a
  single helical parameter.

doc: |-
  Calculate correlation between neighboring base pairs and pairs of helical parameters.

baseCommand: interbpcorr

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_dna:5.1.0--pyhdfd78af_0

inputs:
  input_filename_shift:
    label: Path to .ser file with data for helical parameter 'shift'
    doc: |-
      Path to .ser file with data for helical parameter 'shift'
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/correlation/canal_output_shift.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_filename_shift

  input_filename_slide:
    label: Path to .ser file with data for helical parameter 'slide'
    doc: |-
      Path to .ser file with data for helical parameter 'slide'
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/correlation/canal_output_slide.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --input_filename_slide

  input_filename_rise:
    label: Path to .ser file with data for helical parameter 'rise'
    doc: |-
      Path to .ser file with data for helical parameter 'rise'
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/correlation/canal_output_rise.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 3
      prefix: --input_filename_rise

  input_filename_tilt:
    label: Path to .ser file with data for helical parameter 'tilt'
    doc: |-
      Path to .ser file with data for helical parameter 'tilt'
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/correlation/canal_output_tilt.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 4
      prefix: --input_filename_tilt

  input_filename_roll:
    label: Path to .ser file with data for helical parameter 'roll'
    doc: |-
      Path to .ser file with data for helical parameter 'roll'
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/correlation/canal_output_roll.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 5
      prefix: --input_filename_roll

  input_filename_twist:
    label: Path to .ser file with data for helical parameter 'twist'
    doc: |-
      Path to .ser file with data for helical parameter 'twist'
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/correlation/canal_output_twist.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 6
      prefix: --input_filename_twist

  output_csv_path:
    label: Path to directory where output is saved
    doc: |-
      Path to directory where output is saved
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/correlation/inter_bpcorr_ref.csv
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
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/correlation/inter_bpcorr_ref.jpg
    type: string
    format:
    - edam:format_3579
    inputBinding:
      position: 8
      prefix: --output_jpg_path
    default: system.jpg

  config:
    label: Advanced configuration options for biobb_dna InterBasePairCorrelation
    doc: |-
      Advanced configuration options for biobb_dna InterBasePairCorrelation. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna InterBasePairCorrelation documentation: https://biobb-dna.readthedocs.io/en/latest/interbp_correlations.html#interbp-correlations-interbpcorr-module
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
