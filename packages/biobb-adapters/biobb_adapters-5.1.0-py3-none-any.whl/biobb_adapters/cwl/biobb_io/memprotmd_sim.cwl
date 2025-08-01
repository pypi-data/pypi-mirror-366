#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class is a wrapper of the MemProtMD to download a simulation using its
  REST API.

doc: |-
  Wrapper for the MemProtMD DB REST API to download a simulation.

baseCommand: memprotmd_sim

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_io:5.1.0--pyhdfd78af_0

inputs:
  output_simulation:
    label: Path to the output simulation in a ZIP file
    doc: |-
      Path to the output simulation in a ZIP file
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_io/raw/master/biobb_io/test/reference/api/output_sim.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 1
      prefix: --output_simulation
    default: system.zip

  config:
    label: Advanced configuration options for biobb_io MemProtMDSim
    doc: |-
      Advanced configuration options for biobb_io MemProtMDSim. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_io MemProtMDSim documentation: https://biobb-io.readthedocs.io/en/latest/api.html#module-api.memprotmd_sim
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_simulation:
    label: Path to the output simulation in a ZIP file
    doc: |-
      Path to the output simulation in a ZIP file
    type: File
    outputBinding:
      glob: $(inputs.output_simulation)
    format: edam:format_3987

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
