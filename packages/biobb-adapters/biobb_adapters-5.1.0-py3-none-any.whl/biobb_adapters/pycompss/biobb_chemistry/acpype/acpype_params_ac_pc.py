import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_chemistry.acpype import acpype_params_ac

@task(input_path=FILE_IN, output_path_frcmod=FILE_OUT, output_path_inpcrd=FILE_OUT, output_path_lib=FILE_OUT, output_path_prmtop=FILE_OUT)
def acpype_params_ac_pc(input_path, output_path_frcmod, output_path_inpcrd, output_path_lib, output_path_prmtop, properties, **kwargs):
    try:
        acpype_params_ac.AcpypeParamsAC(input_path=input_path, output_path_frcmod=output_path_frcmod, output_path_inpcrd=output_path_inpcrd, output_path_lib=output_path_lib, output_path_prmtop=output_path_prmtop, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_path_frcmod)
        fu.write_failed_output(output_path_inpcrd)
        fu.write_failed_output(output_path_lib)
        fu.write_failed_output(output_path_prmtop)
