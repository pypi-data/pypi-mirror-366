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
from biobb_amber.cphstats.cestats_run import CestatsRun  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_cein_path=FILE_IN, input_ceout_path=FILE_IN, output_dat_path=FILE_OUT, output_population_path=FILE_OUT, output_chunk_path=FILE_OUT, output_cumulative_path=FILE_OUT, output_conditional_path=FILE_OUT, output_chunk_conditional_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _cestatsrun(input_cein_path, input_ceout_path, output_dat_path, output_population_path, output_chunk_path, output_cumulative_path, output_conditional_path, output_chunk_conditional_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        CestatsRun(input_cein_path=input_cein_path, input_ceout_path=input_ceout_path, output_dat_path=output_dat_path, output_population_path=output_population_path, output_chunk_path=output_chunk_path, output_cumulative_path=output_cumulative_path, output_conditional_path=output_conditional_path, output_chunk_conditional_path=output_chunk_conditional_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def cestats_run(input_cein_path, input_ceout_path, output_dat_path, output_population_path=None, output_chunk_path=None, output_cumulative_path=None, output_conditional_path=None, output_chunk_conditional_path=None, properties=None, **kwargs):

    if (output_dat_path is None or (os.path.exists(output_dat_path) and os.stat(output_dat_path).st_size > 0)) and \
       (output_population_path is None or (os.path.exists(output_population_path) and os.stat(output_population_path).st_size > 0)) and \
       (output_chunk_path is None or (os.path.exists(output_chunk_path) and os.stat(output_chunk_path).st_size > 0)) and \
       (output_cumulative_path is None or (os.path.exists(output_cumulative_path) and os.stat(output_cumulative_path).st_size > 0)) and \
       (output_conditional_path is None or (os.path.exists(output_conditional_path) and os.stat(output_conditional_path).st_size > 0)) and \
       (output_chunk_conditional_path is None or (os.path.exists(output_chunk_conditional_path) and os.stat(output_chunk_conditional_path).st_size > 0)) and \
       True:
        print("WARN: Task CestatsRun already executed.")
    else:
        _cestatsrun( input_cein_path,  input_ceout_path,  output_dat_path,  output_population_path,  output_chunk_path,  output_cumulative_path,  output_conditional_path,  output_chunk_conditional_path,  properties, **kwargs)