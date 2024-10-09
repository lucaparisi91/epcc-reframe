"""ReFrame script for lammps dipole test"""

import reframe as rfm

from lammps_base import LAMMPSBase

#  class DownloadLAMMPS(rfm.RunOnlyRegressionTest):
#      """Download LAMMPS"""
#      descr = "Download LAMMPS tarball"""
#      local = True
#      valid_prog_environs = ["PrgEnv-cray"]
#      executable =


class BuildLAMMPS(rfm.CompileOnlyRegressionTest):
    """Compile LAMMPS"""

    build_system = "CMake"
    modules = ["cpe", "cray-fftw", "cmake", "eigen"]
    sourcesdir = "https://github.com/lammps/lammps.git"
    builddir = "lammps"
    local = True

    @run_before("compile")
    def prepare_build(self):
        """Prepare build"""
        #  export LD_LIBRARY_PATH=$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH
        self.env_vars["LD_LIBRARY_PATH"] = self.env_vars["CRAY_LD_LIBRARY_PATH"] + self.env_vars["LD_LIBRARY_PATH"]
        self.build_system.clags = [
            "-C ../cmake/presets/most.cmake",
            "-D BUILD_MPI=on",
            "-D BUILD_SHARED_LIBS=yes",
            "-D CMAKE_CXX_COMPILER=CC",
            '-D CMAKE_CXX_FLAGS="-O2" ',
            "-D CMAKE_INSTALL_PREFIX=/work/y07/shared/apps/core/lammps/13Feb2024",
            "-D EIGEN3_INCLUDE_DIR=/work/y07/shared/libs/core/eigen/3.4.0/include",
            "-D FFT=FFTW3",
            "-D FFTW3_INCLUDE_DIR=${FFTW_INC}",
            "-D FFTW3_LIBRARY=${FFTW_DIR}/libfftw3_mpi.so",
            "-D LAMMPS_SIZES=bigbig",
        ]


@rfm.simple_test
class ExaaltLammpsSmall(LAMMPSBase):
    """ReFrame LAMMPS small test based on NERSC-10 Exaalt benchmark"""

    valid_systems = ["archer2:compute"]
    #  modules = ["lammps"]
    stream_binary = fixture(BuildLAMMPS, scope="environment")
    descr = "Small performance test using NERSC-10 Exaalt LAMMPS benchmark reference run"
    executable_opts = [
        "-in in.snap.test",
        "-var snapdir 2J8_W.SNAP",
        "-var nx 256",
        "-var ny 256",
        "-var nz 256",
        "-var nsteps 100",
    ]

    n_nodes = 16
    num_cpus_per_task = 1
    time_limit = "30m"
    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    cores = variable(
        dict,
        value={
            "archer2:compute": 128,
        },
    )

    reference = {
        "archer2:compute": {
            "performance": (0.009, -0.1, 0.1, "ns/day"),
        },
    }

    @run_after("init")
    def setup_nnodes(self):
        """sets up number of nodes"""
        if self.current_system.name in ["archer2"]:
            self.num_tasks_per_node = 128

    @run_before("run")
    def setup_resources(self):
        """sets up number of tasks"""
        self.num_tasks = self.n_nodes * self.cores.get(self.current_partition.fullname, 1)
