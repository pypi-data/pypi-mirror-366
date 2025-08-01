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
from biobb_vs.vina.autodock_vina_run import AutoDockVinaRun  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_ligand_pdbqt_path=FILE_IN, input_receptor_pdbqt_path=FILE_IN, input_box_path=FILE_IN, output_pdbqt_path=FILE_OUT, output_log_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _autodockvinarun(input_ligand_pdbqt_path, input_receptor_pdbqt_path, input_box_path, output_pdbqt_path, output_log_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        AutoDockVinaRun(input_ligand_pdbqt_path=input_ligand_pdbqt_path, input_receptor_pdbqt_path=input_receptor_pdbqt_path, input_box_path=input_box_path, output_pdbqt_path=output_pdbqt_path, output_log_path=output_log_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def autodock_vina_run(input_ligand_pdbqt_path, input_receptor_pdbqt_path, input_box_path, output_pdbqt_path, output_log_path=None, properties=None, **kwargs):

    if (output_pdbqt_path is None or (os.path.exists(output_pdbqt_path) and os.stat(output_pdbqt_path).st_size > 0)) and \
       (output_log_path is None or (os.path.exists(output_log_path) and os.stat(output_log_path).st_size > 0)) and \
       True:
        print("WARN: Task AutoDockVinaRun already executed.")
    else:
        _autodockvinarun( input_ligand_pdbqt_path,  input_receptor_pdbqt_path,  input_box_path,  output_pdbqt_path,  output_log_path,  properties, **kwargs)