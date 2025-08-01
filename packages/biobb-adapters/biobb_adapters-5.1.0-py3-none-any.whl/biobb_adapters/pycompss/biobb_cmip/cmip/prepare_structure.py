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
from biobb_cmip.cmip.prepare_structure import PrepareStructure  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_pdb_path=FILE_IN, output_cmip_pdb_path=FILE_OUT, input_topology_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _preparestructure(input_pdb_path, output_cmip_pdb_path, input_topology_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        PrepareStructure(input_pdb_path=input_pdb_path, output_cmip_pdb_path=output_cmip_pdb_path, input_topology_path=input_topology_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def prepare_structure(input_pdb_path, output_cmip_pdb_path, input_topology_path=None, properties=None, **kwargs):

    if (output_cmip_pdb_path is None or (os.path.exists(output_cmip_pdb_path) and os.stat(output_cmip_pdb_path).st_size > 0)) and \
       True:
        print("WARN: Task PrepareStructure already executed.")
    else:
        _preparestructure( input_pdb_path,  output_cmip_pdb_path,  input_topology_path,  properties, **kwargs)