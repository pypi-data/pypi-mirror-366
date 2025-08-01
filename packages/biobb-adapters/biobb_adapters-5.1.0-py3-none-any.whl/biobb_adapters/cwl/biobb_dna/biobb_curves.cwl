#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper for the Cur+ executable  that is part of the Curves+ software suite.

doc: |-
  The Cur+ program is used to analyze the structure of nucleic acids and their complexes.

baseCommand: biobb_curves

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_dna:5.1.0--pyhdfd78af_0

inputs:
  input_struc_path:
    label: Trajectory or PDB input file
    doc: |-
      Trajectory or PDB input file
      Type: string
      File type: input
      Accepted formats: trj, pdb, netcdf, nc
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/curvesplus/structure.stripped.trj
    type: File
    format:
    - edam:format_3910
    - edam:format_1476
    - edam:format_3650
    - edam:format_3650
    inputBinding:
      position: 1
      prefix: --input_struc_path

  output_cda_path:
    label: Filename for Curves+ output .cda file
    doc: |-
      Filename for Curves+ output .cda file
      Type: string
      File type: output
      Accepted formats: cda
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/curvesplus/curves_trj_output.cda
    type: string
    format:
    - edam:format_2330
    inputBinding:
      position: 2
      prefix: --output_cda_path
    default: system.cda

  output_lis_path:
    label: Filename for Curves+ output .lis file
    doc: |-
      Filename for Curves+ output .lis file
      Type: string
      File type: output
      Accepted formats: lis
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/curvesplus/curves_trj_output.lis
    type: string
    format:
    - edam:format_2330
    inputBinding:
      position: 3
      prefix: --output_lis_path
    default: system.lis

  input_top_path:
    label: Topology file, needed along with .trj file (optional)
    doc: |-
      Topology file, needed along with .trj file (optional)
      Type: string
      File type: input
      Accepted formats: top, pdb
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/data/curvesplus/structure.stripped.top
    type: File?
    format:
    - edam:format_3881
    - edam:format_1476
    inputBinding:
      prefix: --input_top_path

  output_zip_path:
    label: Filename for .zip files containing Curves+ output that is not .cda or .lis
      files
    doc: |-
      Filename for .zip files containing Curves+ output that is not .cda or .lis files
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://raw.githubusercontent.com/bioexcel/biobb_dna/master/biobb_dna/test/reference/curvesplus/curves_trj_output.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      prefix: --output_zip_path
    default: system.zip

  config:
    label: Advanced configuration options for biobb_dna Curves
    doc: |-
      Advanced configuration options for biobb_dna Curves. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_dna Curves documentation: https://biobb-dna.readthedocs.io/en/latest/curvesplus.html#module-curvesplus.biobb_curves
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_cda_path:
    label: Filename for Curves+ output .cda file
    doc: |-
      Filename for Curves+ output .cda file
    type: File
    outputBinding:
      glob: $(inputs.output_cda_path)
    format: edam:format_2330

  output_lis_path:
    label: Filename for Curves+ output .lis file
    doc: |-
      Filename for Curves+ output .lis file
    type: File
    outputBinding:
      glob: $(inputs.output_lis_path)
    format: edam:format_2330

  output_zip_path:
    label: Filename for .zip files containing Curves+ output that is not .cda or .lis
      files
    doc: |-
      Filename for .zip files containing Curves+ output that is not .cda or .lis files
    type: File?
    outputBinding:
      glob: $(inputs.output_zip_path)
    format: edam:format_3987

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
