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
from biobb_cmip.cmip.ignore_residues import IgnoreResidues  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_cmip_pdb_path=FILE_IN, output_cmip_pdb_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _ignoreresidues(input_cmip_pdb_path, output_cmip_pdb_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        IgnoreResidues(input_cmip_pdb_path=input_cmip_pdb_path, output_cmip_pdb_path=output_cmip_pdb_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def ignore_residues(input_cmip_pdb_path, output_cmip_pdb_path, properties=None, **kwargs):

    if (output_cmip_pdb_path is None or (os.path.exists(output_cmip_pdb_path) and os.stat(output_cmip_pdb_path).st_size > 0)) and \
       True:
        print("WARN: Task IgnoreResidues already executed.")
    else:
        _ignoreresidues( input_cmip_pdb_path,  output_cmip_pdb_path,  properties, **kwargs)