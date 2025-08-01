#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class is a wrapper of Acpype tool for generation of topologies for OPLS/AA.

doc: |-
  Generation of topologies for OPLS/AA. Acpype is a tool based in Python to use Antechamber to generate topologies for chemical compounds and to interface with others python applications like CCPN or ARIA. Visit the official page.

baseCommand: acpype_params_gmx_opls

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_chemistry:5.1.0--pyhdfd78af_1

inputs:
  input_path:
    label: Path to the input file
    doc: |-
      Path to the input file
      Type: string
      File type: input
      Accepted formats: pdb, mdl, mol2
      Example file: https://github.com/bioexcel/biobb_chemistry/raw/master/biobb_chemistry/test/data/acpype/acpype.params.mol2
    type: File
    format:
    - edam:format_1476
    - edam:format_3815
    - edam:format_3816
    inputBinding:
      position: 1
      prefix: --input_path

  output_path_itp:
    label: Path to the ITP output file
    doc: |-
      Path to the ITP output file
      Type: string
      File type: output
      Accepted formats: itp
      Example file: https://github.com/bioexcel/biobb_chemistry/raw/master/biobb_chemistry/test/reference/acpype/ref_acpype.gmx.opls.itp
    type: string
    format:
    - edam:format_3883
    inputBinding:
      position: 2
      prefix: --output_path_itp
    default: system.itp

  output_path_top:
    label: Path to the TOP output file
    doc: |-
      Path to the TOP output file
      Type: string
      File type: output
      Accepted formats: top
      Example file: https://github.com/bioexcel/biobb_chemistry/raw/master/biobb_chemistry/test/reference/acpype/ref_acpype.gmx.opls.top
    type: string
    format:
    - edam:format_3880
    inputBinding:
      position: 3
      prefix: --output_path_top
    default: system.top

  config:
    label: Advanced configuration options for biobb_chemistry AcpypeParamsGMXOPLS
    doc: |-
      Advanced configuration options for biobb_chemistry AcpypeParamsGMXOPLS. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_chemistry AcpypeParamsGMXOPLS documentation: https://biobb-chemistry.readthedocs.io/en/latest/acpype.html#module-acpype.acpype_params_gmx_opls
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_path_itp:
    label: Path to the ITP output file
    doc: |-
      Path to the ITP output file
    type: File
    outputBinding:
      glob: $(inputs.output_path_itp)
    format: edam:format_3883

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
