#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper for the Canion executable  that is part of the Curves+ software suite.

doc: |-
  Analyzes the trajectory of ions around a DNA molecule.

baseCommand: biobb_canion

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_dna:5.1.0--pyhdfd78af_0

inputs:
  input_cdi_path:
    label: Trajectory input file
    doc: |-
      Trajectory input file
      Type: string
      File type: input
      Accepted formats: cdi
      Example file: https://mmb.irbbarcelona.org/biobb-dev/biobb-api/public/samples/THGA_K.cdi
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_cdi_path

  input_afr_path:
    label: Helical axis frames corresponding to the input conformation to be analyzed
    doc: |-
      Helical axis frames corresponding to the input conformation to be analyzed
      Type: string
      File type: input
      Accepted formats: afr
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/curvesplus/THGA.afr
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --input_afr_path

  input_avg_struc_path:
    label: Average DNA conformation
    doc: |-
      Average DNA conformation
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/curvesplus/THGA_avg.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 3
      prefix: --input_avg_struc_path

  output_zip_path:
    label: Filename for .zip files containing Canion output files
    doc: |-
      Filename for .zip files containing Canion output files
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/curvesplus/canion_output.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 4
      prefix: --output_zip_path
    default: system.zip

  config:
    label: Advanced configuration options for biobb_dna Canion
    doc: |-
      Advanced configuration options for biobb_dna Canion. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna Canion documentation: https://biobb-dna.readthedocs.io/en/latest/curvesplus.html#module-curvesplus.biobb_canion
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_zip_path:
    label: Filename for .zip files containing Canion output files
    doc: |-
      Filename for .zip files containing Canion output files
    type: File
    outputBinding:
      glob: $(inputs.output_zip_path)
    format: edam:format_3987

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
