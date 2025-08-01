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
from biobb_analysis.gromacs.gmx_trjconv_str_ens import GMXTrjConvStrEns  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_traj_path=FILE_IN, input_top_path=FILE_IN, output_str_ens_path=FILE_OUT, input_index_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _gmxtrjconvstrens(input_traj_path, input_top_path, output_str_ens_path, input_index_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        GMXTrjConvStrEns(input_traj_path=input_traj_path, input_top_path=input_top_path, output_str_ens_path=output_str_ens_path, input_index_path=input_index_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def gmx_trjconv_str_ens(input_traj_path, input_top_path, output_str_ens_path, input_index_path=None, properties=None, **kwargs):

    if (output_str_ens_path is None or (os.path.exists(output_str_ens_path) and os.stat(output_str_ens_path).st_size > 0)) and \
       True:
        print("WARN: Task GMXTrjConvStrEns already executed.")
    else:
        _gmxtrjconvstrens( input_traj_path,  input_top_path,  output_str_ens_path,  input_index_path,  properties, **kwargs)