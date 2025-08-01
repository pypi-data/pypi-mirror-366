#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: This class is a wrapper for downloading a FASTA structure from the Protein
  Data Bank.

doc: |-
  Wrapper for the Protein Data Bank and the MMB PDB mirror for downloading a single FASTA structure.

baseCommand: canonical_fasta

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_io:5.1.0--pyhdfd78af_0

inputs:
  output_fasta_path:
    label: Path to the canonical FASTA file
    doc: |-
      Path to the canonical FASTA file
      Type: string
      File type: output
      Accepted formats: fasta
      Example file: https://github.com/bioexcel/biobb_io/raw/master/biobb_io/test/reference/api/canonical_fasta.fasta
    type: string
    format:
    - edam:format_1929
    inputBinding:
      position: 1
      prefix: --output_fasta_path
    default: system.fasta

  config:
    label: Advanced configuration options for biobb_io CanonicalFasta
    doc: |-
      Advanced configuration options for biobb_io CanonicalFasta. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_io CanonicalFasta documentation: https://biobb-io.readthedocs.io/en/latest/api.html#module-api.canonical_fasta
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_fasta_path:
    label: Path to the canonical FASTA file
    doc: |-
      Path to the canonical FASTA file
    type: File
    outputBinding:
      glob: $(inputs.output_fasta_path)
    format: edam:format_1929

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
