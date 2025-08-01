#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Calculate correlation between all base pairs of a single sequence and for a
  single helical parameter.

doc: |-
  Calculate correlation between all base pairs of a single sequence and for a single helical parameter.

baseCommand: interseqcorr

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_dna:5.1.0--pyhdfd78af_0

inputs:
  input_ser_path:
    label: Path to .ser file with data for single helical parameter
    doc: |-
      Path to .ser file with data for single helical parameter
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/correlation/canal_output_roll.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_ser_path

  output_csv_path:
    label: Path to directory where output is saved
    doc: |-
      Path to directory where output is saved
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/correlation/inter_seqcorr_roll.csv
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
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/correlation/inter_seqcorr_roll.jpg
    type: string
    format:
    - edam:format_3579
    inputBinding:
      position: 3
      prefix: --output_jpg_path
    default: system.jpg

  config:
    label: Advanced configuration options for biobb_dna InterSequenceCorrelation
    doc: |-
      Advanced configuration options for biobb_dna InterSequenceCorrelation. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna InterSequenceCorrelation documentation: https://biobb-dna.readthedocs.io/en/latest/interbp_correlations.html#interbp-correlations-interseqcorr-module
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
