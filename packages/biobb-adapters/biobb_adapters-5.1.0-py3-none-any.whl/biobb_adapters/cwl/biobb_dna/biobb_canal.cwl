#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper for the Canal executable that is part of the Curves+ software suite.

doc: |-
  The Canal program is used to analyze the curvature of DNA structures.

baseCommand: biobb_canal

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_dna:5.1.0--pyhdfd78af_0

inputs:
  input_cda_file:
    label: Input cda file, from Cur+ output
    doc: |-
      Input cda file, from Cur+ output
      Type: string
      File type: input
      Accepted formats: cda
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/curvesplus/curves_output.cda
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_cda_file

  output_zip_path:
    label: zip filename for output files
    doc: |-
      zip filename for output files
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/curvesplus/canal_output.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --output_zip_path
    default: system.zip

  input_lis_file:
    label: Input lis file, from Cur+ output
    doc: |-
      Input lis file, from Cur+ output
      Type: string
      File type: input
      Accepted formats: lis
      Example file: null
    type: File?
    format:
    - edam:format_2330
    inputBinding:
      prefix: --input_lis_file

  config:
    label: Advanced configuration options for biobb_dna Canal
    doc: |-
      Advanced configuration options for biobb_dna Canal. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna Canal documentation: https://biobb-dna.readthedocs.io/en/latest/curvesplus.html#module-curvesplus.biobb_canal
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_zip_path:
    label: zip filename for output files
    doc: |-
      zip filename for output files
    type: File
    outputBinding:
      glob: $(inputs.output_zip_path)
    format: edam:format_3987

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
