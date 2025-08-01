#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper class for the PMX gentop module.

doc: |-
  Generate a topology file for a morphing simulation.

baseCommand: pmxgentop

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_pmx:5.1.0--pyhdfd78af_0

inputs:
  input_top_zip_path:
    label: Path the input GROMACS topology TOP and ITP files in zip format
    doc: |-
      Path the input GROMACS topology TOP and ITP files in zip format
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/data/pmx/topology.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 1
      prefix: --input_top_zip_path

  output_top_zip_path:
    label: Path the output TOP topology in zip format
    doc: |-
      Path the output TOP topology in zip format
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/ref_output_topology.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --output_top_zip_path
    default: system.zip

  config:
    label: Advanced configuration options for biobb_pmx Pmxgentop
    doc: |-
      Advanced configuration options for biobb_pmx Pmxgentop. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pmx Pmxgentop documentation: https://biobb-pmx.readthedocs.io/en/latest/pmx.html#module-pmx.pmxgentop
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_top_zip_path:
    label: Path the output TOP topology in zip format
    doc: |-
      Path the output TOP topology in zip format
    type: File
    outputBinding:
      glob: $(inputs.output_top_zip_path)
    format: edam:format_3987

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
