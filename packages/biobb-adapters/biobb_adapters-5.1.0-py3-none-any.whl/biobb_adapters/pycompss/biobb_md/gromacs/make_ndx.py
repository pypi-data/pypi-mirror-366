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
from biobb_md.gromacs.make_ndx import MakeNdx  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_structure_path=FILE_IN, output_ndx_path=FILE_OUT, input_ndx_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _makendx(input_structure_path, output_ndx_path, input_ndx_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        MakeNdx(input_structure_path=input_structure_path, output_ndx_path=output_ndx_path, input_ndx_path=input_ndx_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def make_ndx(input_structure_path, output_ndx_path, input_ndx_path=None, properties=None, **kwargs):

    if (output_ndx_path is None or (os.path.exists(output_ndx_path) and os.stat(output_ndx_path).st_size > 0)) and \
       True:
        print("WARN: Task MakeNdx already executed.")
    else:
        _makendx( input_structure_path,  output_ndx_path,  input_ndx_path,  properties, **kwargs)