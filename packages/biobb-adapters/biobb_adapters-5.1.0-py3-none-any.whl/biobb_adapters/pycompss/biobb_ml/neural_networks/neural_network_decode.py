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
from biobb_ml.neural_networks.neural_network_decode import DecodingNeuralNetwork  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_decode_path=FILE_IN, input_model_path=FILE_IN, output_decode_path=FILE_OUT, output_predict_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _decodingneuralnetwork(input_decode_path, input_model_path, output_decode_path, output_predict_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        DecodingNeuralNetwork(input_decode_path=input_decode_path, input_model_path=input_model_path, output_decode_path=output_decode_path, output_predict_path=output_predict_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def neural_network_decode(input_decode_path, input_model_path, output_decode_path, output_predict_path=None, properties=None, **kwargs):

    if (output_decode_path is None or (os.path.exists(output_decode_path) and os.stat(output_decode_path).st_size > 0)) and \
       (output_predict_path is None or (os.path.exists(output_predict_path) and os.stat(output_predict_path).st_size > 0)) and \
       True:
        print("WARN: Task DecodingNeuralNetwork already executed.")
    else:
        _decodingneuralnetwork( input_decode_path,  input_model_path,  output_decode_path,  output_predict_path,  properties, **kwargs)