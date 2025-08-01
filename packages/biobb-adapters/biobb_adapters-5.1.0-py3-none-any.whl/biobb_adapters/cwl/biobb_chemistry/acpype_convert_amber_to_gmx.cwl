#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class is a wrapper of Acpype tool for the conversion of AMBER topologies
  to GROMACS.

doc: |-
  Acpype is a tool based in Python to use Antechamber to generate topologies for chemical compounds and to interface with others python applications like CCPN or ARIA. Visit the official page.

baseCommand: acpype_convert_amber_to_gmx

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_chemistry:5.1.0--pyhdfd78af_1

inputs:
  input_crd_path:
    label: Path to the input coordinates file (AMBER crd)
    doc: |-
      Path to the input coordinates file (AMBER crd)
      Type: string
      File type: input
      Accepted formats: inpcrd
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_chemistry/master/biobb_chemistry/test/data/acpype/acpype.coords.inpcrd
    type: File
    format:
    - edam:format_3878
    inputBinding:
      position: 1
      prefix: --input_crd_path

  input_top_path:
    label: Path to the input topology file (AMBER ParmTop)
    doc: |-
      Path to the input topology file (AMBER ParmTop)
      Type: string
      File type: input
      Accepted formats: top, parmtop, prmtop
      Example file: https://github.com/bioexcel/biobb_chemistry/raw/master/biobb_chemistry/test/data/acpype/acpype.top.prmtop
    type: File
    format:
    - edam:format_3881
    - edam:format_3881
    - edam:format_3881
    inputBinding:
      position: 2
      prefix: --input_top_path

  output_path_gro:
    label: Path to the GRO output file
    doc: |-
      Path to the GRO output file
      Type: string
      File type: output
      Accepted formats: gro
      Example file: https://github.com/bioexcel/biobb_chemistry/raw/master/biobb_chemistry/test/reference/acpype/ref_acpype.amber2gmx.gro
    type: string
    format:
    - edam:format_2033
    inputBinding:
      position: 3
      prefix: --output_path_gro
    default: system.gro

  output_path_top:
    label: Path to the TOP output file
    doc: |-
      Path to the TOP output file
      Type: string
      File type: output
      Accepted formats: top
      Example file: https://github.com/bioexcel/biobb_chemistry/raw/master/biobb_chemistry/test/reference/acpype/ref_acpype.amber2gmx.top
    type: string
    format:
    - edam:format_3880
    inputBinding:
      position: 4
      prefix: --output_path_top
    default: system.top

  config:
    label: Advanced configuration options for biobb_chemistry AcpypeConvertAMBERtoGMX
    doc: |-
      Advanced configuration options for biobb_chemistry AcpypeConvertAMBERtoGMX. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_chemistry AcpypeConvertAMBERtoGMX documentation: https://biobb-chemistry.readthedocs.io/en/latest/acpype.html#module-acpype.acpype_convert_amber_to_gmx
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_path_gro:
    label: Path to the GRO output file
    doc: |-
      Path to the GRO output file
    type: File
    outputBinding:
      glob: $(inputs.output_path_gro)
    format: edam:format_2033

  output_path_top:
    label: Path to the TOP output file
    doc: |-
      Path to the TOP output file
    type: File
    outputBinding:
      glob: $(inputs.output_path_top)
    format: edam:format_3880

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
