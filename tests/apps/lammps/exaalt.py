"""ReFrame script for lammps dipole test"""

import os

import reframe as rfm
import reframe.utility.sanity as sn

from lammps_base import BuildLAMMPS, LAMMPSBase


class LAMMPSBaseExaalt(LAMMPSBase):
    """ReFrame LAMMPS Base class for Exaalt tests"""

    valid_systems = ["archer2:compute"]
    stream_binary = fixture(BuildLAMMPS, scope="environment")
    num_cpus_per_task = 1
    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    cores = variable(
        dict,
        value={
            "archer2:compute": 128,
        },
    )

    @run_after("init")
    def setup_nnodes(self):
        """sets up number of nodes"""
        if self.current_system.name in ["archer2"]:
            self.num_tasks_per_node = 128

    @run_after("setup")
    def set_executable(self):
        """sets up executable"""
        self.executable = os.path.join(self.stream_binary.build_system.builddir, "lmp")

    @run_before("run")
    def setup_resources(self):
        """sets up number of tasks"""
        self.num_tasks = self.n_nodes * self.cores.get(self.current_partition.fullname, 1)

    @performance_function("kJ/mol", perf_key="energy")
    def extract_energy(self):
        """Extract value of system energy for performance check"""
        return sn.extractsingle(
            r"\s+11000\s+\S+\s+\S+\s+\S+\s+(?P<energy>\S+)",
            self.keep_files[0],
            "energy",
            float,
            item=-1,
        )


@rfm.simple_test
class LAMMPSExaaltSmall(LAMMPSBaseExaalt):
    """ReFrame LAMMPS small test based on NERSC-10 Exaalt benchmark"""

    descr = "Small performance test using NERSC-10 Exaalt LAMMPS benchmark reference run"
    tags = {"applications", "performance"}
    executable_opts = [
        "-in in.snap.test",
        "-var snapdir 2J8_W.SNAP",
        "-var nx 256",
        "-var ny 256",
        "-var nz 256",
        "-var nsteps 100",
    ]

    n_nodes = 16
    time_limit = "30m"

    reference = {
        "archer2:compute": {
            "energy": (-8.7467248, -0.001, 0.001, "kJ/mol"),
            "performance": (0.007, -0.1, None, "ns/day"),
        },
    }


@rfm.simple_test
class LAMMPSExaaltRef(LAMMPSBaseExaalt):
    """ReFrame LAMMPS largescale test based on NERSC-10 Exaalt benchmark"""

    descr = "Largescale performance test using NERSC-10 Exaalt LAMMPS benchmark reference run"
    tags = {"largescale", "applications", "performance"}

    executable_opts = [
        "-in in.snap.test",
        "-var snapdir 2J8_W.SNAP",
        "-var nx 1024",
        "-var ny 1024",
        "-var nz 1024",
        "-var nsteps 100",
    ]

    n_nodes = 1024
    time_limit = "30m"

    reference = {
        "archer2:compute": {
            "energy": (-8.7467248, -0.001, 0.001, "kJ/mol"),
            "performance": (0.004, -0.1, 0.1, "ns/day"),
        },
    }
