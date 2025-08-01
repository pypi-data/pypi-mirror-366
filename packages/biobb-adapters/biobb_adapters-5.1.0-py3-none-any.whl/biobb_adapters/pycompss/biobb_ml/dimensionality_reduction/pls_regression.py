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
from biobb_ml.dimensionality_reduction.pls_regression import PLS_Regression  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_dataset_path=FILE_IN, output_results_path=FILE_OUT, output_plot_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _pls_regression(input_dataset_path, output_results_path, output_plot_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        PLS_Regression(input_dataset_path=input_dataset_path, output_results_path=output_results_path, output_plot_path=output_plot_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def pls_regression(input_dataset_path, output_results_path, output_plot_path=None, properties=None, **kwargs):

    if (output_results_path is None or (os.path.exists(output_results_path) and os.stat(output_results_path).st_size > 0)) and \
       (output_plot_path is None or (os.path.exists(output_plot_path) and os.stat(output_plot_path).st_size > 0)) and \
       True:
        print("WARN: Task PLS_Regression already executed.")
    else:
        _pls_regression( input_dataset_path,  output_results_path,  output_plot_path,  properties, **kwargs)