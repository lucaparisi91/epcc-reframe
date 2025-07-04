# flake8: noqa
# NWChem HF single point energy

from chemsh       import *
from chemsh.utils import testutils

water = Fragment(coords="water.cjson")


nwchem = NWChem(frag=water, method="hf", basis="3-21g")

# TODO: sp = SP(theory=nwchem, frag=water)
sp = SP(theory=nwchem, gradients=True)

sp.run()

ecalc = sp.result.energy

# Test result
eref = -75.58528778


testutils.validate(ecalc, eref)
