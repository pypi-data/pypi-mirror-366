#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class is a wrapper for downloading an ideal SDF ligand from the Protein
  Data Bank.

doc: |-
  Wrapper for the Protein Data Bank in Europe and the Protein Data Bank for downloading a single ideal SDF ligand.

baseCommand: ideal_sdf

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_io:5.1.0--pyhdfd78af_0

inputs:
  output_sdf_path:
    label: Path to the output SDF file
    doc: |-
      Path to the output SDF file
      Type: string
      File type: output
      Accepted formats: sdf
      Example file: https://github.com/bioexcel/biobb_io/raw/master/biobb_io/test/reference/api/ref_output.sdf
    type: string
    format:
    - edam:format_3814
    inputBinding:
      position: 1
      prefix: --output_sdf_path
    default: system.sdf

  config:
    label: Advanced configuration options for biobb_io IdealSdf
    doc: |-
      Advanced configuration options for biobb_io IdealSdf. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_io IdealSdf documentation: https://biobb-io.readthedocs.io/en/latest/api.html#module-api.ideal_sdf
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_sdf_path:
    label: Path to the output SDF file
    doc: |-
      Path to the output SDF file
    type: File
    outputBinding:
      glob: $(inputs.output_sdf_path)
    format: edam:format_3814

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
