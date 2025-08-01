#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper class for the PMX atom_mapping module.

doc: |-
  Perform atom mapping between two ligand structures.

baseCommand: pmxatom_mapping

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

  output_pairs1_path:
    label: Path to the output pairs for the ligand structure 1
    doc: |-
      Path to the output pairs for the ligand structure 1
      Type: string
      File type: output
      Accepted formats: dat, txt
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/ref_mapping_pairs.dat
    type: string
    format:
    - edam:format_1637
    - edam:format_2330
    inputBinding:
      position: 3
      prefix: --output_pairs1_path
    default: system.dat

  output_pairs2_path:
    label: Path to the output pairs for the ligand structure 2
    doc: |-
      Path to the output pairs for the ligand structure 2
      Type: string
      File type: output
      Accepted formats: dat, txt
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/ref_mapping_pairs.dat
    type: string
    format:
    - edam:format_1637
    - edam:format_2330
    inputBinding:
      position: 4
      prefix: --output_pairs2_path
    default: system.dat

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
    label: Path to the superimposed structure for the ligand structure 1
    doc: |-
      Path to the superimposed structure for the ligand structure 1
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/superimposed_ligand.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      prefix: --output_structure1_path
    default: system.pdb

  output_structure2_path:
    label: Path to the superimposed structure for the ligand structure 2
    doc: |-
      Path to the superimposed structure for the ligand structure 2
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/superimposed_ligand.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      prefix: --output_structure2_path
    default: system.pdb

  output_morph1_path:
    label: Path to the morphable atoms for the ligand structure 1
    doc: |-
      Path to the morphable atoms for the ligand structure 1
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/superimposed_ligand.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      prefix: --output_morph1_path
    default: system.pdb

  output_morph2_path:
    label: Path to the morphable atoms for the ligand structure 2
    doc: |-
      Path to the morphable atoms for the ligand structure 2
      Type: string
      File type: output
      Accepted formats: pdb
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/superimposed_ligand.pdb
    type: string
    format:
    - edam:format_1476
    inputBinding:
      prefix: --output_morph2_path
    default: system.pdb

  output_scaffold1_path:
    label: Path to the index of atoms to consider for the ligand structure 1
    doc: |-
      Path to the index of atoms to consider for the ligand structure 1
      Type: string
      File type: output
      Accepted formats: ndx
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/atoms_to_consider.ndx
    type: string
    format:
    - edam:format_2033
    inputBinding:
      prefix: --output_scaffold1_path
    default: system.ndx

  output_scaffold2_path:
    label: Path to the index of atoms to consider for the ligand structure 2
    doc: |-
      Path to the index of atoms to consider for the ligand structure 2
      Type: string
      File type: output
      Accepted formats: ndx
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/atoms_to_consider.ndx
    type: string
    format:
    - edam:format_2033
    inputBinding:
      prefix: --output_scaffold2_path
    default: system.ndx

  output_score_path:
    label: Path to the morphing score
    doc: |-
      Path to the morphing score
      Type: string
      File type: output
      Accepted formats: dat, txt
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/morph_score.dat
    type: string
    format:
    - edam:format_1637
    - edam:format_2330
    inputBinding:
      prefix: --output_score_path
    default: system.dat

  config:
    label: Advanced configuration options for biobb_pmx Pmxatom_mapping
    doc: |-
      Advanced configuration options for biobb_pmx Pmxatom_mapping. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pmx Pmxatom_mapping documentation: https://biobb-pmx.readthedocs.io/en/latest/pmx.html#module-pmx.pmxatom_mapping
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_pairs1_path:
    label: Path to the output pairs for the ligand structure 1
    doc: |-
      Path to the output pairs for the ligand structure 1
    type: File
    outputBinding:
      glob: $(inputs.output_pairs1_path)
    format: edam:format_1637

  output_pairs2_path:
    label: Path to the output pairs for the ligand structure 2
    doc: |-
      Path to the output pairs for the ligand structure 2
    type: File
    outputBinding:
      glob: $(inputs.output_pairs2_path)
    format: edam:format_1637

  output_log_path:
    label: Path to the log file
    doc: |-
      Path to the log file
    type: File
    outputBinding:
      glob: $(inputs.output_log_path)
    format: edam:format_2330

  output_structure1_path:
    label: Path to the superimposed structure for the ligand structure 1
    doc: |-
      Path to the superimposed structure for the ligand structure 1
    type: File?
    outputBinding:
      glob: $(inputs.output_structure1_path)
    format: edam:format_1476

  output_structure2_path:
    label: Path to the superimposed structure for the ligand structure 2
    doc: |-
      Path to the superimposed structure for the ligand structure 2
    type: File?
    outputBinding:
      glob: $(inputs.output_structure2_path)
    format: edam:format_1476

  output_morph1_path:
    label: Path to the morphable atoms for the ligand structure 1
    doc: |-
      Path to the morphable atoms for the ligand structure 1
    type: File?
    outputBinding:
      glob: $(inputs.output_morph1_path)
    format: edam:format_1476

  output_morph2_path:
    label: Path to the morphable atoms for the ligand structure 2
    doc: |-
      Path to the morphable atoms for the ligand structure 2
    type: File?
    outputBinding:
      glob: $(inputs.output_morph2_path)
    format: edam:format_1476

  output_scaffold1_path:
    label: Path to the index of atoms to consider for the ligand structure 1
    doc: |-
      Path to the index of atoms to consider for the ligand structure 1
    type: File?
    outputBinding:
      glob: $(inputs.output_scaffold1_path)
    format: edam:format_2033

  output_scaffold2_path:
    label: Path to the index of atoms to consider for the ligand structure 2
    doc: |-
      Path to the index of atoms to consider for the ligand structure 2
    type: File?
    outputBinding:
      glob: $(inputs.output_scaffold2_path)
    format: edam:format_2033

  output_score_path:
    label: Path to the morphing score
    doc: |-
      Path to the morphing score
    type: File?
    outputBinding:
      glob: $(inputs.output_score_path)
    format: edam:format_1637

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
