#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Calculate Canonical Alpha/Gamma populations from alpha and gamma parameters.

doc: |-
  Calculate Canonical Alpha/Gamma populations from alpha and gamma parameters.

baseCommand: canonicalag

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_dna:5.1.0--pyhdfd78af_0

inputs:
  input_alphaC_path:
    label: 'Path to .ser file for helical parameter ''alphaC''. File type: input'
    doc: |-
      Path to .ser file for helical parameter 'alphaC'. File type: input
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/backbone/canal_output_alphaC.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_alphaC_path

  input_alphaW_path:
    label: 'Path to .ser file for helical parameter ''alphaW''. File type: input'
    doc: |-
      Path to .ser file for helical parameter 'alphaW'. File type: input
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/backbone/canal_output_alphaW.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --input_alphaW_path

  input_gammaC_path:
    label: 'Path to .ser file for helical parameter ''gammaC''. File type: input'
    doc: |-
      Path to .ser file for helical parameter 'gammaC'. File type: input
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/backbone/canal_output_gammaC.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 3
      prefix: --input_gammaC_path

  input_gammaW_path:
    label: 'Path to .ser file for helical parameter ''gammaW''. File type: input'
    doc: |-
      Path to .ser file for helical parameter 'gammaW'. File type: input
      Type: string
      File type: input
      Accepted formats: ser
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/backbone/canal_output_gammaW.ser
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 4
      prefix: --input_gammaW_path

  output_csv_path:
    label: 'Path to .csv file where output is saved. File type: output'
    doc: |-
      Path to .csv file where output is saved. File type: output
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/backbone/canonag_ref.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      position: 5
      prefix: --output_csv_path
    default: system.csv

  output_jpg_path:
    label: 'Path to .jpg file where output is saved. File type: output'
    doc: |-
      Path to .jpg file where output is saved. File type: output
      Type: string
      File type: output
      Accepted formats: jpg
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/backbone/canonag_ref.jpg
    type: string
    format:
    - edam:format_3579
    inputBinding:
      position: 6
      prefix: --output_jpg_path
    default: system.jpg

  config:
    label: Advanced configuration options for biobb_dna CanonicalAG
    doc: |-
      Advanced configuration options for biobb_dna CanonicalAG. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna CanonicalAG documentation: https://biobb-dna.readthedocs.io/en/latest/backbone.html#module-backbone.canonicalag
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_csv_path:
    label: 'Path to .csv file where output is saved. File type: output'
    doc: |-
      Path to .csv file where output is saved. File type: output
    type: File
    outputBinding:
      glob: $(inputs.output_csv_path)
    format: edam:format_3752

  output_jpg_path:
    label: 'Path to .jpg file where output is saved. File type: output'
    doc: |-
      Path to .jpg file where output is saved. File type: output
    type: File
    outputBinding:
      glob: $(inputs.output_jpg_path)
    format: edam:format_3579

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
