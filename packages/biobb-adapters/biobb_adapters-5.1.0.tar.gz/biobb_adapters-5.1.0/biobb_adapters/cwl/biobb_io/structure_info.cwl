#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class is a wrapper for getting all the available information of a structure
  from the Protein Data Bank.

doc: |-
  Wrapper for the MMB PDB mirror for getting all the available information of a structure from the Protein Data Bank.

baseCommand: structure_info

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_io:5.1.0--pyhdfd78af_0

inputs:
  output_json_path:
    label: Path to the output JSON file with all the structure information
    doc: |-
      Path to the output JSON file with all the structure information
      Type: string
      File type: output
      Accepted formats: json
      Example file: https://github.com/bioexcel/biobb_io/raw/master/biobb_io/test/reference/api/ref_str_info.json
    type: string
    format:
    - edam:format_3464
    inputBinding:
      position: 1
      prefix: --output_json_path
    default: system.json

  config:
    label: Advanced configuration options for biobb_io StructureInfo
    doc: |-
      Advanced configuration options for biobb_io StructureInfo. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_io StructureInfo documentation: https://biobb-io.readthedocs.io/en/latest/api.html#module-api.structure_info
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_json_path:
    label: Path to the output JSON file with all the structure information
    doc: |-
      Path to the output JSON file with all the structure information
    type: File
    outputBinding:
      glob: $(inputs.output_json_path)
    format: edam:format_3464

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
