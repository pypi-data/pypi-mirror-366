import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_structure_utils.utils import extract_heteroatoms

@task(input_structure_path=FILE_IN, output_heteroatom_path=FILE_OUT)
def extract_heteroatoms_pc(input_structure_path, output_heteroatom_path, properties, **kwargs):
    try:
        extract_heteroatoms.ExtractHeteroAtoms(input_structure_path=input_structure_path, output_heteroatom_path=output_heteroatom_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_heteroatom_path)