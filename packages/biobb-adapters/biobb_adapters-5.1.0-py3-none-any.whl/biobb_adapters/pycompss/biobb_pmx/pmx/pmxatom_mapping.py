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
from biobb_pmx.pmx.pmxatom_mapping import Pmxatom_mapping  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_structure1_path=FILE_IN, input_structure2_path=FILE_IN, output_pairs1_path=FILE_OUT, output_pairs2_path=FILE_OUT, output_log_path=FILE_OUT, output_structure1_path=FILE_OUT, output_structure2_path=FILE_OUT, output_morph1_path=FILE_OUT, output_morph2_path=FILE_OUT, output_scaffold1_path=FILE_OUT, output_scaffold2_path=FILE_OUT, output_score_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _pmxatom_mapping(input_structure1_path, input_structure2_path, output_pairs1_path, output_pairs2_path, output_log_path, output_structure1_path, output_structure2_path, output_morph1_path, output_morph2_path, output_scaffold1_path, output_scaffold2_path, output_score_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        Pmxatom_mapping(input_structure1_path=input_structure1_path, input_structure2_path=input_structure2_path, output_pairs1_path=output_pairs1_path, output_pairs2_path=output_pairs2_path, output_log_path=output_log_path, output_structure1_path=output_structure1_path, output_structure2_path=output_structure2_path, output_morph1_path=output_morph1_path, output_morph2_path=output_morph2_path, output_scaffold1_path=output_scaffold1_path, output_scaffold2_path=output_scaffold2_path, output_score_path=output_score_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def pmxatom_mapping(input_structure1_path, input_structure2_path, output_pairs1_path, output_pairs2_path, output_log_path, output_structure1_path=None, output_structure2_path=None, output_morph1_path=None, output_morph2_path=None, output_scaffold1_path=None, output_scaffold2_path=None, output_score_path=None, properties=None, **kwargs):

    if (output_pairs1_path is None or (os.path.exists(output_pairs1_path) and os.stat(output_pairs1_path).st_size > 0)) and \
       (output_pairs2_path is None or (os.path.exists(output_pairs2_path) and os.stat(output_pairs2_path).st_size > 0)) and \
       (output_log_path is None or (os.path.exists(output_log_path) and os.stat(output_log_path).st_size > 0)) and \
       (output_structure1_path is None or (os.path.exists(output_structure1_path) and os.stat(output_structure1_path).st_size > 0)) and \
       (output_structure2_path is None or (os.path.exists(output_structure2_path) and os.stat(output_structure2_path).st_size > 0)) and \
       (output_morph1_path is None or (os.path.exists(output_morph1_path) and os.stat(output_morph1_path).st_size > 0)) and \
       (output_morph2_path is None or (os.path.exists(output_morph2_path) and os.stat(output_morph2_path).st_size > 0)) and \
       (output_scaffold1_path is None or (os.path.exists(output_scaffold1_path) and os.stat(output_scaffold1_path).st_size > 0)) and \
       (output_scaffold2_path is None or (os.path.exists(output_scaffold2_path) and os.stat(output_scaffold2_path).st_size > 0)) and \
       (output_score_path is None or (os.path.exists(output_score_path) and os.stat(output_score_path).st_size > 0)) and \
       True:
        print("WARN: Task Pmxatom_mapping already executed.")
    else:
        _pmxatom_mapping( input_structure1_path,  input_structure2_path,  output_pairs1_path,  output_pairs2_path,  output_log_path,  output_structure1_path,  output_structure2_path,  output_morph1_path,  output_morph2_path,  output_scaffold1_path,  output_scaffold2_path,  output_score_path,  properties, **kwargs)