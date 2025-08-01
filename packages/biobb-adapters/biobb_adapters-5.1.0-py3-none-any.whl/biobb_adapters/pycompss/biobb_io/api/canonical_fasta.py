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
from biobb_io.api.canonical_fasta import CanonicalFasta  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(output_fasta_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _canonicalfasta(output_fasta_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        CanonicalFasta(output_fasta_path=output_fasta_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def canonical_fasta(output_fasta_path, properties=None, **kwargs):

    if (output_fasta_path is None or (os.path.exists(output_fasta_path) and os.stat(output_fasta_path).st_size > 0)) and \
       True:
        print("WARN: Task CanonicalFasta already executed.")
    else:
        _canonicalfasta( output_fasta_path,  properties, **kwargs)