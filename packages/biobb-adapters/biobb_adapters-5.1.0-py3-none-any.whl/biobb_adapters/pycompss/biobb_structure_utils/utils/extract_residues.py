# Python
import os
import sys
import traceback
# Pycompss
from pycompss.api.task import task
from pycompss.api.parameter import FILE_IN, FILE_OUT
# Adapters commons pycompss
from biobb_adapters.pycompss.biobb_commons import task_config
# Wrapped Biobb
from biobb_structure_utils.utils.extract_residues import ExtractResidues  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_structure_path=FILE_IN, output_residues_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _extractresidues(input_structure_path, output_residues_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        ExtractResidues(input_structure_path=input_structure_path, output_residues_path=output_residues_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def extract_residues(input_structure_path, output_residues_path, properties=None, **kwargs):

    if (output_residues_path is None or (os.path.exists(output_residues_path) and os.stat(output_residues_path).st_size > 0)) and \
       True:
        print("WARN: Task ExtractResidues already executed.")
    else:
        _extractresidues( input_structure_path,  output_residues_path,  properties, **kwargs)