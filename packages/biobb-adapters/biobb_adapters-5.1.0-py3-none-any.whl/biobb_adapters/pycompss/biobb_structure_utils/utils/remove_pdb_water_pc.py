import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_structure_utils.utils import remove_pdb_water

@task(input_pdb_path=FILE_IN, output_pdb_path=FILE_OUT)
def remove_pdb_water_pc(input_pdb_path, output_pdb_path, properties, **kwargs):
    try:
        remove_pdb_water.RemovePdbWater(input_pdb_path=input_pdb_path, output_pdb_path=output_pdb_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_pdb_path)