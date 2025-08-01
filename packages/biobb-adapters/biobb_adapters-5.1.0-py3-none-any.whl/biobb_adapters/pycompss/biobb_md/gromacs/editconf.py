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
from biobb_md.gromacs.editconf import Editconf  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_gro_path=FILE_IN, output_gro_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _editconf(input_gro_path, output_gro_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Editconf(input_gro_path=input_gro_path, output_gro_path=output_gro_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def editconf(input_gro_path, output_gro_path, properties=None, **kwargs):

    if (output_gro_path is None or (os.path.exists(output_gro_path) and os.stat(output_gro_path).st_size > 0)) and \
       True:
        print("WARN: Task Editconf already executed.")
    else:
        _editconf( input_gro_path,  output_gro_path,  properties, **kwargs)