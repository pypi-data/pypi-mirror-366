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
from biobb_md.gromacs_extra.append_ligand import AppendLigand  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_top_zip_path=FILE_IN, input_itp_path=FILE_IN, output_top_zip_path=FILE_OUT, input_posres_itp_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _appendligand(input_top_zip_path, input_itp_path, output_top_zip_path, input_posres_itp_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        AppendLigand(input_top_zip_path=input_top_zip_path, input_itp_path=input_itp_path, output_top_zip_path=output_top_zip_path, input_posres_itp_path=input_posres_itp_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def append_ligand(input_top_zip_path, input_itp_path, output_top_zip_path, input_posres_itp_path=None, properties=None, **kwargs):

    if (output_top_zip_path is None or (os.path.exists(output_top_zip_path) and os.stat(output_top_zip_path).st_size > 0)) and \
       True:
        print("WARN: Task AppendLigand already executed.")
    else:
        _appendligand( input_top_zip_path,  input_itp_path,  output_top_zip_path,  input_posres_itp_path,  properties, **kwargs)