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
from biobb_vs.utils.extract_model_pdbqt import ExtractModelPDBQT  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_pdbqt_path=FILE_IN, output_pdbqt_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _extractmodelpdbqt(input_pdbqt_path, output_pdbqt_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        ExtractModelPDBQT(input_pdbqt_path=input_pdbqt_path, output_pdbqt_path=output_pdbqt_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def extract_model_pdbqt(input_pdbqt_path, output_pdbqt_path, properties=None, **kwargs):

    if (output_pdbqt_path is None or (os.path.exists(output_pdbqt_path) and os.stat(output_pdbqt_path).st_size > 0)) and \
       True:
        print("WARN: Task ExtractModelPDBQT already executed.")
    else:
        _extractmodelpdbqt( input_pdbqt_path,  output_pdbqt_path,  properties, **kwargs)