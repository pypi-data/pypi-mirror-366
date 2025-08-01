import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.multinode import multinode
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_pmx.pmx import mutate
import os
import sys


# Is constraint decorator needed in this case?
# @constraint(computingUnits=)
@task(input_structure_path=FILE_IN, output_structure_path=FILE_OUT, input_b_structure_path=FILE_OUT, on_failure="IGNORE")
def mutate_bst_pc(input_structure_path, output_structure_path, input_b_structure_path, properties, **kwargs):
    try:
        mutate.Mutate(input_structure_path=input_structure_path, output_structure_path=output_structure_path, input_b_structure_path=input_b_structure_path, properties=properties, **kwargs).launch()
        if not os.path.exists(output_structure_path):
            fu.write_failed_output(output_structure_path)
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_structure_path)
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
