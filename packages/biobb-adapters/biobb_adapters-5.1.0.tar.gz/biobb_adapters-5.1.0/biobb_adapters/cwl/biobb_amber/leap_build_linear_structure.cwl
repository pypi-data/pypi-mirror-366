#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the AmberTools (AMBER MD Package) leap tool module.

doc: |-
  Builds a linear (unfolded) 3D structure from an AA sequence using tLeap tool from the AmberTools MD package.

baseCommand: leap_build_linear_structure

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_amber:5.1.0--pyhdfd78af_0

inputs:
  output_pdb_path:
    label: Linear (unfolded) 3D structure PDB file
    doc: |-
      Linear (unfolded) 3D structure PDB file
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/leap/structure.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --output_pdb_path
    default: system.pdb

  config:
    label: Advanced configuration options for biobb_amber.leap.leap_build_linear_structure
      LeapBuildLinearStructure
    doc: |-
      Advanced configuration options for biobb_amber.leap.leap_build_linear_structure LeapBuildLinearStructure. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_amber.leap.leap_build_linear_structure LeapBuildLinearStructure documentation: https://biobb-amber.readthedocs.io/en/latest/leap.html#module-leap.leap_build_linear_structure
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_pdb_path:
    label: Linear (unfolded) 3D structure PDB file
    doc: |-
      Linear (unfolded) 3D structure PDB file
    type: File
    outputBinding:
      glob: $(inputs.output_pdb_path)
    format: edam:format_1476

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
