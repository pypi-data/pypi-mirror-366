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
from biobb_pmx.pmx.pmxanalyse import Pmxanalyse  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_a_xvg_zip_path=FILE_IN, input_b_xvg_zip_path=FILE_IN, output_result_path=FILE_OUT, output_work_plot_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _pmxanalyse(input_a_xvg_zip_path, input_b_xvg_zip_path, output_result_path, output_work_plot_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Pmxanalyse(input_a_xvg_zip_path=input_a_xvg_zip_path, input_b_xvg_zip_path=input_b_xvg_zip_path, output_result_path=output_result_path, output_work_plot_path=output_work_plot_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def pmxanalyse(input_a_xvg_zip_path, input_b_xvg_zip_path, output_result_path, output_work_plot_path, properties=None, **kwargs):

    if (output_result_path is None or (os.path.exists(output_result_path) and os.stat(output_result_path).st_size > 0)) and \
       (output_work_plot_path is None or (os.path.exists(output_work_plot_path) and os.stat(output_work_plot_path).st_size > 0)) and \
       True:
        print("WARN: Task Pmxanalyse already executed.")
    else:
        _pmxanalyse( input_a_xvg_zip_path,  input_b_xvg_zip_path,  output_result_path,  output_work_plot_path,  properties, **kwargs)