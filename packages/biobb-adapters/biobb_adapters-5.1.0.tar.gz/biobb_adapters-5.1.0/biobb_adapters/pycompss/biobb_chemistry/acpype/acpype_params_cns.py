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
from biobb_chemistry.acpype.acpype_params_cns import AcpypeParamsCNS  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_path=FILE_IN, output_path_par=FILE_OUT, output_path_inp=FILE_OUT, output_path_top=FILE_OUT, output_path_pdb=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _acpypeparamscns(input_path, output_path_par, output_path_inp, output_path_top, output_path_pdb,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        AcpypeParamsCNS(input_path=input_path, output_path_par=output_path_par, output_path_inp=output_path_inp, output_path_top=output_path_top, output_path_pdb=output_path_pdb, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def acpype_params_cns(input_path, output_path_par, output_path_inp, output_path_top, output_path_pdb, properties=None, **kwargs):

    if (output_path_par is None or (os.path.exists(output_path_par) and os.stat(output_path_par).st_size > 0)) and \
       (output_path_inp is None or (os.path.exists(output_path_inp) and os.stat(output_path_inp).st_size > 0)) and \
       (output_path_top is None or (os.path.exists(output_path_top) and os.stat(output_path_top).st_size > 0)) and \
       (output_path_pdb is None or (os.path.exists(output_path_pdb) and os.stat(output_path_pdb).st_size > 0)) and \
       True:
        print("WARN: Task AcpypeParamsCNS already executed.")
    else:
        _acpypeparamscns( input_path,  output_path_par,  output_path_inp,  output_path_top,  output_path_pdb,  properties, **kwargs)