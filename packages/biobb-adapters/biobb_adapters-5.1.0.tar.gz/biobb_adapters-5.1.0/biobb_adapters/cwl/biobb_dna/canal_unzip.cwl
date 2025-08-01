#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Tool for extracting biobb_canal output files.

doc: |-
  Unzips a Canal output file contained within a zip file.

baseCommand: canal_unzip

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_dna:5.1.0--pyhdfd78af_0

inputs:
  input_zip_file:
    label: Zip file with Canal output files
    doc: |-
      Zip file with Canal output files
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/curvesplus/canal_output.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 1
      prefix: --input_zip_file

  output_path:
    label: Canal output file contained within input_zip_file
    doc: |-
      Canal output file contained within input_zip_file
      Type: string
      File type: output
      Accepted formats: ser, his, cor
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/curvesplus/canal_unzip_output.ser
    type: string
    format:
    - edam:format_2330
    - edam:format_3905
    - edam:format_3465
    inputBinding:
      position: 2
      prefix: --output_path
    default: system.ser

  output_list_path:
    label: Text file with a list of all Canal output files contained within input_zip_file
    doc: |-
      Text file with a list of all Canal output files contained within input_zip_file
      Type: string
      File type: output
      Accepted formats: txt
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/curvesplus/canal_unzip_output.txt
    type: string
    format:
    - edam:format_2330
    inputBinding:
      prefix: --output_list_path
    default: system.txt

  config:
    label: Advanced configuration options for biobb_dna CanalUnzip
    doc: |-
      Advanced configuration options for biobb_dna CanalUnzip. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna CanalUnzip documentation: https://biobb-dna.readthedocs.io/en/latest/curvesplus.html#module-curvesplus.canal_unzip
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_path:
    label: Canal output file contained within input_zip_file
    doc: |-
      Canal output file contained within input_zip_file
    type: File
    outputBinding:
      glob: $(inputs.output_path)
    format: edam:format_2330

  output_list_path:
    label: Text file with a list of all Canal output files contained within input_zip_file
    doc: |-
      Text file with a list of all Canal output files contained within input_zip_file
    type: File?
    outputBinding:
      glob: $(inputs.output_list_path)
    format: edam:format_2330

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
