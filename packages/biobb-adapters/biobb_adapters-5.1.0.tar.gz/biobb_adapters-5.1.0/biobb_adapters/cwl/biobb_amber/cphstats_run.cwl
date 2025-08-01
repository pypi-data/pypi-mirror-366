#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper of the AmberTools (AMBER MD Package) cphstats tool module.

doc: |-
  Analyzing the results of constant pH MD simulations using cphstats tool from the AMBER MD package.

baseCommand: cphstats_run

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_amber:5.1.0--pyhdfd78af_0

inputs:
  input_cpin_path:
    label: Input constant pH file (AMBER cpin)
    doc: |-
      Input constant pH file (AMBER cpin)
      Type: string
      File type: input
      Accepted formats: cpin
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/data/cphstats/structure.cpin
    type: File
    format:
    - edam:format_2330
    inputBinding:
      position: 1
      prefix: --input_cpin_path

  input_cpout_path:
    label: Output constant pH file (AMBER cpout)
    doc: |-
      Output constant pH file (AMBER cpout)
      Type: string
      File type: input
      Accepted formats: cpout, zip, gzip
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/data/cphstats/sander.pH.cpout
    type: File
    format:
    - edam:format_2330
    - edam:format_3987
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --input_cpout_path

  output_dat_path:
    label: Output file to which the standard calcpka-type statistics are written
    doc: |-
      Output file to which the standard calcpka-type statistics are written
      Type: string
      File type: output
      Accepted formats: dat, out, txt, o
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/cphstats/cphstats.pH.dat
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
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/cphstats/cphstats.pH.pop.dat
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
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/cphstats/cphstats.pH.dat
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
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/cphstats/cphstats.pH.dat
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
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/cphstats/cphstats.pH.dat
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
      Example file: https://github.com/bioexcel/biobb_amber/raw/master/biobb_amber/test/reference/cphstats/cphstats.pH.dat
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
    label: Advanced configuration options for biobb_amber CphstatsRun
    doc: |-
      Advanced configuration options for biobb_amber CphstatsRun. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_amber CphstatsRun documentation: https://biobb-amber.readthedocs.io/en/latest/cphstats.html#module-cphstats.cphstats_run
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_dat_path:
    label: Output file to which the standard calcpka-type statistics are written
    doc: |-
      Output file to which the standard calcpka-type statistics are written
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
