import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_analysis.gromacs import gmx_image
import os
import sys


@constraint(computingUnits="1")
@task(input_traj_path=FILE_IN, input_top_path=FILE_IN,
      output_traj_path=FILE_OUT, on_failure='IGNORE')
def gmx_image_pc(input_traj_path, input_top_path,
                 output_traj_path, properties,
                 **kwargs):
    try:
        os.environ.pop('PMI_FD', None)
        os.environ.pop('PMI_JOBID', None)
        os.environ.pop('PMI_RANK', None)
        os.environ.pop('PMI_SIZE', None)
        gmx_image.GMXImage(input_traj_path=input_traj_path, input_top_path=input_top_path,
                           output_traj_path=output_traj_path, properties=properties,
                           **kwargs).launch()
        if not os.path.exists(output_traj_path):
            fu.write_failed_output(output_traj_path)
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_traj_path)
    finally:
        sys.stdout.flush()
        sys.stderr.flush()