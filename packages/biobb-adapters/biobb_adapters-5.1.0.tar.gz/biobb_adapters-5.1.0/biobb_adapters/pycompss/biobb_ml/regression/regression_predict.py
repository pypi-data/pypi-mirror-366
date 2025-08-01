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
from biobb_ml.regression.regression_predict import RegressionPredict  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_model_path=FILE_IN, output_results_path=FILE_OUT, input_dataset_path=FILE_IN, 
      on_failure="IGNORE", time_out=task_time_out)
def _regressionpredict(input_model_path, output_results_path, input_dataset_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        RegressionPredict(input_model_path=input_model_path, output_results_path=output_results_path, input_dataset_path=input_dataset_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def regression_predict(input_model_path, output_results_path, input_dataset_path=None, properties=None, **kwargs):

    if (output_results_path is None or (os.path.exists(output_results_path) and os.stat(output_results_path).st_size > 0)) and \
       True:
        print("WARN: Task RegressionPredict already executed.")
    else:
        _regressionpredict( input_model_path,  output_results_path,  input_dataset_path,  properties, **kwargs)