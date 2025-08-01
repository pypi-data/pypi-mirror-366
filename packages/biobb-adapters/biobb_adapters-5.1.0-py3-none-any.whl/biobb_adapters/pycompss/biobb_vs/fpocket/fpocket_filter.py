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
from biobb_vs.fpocket.fpocket_filter import FPocketFilter  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_pockets_zip=FILE_IN, input_summary=FILE_IN, output_filter_pockets_zip=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _fpocketfilter(input_pockets_zip, input_summary, output_filter_pockets_zip,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        FPocketFilter(input_pockets_zip=input_pockets_zip, input_summary=input_summary, output_filter_pockets_zip=output_filter_pockets_zip, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def fpocket_filter(input_pockets_zip, input_summary, output_filter_pockets_zip, properties=None, **kwargs):

    if (output_filter_pockets_zip is None or (os.path.exists(output_filter_pockets_zip) and os.stat(output_filter_pockets_zip).st_size > 0)) and \
       True:
        print("WARN: Task FPocketFilter already executed.")
    else:
        _fpocketfilter( input_pockets_zip,  input_summary,  output_filter_pockets_zip,  properties, **kwargs)