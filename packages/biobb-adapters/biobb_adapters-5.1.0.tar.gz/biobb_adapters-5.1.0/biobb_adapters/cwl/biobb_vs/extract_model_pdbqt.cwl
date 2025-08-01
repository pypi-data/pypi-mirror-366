#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Extracts a model from a PDBQT file with several models.

doc: |-
  Extracts a model from a PDBQT file with several models. The model number to extract is defined by the user.

baseCommand: extract_model_pdbqt

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_vs:5.1.0--pyhdfd78af_0

inputs:
  input_pdbqt_path:
    label: Input PDBQT file
    doc: |-
      Input PDBQT file
      Type: string
      File type: input
      Accepted formats: pdbqt
      Example file: https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/models.pdbqt
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --input_pdbqt_path

  output_pdbqt_path:
    label: Output PDBQT file
    doc: |-
      Output PDBQT file
      Type: string
      File type: output
      Accepted formats: pdbqt
      Example file: https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_extract_model.pdbqt
    type: string
    format:
    - edam:format_1476
    inputBinding:
      position: 2
      prefix: --output_pdbqt_path
    default: system.pdbqt

  config:
    label: Advanced configuration options for biobb_vs ExtractModelPDBQT
    doc: |-
      Advanced configuration options for biobb_vs ExtractModelPDBQT. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_vs ExtractModelPDBQT documentation: https://biobb-vs.readthedocs.io/en/latest/utils.html#module-utils.extract_model_pdbqt
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_pdbqt_path:
    label: Output PDBQT file
    doc: |-
      Output PDBQT file
    type: File
    outputBinding:
      glob: $(inputs.output_pdbqt_path)
    format: edam:format_1476

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
