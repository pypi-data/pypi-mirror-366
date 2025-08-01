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
from biobb_vs.fpocket.fpocket_run import FPocketRun  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_pdb_path=FILE_IN, output_pockets_zip=FILE_OUT, output_summary=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _fpocketrun(input_pdb_path, output_pockets_zip, output_summary,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        FPocketRun(input_pdb_path=input_pdb_path, output_pockets_zip=output_pockets_zip, output_summary=output_summary, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def fpocket_run(input_pdb_path, output_pockets_zip, output_summary, properties=None, **kwargs):

    if (output_pockets_zip is None or (os.path.exists(output_pockets_zip) and os.stat(output_pockets_zip).st_size > 0)) and \
       (output_summary is None or (os.path.exists(output_summary) and os.stat(output_summary).st_size > 0)) and \
       True:
        print("WARN: Task FPocketRun already executed.")
    else:
        _fpocketrun( input_pdb_path,  output_pockets_zip,  output_summary,  properties, **kwargs)