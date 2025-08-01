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
from biobb_vs.fpocket.fpocket_select import FPocketSelect  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_pockets_zip=FILE_IN, output_pocket_pdb=FILE_OUT, output_pocket_pqr=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _fpocketselect(input_pockets_zip, output_pocket_pdb, output_pocket_pqr,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        FPocketSelect(input_pockets_zip=input_pockets_zip, output_pocket_pdb=output_pocket_pdb, output_pocket_pqr=output_pocket_pqr, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def fpocket_select(input_pockets_zip, output_pocket_pdb, output_pocket_pqr, properties=None, **kwargs):

    if (output_pocket_pdb is None or (os.path.exists(output_pocket_pdb) and os.stat(output_pocket_pdb).st_size > 0)) and \
       (output_pocket_pqr is None or (os.path.exists(output_pocket_pqr) and os.stat(output_pocket_pqr).st_size > 0)) and \
       True:
        print("WARN: Task FPocketSelect already executed.")
    else:
        _fpocketselect( input_pockets_zip,  output_pocket_pdb,  output_pocket_pqr,  properties, **kwargs)