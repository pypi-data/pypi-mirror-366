import os
import sys
import uuid

OMPI="OMPI"
OMPI_HOSTFILE_FLAG="-hostfile"
IMPI="IMPI"
IMPI_HOSTFILE_FLAG="-hostfile"
SLURM="SLURM"
SLURM_HOSTLIST_FLAG="--nodelist="

DEFAULT_MPI="IMPI"

def config_multinode( properties , all_mpi=True):
    mpi_env = os.environ.get("MULTINODE_MPI_ENV")
    if mpi_env is None:
        print("WARNING: NO MULTINODE_MPI_ENVIRONMENT DEFINED. Setting default MPI as " + DEFAULT_MPI) 
        mpi_env = DEFAULT_MPI
    else: 
        print("Configuring multinode task with MPI environment " + mpi_env)
    mpi_extra_flags = os.environ.get("MULTINODE_MPI_EXTRA_FLAGS") 
    num_nodes = int(os.environ["COMPSS_NUM_NODES"])
    num_threads = int(os.environ["COMPSS_NUM_THREADS"])
    if all_mpi :
        hostnames = os.environ["COMPSS_HOSTNAMES"]
        total_threads = num_nodes*num_threads
        properties["mpi_np"] = num_nodes * num_threads
        os.environ["OMP_NUM_THREADS"] = "1"
    else :
        properties["num_omp_threads"] = num_threads
        properties["mpi_np"] = num_nodes
    properties["mpi_flags"] = create_mpi_flags(mpi_env.upper(), mpi_extra_flags, num_threads)

def create_mpi_flags(mpi_env, mpi_extra_flags, num_threads):
    
    hostnames = os.environ["COMPSS_HOSTNAMES"]
    if mpi_env == SLURM:
        mpi_flags = [SLURM_HOSTLIST_FLAG + os.environ['SLURM_NODELIST']]
    elif mpi_env == OMPI:
        hostlist_file=str(uuid.uuid1())+".hostfile"
        create_hostfile_ompi(hostlist_file, hostnames, num_threads)
        mpi_flags = [OMPI_HOSTFILE_FLAG, hostlist_file]
    elif mpi_env == IMPI:
        hostlist_file=str(uuid.uuid1())+".hostfile"
        create_hostfile_impi(hostlist_file, hostnames)
        mpi_flags = [OMPI_HOSTFILE_FLAG, hostlist_file]
    else :
        print("ERROR: Undefined MPI enviroment: " + mpi_env)
        raise Exception("Undefined MPI enviroment: " + mpi_env)

    if mpi_extra_flags is None:
        return mpi_flags
    else:
        return mpi_flags + mpi_extra_flags.split(" ")

def create_hostfile_impi(hostlist_file, hostnames):
    with open(hostlist_file, "w") as h_file:
        h_file.write(hostnames.replace(",","\n"))

def create_hostfile_ompi(hostlist_file, hostnames, num_threads):
    host_slots=dict()
    try:
        for hname in hostnames.split(','):
            slots = host_slots.get(hname,0)
            host_slots[hname]=slots + num_threads
    except Exception as e:
        print("An exception occurred: " + str(e))
        raise e

    # Create hostfile
    with open(hostlist_file, "w") as h_file:
        for hname, slots in host_slots.items():
            h_file.write(str(hname) + " slots=" + str(slots) + "\n")

def pop_pmi(environ_dic):
    environ_dic.pop('PMI_FD', None)
    environ_dic.pop('PMI_JOBID', None)
    environ_dic.pop('PMI_RANK', None)
    environ_dic.pop('PMI_SIZE', None)

