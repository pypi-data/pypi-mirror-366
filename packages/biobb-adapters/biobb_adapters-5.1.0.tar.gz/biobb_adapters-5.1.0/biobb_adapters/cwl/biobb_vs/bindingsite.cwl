#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class finds the binding site of the input_pdb.

doc: |-
  Finds the binding site of the input_pdb_path file based on the ligands' location of similar structures (members of the sequence identity cluster)

baseCommand: bindingsite

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_vs:5.1.0--pyhdfd78af_0

inputs:
  input_pdb_path:
    label: Path to the PDB structure where the binding site is to be found
    doc: |-
      Path to the PDB structure where the binding site is to be found
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/bindingsite.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --input_pdb_path

  input_clusters_zip:
    label: Path to the ZIP file with all the PDB members of the identity cluster
    doc: |-
      Path to the ZIP file with all the PDB members of the identity cluster
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/bindingsite.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --input_clusters_zip

  output_pdb_path:
    label: Path to the PDB containig the residues belonging to the binding site
    doc: |-
      Path to the PDB containig the residues belonging to the binding site
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_output_bindingsite.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      position: 3
      prefix: --output_pdb_path
    default: system.pdb

  config:
    label: Advanced configuration options for biobb_vs BindingSite
    doc: |-
      Advanced configuration options for biobb_vs BindingSite. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_vs BindingSite documentation: https://biobb-vs.readthedocs.io/en/latest/utils.html#module-utils.bindingsite
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_pdb_path:
    label: Path to the PDB containig the residues belonging to the binding site
    doc: |-
      Path to the PDB containig the residues belonging to the binding site
    type: File
    outputBinding:
      glob: $(inputs.output_pdb_path)
    format: edam:format_1476

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
