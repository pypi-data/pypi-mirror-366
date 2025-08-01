#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper class for the PMX merge_ff module.

doc: |-
  Merge ligand topology files.

baseCommand: pmxmerge_ff

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_pmx:5.1.0--pyhdfd78af_0

inputs:
  input_topology_path:
    label: Path to the input ligand topologies as a zip file containing a list of
      itp files
    doc: |-
      Path to the input ligand topologies as a zip file containing a list of itp files
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/data/pmx/ligand_itps.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 1
      prefix: --input_topology_path

  output_topology_path:
    label: Path to the merged ligand topology file
    doc: |-
      Path to the merged ligand topology file
      Type: string
      File type: output
      Accepted formats: itp
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/data/pmx/ligand.itp
    type: string
    format:
    - edam:format_3883
    inputBinding:
      position: 2
      prefix: --output_topology_path
    default: system.itp

  config:
    label: Advanced configuration options for biobb_pmx Pmxmerge_ff
    doc: |-
      Advanced configuration options for biobb_pmx Pmxmerge_ff. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pmx Pmxmerge_ff documentation: https://biobb-pmx.readthedocs.io/en/latest/pmx.html#module-pmx.pmxmerge_ff
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_topology_path:
    label: Path to the merged ligand topology file
    doc: |-
      Path to the merged ligand topology file
    type: File
    outputBinding:
      glob: $(inputs.output_topology_path)
    format: edam:format_3883

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
