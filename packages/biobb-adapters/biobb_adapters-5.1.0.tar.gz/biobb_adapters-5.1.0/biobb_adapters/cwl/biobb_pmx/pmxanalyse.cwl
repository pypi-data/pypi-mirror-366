#!/usr/bin/env cwl-runner
cwlVersion: v1.0

class: CommandLineTool

label: Wrapper class for the PMX analyse module.

doc: |-
  Analyze the work values from the dgdl.xvg files of the A and B states to calculate the free energy difference between two states.

baseCommand: pmxanalyse

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/biobb_pmx:5.1.0--pyhdfd78af_0

inputs:
  input_a_xvg_zip_path:
    label: Path the zip file containing the dgdl.xvg files of the A state
    doc: |-
      Path the zip file containing the dgdl.xvg files of the A state
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/data/pmx/xvg_A.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 1
      prefix: --input_a_xvg_zip_path

  input_b_xvg_zip_path:
    label: Path the zip file containing the dgdl.xvg files of the B state
    doc: |-
      Path the zip file containing the dgdl.xvg files of the B state
      Type: string
      File type: input
      Accepted formats: zip
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/data/pmx/xvg_B.zip
    type: File
    format:
    - edam:format_3987
    inputBinding:
      position: 2
      prefix: --input_b_xvg_zip_path

  output_result_path:
    label: Path to the TXT results file
    doc: |-
      Path to the TXT results file
      Type: string
      File type: output
      Accepted formats: txt
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/ref_result.txt
    type: string
    format:
    - edam:format_2330
    inputBinding:
      position: 3
      prefix: --output_result_path
    default: system.txt

  output_work_plot_path:
    label: Path to the PNG plot results file
    doc: |-
      Path to the PNG plot results file
      Type: string
      File type: output
      Accepted formats: png
      Example file: https://github.com/bioexcel/biobb_pmx/raw/master/biobb_pmx/test/reference/pmx/ref_plot.png
    type: string
    format:
    - edam:format_3603
    inputBinding:
      position: 4
      prefix: --output_work_plot_path
    default: system.png

  config:
    label: Advanced configuration options for biobb_pmx Pmxanalyse
    doc: |-
      Advanced configuration options for biobb_pmx Pmxanalyse. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the biobb_pmx Pmxanalyse documentation: https://biobb-pmx.readthedocs.io/en/latest/pmx.html#module-pmx.pmxanalyse
    type: string?
    inputBinding:
      prefix: --config

outputs:
  output_result_path:
    label: Path to the TXT results file
    doc: |-
      Path to the TXT results file
    type: File
    outputBinding:
      glob: $(inputs.output_result_path)
    format: edam:format_2330

  output_work_plot_path:
    label: Path to the PNG plot results file
    doc: |-
      Path to the PNG plot results file
    type: File
    outputBinding:
      glob: $(inputs.output_work_plot_path)
    format: edam:format_3603

$namespaces:
  edam: https://edamontology.org/

$schemas:
- https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl
