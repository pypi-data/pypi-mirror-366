#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Tool for extracting dna_timeseries output files.

doc: |-
  Unzips a zip file containing dna_timeseries output files and extracts the csv and jpg files.

baseCommand: dna_timeseries_unzip

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_dna:5.1.0--pyhdfd78af_0

inputs:
  input_zip_file:
    label: Zip file with dna_timeseries output files
    doc: |-
      Zip file with dna_timeseries output files
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/dna/timeseries_output.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 1
      prefix: --input_zip_file

  output_path_csv:
    label: dna_timeseries output csv file contained within input_zip_file
    doc: |-
      dna_timeseries output csv file contained within input_zip_file
      Type: string
      File type: output
      Accepted formats: csv
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/dna/dna_timeseries_unzip.csv
    type: string
    format:
    - edam:format_3752
    inputBinding:
      position: 2
      prefix: --output_path_csv
    default: system.csv

  output_path_jpg:
    label: dna_timeseries output jpg file contained within input_zip_file
    doc: |-
      dna_timeseries output jpg file contained within input_zip_file
      Type: string
      File type: output
      Accepted formats: jpg
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/dna/dna_timeseries_unzip.jpg
    type: string
    format:
    - edam:format_3579
    inputBinding:
      position: 3
      prefix: --output_path_jpg
    default: system.jpg

  output_list_path:
    label: Text file with a list of all dna_timeseries output files contained within
      input_zip_file
    doc: |-
      Text file with a list of all dna_timeseries output files contained within input_zip_file
      Type: string
      File type: output
      Accepted formats: txt
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/dna/dna_timeseries_unzip.txt
    type: string
    format:
    - edam:format_2330
    inputBinding:
      prefix: --output_list_path
    default: system.txt

  config:
    label: Advanced configuration options for biobb_dna DnaTimeseriesUnzip
    doc: |-
      Advanced configuration options for biobb_dna DnaTimeseriesUnzip. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna DnaTimeseriesUnzip documentation: https://biobb-dna.readthedocs.io/en/latest/dna.html#module-dna.dna_timeseries_unzip
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_path_csv:
    label: dna_timeseries output csv file contained within input_zip_file
    doc: |-
      dna_timeseries output csv file contained within input_zip_file
    type: File
    outputBinding:
      glob: $(inputs.output_path_csv)
    format: edam:format_3752

  output_path_jpg:
    label: dna_timeseries output jpg file contained within input_zip_file
    doc: |-
      dna_timeseries output jpg file contained within input_zip_file
    type: File
    outputBinding:
      glob: $(inputs.output_path_jpg)
    format: edam:format_3579

  output_list_path:
    label: Text file with a list of all dna_timeseries output files contained within
      input_zip_file
    doc: |-
      Text file with a list of all dna_timeseries output files contained within input_zip_file
    type: File?
    outputBinding:
      glob: $(inputs.output_list_path)
    format: edam:format_2330

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
