"""
Py-chemshell tests

The package py-chemshell allows creating a Python script that submits external chemical simulation codes to the compute nodes.
The packages runs locally and creates task farms and other workflows on the compute nodes.

Supported external applications include: 
- Gulp
- NWchem

"""

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.backends import getlauncher



def parse_chemshell_options(known_options,extra_options):
    """ Creates a dictionary of chemshell options

    Args:
    known_options: slurm options recognised by chemshell
    extra_options: slurm options. May not be supported by chemshell.
    
    """
    chemshell_opts = { }
    for name in known_options:
        # Check if the option matches one of the slurm flags. If it does, then add as a chemshell options
        for opt in extra_options:
            if opt.startswith(f'--{name}='):
                chemshell_opts[name] = opt.split('=')[1]
    return chemshell_opts


def flatten_options(options: dict) -> str:
    """
    Converts a dictionary of (name,value) pairs to a single 
    string formed by the concatenation of  
    -- {name} = {value} strings, separated by 
    an empty space .
    """

    chemshell_opt_flattened= " ".join([  f"--{key}={value}"
                for key,value in options.items()  ])

    return f"'{chemshell_opt_flattened}'"


class PyChemshellBase(rfm.RunOnlyRegressionTest):
    """"
    Pychemshell base class for all py-chemshell tests
    """
    
    maintainers = ["l.parisi@epcc.ed.ac.uk"]
    strict_check = True
    use_multithreading = False
    valid_prog_environs = ["PrgEnv-cray"]
    executable = "./chemshell_wrapper.sh" # The script wraps calling the chemshell launcher
    modules = ["py-chemshell"]
    valid_systems = ["archer2:login"]
    local = True
    partition = "standard" # Is there a way to get the partition from "archer2:compute" instead of hardcoding it ?
    account = "z19" # Hard coded. Could the default be obtained from a configuration file ? Can be overriden from the cli

    @property
    def name(self):
        """Returns the chemshell job name based on the test case name"""

        components=self.test_case.split(".")
        assert len(components)>=2 , "The test case name should end with .py"
        assert components[-1] == "py" , "The test case name should end with .py"
        
        return components[-2]

    @run_before('run')
    def set_chemshell_options(self):
        
        # default options for submission through chemshell
        chem_shell_options  = {
                    "partition" : self.partition, 
                    # Account is mandatory for       chemshell. 
                    # Set z19 as the default, but can be overidden from cli options.
                    "account" : "z19",
                    "nnodes" : self.n_nodes, 
                    "nprocs" : self.num_tasks,
                    "walltime": self.walltime
                    }

        # overrider default options from corresponding slurm options given from the command line
        chem_shell_options.update(parse_chemshell_options(["qos","partition","account"],self.job.cli_options  ) )
        self.env_vars = {
            "CHEMSHELL_SUBMIT_OPTIONS" : flatten_options(chem_shell_options), # chemshell submission options
            "TEST_CASE" : self.test_case, # chemshell python script
            "NAME" : self.name # used by chemshell to specify the name of the slurm job and output files 
            }

    @performance_function("s",perf_key="time")
    def extract_time(self):
        """Extract performance value to compare with reference value"""
        return sn.extractsingle(
            r" Elapsed time of procedure chemsh\..*:\s+(?P<time>\d+\.?\d*)\s+sec",
            f"{self.name}.log",
            "time",
            float,
        )

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found(r"Job\s+\d+\s+has\s+completed", self.stdout)

@rfm.simple_test
class PyChemshellH20HF(PyChemshellBase):
    """"
    Pychemshell H2O HF test

    Computes Hartree-Fock energy for a water molecule using NWchem as a backend. It is mainly a functionality test, as the test is too small to be significant for measuring performance.

    Makes use of the nwchem package.
    
    """

    test_case = "h2o_energy_hf.py"
    
    n_nodes = 1
    num_tasks = 128
    walltime = "0:10:0"
    
@rfm.simple_test
class PyChemshellButanolOpt(PyChemshellBase):
    """"
    Pychemshell Butanol test

    Makes use of the gulp package. This is mainly a functionality test, 
    as the test is too quick to judge performance.

    """

    test_case = "butanol_opt.py"
    
    n_nodes = 1
    num_tasks = 128
    walltime = "0:10:0"