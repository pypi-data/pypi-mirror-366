import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_md.mmb_api import pdb_variants

@task(output_mutations_list_txt=FILE_OUT, on_failure="IGNORE")
def pdb_variants_pc(output_mutations_list_txt, properties, **kwargs):
    try:
        pdb_variants.MmbPdbVariants(output_mutations_list_txt=output_mutations_list_txt, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_mutations_list_txt)
