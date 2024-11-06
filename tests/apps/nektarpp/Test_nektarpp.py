#!/usr/bin/env python3

"""Reframe test for Nektarplusplus"""

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps


class FetchNektarplusplus(rfm.RunOnlyRegressionTest):
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


class CompileNektarplusplus(rfm.CompileOnlyRegressionTest):
    descr = 'Build Nektarplusplus'    
    build_system = 'Make'
    fetch_nektarpp = fixture(FetchNektarplusplus, scope="environment")

    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-cray"]

    tags = {"compile"}


    #@require_deps
    @run_before('compile')
    def prepare_build(self):
        NEKTAR_VERSION="5.5.0"
        NEKTAR_LABEL="nektar"
        NEKTAR_ARCHIVE=f"{NEKTAR_LABEL}-v{NEKTAR_VERSION}.tar.gz"
        NEKTAR_NAME=f"{NEKTAR_LABEL}-v{NEKTAR_VERSION}"
        tarball = f'{NEKTAR_ARCHIVE}'
        self.build_prefix = f'{NEKTAR_NAME}'

        fullpath = os.path.join(self.fetch_nektarpp.stagedir, tarball)
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
        # If compilation fails, the test would fail in any case, so nothing to
        # further validate here.
        return True



@rfm.simple_test
class TestNektarpluslus(rfm.RunOnlyRegressionTest):
    """Nektarplusplus Test"""
    descr = 'Test Nektarplusplus'
    
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]

    tags = {"performance", "applications"}
    
    compile_nektarpp = fixture(CompileNektarplusplus, scope="environment")

    num_nodes = 1
    num_tasks_per_node = 32
    num_cpus_per_task = 1
    num_tasks = num_nodes * num_tasks_per_node * num_cpus_per_task
    
    time_limit = "20m"

    executable_opts = ["TGV64_mesh.xml TGV64_conditions.xml"]

    reference = {"archer2:compute": {"Computationtime": (953, -5, 5, "seconds")}}


    @run_before('run')
    def prepare_run(self):

        #num_nodes = 1
        #num_tasks_per_node = 32
        #num_cpus_per_task = 1
        #num_tasks = num_nodes * num_tasks_per_node * num_cpus_per_task
        
        #time_limit = "2h"

        modules = ["cpe/22.12"]

        env_vars = {"CRAY_ADD_RPATH": "yes"}

        self.executable = os.path.join(
            self.compile_nektarpp.stagedir,
            self.compile_nektarpp.build_prefix,
            'build', 'nektar', 'bin/IncNavierStokesSolver'
        )

        #self.executable_opts = ["TGV64_mesh.xml TGV64_conditions.xml"]
    
        #reference = {"archer2:compute": {"Computationtime": (953, -5, 5, "seconds")}}

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("", self.stdout)

    @performance_function("seconds", perf_key="Computationtime")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        print("stdout: ", self.stdout)
        sn.extractsingle(
        r"Total\s+Computation\s+Time\s+=\s+(?P<Computationtime>[0-9]+.[0-9]+)s",
        self.stdout,
        1,
        float,
        )
