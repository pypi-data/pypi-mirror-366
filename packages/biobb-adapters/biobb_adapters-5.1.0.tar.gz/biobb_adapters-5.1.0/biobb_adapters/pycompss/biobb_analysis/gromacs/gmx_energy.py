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
from biobb_analysis.gromacs.gmx_energy import GMXEnergy  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_energy_path=FILE_IN, output_xvg_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _gmxenergy(input_energy_path, output_xvg_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        GMXEnergy(input_energy_path=input_energy_path, output_xvg_path=output_xvg_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def gmx_energy(input_energy_path, output_xvg_path, properties=None, **kwargs):

    if (output_xvg_path is None or (os.path.exists(output_xvg_path) and os.stat(output_xvg_path).st_size > 0)) and \
       True:
        print("WARN: Task GMXEnergy already executed.")
    else:
        _gmxenergy( input_energy_path,  output_xvg_path,  properties, **kwargs)