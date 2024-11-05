#!/usr/bin/env python3

"""Reframe test for XCompact3D"""

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
#import reframe.core.buildsystems.Make
import reframe.utility.udeps as udeps


@rfm.simple_test
class Fetch_Nektarplusplus(rfm.RunOnlyRegressionTest):
    descr = 'Fetch Nektarplusplus'
    NEKTAR_VERSION="5.5.0"
    NEKTAR_LABEL="nektar"
    NEKTAR_ARCHIVE=f"{NEKTAR_LABEL}-v{NEKTAR_VERSION}.tar.gz"
    NEKTAR_NAME=f"{NEKTAR_LABEL}-{NEKTAR_VERSION}"
    version = variable(str, value=NEKTAR_VERSION)
    executable = 'wget'
    executable_opts = [
        f"https://gitlab.nektar.info/nektar/nektar/-/archive/v{NEKTAR_VERSION}/{NEKTAR_ARCHIVE}"
    ]
    local = True
    valid_systems = ['archer2:login']
    valid_prog_environs = ['PrgEnv-cray']

    tags = {"fetch"}

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)

@rfm.simple_test
class Compile_Nektarplusplus(rfm.CompileOnlyRegressionTest):
    descr = 'Build Nektarplusplus'
    build_system = 'Make'
    #build_prefix = variable(str)
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]

    tags = {"compile"}

    @run_after('init')
    def add_dependencies(self):
        self.depends_on('Fetch_Nektarplusplus', udeps.fully)

    @require_deps
    def prepare_build(self, fetch_Nektarplusplus):
        target = Fetch_Nektarplusplus(part='login', environ='PrgEnv-cray')
        NEKTAR_VERSION="5.5.0"
        NEKTAR_LABEL="nektar"
        NEKTAR_ARCHIVE=f"{NEKTAR_LABEL}-v{NEKTAR_VERSION}.tar.gz"
        NEKTAR_NAME=f"{NEKTAR_LABEL}-v{NEKTAR_VERSION}"
        tarball = f'{NEKTAR_ARCHIVE}'
        self.build_prefix = f'{NEKTAR_NAME}'

        fullpath = os.path.join(target.stagedir, tarball)
        env_vars = {"CRAY_ADD_RPATH": "yes"}

        self.prebuild_cmds = [
            f'cp {fullpath} {self.stagedir}',
            f'tar xzf {tarball}',
            f'cd {self.build_prefix}',
            f"source ../cmake_nektarpp.sh {NEKTAR_LABEL}",
        ]
        self.build_system.max_concurrency = 8
        self.build_system.options=["install"]

    @sanity_function
    def validate_compile(self):
        return sn.assert_eq(0, 0)

#@rfm.simple_test
#class NektarpluslusTest(rfm.RegressionTest):
#    """Nektarplusplus Test"""
#
#    valid_systems = ["archer2:compute"]
#    valid_prog_environs = ["*"]
#
#    tags = {"performance", "applications"}
#
#    env_vars = {"CRAY_ADD_RPATH": "yes"}
#
#    NEKTAR_VERSION="5.5.0"
#    NEKTAR_LABEL="nektar"
#    NEKTAR_ARCHIVE=f"{NEKTAR_LABEL}-v{NEKTAR_VERSION}.tar.gz"
#    NEKTAR_NAME=f"{NEKTAR_LABEL}-{NEKTAR_VERSION}"
#
#    time_limit = "2h"
#    build_system = "Make"
#    max_concurrency = 8
#    prebuild_cmds = [
#        f"mkdir -p {NEKTAR_LABEL}",
#        f"cd {NEKTAR_LABEL}",
#        f"wget https://gitlab.nektar.info/nektar/nektar/-/archive/v{NEKTAR_VERSION}/{NEKTAR_ARCHIVE}",
#        f"tar -xvzf {NEKTAR_ARCHIVE}",
#        f"mv {NEKTAR_LABEL}-v{NEKTAR_VERSION} {NEKTAR_NAME}",
#        f"cd {NEKTAR_NAME}",
#        f"source ../../cmake_nektarpp.sh {NEKTAR_NAME}"
#
#    ]
#    max_concurrency = 8
#    builddir = "build"
#    executable = f"{NEKTAR_LABEL}/{NEKTAR_NAME}/bin/IncNavierStokesSolver"
#    executable_opts = ["TGV64_mesh.xml TGV64_conditions.xml"]
#    modules = ["cpe/22.12", "PrgEnv-gnu", "cmake"]
#
#    reference = {"archer2:compute": {"steptime": (6.3, -0.2, 0.2, "seconds")}}
#
#    @sanity_function
#    def assert_finished(self):
#        """Sanity check that simulation finished successfully"""
#        return sn.assert_found("", self.stdout)
#
#    @performance_function("seconds", perf_key="performance")
#    def extract_perf(self):
#        """Extract performance value to compare with reference value"""
#        return sn.extractsingle(
#            r"Averaged time per step \(s\):\s+(?P<steptime>\S+)",
#            self.stdout,
#            "steptime",
#            float,
#        )
