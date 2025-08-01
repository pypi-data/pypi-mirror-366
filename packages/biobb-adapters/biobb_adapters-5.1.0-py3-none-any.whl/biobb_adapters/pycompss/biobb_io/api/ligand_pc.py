import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_io.api import ligand

@task(output_pdb_path=FILE_OUT)
def ligand_pc(output_pdb_path, properties, **kwargs):
    try:
        ligand.Ligand(output_pdb_path=output_pdb_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_pdb_path)
