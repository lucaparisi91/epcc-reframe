#!/usr/bin/env python3

"""Reframe test for Nektarplusplus"""

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class TestModuleNektarplusplusBase(rfm.RunOnlyRegressionTest):
    """Nektarplusplus Test Base"""

    descr = "Test Nektarplusplus Base"

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]

    tags = {"performance", "applications"}

    modules = ["nektar/5.5.0"]

    env_vars = {"CRAY_ADD_RPATH": "yes"}

    keep_files = ["rfm_job.out"]

    @run_before("run")
    def prepare_run(self):
        """Setup test execution"""

        self.executable = "IncNavierStokesSolver"

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found(
            r"Total\s+Computation\s+Time\s+=\s+",
            self.keep_files[0],
            msg="test_module_nektarplusplus: Completion message not found",
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


@rfm.simple_test
class TestModuleNektarplusplusSerial(TestModuleNektarplusplusBase):
    """Module Nektarplusplus Test Serial"""

    descr = "Test Module Nektarplusplus Serial"

    num_nodes = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    num_tasks = num_nodes * num_tasks_per_node

    time_limit = "20m"

    executable_opts = ["TGV64_mesh.xml TGV64_conditions.xml"]

    reference = {"archer2:compute": {"Computationtime": (953, -0.1, 0.1, "seconds")}}


@rfm.simple_test
class TestModuleNektarplusplusParallel(TestModuleNektarplusplusBase):
    """Module Nektarplusplus Test Parallel"""

    descr = "Test Module Nektarplusplus Parallel"

    num_nodes = 1
    num_tasks_per_node = 32
    num_cpus_per_task = 4
    num_tasks = num_nodes * num_tasks_per_node

    time_limit = "1h"

    executable_opts = ["TGV128_mesh.xml TGV128_conditions.xml"]

    reference = {"archer2:compute": {"Computationtime": (1570, -0.1, 0.1, "seconds")}}


@rfm.simple_test
class TestModuleNektarplusplusMultiNode(TestModuleNektarplusplusBase):
    """Module Nektarplusplus Test Multi Node"""

    descr = "Test Module Nektarplusplus Multi Node"

    num_nodes = 1
    num_tasks_per_node = 32
    num_cpus_per_task = 4
    num_tasks = num_nodes * num_tasks_per_node

    time_limit = "1h"

    executable_opts = ["TGV128_mesh.xml TGV128_conditions.xml"]

    reference = {"archer2:compute": {"Computationtime": (1570, -0.1, 0.1, "seconds")}}
