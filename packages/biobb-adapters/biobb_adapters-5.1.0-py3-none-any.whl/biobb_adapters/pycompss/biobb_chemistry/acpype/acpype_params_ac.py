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
from biobb_chemistry.acpype.acpype_params_ac import AcpypeParamsAC  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_path=FILE_IN, output_path_frcmod=FILE_OUT, output_path_inpcrd=FILE_OUT, output_path_lib=FILE_OUT, output_path_prmtop=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _acpypeparamsac(input_path, output_path_frcmod, output_path_inpcrd, output_path_lib, output_path_prmtop,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        AcpypeParamsAC(input_path=input_path, output_path_frcmod=output_path_frcmod, output_path_inpcrd=output_path_inpcrd, output_path_lib=output_path_lib, output_path_prmtop=output_path_prmtop, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def acpype_params_ac(input_path, output_path_frcmod, output_path_inpcrd, output_path_lib, output_path_prmtop, properties=None, **kwargs):

    if (output_path_frcmod is None or (os.path.exists(output_path_frcmod) and os.stat(output_path_frcmod).st_size > 0)) and \
       (output_path_inpcrd is None or (os.path.exists(output_path_inpcrd) and os.stat(output_path_inpcrd).st_size > 0)) and \
       (output_path_lib is None or (os.path.exists(output_path_lib) and os.stat(output_path_lib).st_size > 0)) and \
       (output_path_prmtop is None or (os.path.exists(output_path_prmtop) and os.stat(output_path_prmtop).st_size > 0)) and \
       True:
        print("WARN: Task AcpypeParamsAC already executed.")
    else:
        _acpypeparamsac( input_path,  output_path_frcmod,  output_path_inpcrd,  output_path_lib,  output_path_prmtop,  properties, **kwargs)