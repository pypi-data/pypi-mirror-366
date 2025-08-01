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
from biobb_md.gromacs.grompp import Grompp  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_gro_path=FILE_IN, input_top_zip_path=FILE_IN, output_tpr_path=FILE_OUT, input_cpt_path=FILE_IN, input_ndx_path=FILE_IN, input_mdp_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _grompp(input_gro_path, input_top_zip_path, output_tpr_path, input_cpt_path, input_ndx_path, input_mdp_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Grompp(input_gro_path=input_gro_path, input_top_zip_path=input_top_zip_path, output_tpr_path=output_tpr_path, input_cpt_path=input_cpt_path, input_ndx_path=input_ndx_path, input_mdp_path=input_mdp_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def grompp(input_gro_path, input_top_zip_path, output_tpr_path, input_cpt_path=None, input_ndx_path=None, input_mdp_path=None, properties=None, **kwargs):

    if (output_tpr_path is None or (os.path.exists(output_tpr_path) and os.stat(output_tpr_path).st_size > 0)) and \
       True:
        print("WARN: Task Grompp already executed.")
    else:
        _grompp( input_gro_path,  input_top_zip_path,  output_tpr_path,  input_cpt_path,  input_ndx_path,  input_mdp_path,  properties, **kwargs)