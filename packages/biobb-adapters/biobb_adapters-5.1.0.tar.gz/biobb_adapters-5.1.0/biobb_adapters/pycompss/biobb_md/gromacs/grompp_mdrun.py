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
from biobb_md.gromacs.grompp_mdrun import GromppMdrun  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_gro_path=FILE_IN, input_top_zip_path=FILE_IN, output_trr_path=FILE_OUT, output_gro_path=FILE_OUT, output_edr_path=FILE_OUT, output_log_path=FILE_OUT, input_cpt_path=FILE_IN, input_ndx_path=FILE_IN, input_mdp_path=FILE_IN, output_xtc_path=FILE_OUT, output_cpt_path=FILE_OUT, output_dhdl_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _gromppmdrun(input_gro_path, input_top_zip_path, output_trr_path, output_gro_path, output_edr_path, output_log_path, input_cpt_path, input_ndx_path, input_mdp_path, output_xtc_path, output_cpt_path, output_dhdl_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        GromppMdrun(input_gro_path=input_gro_path, input_top_zip_path=input_top_zip_path, output_trr_path=output_trr_path, output_gro_path=output_gro_path, output_edr_path=output_edr_path, output_log_path=output_log_path, input_cpt_path=input_cpt_path, input_ndx_path=input_ndx_path, input_mdp_path=input_mdp_path, output_xtc_path=output_xtc_path, output_cpt_path=output_cpt_path, output_dhdl_path=output_dhdl_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def grompp_mdrun(input_gro_path, input_top_zip_path, output_trr_path, output_gro_path, output_edr_path, output_log_path, input_cpt_path=None, input_ndx_path=None, input_mdp_path=None, output_xtc_path=None, output_cpt_path=None, output_dhdl_path=None, properties=None, **kwargs):

    if (output_trr_path is None or (os.path.exists(output_trr_path) and os.stat(output_trr_path).st_size > 0)) and \
       (output_gro_path is None or (os.path.exists(output_gro_path) and os.stat(output_gro_path).st_size > 0)) and \
       (output_edr_path is None or (os.path.exists(output_edr_path) and os.stat(output_edr_path).st_size > 0)) and \
       (output_log_path is None or (os.path.exists(output_log_path) and os.stat(output_log_path).st_size > 0)) and \
       (output_xtc_path is None or (os.path.exists(output_xtc_path) and os.stat(output_xtc_path).st_size > 0)) and \
       (output_cpt_path is None or (os.path.exists(output_cpt_path) and os.stat(output_cpt_path).st_size > 0)) and \
       (output_dhdl_path is None or (os.path.exists(output_dhdl_path) and os.stat(output_dhdl_path).st_size > 0)) and \
       True:
        print("WARN: Task GromppMdrun already executed.")
    else:
        _gromppmdrun( input_gro_path,  input_top_zip_path,  output_trr_path,  output_gro_path,  output_edr_path,  output_log_path,  input_cpt_path,  input_ndx_path,  input_mdp_path,  output_xtc_path,  output_cpt_path,  output_dhdl_path,  properties, **kwargs)