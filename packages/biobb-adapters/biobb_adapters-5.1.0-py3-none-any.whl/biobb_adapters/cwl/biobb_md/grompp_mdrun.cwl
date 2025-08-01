#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the GROMACS grompp module and the GROMACS mdrun module.

doc: |-
  Grompp The GROMACS preprocessor module needs to be fed with the input system and the dynamics parameters to create a portable binary run input file TPR. The simulation parameters can be specified by two methods:  1.The predefined mdp settings defined at simulation_type property or  2.A custom mdp file defined at the input_mdp_path argument.  These two methods are mutually exclusive. In both cases can be further modified by adding parameters to the mdp section in the yaml configuration file. The simulation parameter names and default values can be consulted in the official MDP specification. MDRun is the main computational chemistry engine within GROMACS. It performs Molecular Dynamics simulations, but it can also perform Stochastic Dynamics, Energy Minimization, test particle insertion or (re)calculation of energies.

baseCommand: grompp_mdrun

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_md:3.7.2--pyhdfd78af_0

inputs:
  input_gro_path:
    label: Path to the input GROMACS structure GRO file
    doc: |-
      Path to the input GROMACS structure GRO file
      Type: string
      File type: input
      Accepted formats: gro
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs/grompp.gro
    type: File
    format:
    - edam:format_2033
    inputBinding:
      position: 1
      prefix: --input_gro_path

  input_top_zip_path:
    label: Path to the input GROMACS topology TOP and ITP files in zip format
    doc: |-
      Path to the input GROMACS topology TOP and ITP files in zip format
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs/grompp.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --input_top_zip_path

  output_trr_path:
    label: Path to the GROMACS uncompressed raw trajectory file TRR
    doc: |-
      Path to the GROMACS uncompressed raw trajectory file TRR
      Type: string
      File type: output
      Accepted formats: trr
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/reference/gromacs/ref_mdrun.trr
    type: string
    format:
    - edam:format_3910
    inputBinding:
      position: 3
      prefix: --output_trr_path
    default: system.trr

  output_gro_path:
    label: Path to the output GROMACS structure GRO file
    doc: |-
      Path to the output GROMACS structure GRO file
      Type: string
      File type: output
      Accepted formats: gro
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/reference/gromacs/ref_mdrun.gro
    type: string
    format:
    - edam:format_2033
    inputBinding:
      position: 4
      prefix: --output_gro_path
    default: system.gro

  output_edr_path:
    label: Path to the output GROMACS portable energy file EDR
    doc: |-
      Path to the output GROMACS portable energy file EDR
      Type: string
      File type: output
      Accepted formats: edr
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/reference/gromacs/ref_mdrun.edr
    type: string
    format:
    - edam:format_2330
    inputBinding:
      position: 5
      prefix: --output_edr_path
    default: system.edr

  output_log_path:
    label: Path to the output GROMACS trajectory log file LOG
    doc: |-
      Path to the output GROMACS trajectory log file LOG
      Type: string
      File type: output
      Accepted formats: log
      Example file: https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/reference/gromacs/ref_gmx_mdrun.log
    type: string
    format:
    - edam:format_2330
    inputBinding:
      position: 6
      prefix: --output_log_path
    default: system.log

  input_cpt_path:
    label: Path to the input GROMACS checkpoint file CPT
    doc: |-
      Path to the input GROMACS checkpoint file CPT
      Type: string
      File type: input
      Accepted formats: cpt
      Example file: null
    type: File?
    format:
    - edam:format_2333
    inputBinding:
      prefix: --input_cpt_path

  input_ndx_path:
    label: Path to the input GROMACS index files NDX
    doc: |-
      Path to the input GROMACS index files NDX
      Type: string
      File type: input
      Accepted formats: ndx
      Example file: null
    type: File?
    format:
    - edam:format_2033
    inputBinding:
      prefix: --input_ndx_path

  input_mdp_path:
    label: Path to the input GROMACS MDP file
    doc: |-
      Path to the input GROMACS MDP file
      Type: string
      File type: input
      Accepted formats: mdp
      Example file: null
    type: File?
    format:
    - edam:format_2330
    inputBinding:
      prefix: --input_mdp_path

  output_xtc_path:
    label: Path to the GROMACS compressed trajectory file XTC
    doc: |-
      Path to the GROMACS compressed trajectory file XTC
      Type: string
      File type: output
      Accepted formats: xtc
      Example file: null
    type: string
    format:
    - edam:format_3875
    inputBinding:
      prefix: --output_xtc_path
    default: system.xtc

  output_cpt_path:
    label: Path to the output GROMACS checkpoint file CPT
    doc: |-
      Path to the output GROMACS checkpoint file CPT
      Type: string
      File type: output
      Accepted formats: cpt
      Example file: null
    type: string
    format:
    - edam:format_2333
    inputBinding:
      prefix: --output_cpt_path
    default: system.cpt

  output_dhdl_path:
    label: Path to the output dhdl.xvg file only used when free energy calculation
      is turned on
    doc: |-
      Path to the output dhdl.xvg file only used when free energy calculation is turned on
      Type: string
      File type: output
      Accepted formats: xvg
      Example file: null
    type: string
    format:
    - edam:format_2033
    inputBinding:
      prefix: --output_dhdl_path
    default: system.xvg

  config:
    label: Advanced configuration options for biobb_md GromppMdrun
    doc: |-
      Advanced configuration options for biobb_md GromppMdrun. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_md GromppMdrun documentation: https://biobb-md.readthedocs.io/en/latest/gromacs.html#module-gromacs.grompp_mdrun
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_trr_path:
    label: Path to the GROMACS uncompressed raw trajectory file TRR
    doc: |-
      Path to the GROMACS uncompressed raw trajectory file TRR
    type: File
    outputBinding:
      glob: $(inputs.output_trr_path)
    format: edam:format_3910

  output_gro_path:
    label: Path to the output GROMACS structure GRO file
    doc: |-
      Path to the output GROMACS structure GRO file
    type: File
    outputBinding:
      glob: $(inputs.output_gro_path)
    format: edam:format_2033

  output_edr_path:
    label: Path to the output GROMACS portable energy file EDR
    doc: |-
      Path to the output GROMACS portable energy file EDR
    type: File
    outputBinding:
      glob: $(inputs.output_edr_path)
    format: edam:format_2330

  output_log_path:
    label: Path to the output GROMACS trajectory log file LOG
    doc: |-
      Path to the output GROMACS trajectory log file LOG
    type: File
    outputBinding:
      glob: $(inputs.output_log_path)
    format: edam:format_2330

  output_xtc_path:
    label: Path to the GROMACS compressed trajectory file XTC
    doc: |-
      Path to the GROMACS compressed trajectory file XTC
    type: File?
    outputBinding:
      glob: $(inputs.output_xtc_path)
    format: edam:format_3875

  output_cpt_path:
    label: Path to the output GROMACS checkpoint file CPT
    doc: |-
      Path to the output GROMACS checkpoint file CPT
    type: File?
    outputBinding:
      glob: $(inputs.output_cpt_path)
    format: edam:format_2333

  output_dhdl_path:
    label: Path to the output dhdl.xvg file only used when free energy calculation
      is turned on
    doc: |-
      Path to the output dhdl.xvg file only used when free energy calculation is turned on
    type: File?
    outputBinding:
      glob: $(inputs.output_dhdl_path)
    format: edam:format_2033

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
