#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class creates a text file containing a list of all the variants mapped
  to a PDB code from the corresponding UNIPROT entries.

doc: |-
  Wrapper for the UNIPROT mirror of the MMB group REST API for creating a list of all the variants mapped to a PDB code from the corresponding UNIPROT entries.

baseCommand: pdb_variants

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_io:5.1.0--pyhdfd78af_0

inputs:
  output_mutations_list_txt:
    label: Path to the TXT file containing an ASCII comma separated values of the
      mutations
    doc: |-
      Path to the TXT file containing an ASCII comma separated values of the mutations
      Type: string
      File type: output
      Accepted formats: txt
      Example file: https://github.com/bioexcel/biobb_io/raw/master/biobb_io/test/reference/api/output_pdb_variants.txt
    type: string
    format:
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --output_mutations_list_txt
    default: system.txt

  config:
    label: Advanced configuration options for biobb_io PdbVariants
    doc: |-
      Advanced configuration options for biobb_io PdbVariants. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_io PdbVariants documentation: https://biobb-io.readthedocs.io/en/latest/api.html#module-api.pdb_variants
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_mutations_list_txt:
    label: Path to the TXT file containing an ASCII comma separated values of the
      mutations
    doc: |-
      Path to the TXT file containing an ASCII comma separated values of the mutations
    type: File
    outputBinding:
      glob: $(inputs.output_mutations_list_txt)
    format: edam:format_2330

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
