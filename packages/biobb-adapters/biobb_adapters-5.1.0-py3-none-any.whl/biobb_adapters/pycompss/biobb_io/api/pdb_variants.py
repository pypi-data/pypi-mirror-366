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
from biobb_io.api.pdb_variants import PdbVariants  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(output_mutations_list_txt=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _pdbvariants(output_mutations_list_txt,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        PdbVariants(output_mutations_list_txt=output_mutations_list_txt, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def pdb_variants(output_mutations_list_txt, properties=None, **kwargs):

    if (output_mutations_list_txt is None or (os.path.exists(output_mutations_list_txt) and os.stat(output_mutations_list_txt).st_size > 0)) and \
       True:
        print("WARN: Task PdbVariants already executed.")
    else:
        _pdbvariants( output_mutations_list_txt,  properties, **kwargs)