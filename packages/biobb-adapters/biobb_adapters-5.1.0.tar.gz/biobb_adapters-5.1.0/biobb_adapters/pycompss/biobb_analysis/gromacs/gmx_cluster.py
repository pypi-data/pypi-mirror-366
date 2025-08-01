# Python
import os
import sys
import traceback
# Pycompss
from pycompss.api.task import task
from pycompss.api.parameter import FILE_IN, FILE_OUT
# Adapters commons pycompss
from biobb_adapters.pycompss.biobb_commons import task_config
# Wrapped Biobb
from biobb_analysis.gromacs.gmx_cluster import GMXCluster  # Importing class instead of module to avoid name collision

task_time_out = int(os.environ.get('TASK_TIME_OUT', 0))


@task(input_structure_path=FILE_IN, input_traj_path=FILE_IN, output_pdb_path=FILE_OUT, input_index_path=FILE_IN, output_cluster_log_path=FILE_OUT, output_rmsd_cluster_xpm_path=FILE_OUT, output_rmsd_dist_xvg_path=FILE_OUT, 
      on_failure="IGNORE", time_out=task_time_out)
def _gmxcluster(input_structure_path, input_traj_path, output_pdb_path, input_index_path, output_cluster_log_path, output_rmsd_cluster_xpm_path, output_rmsd_dist_xvg_path,  properties, **kwargs):
    
    task_config.pop_pmi(os.environ)
    
    try:
        GMXCluster(input_structure_path=input_structure_path, input_traj_path=input_traj_path, output_pdb_path=output_pdb_path, input_index_path=input_index_path, output_cluster_log_path=output_cluster_log_path, output_rmsd_cluster_xpm_path=output_rmsd_cluster_xpm_path, output_rmsd_dist_xvg_path=output_rmsd_dist_xvg_path, properties=properties, **kwargs).launch()
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        sys.stdout.flush()
        sys.stderr.flush()


def gmx_cluster(input_structure_path, input_traj_path, output_pdb_path, input_index_path=None, output_cluster_log_path=None, output_rmsd_cluster_xpm_path=None, output_rmsd_dist_xvg_path=None, properties=None, **kwargs):

    if (output_pdb_path is None or (os.path.exists(output_pdb_path) and os.stat(output_pdb_path).st_size > 0)) and \
       (output_cluster_log_path is None or (os.path.exists(output_cluster_log_path) and os.stat(output_cluster_log_path).st_size > 0)) and \
       (output_rmsd_cluster_xpm_path is None or (os.path.exists(output_rmsd_cluster_xpm_path) and os.stat(output_rmsd_cluster_xpm_path).st_size > 0)) and \
       (output_rmsd_dist_xvg_path is None or (os.path.exists(output_rmsd_dist_xvg_path) and os.stat(output_rmsd_dist_xvg_path).st_size > 0)) and \
       True:
        print("WARN: Task GMXCluster already executed.")
    else:
        _gmxcluster( input_structure_path,  input_traj_path,  output_pdb_path,  input_index_path,  output_cluster_log_path,  output_rmsd_cluster_xpm_path,  output_rmsd_dist_xvg_path,  properties, **kwargs)