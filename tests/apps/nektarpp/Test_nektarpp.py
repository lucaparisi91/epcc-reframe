#!/usr/bin/env python3

"""Reframe test for Nektarplusplus"""

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.utility import udeps


class FetchNektarplusplus(rfm.RunOnlyRegressionTest):
    """Test access to nektarplusplus source code"""
    descr = "Fetch Nektarplusplus"
    nektar_version = "5.5.0"
    nektar_label = "nektar"
    nektar_archive = f"{nektar_label}-v{nektar_version}.tar.gz"
    nektar_name = f"{nektar_label}-{nektar_version}"
    version = variable(str, value=nektar_version)
    executable = "wget"
    executable_opts = [f"https://gitlab.nektar.info/nektar/nektar/-/archive/v{nektar_version}/{nektar_archive}"]
    local = True
    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-cray"]

    tags = {"fetch"}

    @sanity_function
    def validate_download(self):
        """Validate download of source code sucessful"""
        return sn.assert_eq(self.job.exitcode, 0)


class CompileNektarplusplus(rfm.CompileOnlyRegressionTest):
    """Test compilation of nektarplusplus"""
    descr = "Build Nektarplusplus"
    build_system = "Make"
    fetch_nektarpp = fixture(FetchNektarplusplus, scope="environment")

    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-cray"]

    tags = {"compile"}

    @run_before("compile")
    def prepare_build(self):
        """Prepare environment for build"""
        nektar_version = "5.5.0"
        nektar_label = "nektar"
        nektar_archive = f"{nektar_label}-v{nektar_version}.tar.gz"
        nektar_name = f"{nektar_label}-v{nektar_version}"
        tarball = f"{nektar_name}"
        self.build_prefix = f"{nektar_name}"

        fullpath = os.path.join(self.fetch_nektarpp.stagedir, tarball)
        env_vars = {"CRAY_ADD_RPATH": "yes"}

        self.prebuild_cmds = [
            f"cp {fullpath} {self.stagedir}",
            f"tar xzf {tarball}",
            f"cd {self.build_prefix}",
            f"source ../cmake_nektarpp.sh {nektar_label}",
        ]
        self.build_system.max_concurrency = 8
        self.build_system.options = ["install"]

    @sanity_function
    def validate_compile(self):
        """Validate compilation by checking existance of binary"""
        return sn.path_isfile("nektar-v5.5.0/build/nektar/bin/IncNavierStokesSolver")


@rfm.simple_test
class TestNektarpluslus(rfm.RunOnlyRegressionTest):
    """Nektarplusplus Test"""

    descr = "Test Nektarplusplus"

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]

    tags = {"performance", "applications"}

    compile_nektarpp = fixture(CompileNektarplusplus, scope="environment")

    num_nodes = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    num_tasks = num_nodes * num_tasks_per_node * num_cpus_per_task

    time_limit = "20m"

    keep_files = ["rfm_job.out"]

    executable_opts = ["TGV64_mesh.xml TGV64_conditions.xml"]

    reference = {"archer2:compute": {"Computationtime": (953, -0.1, 0.1, "seconds")}}

    @run_before("run")
    def prepare_run(self):

        modules = ["cpe/22.12"]

        env_vars = {"CRAY_ADD_RPATH": "yes"}

        self.executable = os.path.join(
            self.compile_nektarpp.stagedir,
            self.compile_nektarpp.build_prefix,
            "build",
            "nektar",
            "bin/IncNavierStokesSolver",
        )

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found(
            r"Total\s+Computation\s+Time\s+=\s+",
            self.keep_files[0],
            msg="Test_Nektarplusplus: Completion message not found",
        )

    @performance_function("seconds", perf_key="Computationtime")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        return sn.extractsingle(
            r"Total\s+Computation\s+Time\s+=\s+(?P<Comptime>[0-9]+.[0-9]+)s",
            self.keep_files[0],
            "Comptime",
            float,
        )
