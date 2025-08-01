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
from biobb_structure_utils.utils.cat_pdb import CatPDB  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_structure1=FILE_IN, input_structure2=FILE_IN, output_structure_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _catpdb(input_structure1, input_structure2, output_structure_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        CatPDB(input_structure1=input_structure1, input_structure2=input_structure2, output_structure_path=output_structure_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def cat_pdb(input_structure1, input_structure2, output_structure_path, properties=None, **kwargs):

    if (output_structure_path is None or (os.path.exists(output_structure_path) and os.stat(output_structure_path).st_size > 0)) and \
       True:
        print("WARN: Task CatPDB already executed.")
    else:
        _catpdb( input_structure1,  input_structure2,  output_structure_path,  properties, **kwargs)