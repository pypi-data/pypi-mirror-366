#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper class for the Haddock RigidBody module.

doc: |-
  The RigidBody module. Haddock RigidBody module compute rigid body docking between two molecules.

baseCommand: rigid_body

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
      Example file: https://github.com/bioexcel/biobb_haddock/raw/master/biobb_haddock/test/data/haddock/haddock_wf_data_topology.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 1
      prefix: --input_haddock_wf_data_zip

  docking_output_zip_path:
    label: Path to the output PDB file collection in zip format
    doc: |-
      Path to the output PDB file collection in zip format
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/reference/haddock/ref_rigidbody.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --docking_output_zip_path
    default: system.zip

  ambig_restraints_table_path:
    label: Path to the input TBL file containing a list of ambiguous restraints for
      docking
    doc: |-
      Path to the input TBL file containing a list of ambiguous restraints for docking
      Type: string
      File type: input
      Accepted formats: tbl
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/data/haddock/e2a-hpr_air.tbl
    type: File?
    format:
    - edam:format_2330
    inputBinding:
      prefix: --ambig_restraints_table_path

  unambig_restraints_table_path:
    label: Path to the input TBL file containing a list of unambiguous restraints
      for docking
    doc: |-
      Path to the input TBL file containing a list of unambiguous restraints for docking
      Type: string
      File type: input
      Accepted formats: tbl
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/data/haddock/e2a-hpr_air.tbl
    type: File?
    format:
    - edam:format_2330
    inputBinding:
      prefix: --unambig_restraints_table_path

  hb_restraints_table_path:
    label: Path to the input TBL file containing a list of hydrogen bond restraints
      for docking
    doc: |-
      Path to the input TBL file containing a list of hydrogen bond restraints for docking
      Type: string
      File type: input
      Accepted formats: tbl
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/data/haddock/e2a-hpr_air.tbl
    type: File?
    format:
    - edam:format_2330
    inputBinding:
      prefix: --hb_restraints_table_path

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
    label: Advanced configuration options for biobb_haddock RigidBody
    doc: |-
      Advanced configuration options for biobb_haddock RigidBody. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_haddock RigidBody documentation: https://biobb-haddock.readthedocs.io/en/latest/haddock.html#module-haddock.rigid_body
    type: string?
    inputBinding:
      prefix: --config

outputs:
  docking_output_zip_path:
    label: Path to the output PDB file collection in zip format
    doc: |-
      Path to the output PDB file collection in zip format
    type: File
    outputBinding:
      glob: $(inputs.docking_output_zip_path)
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
