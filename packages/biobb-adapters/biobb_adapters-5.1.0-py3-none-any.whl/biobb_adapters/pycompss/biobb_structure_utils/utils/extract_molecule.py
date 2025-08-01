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
from biobb_structure_utils.utils.extract_molecule import ExtractMolecule  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_structure_path=FILE_IN, output_molecule_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _extractmolecule(input_structure_path, output_molecule_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        ExtractMolecule(input_structure_path=input_structure_path, output_molecule_path=output_molecule_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def extract_molecule(input_structure_path, output_molecule_path, properties=None, **kwargs):

    if (output_molecule_path is None or (os.path.exists(output_molecule_path) and os.stat(output_molecule_path).st_size > 0)) and \
       True:
        print("WARN: Task ExtractMolecule already executed.")
    else:
        _extractmolecule( input_structure_path,  output_molecule_path,  properties, **kwargs)