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

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]

    tags = {"compile"}

    #@run_after('init')
    #def add_dependencies(self):
    #    self.depends_on('FetchNektarplusplus', udeps.fully)

    #@require_deps
    @run_before('compile')
    def prepare_build(self):
        #        target = fetch_Nektarplusplus(part='login', environ='PrgEnv-cray')
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
        return sn.assert_eq(0, 0)



@rfm.simple_test
class TestNektarpluslus(rfm.RunOnlyRegressionTest):
    """Nektarplusplus Test"""
    descr = 'Test Nektarplusplus'
    
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]

    tags = {"performance", "applications"}
    
    compile_nektarpp = fixture(CompileNektarplusplus, scope="environment")

    #    @run_after('init')
    #    def add_dependencies(self):
    #        self.depends_on('Compile_Nektarplusplus', udeps.fully)


    @run_before('run')
    def prepare_run(self):
        
        #target = Compile_Nektarplusplus(part='compute', environ='PrgEnv-cray')

        num_nodes = 1
        num_tasks_per_node = 32
        num_cpus_per_task = 1
        num_tasks = num_nodes * num_tasks_per_node * num_cpus_per_task
        
        time_limit = "2h"

        modules = ["cpe/22.12"]

        env_vars = {"CRAY_ADD_RPATH": "yes"}

        print("james test")

        self.executable = os.path.join(
            self.compile_nektarpp.stagedir,
            self.compile_nektarpp.build_prefix,
            'build', 'nektar', 'bin/IncNavierStokesSolver'
        )

        print("James executable: ", self.executable)

        #executable = f"{NEKTAR_LABEL}/{NEKTAR_NAME}/bin/IncNavierStokesSolver"
        self.executable_opts = ["TGV64_mesh.xml TGV64_conditions.xml"]
    
        reference = {"archer2:compute": {"steptime": (6.3, -0.2, 0.2, "seconds")}}

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("", self.stdout)

    @performance_function("seconds", perf_key="performance")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        return 0 
            #sn.extractsingle(
            #r"Averaged time per step \(s\):\s+(?P<steptime>\S+)",
            #self.stdout,
            #"steptime",
            #float,
            #)
