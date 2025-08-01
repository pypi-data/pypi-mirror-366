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
from biobb_io.api.mmcif import Mmcif  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(output_mmcif_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _mmcif(output_mmcif_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Mmcif(output_mmcif_path=output_mmcif_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def mmcif(output_mmcif_path, properties=None, **kwargs):

    if (output_mmcif_path is None or (os.path.exists(output_mmcif_path) and os.stat(output_mmcif_path).st_size > 0)) and \
       True:
        print("WARN: Task Mmcif already executed.")
    else:
        _mmcif( output_mmcif_path,  properties, **kwargs)