import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.multinode import multinode
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_pmx.pmx import analyse
import os
import sys


@constraint(computingUnits="1")
@task(input_a_xvg_zip_path=FILE_IN, input_b_xvg_zip_path=FILE_IN,
      output_result_path=FILE_OUT, output_work_plot_path=FILE_OUT,
      on_failure="IGNORE")
def analyse_pc(input_a_xvg_zip_path, input_b_xvg_zip_path,
               output_result_path, output_work_plot_path,
               properties, **kwargs):
    try:
        os.environ.pop('PMI_FD', None)
        os.environ.pop('PMI_JOBID', None)
        os.environ.pop('PMI_RANK', None)
        os.environ.pop('PMI_SIZE', None)
        analyse.Analyse(input_a_xvg_zip_path=input_a_xvg_zip_path, input_b_xvg_zip_path=input_b_xvg_zip_path,
                        output_result_path=output_result_path, output_work_plot_path=output_work_plot_path,
                        properties=properties, **kwargs).launch()
        if not os.path.exists(output_result_path):
            fu.write_failed_output(output_result_path)
        if not os.path.exists(output_work_plot_path):
            fu.write_failed_output(output_work_plot_path)
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_result_path)
        fu.write_failed_output(output_work_plot_path)
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
