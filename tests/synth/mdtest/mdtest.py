#!/usr/bin/env python3
"""ReFrame test for mdtest benchmark."""

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import performance_function, run_before, sanity_function

@rfm.simple_test
class Mdtest(rfm.RunOnlyRegressionTest):
    """Run mdtest with the same configuration as test-run/mdtest/submit.sh."""

    valid_systems = ["cirrus-ex:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]
    modules = ["mdtest-gcc"]
    
    num_tasks = 288
    num_tasks_per_node = 288
    num_cpus_per_task = 1
    time_limit = "20m"
    executable = "mdtest"
    executable_opts = ["-F", "-C", "-T", "-r", "-n", "10000", "-N", "288", "-u", "-d", "test_dir"]
    env_vars = {
        "OMP_NUM_THREADS": "1",
        "OMP_PLACES": "cores",
    }

    postrun_cmds = ["rm -rf test_dir"]

    tags = {"performance", "io"}

    @run_before("run")
    def set_run_options(self):
        """Set srun options for the job launcher.
                """
        self.job.launcher.options = ["--mem=0", "--hint=nomultithread", "--distribution=block:block"]

    @sanity_function
    def assert_mdtest_finished(self):
        """Sanity checks."""
        return sn.assert_found(r"SUMMARY:\s+\(of\s+1\s+iterations\)", self.stdout)

    @performance_function("ops/s")
    def file_creation_mean(self):
        """Extract mean file creation rate from mdtest summary."""
        return sn.extractsingle(
            r"^\s*File creation\s*:\s*\S+\s+\S+\s+(\S+)",
            self.stdout,
            1,
            float,
            item=-1,
        )

    @performance_function("ops/s")
    def file_stat_mean(self):
        """Extract mean file stat rate from mdtest summary."""
        return sn.extractsingle(
            r"^\s*File stat\s*:\s*\S+\s+\S+\s+(\S+)",
            self.stdout,
            1,
            float,
            item=-1,
        )

    @performance_function("ops/s")
    def file_removal_mean(self):
        """Extract mean file removal rate from mdtest summary."""
        return sn.extractsingle(
            r"^\s*File removal\s*:\s*\S+\s+\S+\s+(\S+)",
            self.stdout,
            1,
            float,
            item=-1,
        )

    @performance_function("ops/s")
    def tree_creation_mean(self):
        """Extract mean tree creation rate from mdtest summary."""
        return sn.extractsingle(
            r"^\s*Tree creation\s*:\s*\S+\s+\S+\s+(\S+)",
            self.stdout,
            1,
            float,
            item=-1,
        )
    
    @performance_function("ops/s")
    def tree_removal_mean(self):
        """Extract mean tree removal rate from mdtest summary."""
        return sn.extractsingle(
            r"^\s*Tree removal\s*:\s*\S+\s+\S+\s+(\S+)",
            self.stdout,
            1,
            float,
            item=-1,
        )

