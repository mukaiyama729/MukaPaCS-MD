
gmx_command = "gmx_mpi"
mpi_command = "mpirun -np "

def mpirun_command(process, use_gpu=True):
    if use_gpu:
        return mpi_command + "{} gmx_mpi ".format(process)
    else:
        return mpi_command + "{} -mca coll_hcoll_enable 0 gmx_mpi ".format(process)
