#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper class for the PMX create_top module.

doc: |-
  Create a complete ligand topology file from two input topology files.

baseCommand: pmxcreate_top

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_pmx:5.1.0--pyhdfd78af_0

inputs:
  input_topology1_path:
    label: Path to the input topology file 1
    doc: |-
      Path to the input topology file 1
      Type: string
      File type: input
      Accepted formats: itp
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/data/pmx/ligand.itp
    type: File
    format:
    - edam:format_3883
    inputBinding:
      position: 1
      prefix: --input_topology1_path

  input_topology2_path:
    label: Path to the input topology file 2
    doc: |-
      Path to the input topology file 2
      Type: string
      File type: input
      Accepted formats: itp
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/data/pmx/ligand.itp
    type: File
    format:
    - edam:format_3883
    inputBinding:
      position: 2
      prefix: --input_topology2_path

  output_topology_path:
    label: Path to the complete ligand topology file
    doc: |-
      Path to the complete ligand topology file
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/data/pmx/ligand_top.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 3
      prefix: --output_topology_path
    default: system.zip

  config:
    label: Advanced configuration options for biobb_pmx Pmxcreate_top
    doc: |-
      Advanced configuration options for biobb_pmx Pmxcreate_top. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pmx Pmxcreate_top documentation: https://biobb-pmx.readthedocs.io/en/latest/pmx.html#module-pmx.pmxcreate_top
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_topology_path:
    label: Path to the complete ligand topology file
    doc: |-
      Path to the complete ligand topology file
    type: File
    outputBinding:
      glob: $(inputs.output_topology_path)
    format: edam:format_3987

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
