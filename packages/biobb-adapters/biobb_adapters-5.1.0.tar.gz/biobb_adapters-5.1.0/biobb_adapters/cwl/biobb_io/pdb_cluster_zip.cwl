#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class is a wrapper for downloading a PDB cluster from the Protein Data
  Bank.

doc: |-
  Wrapper for the Protein Data Bank in Europe, the Protein Data Bank and the MMB PDB mirror for downloading a PDB cluster.

baseCommand: pdb_cluster_zip

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_io:5.1.0--pyhdfd78af_0

inputs:
  output_pdb_zip_path:
    label: Path to the ZIP file containing the output PDB files
    doc: |-
      Path to the ZIP file containing the output PDB files
      Type: string
      File type: output
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_io/raw/master/biobb_io/test/reference/api/output_pdb_cluster.zip
    type: string
    format:
    - edam:format_3987
    inputBinding:
      position: 1
      prefix: --output_pdb_zip_path
    default: system.zip

  config:
    label: Advanced configuration options for biobb_io PdbClusterZip
    doc: |-
      Advanced configuration options for biobb_io PdbClusterZip. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_io PdbClusterZip documentation: https://biobb-io.readthedocs.io/en/latest/api.html#module-api.pdb_cluster_zip
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_pdb_zip_path:
    label: Path to the ZIP file containing the output PDB files
    doc: |-
      Path to the ZIP file containing the output PDB files
    type: File
    outputBinding:
      glob: $(inputs.output_pdb_zip_path)
    format: edam:format_3987

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
