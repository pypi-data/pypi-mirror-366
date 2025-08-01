#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class is a wrapper of Acpype tool for small molecule parameterization
  for CNS/XPLOR MD package.

doc: |-
  Generation of topologies for CNS/XPLOR. Acpype is a tool based in Python to use Antechamber to generate topologies for chemical compounds and to interface with others python applications like CCPN or ARIA. Visit the official page.

baseCommand: acpype_params_cns

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

  output_path_par:
    label: Path to the PAR output file
    doc: |-
      Path to the PAR output file
      Type: string
      File type: output
      Accepted formats: par
      Example file: https://github.com/bioexcel/biobb_chemistry/raw/master/biobb_chemistry/test/reference/acpype/ref_acpype.cns.par
    type: string
    format:
    - edam:format_3881
    inputBinding:
      position: 2
      prefix: --output_path_par
    default: system.par

  output_path_inp:
    label: Path to the INP output file
    doc: |-
      Path to the INP output file
      Type: string
      File type: output
      Accepted formats: inp
      Example file: https://github.com/bioexcel/biobb_chemistry/raw/master/biobb_chemistry/test/reference/acpype/ref_acpype.cns.inp
    type: string
    format:
    - edam:format_3878
    inputBinding:
      position: 3
      prefix: --output_path_inp
    default: system.inp

  output_path_top:
    label: Path to the TOP output file
    doc: |-
      Path to the TOP output file
      Type: string
      File type: output
      Accepted formats: top
      Example file: https://github.com/bioexcel/biobb_chemistry/raw/master/biobb_chemistry/test/reference/acpype/ref_acpype.cns.top
    type: string
    format:
    - edam:format_3881
    inputBinding:
      position: 4
      prefix: --output_path_top
    default: system.top

  output_path_pdb:
    label: Path to the PDB output file
    doc: |-
      Path to the PDB output file
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_chemistry/raw/master/biobb_chemistry/test/reference/acpype/ref_acpype.cns.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      position: 5
      prefix: --output_path_pdb
    default: system.pdb

  config:
    label: Advanced configuration options for biobb_chemistry AcpypeParamsCNS
    doc: |-
      Advanced configuration options for biobb_chemistry AcpypeParamsCNS. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_chemistry AcpypeParamsCNS documentation: https://biobb-chemistry.readthedocs.io/en/latest/acpype.html#module-acpype.acpype_params_cns
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_path_par:
    label: Path to the PAR output file
    doc: |-
      Path to the PAR output file
    type: File
    outputBinding:
      glob: $(inputs.output_path_par)
    format: edam:format_3881

  output_path_inp:
    label: Path to the INP output file
    doc: |-
      Path to the INP output file
    type: File
    outputBinding:
      glob: $(inputs.output_path_inp)
    format: edam:format_3878

  output_path_top:
    label: Path to the TOP output file
    doc: |-
      Path to the TOP output file
    type: File
    outputBinding:
      glob: $(inputs.output_path_top)
    format: edam:format_3881

  output_path_pdb:
    label: Path to the PDB output file
    doc: |-
      Path to the PDB output file
    type: File
    outputBinding:
      glob: $(inputs.output_path_pdb)
    format: edam:format_1476

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
