
gmx_command = "gmx_mpi"
mpi_command = "mpirun -np "

def mpirun_command(process):
    return  mpi_command + "{} gmx_mpi ".format(process)
