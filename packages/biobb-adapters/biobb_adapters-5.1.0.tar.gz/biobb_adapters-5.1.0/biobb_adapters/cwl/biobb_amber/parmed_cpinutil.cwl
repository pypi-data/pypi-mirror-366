#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the AmberTools (AMBER MD Package) parmed tool module.

doc: |-
  Creates a cpin file for constant pH simulations from an AMBER topology file using parmed tool from the AmberTools MD package.

baseCommand: parmed_cpinutil

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_amber:5.1.0--pyhdfd78af_0

inputs:
  input_top_path:
    label: Input AMBER topology file
    doc: |-
      Input AMBER topology file
      Type: string
      File type: input
      Accepted formats: top, parmtop, prmtop
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/data/parmed/structure.solv.top
    type: File
    format:
    - edam:format_3881
    - edam:format_3881
    - edam:format_3881
    inputBinding:
      position: 1
      prefix: --input_top_path

  output_cpin_path:
    label: Output AMBER constant pH input (CPin) file
    doc: |-
      Output AMBER constant pH input (CPin) file
      Type: string
      File type: output
      Accepted formats: cpin
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/parmed/cln025.cpin
    type: string
    format:
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --output_cpin_path
    default: system.cpin

  output_top_path:
    label: Output topology file (AMBER ParmTop)
    doc: |-
      Output topology file (AMBER ParmTop)
      Type: string
      File type: output
      Accepted formats: top, parmtop, prmtop
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/parmed/cln025.cpH.prmtop
    type: string
    format:
    - edam:format_3881
    - edam:format_3881
    - edam:format_3881
    inputBinding:
      prefix: --output_top_path
    default: system.top

  config:
    label: Advanced configuration options for biobb_amber ParmedCpinUtil
    doc: |-
      Advanced configuration options for biobb_amber ParmedCpinUtil. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_amber ParmedCpinUtil documentation: https://biobb-amber.readthedocs.io/en/latest/parmed.html#module-parmed.parmed_cpinutil
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_cpin_path:
    label: Output AMBER constant pH input (CPin) file
    doc: |-
      Output AMBER constant pH input (CPin) file
    type: File
    outputBinding:
      glob: $(inputs.output_cpin_path)
    format: edam:format_2330

  output_top_path:
    label: Output topology file (AMBER ParmTop)
    doc: |-
      Output topology file (AMBER ParmTop)
    type: File?
    outputBinding:
      glob: $(inputs.output_top_path)
    format: edam:format_3881

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
