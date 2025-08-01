#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper class for the Haddock Topology module.

doc: |-
  The Topology module. Haddock Topology module creates a topology from a system to be used for docking.

baseCommand: topology

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_haddock:5.1.0--pyhdfd78af_0

inputs:
  mol1_input_pdb_path:
    label: Path to the input PDB file
    doc: |-
      Path to the input PDB file
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/data/haddock/e2aP_1F3G.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --mol1_input_pdb_path

  mol1_output_top_zip_path:
    label: Path to the output PDB file collection in zip format
    doc: |-
      Path to the output PDB file collection in zip format
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/reference/haddock/ref_mol1_top.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --mol1_output_top_zip_path
    default: system.zip

  mol2_input_pdb_path:
    label: Path to the input PDB file
    doc: |-
      Path to the input PDB file
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/data/haddock/hpr_ensemble.pdb
    type: File?
    format:
    - edam:format_1476
    inputBinding:
      prefix: --mol2_input_pdb_path

  mol2_output_top_zip_path:
    label: Path to the output PDB file collection in zip format
    doc: |-
      Path to the output PDB file collection in zip format
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_haddock/master/biobb_haddock/test/reference/haddock/ref_mol2_top.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      prefix: --mol2_output_top_zip_path
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
    label: Advanced configuration options for biobb_haddock Topology
    doc: |-
      Advanced configuration options for biobb_haddock Topology. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_haddock Topology documentation: https://biobb-haddock.readthedocs.io/en/latest/haddock.html#module-haddock.topology
    type: string?
    inputBinding:
      prefix: --config

outputs:
  mol1_output_top_zip_path:
    label: Path to the output PDB file collection in zip format
    doc: |-
      Path to the output PDB file collection in zip format
    type: File
    outputBinding:
      glob: $(inputs.mol1_output_top_zip_path)
    format: edam:format_3987

  mol2_output_top_zip_path:
    label: Path to the output PDB file collection in zip format
    doc: |-
      Path to the output PDB file collection in zip format
    type: File?
    outputBinding:
      glob: $(inputs.mol2_output_top_zip_path)
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
