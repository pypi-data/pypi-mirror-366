#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class is a wrapper for the Drugbank REST API.

doc: |-
  Download a single component in SDF format from the Drugbank REST API.

baseCommand: drugbank

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_io:4.2.0--pyhdfd78af_0

inputs:
  output_sdf_path:
    label: Path to the output SDF component file
    doc: |-
      Path to the output SDF component file
      Type: string
      File type: output
      Accepted formats: sdf
      Example file: https://github.com/bioexcel/biobb_io/raw/master/biobb_io/test/reference/api/output_drugbank.sdf
    type: string
    format:
    - edam:format_3814
    inputBinding:
      position: 1
      prefix: --output_sdf_path
    default: system.sdf

  config:
    label: Advanced configuration options for biobb_io Drugbank
    doc: |-
      Advanced configuration options for biobb_io Drugbank. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_io Drugbank documentation: https://biobb-io.readthedocs.io/en/latest/api.html#api-drugbank-module
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_sdf_path:
    label: Path to the output SDF component file
    doc: |-
      Path to the output SDF component file
    type: File
    outputBinding:
      glob: $(inputs.output_sdf_path)
    format: edam:format_3814

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
