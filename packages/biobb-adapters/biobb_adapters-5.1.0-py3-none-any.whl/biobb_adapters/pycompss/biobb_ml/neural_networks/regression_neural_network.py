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
from biobb_ml.neural_networks.regression_neural_network import RegressionNeuralNetwork  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_dataset_path=FILE_IN, output_model_path=FILE_OUT, output_test_table_path=FILE_OUT, output_plot_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _regressionneuralnetwork(input_dataset_path, output_model_path, output_test_table_path, output_plot_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        RegressionNeuralNetwork(input_dataset_path=input_dataset_path, output_model_path=output_model_path, output_test_table_path=output_test_table_path, output_plot_path=output_plot_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def regression_neural_network(input_dataset_path, output_model_path, output_test_table_path=None, output_plot_path=None, properties=None, **kwargs):

    if (output_model_path is None or (os.path.exists(output_model_path) and os.stat(output_model_path).st_size > 0)) and \
       (output_test_table_path is None or (os.path.exists(output_test_table_path) and os.stat(output_test_table_path).st_size > 0)) and \
       (output_plot_path is None or (os.path.exists(output_plot_path) and os.stat(output_plot_path).st_size > 0)) and \
       True:
        print("WARN: Task RegressionNeuralNetwork already executed.")
    else:
        _regressionneuralnetwork( input_dataset_path,  output_model_path,  output_test_table_path,  output_plot_path,  properties, **kwargs)