"""Contains py-chemshell tests

The package py-chemshell allows creating a Python script that submits external chemical simulation codes to the compute nodes.
The packages runs locally and creates task farms and other workflows on the compute nodes.

Supported external applications include: 
- Gulp
- NWchem

"""

import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class PyChemshellFunctionality(rfm.RunOnlyRegressionTest):
    """"
    Pychemshell functionality test
    """
    
    maintainers = ["l.parisi@epcc.ed.ac.uk"]
    strict_check = True
    use_multithreading = False
    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-cray"]
    executable = "./test_submit_compute_nodes.sh"
    modules = ["py-chemshell"]
    local = True

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found(r"Job\s+\d+\s+has\s+completed", self.stdout)

    @performance_function("s",perf_key="time")
    def extract_time(self):
        """Extract performance value to compare with reference value"""
        return sn.extractsingle(
            r" Elapsed time of procedure chemsh.tasks.sp.run:\s+(?P<time>\d+\.?\d*)\s+sec",
            "pycs-nwchem.log",
            "time",
            float,
        )
