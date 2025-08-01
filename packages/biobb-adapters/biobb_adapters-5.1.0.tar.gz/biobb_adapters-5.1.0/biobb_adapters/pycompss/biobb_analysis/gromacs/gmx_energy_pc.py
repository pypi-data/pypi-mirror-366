import traceback
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.parameter import FILE_IN, FILE_OUT
from biobb_common.tools import file_utils as fu
from biobb_analysis.gromacs import gmx_energy
import os
import sys


# Is constraint decorator needed in this case?
# @constraint(computingUnits=)
@task(input_energy_path=FILE_IN, output_xvg_path=FILE_OUT, on_failure="IGNORE")
def gmx_energy_pc(input_energy_path, output_xvg_path, properties, **kwargs):
    try:
        gmx_energy.GMXEnergy(input_energy_path=input_energy_path, output_xvg_path=output_xvg_path,
                             properties=properties, **kwargs).launch()
        if not os.path.exists(output_xvg_path):
            fu.write_failed_output(output_xvg_path)
    except Exception:
        traceback.print_exc()
        fu.write_failed_output(output_xvg_path)
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
