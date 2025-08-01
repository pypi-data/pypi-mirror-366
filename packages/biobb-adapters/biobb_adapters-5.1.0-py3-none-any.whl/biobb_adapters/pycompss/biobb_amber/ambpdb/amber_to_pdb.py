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
from biobb_amber.ambpdb.amber_to_pdb import AmberToPDB  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_top_path=FILE_IN, input_crd_path=FILE_IN, output_pdb_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _ambertopdb(input_top_path, input_crd_path, output_pdb_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        AmberToPDB(input_top_path=input_top_path, input_crd_path=input_crd_path, output_pdb_path=output_pdb_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def amber_to_pdb(input_top_path, input_crd_path, output_pdb_path, properties=None, **kwargs):

    if (output_pdb_path is None or (os.path.exists(output_pdb_path) and os.stat(output_pdb_path).st_size > 0)) and \
       True:
        print("WARN: Task AmberToPDB already executed.")
    else:
        _ambertopdb( input_top_path,  input_crd_path,  output_pdb_path,  properties, **kwargs)