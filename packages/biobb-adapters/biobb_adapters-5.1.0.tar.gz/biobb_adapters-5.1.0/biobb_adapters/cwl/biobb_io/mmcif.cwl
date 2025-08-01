#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class is a wrapper for downloading a MMCIF structure from the Protein
  Data Bank.

doc: |-
  Wrapper for the Protein Data Bank in Europe, the Protein Data Bank and the MMB PDB mirror for downloading a single MMCIF structure.

baseCommand: mmcif

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_io:5.1.0--pyhdfd78af_0

inputs:
  output_mmcif_path:
    label: Path to the output MMCIF file
    doc: |-
      Path to the output MMCIF file
      Type: string
      File type: output
      Accepted formats: cif, mmcif
      Example file: https://github.com/bioexcel/biobb_io/raw/master/biobb_io/test/reference/api/ref_output.mmcif
    type: string
    format:
    - edam:format_1477
    - edam:format_1477
    inputBinding:
      position: 1
      prefix: --output_mmcif_path
    default: system.cif

  config:
    label: Advanced configuration options for biobb_io Mmcif
    doc: |-
      Advanced configuration options for biobb_io Mmcif. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_io Mmcif documentation: https://biobb-io.readthedocs.io/en/latest/api.html#module-api.mmcif
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_mmcif_path:
    label: Path to the output MMCIF file
    doc: |-
      Path to the output MMCIF file
    type: File
    outputBinding:
      glob: $(inputs.output_mmcif_path)
    format: edam:format_1477

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
