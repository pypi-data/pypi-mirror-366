#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the AmberTools (AMBER MD Package) nab tool module.

doc: |-
  Builds a 3D structure from a DNA sequence using nab (Nucleic Acid Builder) tool from the AmberTools MD package.

baseCommand: nab_build_dna_structure

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_amber:5.0.2--pyhdfd78af_0

inputs:
  output_pdb_path:
    label: DNA 3D structure PDB file
    doc: |-
      DNA 3D structure PDB file
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/nab/ref_nab_build_dna_structure.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --output_pdb_path
    default: system.pdb

  config:
    label: Advanced configuration options for biobb_amber.nab.nab_build_dna_structure
      NabBuildDNAStructure
    doc: |-
      Advanced configuration options for biobb_amber.nab.nab_build_dna_structure NabBuildDNAStructure. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_amber.nab.nab_build_dna_structure NabBuildDNAStructure documentation: https://biobb-amber.readthedocs.io/en/latest/nab.html#module-nab.nab_build_dna_structure
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_pdb_path:
    label: DNA 3D structure PDB file
    doc: |-
      DNA 3D structure PDB file
    type: File
    outputBinding:
      glob: $(inputs.output_pdb_path)
    format: edam:format_1476

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
