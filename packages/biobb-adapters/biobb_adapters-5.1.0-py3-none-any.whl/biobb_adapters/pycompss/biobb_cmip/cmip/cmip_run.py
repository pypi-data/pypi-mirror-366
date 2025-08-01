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
from biobb_cmip.cmip.cmip_run import Titration  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_pdb_path=FILE_IN, input_probe_pdb_path=FILE_IN, output_pdb_path=FILE_OUT, output_grd_path=FILE_OUT, output_cube_path=FILE_OUT, output_rst_path=FILE_OUT, input_rst_path=FILE_IN, output_byat_path=FILE_OUT, output_log_path=FILE_OUT, input_vdw_params_path=FILE_IN, input_params_path=FILE_IN, output_json_box_path=FILE_OUT, output_json_external_box_path=FILE_OUT, input_json_box_path=FILE_IN, input_json_external_box_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _titration(input_pdb_path, input_probe_pdb_path, output_pdb_path, output_grd_path, output_cube_path, output_rst_path, input_rst_path, output_byat_path, output_log_path, input_vdw_params_path, input_params_path, output_json_box_path, output_json_external_box_path, input_json_box_path, input_json_external_box_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Titration(input_pdb_path=input_pdb_path, input_probe_pdb_path=input_probe_pdb_path, output_pdb_path=output_pdb_path, output_grd_path=output_grd_path, output_cube_path=output_cube_path, output_rst_path=output_rst_path, input_rst_path=input_rst_path, output_byat_path=output_byat_path, output_log_path=output_log_path, input_vdw_params_path=input_vdw_params_path, input_params_path=input_params_path, output_json_box_path=output_json_box_path, output_json_external_box_path=output_json_external_box_path, input_json_box_path=input_json_box_path, input_json_external_box_path=input_json_external_box_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def cmip_run(input_pdb_path, input_probe_pdb_path=None, output_pdb_path=None, output_grd_path=None, output_cube_path=None, output_rst_path=None, input_rst_path=None, output_byat_path=None, output_log_path=None, input_vdw_params_path=None, input_params_path=None, output_json_box_path=None, output_json_external_box_path=None, input_json_box_path=None, input_json_external_box_path=None, properties=None, **kwargs):

    if (output_pdb_path is None or (os.path.exists(output_pdb_path) and os.stat(output_pdb_path).st_size > 0)) and \
       (output_grd_path is None or (os.path.exists(output_grd_path) and os.stat(output_grd_path).st_size > 0)) and \
       (output_cube_path is None or (os.path.exists(output_cube_path) and os.stat(output_cube_path).st_size > 0)) and \
       (output_rst_path is None or (os.path.exists(output_rst_path) and os.stat(output_rst_path).st_size > 0)) and \
       (output_byat_path is None or (os.path.exists(output_byat_path) and os.stat(output_byat_path).st_size > 0)) and \
       (output_log_path is None or (os.path.exists(output_log_path) and os.stat(output_log_path).st_size > 0)) and \
       (output_json_box_path is None or (os.path.exists(output_json_box_path) and os.stat(output_json_box_path).st_size > 0)) and \
       (output_json_external_box_path is None or (os.path.exists(output_json_external_box_path) and os.stat(output_json_external_box_path).st_size > 0)) and \
       True:
        print("WARN: Task Titration already executed.")
    else:
        _titration( input_pdb_path,  input_probe_pdb_path,  output_pdb_path,  output_grd_path,  output_cube_path,  output_rst_path,  input_rst_path,  output_byat_path,  output_log_path,  input_vdw_params_path,  input_params_path,  output_json_box_path,  output_json_external_box_path,  input_json_box_path,  input_json_external_box_path,  properties, **kwargs)