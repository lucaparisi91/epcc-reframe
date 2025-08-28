#!/usr/bin/env python3

"""Reframe test for Nemo"""

import os
import reframe as rfm
import reframe.utility.sanity as sn

class FetchXIOS2(rfm.RunOnlyRegressionTest):
    """
    Fetch XIOS2 source code
    
    Warning: The ipsl repository can occasionally be unreliable
    
    """

    descr = "Fetch XIOS2"
    version = variable(str, value="head")
    executable = "svn"
    src = "xios2"   
    executable_opts = ["co", f"https://forge.ipsl.fr/ioserver/svn/XIOS2/trunk","xios2"]
    local = True
    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-gnu"]

    tags = {"fetch"}
    
    @sanity_function
    def validate_download(self):
        """Validate download of source code sucessful"""
        return sn.assert_eq(self.job.exitcode, 0)

@rfm.simple_test
class CompileXIOS2(rfm.CompileOnlyRegressionTest):
    """Test compilation of XIOS2"""

    descr = "Build XIOS2"
    build_system = "CustomBuild"
    fetch_xios2 = fixture(FetchXIOS2, scope="environment")
    src = FetchXIOS2.src
    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-gnu"]
    modules = ["cray-hdf5-parallel","cray-netcdf-hdf5parallel"]

    tags = {"compile"}


    @run_before("compile")
    def prepare_build(self):
        """Prepare environment for build"""
        
        xios2_src_fullpath = os.path.join(self.fetch_xios2.stagedir, self.src)
        
        self.prebuild_cmds = [
            f"cp -r {xios2_src_fullpath} {self.stagedir}",
            f"cp build_xios2/arch/*  {self.src}/arch "
        ]

        self.build_system.commands = [
            f"cd {self.src}",
            "./make_xios --job 16 --dev --arch ARCHER2_GNU"
        ]


    @sanity_function
    def validate_compile(self):
        """Validate compilation by checking existance of binary"""
        return sn.path_isfile(f"{self.src}/bin/xios_server.exe")

class FetchNemo(rfm.RunOnlyRegressionTest):
    """
    Fetch Nemo source source code 
    
    Warning: The ipsl repository can occasionally be unreliable
    
    """

    descr = "Fetch Nemo"
    version = "4.2.2"
    executable = "wget"
    nemo_label = f"nemo-{self.version}"
    executable_opts = [f"https://forge.nemo-ocean.eu/nemo/nemo/-/archive/{self.version}/{self.nemo_label}.tar.gz","-o",f"{self.nemo_label}.tar.gz"]

    local = True
    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-gnu"]

    tags = {"fetch"}
    
    @sanity_function
    def validate_download(self):
        """Validate download of source code sucessful"""
        return sn.assert_eq(self.job.exitcode, 0)

@rfm.simple_test
class CompileNemo(rfm.CompileOnlyRegressionTest):
    """Test compilation of Nemo"""

    descr = "Build Nemo"
    build_system = "CustomBuild"
    fetch_nemo = fixture(FetchNemo, scope="environment")
    compile_xios2 = fixture(CompileXIOS2, scope="environment")

    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-gnu"]
    modules = ["cray-hdf5-parallel","cray-netcdf-hdf5parallel"]

    tags = {"compile"}
    test_case = "BENCH"
    experiment_name = "BENCH_GCC"

    @run_before("compile")
    def prepare_build(self):
        """Prepare environment for build"""

        nemo_label = self.fetch_nemo.nemo_label
        archive_name = f"{nemo_label}.tar.gz"
        nemo_archive = os.path.join(self.fetch_nemo.stagedir, archive_name)
        xios2_full_src = os.path.join(self.fetch_xios2.stagedir, "xios2")

        self.prebuild_cmds = [
            f"cp -r {nemo_archive} {self.stagedir}",
            f"tar -xzf {archive_name}",
            f"cp build_nemo/arch/arch-ARCHER2_GNU.fcm  {nemo_label}/arch ",
            f"cd {nemo_label}",
            r"sed -i -e  \"s/FC_MODSEARCH => ''/FC_MODSEARCH => '-J',/g\" ./ext/FCM/lib/Fcm/Config.pm",
            f"export CFLAGS=-I{xios2_full_src}/include",
            f"export LFLAGS=-L{xios2_full_src}/lib"
        ]

        self.build_system.commands = [

            f"./makenemo -n {self.experiment_name}_GCC -a {self.test_case} -m ARCHER2_GNU -j 16"
        ]

    @sanity_function
    def validate_compile(self):
        """Validate compilation by checking existance of binary"""
        return sn.path_isfile(f"{self.nemo_label}/{self.experiment_name}/EXP00/nemo")
    

# class TestNektarplusplusBase(rfm.RunOnlyRegressionTest):
#     """Nektarplusplus Test"""

#     descr = "Test Nektarplusplus"

#     valid_systems = ["archer2:compute"]
#     valid_prog_environs = ["PrgEnv-gnu"]

#     tags = {"performance", "applications"}

#     compile_nektarpp = fixture(CompileNektarplusplus, scope="environment")

#     modules = []

#     env_vars = {"CRAY_ADD_RPATH": "yes"}

#     keep_files = ["rfm_job.out"]

#     @run_before("run")
#     def prepare_run(self):
#         """set up job execution"""

#         self.executable = os.path.join(
#             self.compile_nektarpp.stagedir,
#             self.compile_nektarpp.build_prefix,
#             "build",
#             "nektar",
#             "bin/IncNavierStokesSolver",
#         )

#     @sanity_function
#     def assert_finished(self):
#         """Sanity check that simulation finished successfully"""
#         return sn.assert_found(
#             r"Total\s+Computation\s+Time\s+=\s+",
#             self.keep_files[0],
#             msg="Test_Nektarplusplus: Completion message not found",
#         )

#     @performance_function("seconds", perf_key="Computationtime")
#     def extract_perf(self):
#         """Extract performance value to compare with reference value"""
#         return sn.extractsingle(
#             r"Total\s+Computation\s+Time\s+=\s+(?P<Comptime>[0-9]+.[0-9]+)s",
#             self.keep_files[0],
#             "Comptime",
#             float,
#         )


# @rfm.simple_test
# class TestNektarpluslusSerial(TestNektarplusplusBase):
#     """Nektarplusplus Test Serial"""

#     descr = "Test Nektarplusplus Serial"

#     num_nodes = 1
#     num_tasks_per_node = 1
#     num_cpus_per_task = 1
#     num_tasks = num_nodes * num_tasks_per_node

#     time_limit = "20m"

#     executable_opts = ["TGV64_mesh.xml TGV64_conditions.xml"]

#     reference = {"archer2:compute": {"Computationtime": (953, -0.1, 0.1, "seconds")}}


# @rfm.simple_test
# class TestNektarpluslusParallel(TestNektarplusplusBase):
#     """Nektarplusplus Test Parallel"""

#     descr = "Test Nektarplusplus Parallel"

#     num_nodes = 1
#     num_tasks_per_node = 32
#     num_cpus_per_task = 4
#     num_tasks = num_nodes * num_tasks_per_node

#     time_limit = "1h"

#     executable_opts = ["TGV128_mesh.xml TGV128_conditions.xml"]

#     reference = {"archer2:compute": {"Computationtime": (1570, -0.1, 0.1, "seconds")}}


# @rfm.simple_test
# class TestNektarpluslusMultiNode(TestNektarplusplusBase):
#     """Nektarplusplus Test Multi Node"""

#     descr = "Test Nektarplusplus Multi Node"

#     num_nodes = 4
#     num_tasks_per_node = 8
#     num_cpus_per_task = 16
#     num_tasks = num_nodes * num_tasks_per_node

#     time_limit = "1h"

#     executable_opts = ["TGV128_mesh.xml TGV128_conditions.xml"]

#     reference = {"archer2:compute": {"Computationtime": (1570, -0.1, 0.1, "seconds")}}
