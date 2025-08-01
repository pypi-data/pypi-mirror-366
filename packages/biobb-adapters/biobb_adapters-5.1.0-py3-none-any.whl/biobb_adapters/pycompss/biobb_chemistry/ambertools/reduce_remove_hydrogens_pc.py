import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_chemistry.ambertools import reduce_remove_hydrogens

@task(input_path=FILE_IN, output_path=FILE_OUT)
def reduce_remove_hydrogens_pc(input_path, output_path, properties, **kwargs):
    try:
        reduce_remove_hydrogens.ReduceRemoveHydrogens(input_path=input_path, output_path=output_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_path)
