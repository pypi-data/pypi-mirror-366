#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper class for the PMX ligand_hybrid module.

doc: |-
  Create a hybrid topology and structure based on two ligand structures.

baseCommand: pmxligand_hybrid

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_pmx:5.1.0--pyhdfd78af_0

inputs:
  input_structure1_path:
    label: Path to the input ligand structure file 1
    doc: |-
      Path to the input ligand structure file 1
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/data/pmx/ligand.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 1
      prefix: --input_structure1_path

  input_structure2_path:
    label: Path to the input ligand structure file 2
    doc: |-
      Path to the input ligand structure file 2
      Type: string
      File type: input
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/data/pmx/ligand.pdb
    type: File
    format:
    - edam:format_1476
    inputBinding:
      position: 2
      prefix: --input_structure2_path

  input_topology1_path:
    label: Path to the input ligand topology file 1
    doc: |-
      Path to the input ligand topology file 1
      Type: string
      File type: input
      Accepted formats: itp
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/data/pmx/ligand.itp
    type: File
    format:
    - edam:format_3883
    inputBinding:
      position: 3
      prefix: --input_topology1_path

  input_topology2_path:
    label: Path to the input ligand topology file 2
    doc: |-
      Path to the input ligand topology file 2
      Type: string
      File type: input
      Accepted formats: itp
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/data/pmx/ligand.itp
    type: File
    format:
    - edam:format_3883
    inputBinding:
      position: 4
      prefix: --input_topology2_path

  output_log_path:
    label: Path to the log file
    doc: |-
      Path to the log file
      Type: string
      File type: output
      Accepted formats: log, txt, out
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/atom_mapping.log
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      position: 5
      prefix: --output_log_path
    default: system.log

  output_structure1_path:
    label: Path to the output hybrid structure based on the ligand 1
    doc: |-
      Path to the output hybrid structure based on the ligand 1
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/superimposed_ligand.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      position: 6
      prefix: --output_structure1_path
    default: system.pdb

  output_structure2_path:
    label: Path to the output hybrid structure based on the ligand 2
    doc: |-
      Path to the output hybrid structure based on the ligand 2
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/superimposed_ligand.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      position: 7
      prefix: --output_structure2_path
    default: system.pdb

  output_topology_path:
    label: Path to the output hybrid topology
    doc: |-
      Path to the output hybrid topology
      Type: string
      File type: output
      Accepted formats: itp
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/ligand_hybrid.itp
    type: string
    format:
    - edam:format_3883
    inputBinding:
      position: 8
      prefix: --output_topology_path
    default: system.itp

  output_atomtypes_path:
    label: Path to the atom types for the output hybrid topology
    doc: |-
      Path to the atom types for the output hybrid topology
      Type: string
      File type: output
      Accepted formats: itp
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/ligand_hybrid_atomtypes.itp
    type: string
    format:
    - edam:format_3883
    inputBinding:
      position: 9
      prefix: --output_atomtypes_path
    default: system.itp

  input_pairs_path:
    label: Path to the input atom pair mapping
    doc: |-
      Path to the input atom pair mapping
      Type: string
      File type: input
      Accepted formats: dat, txt
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/ref_mapping_pairs.dat
    type: File?
    format:
    - edam:format_1637
    - edam:format_2330
    inputBinding:
      prefix: --input_pairs_path

  input_scaffold1_path:
    label: Path to the index of atoms to consider for the ligand structure 1
    doc: |-
      Path to the index of atoms to consider for the ligand structure 1
      Type: string
      File type: input
      Accepted formats: ndx
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/atoms_to_consider.ndx
    type: File?
    format:
    - edam:format_2033
    inputBinding:
      prefix: --input_scaffold1_path

  input_scaffold2_path:
    label: Path to the index of atoms to consider for the ligand structure 2
    doc: |-
      Path to the index of atoms to consider for the ligand structure 2
      Type: string
      File type: input
      Accepted formats: ndx
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/atoms_to_consider.ndx
    type: File?
    format:
    - edam:format_2033
    inputBinding:
      prefix: --input_scaffold2_path

  config:
    label: Advanced configuration options for biobb_pmx Pmxligand_hybrid
    doc: |-
      Advanced configuration options for biobb_pmx Pmxligand_hybrid. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pmx Pmxligand_hybrid documentation: https://biobb-pmx.readthedocs.io/en/latest/pmx.html#module-pmx.pmxligand_hybrid
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_log_path:
    label: Path to the log file
    doc: |-
      Path to the log file
    type: File
    outputBinding:
      glob: $(inputs.output_log_path)
    format: edam:format_2330

  output_structure1_path:
    label: Path to the output hybrid structure based on the ligand 1
    doc: |-
      Path to the output hybrid structure based on the ligand 1
    type: File
    outputBinding:
      glob: $(inputs.output_structure1_path)
    format: edam:format_1476

  output_structure2_path:
    label: Path to the output hybrid structure based on the ligand 2
    doc: |-
      Path to the output hybrid structure based on the ligand 2
    type: File
    outputBinding:
      glob: $(inputs.output_structure2_path)
    format: edam:format_1476

  output_topology_path:
    label: Path to the output hybrid topology
    doc: |-
      Path to the output hybrid topology
    type: File
    outputBinding:
      glob: $(inputs.output_topology_path)
    format: edam:format_3883

  output_atomtypes_path:
    label: Path to the atom types for the output hybrid topology
    doc: |-
      Path to the atom types for the output hybrid topology
    type: File
    outputBinding:
      glob: $(inputs.output_atomtypes_path)
    format: edam:format_3883

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
