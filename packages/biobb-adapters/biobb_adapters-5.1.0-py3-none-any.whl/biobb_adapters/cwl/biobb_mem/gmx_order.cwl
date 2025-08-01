#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the GROMACS order module for computing lipid order parameters per
  atom for carbon tails.

doc: |-
  GROMCAS order only works for saturated carbons and united atom force fields.

baseCommand: gmx_order

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_mem:5.1.0--pyhdfd78af_0

inputs:
  input_top_path:
    label: Path to the input structure or topology file
    doc: |-
      Path to the input structure or topology file
      Type: string
      File type: input
      Accepted formats: tpr
      Example file: https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/data/ambertools/topology.tpr
    type: File
    format:
    - edam:format_2333
    inputBinding:
      position: 1
      prefix: --input_top_path

  input_traj_path:
    label: Path to the input trajectory to be processed
    doc: |-
      Path to the input trajectory to be processed
      Type: string
      File type: input
      Accepted formats: xtc, trr, cpt, gro, g96, pdb, tng
      Example file: https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/data/ambertools/trajectory.xtc
    type: File
    format:
    - edam:format_3875
    - edam:format_3910
    - edam:format_2333
    - edam:format_2033
    - edam:format_2033
    - edam:format_1476
    - edam:format_3876
    inputBinding:
      position: 2
      prefix: --input_traj_path

  input_index_path:
    label: Path to the GROMACS index file
    doc: "Path to the GROMACS index file\nType: string\nFile type: input\nAccepted\
      \ formats: ndx\nExample file: https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/data/\
      \       "
    type: File
    format:
    - edam:format_2033
    inputBinding:
      position: 3
      prefix: --input_index_path

  output_deuter_path:
    label: Path to deuterium order parameters xvgr/xmgr file
    doc: |-
      Path to deuterium order parameters xvgr/xmgr file
      Type: string
      File type: output
      Accepted formats: xvg
      Example file: https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/data/gromacs/deuter.xvg
    type: string
    format:
    - edam:format_2330
    inputBinding:
      position: 4
      prefix: --output_deuter_path
    default: system.xvg

  output_order_path:
    label: Path to order tensor diagonal elements xvgr/xmgr file
    doc: |-
      Path to order tensor diagonal elements xvgr/xmgr file
      Type: string
      File type: output
      Accepted formats: xvg
      Example file: https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/data/gromacs/order.xvg
    type: string
    format:
    - edam:format_2330
    inputBinding:
      prefix: --output_order_path
    default: system.xvg

  config:
    label: Advanced configuration options for biobb_mem GMXOrder
    doc: |-
      Advanced configuration options for biobb_mem GMXOrder. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_mem GMXOrder documentation: https://biobb-mem.readthedocs.io/en/latest/gromacs.html#module-gromacs.gmx_order
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_deuter_path:
    label: Path to deuterium order parameters xvgr/xmgr file
    doc: |-
      Path to deuterium order parameters xvgr/xmgr file
    type: File
    outputBinding:
      glob: $(inputs.output_deuter_path)
    format: edam:format_2330

  output_order_path:
    label: Path to order tensor diagonal elements xvgr/xmgr file
    doc: |-
      Path to order tensor diagonal elements xvgr/xmgr file
    type: File?
    outputBinding:
      glob: $(inputs.output_order_path)
    format: edam:format_2330

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
