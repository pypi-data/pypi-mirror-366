#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class is a wrapper of the MemProtMD to get all available membrane-protein
  systems from its REST API.

doc: |-
  Wrapper for the MemProtMD DB REST API to get all available membrane-protein systems (simulations).

baseCommand: memprotmd_sim_list

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_io:5.1.0--pyhdfd78af_0

inputs:
  output_simulations:
    label: Path to the output JSON file
    doc: |-
      Path to the output JSON file
      Type: string
      File type: output
      Accepted formats: json
      Example file: https://github.com/bioexcel/biobb_io/raw/master/biobb_io/test/reference/api/output_sim_list.json
    type: string
    format:
    - edam:format_3464
    inputBinding:
      position: 1
      prefix: --output_simulations
    default: system.json

  config:
    label: Advanced configuration options for biobb_io MemProtMDSimList
    doc: |-
      Advanced configuration options for biobb_io MemProtMDSimList. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_io MemProtMDSimList documentation: https://biobb-io.readthedocs.io/en/latest/api.html#module-api.memprotmd_sim_list
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_simulations:
    label: Path to the output JSON file
    doc: |-
      Path to the output JSON file
    type: File
    outputBinding:
      glob: $(inputs.output_simulations)
    format: edam:format_3464

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
