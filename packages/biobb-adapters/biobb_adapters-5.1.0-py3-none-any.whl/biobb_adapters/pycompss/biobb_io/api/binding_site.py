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
from biobb_io.api.binding_site import BindingSite  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(output_json_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _bindingsite(output_json_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        BindingSite(output_json_path=output_json_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def bindingsite(output_json_path, properties=None, **kwargs):

    if (output_json_path is None or os.path.exists(output_json_path)) and \
       True:
        print("WARN: Task BindingSite already executed.")
    else:
        _bindingsite( output_json_path,  properties, **kwargs)