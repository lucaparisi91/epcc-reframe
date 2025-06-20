#!/usr/bin/env python3
"""
R benchmarks

These tests checks that the R programming language is functional.

"""

import reframe as rfm
import reframe.utility.sanity as sn
import os

class RscriptBase(rfm.RunOnlyRegressionTest):
    """ A functional test of the R programming language"""

    descr = "Run a basic R script. Checks packages can be locally installed and basic functionality is present "
    valid_prog_environs = ["PrgEnv-gnu"]
    modules = ["cray-R"]
    executable = "Rscript"    

    @sanity_function
    def validate_job_run(self):
        """Basic check that any output was produced and the job run until completion"""
        return sn.assert_found("Success", self.stdout)


class RscriptInstall( RscriptBase ):
    """ Tests installing packages with R on the login nodes """

    valid_systems = ["archer2:login"]
    local = True
    executable_opts = ["install_benchmark_packages.R"]

    @run_before("run")
    def setup_R_library(self):
        """ Setup R library path
        
        The default R library directory is on the home folder, which is not writable on the compute nodes and pollute user's environment. This sets environment variables so that packages are written/read in a local directory.
        """
        
        self.libs_path = os.path.join(self.stagedir, ".libs")

        self.env_vars = {
            "R_LIBS_USER" : self.libs_path
            }

        self.prerun_cmds = [f"mkdir -p {self.libs_path}" ]


@rfm.simple_test
class RscriptRun( RscriptBase ):

    """ Runs a basic R functionality test. Uses packages installed locally in a previous test."""


    valid_systems = ["archer2:login","archer2:compute"]
    executable_opts = ["run_benchmark.R"]
    library =  fixture(RscriptInstall, scope="session")

    @run_before("run")
    def setup_R_library(self):
        """ Setup R library path
        
        Set the library path to where packages were installed in the R package install test.
        """

        self.libs_path = self.library.libs_path

        self.env_vars = {
            "R_LIBS_USER" : self.libs_path
            }