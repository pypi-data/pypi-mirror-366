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
from biobb_pmx.pmx.pmxligand_hybrid import Pmxligand_hybrid  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_structure1_path=FILE_IN, input_structure2_path=FILE_IN, input_topology1_path=FILE_IN, input_topology2_path=FILE_IN, output_log_path=FILE_OUT, output_structure1_path=FILE_OUT, output_structure2_path=FILE_OUT, output_topology_path=FILE_OUT, output_atomtypes_path=FILE_OUT, input_pairs_path=FILE_IN, input_scaffold1_path=FILE_IN, input_scaffold2_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _pmxligand_hybrid(input_structure1_path, input_structure2_path, input_topology1_path, input_topology2_path, output_log_path, output_structure1_path, output_structure2_path, output_topology_path, output_atomtypes_path, input_pairs_path, input_scaffold1_path, input_scaffold2_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Pmxligand_hybrid(input_structure1_path=input_structure1_path, input_structure2_path=input_structure2_path, input_topology1_path=input_topology1_path, input_topology2_path=input_topology2_path, output_log_path=output_log_path, output_structure1_path=output_structure1_path, output_structure2_path=output_structure2_path, output_topology_path=output_topology_path, output_atomtypes_path=output_atomtypes_path, input_pairs_path=input_pairs_path, input_scaffold1_path=input_scaffold1_path, input_scaffold2_path=input_scaffold2_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def pmxligand_hybrid(input_structure1_path, input_structure2_path, input_topology1_path, input_topology2_path, output_log_path, output_structure1_path, output_structure2_path, output_topology_path, output_atomtypes_path, input_pairs_path=None, input_scaffold1_path=None, input_scaffold2_path=None, properties=None, **kwargs):

    if (output_log_path is None or (os.path.exists(output_log_path) and os.stat(output_log_path).st_size > 0)) and \
       (output_structure1_path is None or (os.path.exists(output_structure1_path) and os.stat(output_structure1_path).st_size > 0)) and \
       (output_structure2_path is None or (os.path.exists(output_structure2_path) and os.stat(output_structure2_path).st_size > 0)) and \
       (output_topology_path is None or (os.path.exists(output_topology_path) and os.stat(output_topology_path).st_size > 0)) and \
       (output_atomtypes_path is None or (os.path.exists(output_atomtypes_path) and os.stat(output_atomtypes_path).st_size > 0)) and \
       True:
        print("WARN: Task Pmxligand_hybrid already executed.")
    else:
        _pmxligand_hybrid( input_structure1_path,  input_structure2_path,  input_topology1_path,  input_topology2_path,  output_log_path,  output_structure1_path,  output_structure2_path,  output_topology_path,  output_atomtypes_path,  input_pairs_path,  input_scaffold1_path,  input_scaffold2_path,  properties, **kwargs)