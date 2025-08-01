import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_structure_utils.utils import sort_gro_residues
import os
import sys


@constraint(computingUnits="1")
@task(input_gro_path=FILE_IN, output_gro_path=FILE_OUT,
      on_failure='IGNORE')
def sort_gro_residues_pc(input_gro_path, output_gro_path,
                         properties, **kwargs):
    try:
        os.environ.pop('PMI_FD', None)
        os.environ.pop('PMI_JOBID', None)
        os.environ.pop('PMI_RANK', None)
        os.environ.pop('PMI_SIZE', None)
        sort_gro_residues.SortGroResidues(input_gro_path=input_gro_path, output_gro_path=output_gro_path,
                                          properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_gro_path)
    finally:
        sys.stdout.flush()
        sys.stderr.flush()