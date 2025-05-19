"""ReFrame base module for LAMMPS tests"""

import os

import reframe as rfm
import reframe.utility.sanity as sn


class BuildLAMMPS(rfm.CompileOnlyRegressionTest):
    """Compile LAMMPS"""

    build_system = "CMake"
    modules = ["cpe", "cray-fftw", "cmake", "eigen"]
    sourcesdir = "https://github.com/lammps/lammps.git"
    sourcepath = "src"
    prebuild_cmds = ["git checkout stable_29Aug2024_update2"]
    local = True
    build_locally = False

    @run_before("compile")
    def prepare_build(self):
        """Prepare build"""
        self.build_system.max_concurrency = 8
        self.build_system.builddir = f"{self.stagedir}/lammps_build"
        #  Equivalent to:
        #  export LD_LIBRARY_PATH=$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH
        self.env_vars["LD_LIBRARY_PATH"] = os.getenv("CRAY_LD_LIBRARY_PATH") + ":" + os.getenv("LD_LIBRARY_PATH")
        self.build_system.config_opts = [
            f"-C {self.stagedir}/cmake/presets/most.cmake",
            "-D BUILD_MPI=on",
            "-D BUILD_SHARED_LIBS=yes",
            "-D CMAKE_CXX_COMPILER=CC",
            '-D CMAKE_CXX_FLAGS="-O2" ',
            f"-D CMAKE_INSTALL_PREFIX={self.stagedir}/install",
            "-D EIGEN3_INCLUDE_DIR=/work/y07/shared/libs/core/eigen/3.4.0/include",
            "-D FFT=FFTW3",
            "-D FFTW3_INCLUDE_DIR=${FFTW_INC}",
            "-D FFTW3_LIBRARY=${FFTW_DIR}/libfftw3_mpi.so",
            "-D LAMMPS_SIZES=bigbig",
            f"{self.stagedir}/cmake",
        ]

    @sanity_function
    def sanity_executable_exists(self):
        """Check that the executable was created"""
        build_dir = f"{self.stagedir}/lammps_build"
        return sn.path_exists(os.path.join(build_dir, "lmp"))


class LAMMPSBase(rfm.RunOnlyRegressionTest):
    """ReFrame base class for LAMMPS tests"""

    valid_prog_environs = ["PrgEnv-cray", "intel", "nvidia-mpi", "rocm-PrgEnv-cray"]
    executable = "lmp"
    extra_resources = {"qos": {"qos": "standard"}}

    keep_files = ["log.lammps"]

    maintainers = ["r.apostolo@epcc.ed.ac.uk"]
    strict_check = True
    tags = {"applications", "performance"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found(r"Total wall time", self.keep_files[0])

    @performance_function("ns/day", perf_key="performance")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        return sn.extractsingle(
            r"Performance:\s+(?P<perf>\S+)",
            self.keep_files[0],
            "perf",
            float,
            -1,
        )
