#!/usr/bin/env python3

"""Reframe test for XCompact3D"""

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class NektarpluslusTest(rfm.RegressionTest):
    """Nektarplusplus Test"""

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["*"]

    tags = {"performance", "applications"}

    num_nodes = 1
    num_tasks_per_node = 32
    num_cpus_per_task = 1
    num_tasks = num_nodes * num_tasks_per_node * num_cpus_per_task

    env_vars = {"CRAY_ADD_RPATH": "yes"}

    NEKTAR_VERSION="5.5.0"
    NEKTAR_LABEL="nektar"
    NEKTAR_ARCHIVE=f"{NEKTAR_LABEL}-v{NEKTAR_VERSION}.tar.gz"
    NEKTAR_NAME=f"{NEKTAR_LABEL}-{NEKTAR_VERSION}"

    time_limit = "2h"
    build_system = "Make"
    prebuild_cmds = [
        f"mkdir -p {NEKTAR_LABEL}",
        f"cd {NEKTAR_LABEL}",
        f"wget https://gitlab.nektar.info/nektar/nektar/-/archive/v{NEKTAR_VERSION}/{NEKTAR_ARCHIVE}",
        f"tar -xvzf {NEKTAR_ARCHIVE}",
        f"mv {NEKTAR_LABEL}-v{NEKTAR_VERSION} {NEKTAR_NAME}",
        f"cd {NEKTAR_NAME}",
        f"source ../../cmake_nektarpp.sh {NEKTAR_NAME}"

    ]
    builddir = "build"
    executable = f"{NEKTAR_LABEL}/{NEKTAR_NAME}/bin/IncNavierStokesSolver"
    executable_opts = ["TGV64_mesh.xml TGV64_conditions.xml"]
    modules = ["cpe/22.12", "PrgEnv-gnu", "cmake"]

    reference = {"archer2:compute": {"steptime": (6.3, -0.2, 0.2, "seconds")}}

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("", self.stdout)

    @performance_function("seconds", perf_key="performance")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        return sn.extractsingle(
            r"Averaged time per step \(s\):\s+(?P<steptime>\S+)",
            self.stdout,
            "steptime",
            float,
        )
