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
from biobb_pmx.pmx.pmxmerge_ff import Pmxmerge_ff  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_topology_path=FILE_IN, output_topology_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _pmxmerge_ff(input_topology_path, output_topology_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Pmxmerge_ff(input_topology_path=input_topology_path, output_topology_path=output_topology_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def pmxmerge_ff(input_topology_path, output_topology_path, properties=None, **kwargs):

    if (output_topology_path is None or (os.path.exists(output_topology_path) and os.stat(output_topology_path).st_size > 0)) and \
       True:
        print("WARN: Task Pmxmerge_ff already executed.")
    else:
        _pmxmerge_ff( input_topology_path,  output_topology_path,  properties, **kwargs)