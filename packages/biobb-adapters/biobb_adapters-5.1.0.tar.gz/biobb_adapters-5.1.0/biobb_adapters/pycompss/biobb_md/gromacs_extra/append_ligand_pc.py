import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_md.gromacs_extra import append_ligand
import os
import sys

@constraint(computingUnits="1")
@task(input_top_zip_path=FILE_IN, input_itp_path=FILE_IN,
      output_top_zip_path=FILE_OUT, input_posres_itp_path=FILE_IN,
      on_failure="IGNORE")
def append_ligand_pc(input_top_zip_path, input_itp_path,
                     output_top_zip_path, input_posres_itp_path,
                     properties, **kwargs):
    try:
        os.environ.pop('PMI_FD', None)
        os.environ.pop('PMI_JOBID', None)
        os.environ.pop('PMI_RANK', None)
        os.environ.pop('PMI_SIZE', None)
        append_ligand.AppendLigand(input_top_zip_path=input_top_zip_path, input_itp_path=input_itp_path,
                                   output_top_zip_path=output_top_zip_path, input_posres_itp_path=input_posres_itp_path,
                                   properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_top_zip_path)
    finally:
        sys.stdout.flush()
        sys.stderr.flush()