import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_structure_utils.utils import extract_atoms
import os
import sys


@constraint(computingUnits="1")
@task(input_structure_path=FILE_IN, output_structure_path=FILE_OUT,
      on_failure='IGNORE')
def extract_atoms_pc(input_structure_path, output_structure_path,
                     properties, **kwargs):
    try:
        os.environ.pop('PMI_FD', None)
        os.environ.pop('PMI_JOBID', None)
        os.environ.pop('PMI_RANK', None)
        os.environ.pop('PMI_SIZE', None)
        extract_atoms.ExtractAtoms(input_structure_path=input_structure_path, output_structure_path=output_structure_path,
                                   properties=properties, **kwargs).launch()
        if not os.path.exists(output_structure_path):
            fu.write_failed_output(output_structure_path)
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_structure_path)
    finally:
        sys.stdout.flush()
        sys.stderr.flush()