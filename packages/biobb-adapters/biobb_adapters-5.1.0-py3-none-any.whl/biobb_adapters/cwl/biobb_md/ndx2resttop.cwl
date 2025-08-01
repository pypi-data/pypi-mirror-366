#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Generate a restrained topology from an index NDX file.

doc: |-
  This module automatizes the process of restrained topology generation starting from an index NDX file.

baseCommand: ndx2resttop

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_md:3.7.2--pyhdfd78af_0

inputs:
  input_ndx_path:
    label: Path to the input NDX index file
    doc: |-
      Path to the input NDX index file
      Type: string
      File type: input
      Accepted formats: ndx
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs_extra/ndx2resttop.ndx
    type: File
    format:
    - edam:format_2033
    inputBinding:
      position: 1
      prefix: --input_ndx_path

  input_top_zip_path:
    label: Path the input TOP topology in zip format
    doc: |-
      Path the input TOP topology in zip format
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs_extra/ndx2resttop.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --input_top_zip_path

  output_top_zip_path:
    label: Path the output TOP topology in zip format
    doc: |-
      Path the output TOP topology in zip format
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/reference/gromacs_extra/ref_ndx2resttop.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 3
      prefix: --output_top_zip_path
    default: system.zip

  config:
    label: Advanced configuration options for biobb_md Ndx2resttop
    doc: |-
      Advanced configuration options for biobb_md Ndx2resttop. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_md Ndx2resttop documentation: https://biobb-md.readthedocs.io/en/latest/gromacs_extra.html#gromacs-extra-ndx2resttop-module
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_top_zip_path:
    label: Path the output TOP topology in zip format
    doc: |-
      Path the output TOP topology in zip format
    type: File
    outputBinding:
      glob: $(inputs.output_top_zip_path)
    format: edam:format_3987

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
