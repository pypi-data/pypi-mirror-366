#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper class for the Haddock ContactMap module.

doc: |-
  The ContactMap module. Haddock ContactMap module computes contacts between chains in complexes and generates heatmaps and chordcharts.

baseCommand: contact_map

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_haddock:5.1.0--pyhdfd78af_0

inputs:
  input_haddock_wf_data_zip:
    label: Path to the input zipball containing all the current Haddock workflow data
    doc: |-
      Path to the input zipball containing all the current Haddock workflow data
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_haddock/raw/master/biobb_haddock/test/data/haddock/haddock_wf_data_rigid.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 1
      prefix: --input_haddock_wf_data_zip

  output_contactmap_zip_path:
    label: Path to the output contact map files in zip format
    doc: |-
      Path to the output contact map files in zip format
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/reference/haddock/ref_contactmap.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --output_contactmap_zip_path
    default: system.zip

  output_haddock_wf_data_zip:
    label: Path to the output zipball containing all the current Haddock workflow
      data
    doc: |-
      Path to the output zipball containing all the current Haddock workflow data
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_haddock/raw/master/biobb_haddock/test/data/haddock/haddock_wf_data_emref.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      prefix: --output_haddock_wf_data_zip
    default: system.zip

  haddock_config_path:
    label: Haddock configuration CFG file path
    doc: |-
      Haddock configuration CFG file path
      Type: string
      File type: input
      Accepted formats: cfg
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/data/haddock/run.cfg
    type: File?
    format:
    - edam:format_1476
    inputBinding:
      prefix: --haddock_config_path

  config:
    label: Advanced configuration options for biobb_haddock ContactMap
    doc: |-
      Advanced configuration options for biobb_haddock ContactMap. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_haddock ContactMap documentation: https://biobb-haddock.readthedocs.io/en/latest/haddock.html#module-haddock.contact_map
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_contactmap_zip_path:
    label: Path to the output contact map files in zip format
    doc: |-
      Path to the output contact map files in zip format
    type: File
    outputBinding:
      glob: $(inputs.output_contactmap_zip_path)
    format: edam:format_3987

  output_haddock_wf_data_zip:
    label: Path to the output zipball containing all the current Haddock workflow
      data
    doc: |-
      Path to the output zipball containing all the current Haddock workflow data
    type: File?
    outputBinding:
      glob: $(inputs.output_haddock_wf_data_zip)
    format: edam:format_3987

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
