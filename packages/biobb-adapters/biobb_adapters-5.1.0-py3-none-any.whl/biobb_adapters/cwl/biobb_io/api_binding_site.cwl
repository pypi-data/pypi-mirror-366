#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class is a wrapper for the PDBe REST API Binding Sites endpoint.

doc: |-
  This call provides details on binding sites in the entry as per STRUCT_SITE records in PDB files, such as ligand, residues in the site, description of the site, etc.

baseCommand: api_binding_site

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_io:5.1.0--pyhdfd78af_0

inputs:
  output_json_path:
    label: Path to the JSON file with the binding sites for the requested structure
    doc: |-
      Path to the JSON file with the binding sites for the requested structure
      Type: string
      File type: output
      Accepted formats: json
      Example file: https://github.com/bioexcel/biobb_io/raw/master/biobb_io/test/reference/api/output_binding_site.json
    type: string
    format:
    - edam:format_3464
    inputBinding:
      position: 1
      prefix: --output_json_path
    default: system.json

  config:
    label: Advanced configuration options for biobb_io ApiBindingSite
    doc: |-
      Advanced configuration options for biobb_io ApiBindingSite. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_io ApiBindingSite documentation: https://biobb-io.readthedocs.io/en/latest/api.html#module-api.api_binding_site
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_json_path:
    label: Path to the JSON file with the binding sites for the requested structure
    doc: |-
      Path to the JSON file with the binding sites for the requested structure
    type: File
    outputBinding:
      glob: $(inputs.output_json_path)
    format: edam:format_3464

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
