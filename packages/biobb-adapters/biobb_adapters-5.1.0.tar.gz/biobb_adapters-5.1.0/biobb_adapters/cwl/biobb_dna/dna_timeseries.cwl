#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Created time series and histogram plots for each base pair from a helical parameter
  series file.

doc: |-
  The helical parameter series file is expected to be a table, with the first column being an index and the rest the helical parameter values for each base/basepair.

baseCommand: dna_timeseries

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

  output_zip_path:
    label: Path to output .zip files where data is saved
    doc: |-
      Path to output .zip files where data is saved
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/dna/timeseries_output.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --output_zip_path
    default: system.zip

  config:
    label: Advanced configuration options for biobb_dna HelParTimeSeries
    doc: |-
      Advanced configuration options for biobb_dna HelParTimeSeries. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna HelParTimeSeries documentation: https://biobb-dna.readthedocs.io/en/latest/dna.html#module-dna.dna_timeseries
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_zip_path:
    label: Path to output .zip files where data is saved
    doc: |-
      Path to output .zip files where data is saved
    type: File
    outputBinding:
      glob: $(inputs.output_zip_path)
    format: edam:format_3987

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
