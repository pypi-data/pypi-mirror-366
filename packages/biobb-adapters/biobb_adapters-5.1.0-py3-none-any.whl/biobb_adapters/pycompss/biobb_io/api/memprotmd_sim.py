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
from biobb_io.api.memprotmd_sim import MemProtMDSim  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(output_simulation=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _memprotmdsim(output_simulation,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        MemProtMDSim(output_simulation=output_simulation, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def memprotmd_sim(output_simulation, properties=None, **kwargs):

    if (output_simulation is None or (os.path.exists(output_simulation) and os.stat(output_simulation).st_size > 0)) and \
       True:
        print("WARN: Task MemProtMDSim already executed.")
    else:
        _memprotmdsim( output_simulation,  properties, **kwargs)