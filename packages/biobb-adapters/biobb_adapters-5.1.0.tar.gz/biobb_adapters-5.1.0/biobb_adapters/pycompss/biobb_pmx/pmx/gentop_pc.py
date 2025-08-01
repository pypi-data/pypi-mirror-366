import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.multinode import multinode
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_pmx.pmx import gentop
import os
import sys


@constraint(computingUnits="1")
@task(input_top_zip_path=FILE_IN, output_top_zip_path=FILE_OUT, on_failure="IGNORE")
def gentop_pc(input_top_zip_path, output_top_zip_path, properties, **kwargs):
    try:
        os.environ.pop('PMI_FD', None)
        os.environ.pop('PMI_JOBID', None)
        os.environ.pop('PMI_RANK', None)
        os.environ.pop('PMI_SIZE', None)
        gentop.Gentop(input_top_zip_path=input_top_zip_path, output_top_zip_path=output_top_zip_path, properties=properties, **kwargs).launch()
        if not os.path.exists(output_top_zip_path):
            fu.write_failed_output(output_top_zip_path)
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_top_zip_path)
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
