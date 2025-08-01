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
from biobb_amber.parmed.parmed_hmassrepartition import ParmedHMassRepartition  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_top_path=FILE_IN, output_top_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _parmedhmassrepartition(input_top_path, output_top_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        ParmedHMassRepartition(input_top_path=input_top_path, output_top_path=output_top_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def parmed_hmassrepartition(input_top_path, output_top_path, properties=None, **kwargs):

    if (output_top_path is None or (os.path.exists(output_top_path) and os.stat(output_top_path).st_size > 0)) and \
       True:
        print("WARN: Task ParmedHMassRepartition already executed.")
    else:
        _parmedhmassrepartition( input_top_path,  output_top_path,  properties, **kwargs)