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
from biobb_structure_utils.utils.extract_protein import ExtractProtein  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_structure_path=FILE_IN, output_protein_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _extractprotein(input_structure_path, output_protein_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        ExtractProtein(input_structure_path=input_structure_path, output_protein_path=output_protein_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def extractprotein(input_structure_path, output_protein_path, properties=None, **kwargs):

    if (output_protein_path is None or os.path.exists(output_protein_path)) and \
       True:
        print("WARN: Task ExtractProtein already executed.")
    else:
        _extractprotein( input_structure_path,  output_protein_path,  properties, **kwargs)