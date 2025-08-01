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
from biobb_io.api.drugbank import Drugbank  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(output_sdf_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _drugbank(output_sdf_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Drugbank(output_sdf_path=output_sdf_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def drugbank(output_sdf_path, properties=None, **kwargs):

    if (output_sdf_path is None or (os.path.exists(output_sdf_path) and os.stat(output_sdf_path).st_size > 0)) and \
       True:
        print("WARN: Task Drugbank already executed.")
    else:
        _drugbank( output_sdf_path,  properties, **kwargs)