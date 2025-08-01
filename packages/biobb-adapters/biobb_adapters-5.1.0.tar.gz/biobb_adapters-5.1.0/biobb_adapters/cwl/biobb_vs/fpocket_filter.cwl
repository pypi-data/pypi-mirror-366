#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Performs a search over the outputs of the fpocket building block.

doc: |-
  Finds one or more binding sites in the outputs of the fpocket building block from given parameters.

baseCommand: fpocket_filter

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_vs:5.1.0--pyhdfd78af_0

inputs:
  input_pockets_zip:
    label: Path to all the pockets found by fpocket
    doc: |-
      Path to all the pockets found by fpocket
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/fpocket/input_pockets.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 1
      prefix: --input_pockets_zip

  input_summary:
    label: Path to the JSON summary file returned by fpocket
    doc: |-
      Path to the JSON summary file returned by fpocket
      Type: string
      File type: input
      Accepted formats: json
      Example file: https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/fpocket/input_summary.json
    type: File
    format:
    - edam:format_3464
    inputBinding:
      position: 2
      prefix: --input_summary

  output_filter_pockets_zip:
    label: Path to the selected pockets after filtering
    doc: |-
      Path to the selected pockets after filtering
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_filter_pockets.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 3
      prefix: --output_filter_pockets_zip
    default: system.zip

  config:
    label: Advanced configuration options for biobb_vs FPocketFilter
    doc: |-
      Advanced configuration options for biobb_vs FPocketFilter. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_vs FPocketFilter documentation: https://biobb-vs.readthedocs.io/en/latest/fpocket.html#module-fpocket.fpocket_filter
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_filter_pockets_zip:
    label: Path to the selected pockets after filtering
    doc: |-
      Path to the selected pockets after filtering
    type: File
    outputBinding:
      glob: $(inputs.output_filter_pockets_zip)
    format: edam:format_3987

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
