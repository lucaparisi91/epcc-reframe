#!/usr/bin/env python3
"""
R benchmarks

These tests checks that the R programming language is functional.

"""

import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class RscriptBasic(rfm.RunOnlyRegressionTest):
    """ A functional test of the R programming language"""

    descr = "Run a basic R script. Checks packages can be locally installed and basic functionality is present "
    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-gnu"]
    modules = ["cray-R"]
    executable_opts = ["basic_benchmark.R"]
    executable = "Rscript"
    local = True
    prerun_cmds = ["mkdir -p packages"]

    @sanity_function
    def validate_job_run(self):
        """Basic check that any output was produced and the job run until completion"""
        return sn.assert_found("Success", self.stdout)
