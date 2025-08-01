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
from biobb_chemistry.acpype.acpype_params_gmx_opls import AcpypeParamsGMXOPLS  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_path=FILE_IN, output_path_itp=FILE_OUT, output_path_top=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _acpypeparamsgmxopls(input_path, output_path_itp, output_path_top,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        AcpypeParamsGMXOPLS(input_path=input_path, output_path_itp=output_path_itp, output_path_top=output_path_top, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def acpype_params_gmx_opls(input_path, output_path_itp, output_path_top, properties=None, **kwargs):

    if (output_path_itp is None or (os.path.exists(output_path_itp) and os.stat(output_path_itp).st_size > 0)) and \
       (output_path_top is None or (os.path.exists(output_path_top) and os.stat(output_path_top).st_size > 0)) and \
       True:
        print("WARN: Task AcpypeParamsGMXOPLS already executed.")
    else:
        _acpypeparamsgmxopls( input_path,  output_path_itp,  output_path_top,  properties, **kwargs)