#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class sets the center and the size of a rectangular parallelepiped box
  around a set of residues.

doc: |-
  Sets the center and the size of a rectangular parallelepiped box around a selection of residues found in a given PDB. The residue identifiers that compose the selection (i.e. binding site) are provided by a property list.

baseCommand: box_residues

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_vs:5.1.0--pyhdfd78af_0

inputs:
  input_pdb_path:
    label: PDB protein structure for which the box will be build. Its size and center
      will be set around the 'resid_list' property once mapped against this PDB
    doc: |-
      PDB protein structure for which the box will be build. Its size and center will be set around the 'resid_list' property once mapped against this PDB
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/input_box_residues.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --input_pdb_path

  output_pdb_path:
    label: PDB including the annotation of the box center and size as REMARKs
    doc: |-
      PDB including the annotation of the box center and size as REMARKs
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_output_box_residues.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      position: 2
      prefix: --output_pdb_path
    default: system.pdb

  config:
    label: Advanced configuration options for biobb_vs BoxResidues
    doc: |-
      Advanced configuration options for biobb_vs BoxResidues. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_vs BoxResidues documentation: https://biobb-vs.readthedocs.io/en/latest/utils.html#module-utils.box_residues
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_pdb_path:
    label: PDB including the annotation of the box center and size as REMARKs
    doc: |-
      PDB including the annotation of the box center and size as REMARKs
    type: File
    outputBinding:
      glob: $(inputs.output_pdb_path)
    format: edam:format_1476

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
