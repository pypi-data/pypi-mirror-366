#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class is a wrapper for downloading a trajectory / topology pair from the
  MDDB Database.

doc: |-
  Wrapper for the MDDB Database for downloading a trajectory and its corresponding topology.

baseCommand: mddb

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_io:5.1.0--pyhdfd78af_0

inputs:
  output_top_path:
    label: Path to the output toplogy file
    doc: |-
      Path to the output toplogy file
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_io/raw/master/biobb_io/test/reference/api/output_mddb.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --output_top_path
    default: system.pdb

  output_trj_path:
    label: Path to the output trajectory file
    doc: |-
      Path to the output trajectory file
      Type: string
      File type: output
      Accepted formats: mdcrd, trr, xtc
      Example file: https://github.com/bioexcel/biobb_io/raw/master/biobb_io/test/reference/api/output_mddb.xtc
    type: string
    format:
    - edam:format_3878
    - edam:format_3910
    - edam:format_3875
    inputBinding:
      position: 2
      prefix: --output_trj_path
    default: system.mdcrd

  config:
    label: Advanced configuration options for biobb_io MDDB
    doc: |-
      Advanced configuration options for biobb_io MDDB. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_io MDDB documentation: https://biobb-io.readthedocs.io/en/latest/api.html#module-api.mddb
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_top_path:
    label: Path to the output toplogy file
    doc: |-
      Path to the output toplogy file
    type: File
    outputBinding:
      glob: $(inputs.output_top_path)
    format: edam:format_1476

  output_trj_path:
    label: Path to the output trajectory file
    doc: |-
      Path to the output trajectory file
    type: File
    outputBinding:
      glob: $(inputs.output_trj_path)
    format: edam:format_3878

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
