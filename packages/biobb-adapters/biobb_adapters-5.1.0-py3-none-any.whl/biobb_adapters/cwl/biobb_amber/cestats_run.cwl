#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the AmberTools (AMBER MD Package) cestats tool module.

doc: |-
  Analyzing the results of constant Redox potential MD simulations using cestats tool from the AMBER MD package.

baseCommand: cestats_run

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_amber:5.1.0--pyhdfd78af_0

inputs:
  input_cein_path:
    label: Input cein or cpein file (from pmemd or sander) with titrating residue
      information
    doc: |-
      Input cein or cpein file (from pmemd or sander) with titrating residue information
      Type: string
      File type: input
      Accepted formats: cein, cpein
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/data/cphstats/structure.cein
    type: File
    format:
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_cein_path

  input_ceout_path:
    label: Output ceout file (AMBER ceout)
    doc: |-
      Output ceout file (AMBER ceout)
      Type: string
      File type: input
      Accepted formats: ceout, zip, gzip, gz
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/data/cphstats/sander.ceout.gz
    type: File
    format:
    - edam:format_2330
    - edam:format_3987
    - edam:format_3987
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --input_ceout_path

  output_dat_path:
    label: Output file to which the standard calceo-type statistics are written
    doc: |-
      Output file to which the standard calceo-type statistics are written
      Type: string
      File type: output
      Accepted formats: dat, out, txt, o
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/cphstats/cestats.dat
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      position: 3
      prefix: --output_dat_path
    default: system.dat

  output_population_path:
    label: Output file where protonation state populations are printed for every state
      of every residue
    doc: |-
      Output file where protonation state populations are printed for every state of every residue
      Type: string
      File type: output
      Accepted formats: dat, out, txt, o
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/cphstats/cestats.dat
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      prefix: --output_population_path
    default: system.dat

  output_chunk_path:
    label: Output file where the time series data calculated over chunks of the simulation
      are printed
    doc: |-
      Output file where the time series data calculated over chunks of the simulation are printed
      Type: string
      File type: output
      Accepted formats: dat, out, txt, o
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/cphstats/cestats.dat
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      prefix: --output_chunk_path
    default: system.dat

  output_cumulative_path:
    label: Output file where the cumulative time series data is printed
    doc: |-
      Output file where the cumulative time series data is printed
      Type: string
      File type: output
      Accepted formats: dat, out, txt, o
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/cphstats/cestats.dat
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      prefix: --output_cumulative_path
    default: system.dat

  output_conditional_path:
    label: Output file with requested conditional probabilities
    doc: |-
      Output file with requested conditional probabilities
      Type: string
      File type: output
      Accepted formats: dat, out, txt, o
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/cphstats/cestats.dat
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      prefix: --output_conditional_path
    default: system.dat

  output_chunk_conditional_path:
    label: Output file with a time series of the conditional probabilities over a
      trajectory split up into chunks
    doc: |-
      Output file with a time series of the conditional probabilities over a trajectory split up into chunks
      Type: string
      File type: output
      Accepted formats: dat, out, txt, o
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/cphstats/cestats.dat
    type: string
    format:
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    - edam:format_2330
    inputBinding:
      prefix: --output_chunk_conditional_path
    default: system.dat

  config:
    label: Advanced configuration options for biobb_amber CestatsRun
    doc: |-
      Advanced configuration options for biobb_amber CestatsRun. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_amber CestatsRun documentation: https://biobb-amber.readthedocs.io/en/latest/cphstats.html#module-cphstats.cestats_run
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_dat_path:
    label: Output file to which the standard calceo-type statistics are written
    doc: |-
      Output file to which the standard calceo-type statistics are written
    type: File
    outputBinding:
      glob: $(inputs.output_dat_path)
    format: edam:format_2330

  output_population_path:
    label: Output file where protonation state populations are printed for every state
      of every residue
    doc: |-
      Output file where protonation state populations are printed for every state of every residue
    type: File?
    outputBinding:
      glob: $(inputs.output_population_path)
    format: edam:format_2330

  output_chunk_path:
    label: Output file where the time series data calculated over chunks of the simulation
      are printed
    doc: |-
      Output file where the time series data calculated over chunks of the simulation are printed
    type: File?
    outputBinding:
      glob: $(inputs.output_chunk_path)
    format: edam:format_2330

  output_cumulative_path:
    label: Output file where the cumulative time series data is printed
    doc: |-
      Output file where the cumulative time series data is printed
    type: File?
    outputBinding:
      glob: $(inputs.output_cumulative_path)
    format: edam:format_2330

  output_conditional_path:
    label: Output file with requested conditional probabilities
    doc: |-
      Output file with requested conditional probabilities
    type: File?
    outputBinding:
      glob: $(inputs.output_conditional_path)
    format: edam:format_2330

  output_chunk_conditional_path:
    label: Output file with a time series of the conditional probabilities over a
      trajectory split up into chunks
    doc: |-
      Output file with a time series of the conditional probabilities over a trajectory split up into chunks
    type: File?
    outputBinding:
      glob: $(inputs.output_chunk_conditional_path)
    format: edam:format_2330

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
