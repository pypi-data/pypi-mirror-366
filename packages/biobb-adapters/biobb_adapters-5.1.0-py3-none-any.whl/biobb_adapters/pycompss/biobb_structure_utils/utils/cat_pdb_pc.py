import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_structure_utils.utils import cat_pdb

@task(input_structure1=FILE_IN, input_structure2=FILE_IN, output_structure_path=FILE_OUT)
def cat_pdb_pc(input_structure1, input_structure2, output_structure_path, properties, **kwargs):
    try:
        cat_pdb.CatPDB(input_structure1=input_structure1, input_structure2=input_structure2, output_structure_path=output_structure_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_structure_path)