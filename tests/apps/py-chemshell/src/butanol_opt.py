# Unprotonated n-butanol
# using amber ff and scale { 0.5 0.5 }
#
# Adapted from butanol_shift_gamess_gulp in Chemsh3 hybrid tests
#

from chemsh       import *
from chemsh.utils import testutils

butanol = Fragment(coords='butanol.cjson')

ff = '''#
# Amber forcefield entries
# Use with 1-4 scale factors of 0.5 0.5 to match Iris Antes calcs
#
# molmec removes Coulomb terms between bonded atoms 
# and between atoms bonded to a common third atom
keyword molmec
# atom types, with legal connectivities
species
C_T core
H_C core
O_H core
H_O core
# GULP harmonic bond term has an additional coefficient of 0.5
# Therefore we scale k here by 2
harmonic bond kcal
C_T C_T  620.0   1.526
C_T H_C  680.0   1.090
C_T O_H  640.0   1.410
H_O O_H 1106.0   0.960
# GULP angle term has an additional coefficient of 0.5
# Therefore we scale k here by 2
three bond kcal
C_T C_T C_T    80.0  109.50
C_T C_T H_C   100.0  109.50
C_T C_T O_H   100.0  109.50
C_T H_C H_C    70.0  109.50
O_H C_T H_O   110.0  108.50
C_T H_C O_H    70.0  109.50
O_H H_O H_O    94.0  104.50
torsion bond kcal
# adjusted by factor of 9 relative to amber value of 1.4
X C_T C_T X   0.1555555  3  0.0
# adjusted by factor of 3 relative to amber value of 1.4
X C_T O_H X   0.1666666  3  0.0
# scale vdw by 0.5
# last number in entries is a cutoff
lennard 12 6 kcal x13 0.5
 H_O   H_O  0.0  0.0   99.9
 H_O   H_C  0.0  0.0   99.9
 H_O   O_H  0.0  0.0   99.9
 H_O   C_T  0.0  0.0   99.9
 H_C   H_C     7516.0     21.73    99.9
 H_C   O_H    68280.0    125.3     99.9
 H_C   C_T    97170.0    126.9     99.9
 O_H   O_H   581800.0    699.7     99.9
 O_H   C_T   791500.0    693.1     99.9
 C_T   C_T  1043000.0    675.6     99.9
# scale 1-4 Coulomb by 0.5 by subtraction
coulomb o14
 C_T C_T 0.5 0.0 99.9
 C_T H_C 0.5 0.0 99.9
 C_T O_H 0.5 0.0 99.9
 C_T H_O 0.5 0.0 99.9
 H_C H_C 0.5 0.0 99.9
 H_C O_H 0.5 0.0 99.9
 H_C H_O 0.5 0.0 99.9
 O_H O_H 0.5 0.0 99.9
 O_H H_O 0.5 0.0 99.9
 H_O H_O 0.5 0.0 99.9
'''


mm = GULP(frag=butanol, ff=ff, molecule=True)

opt = Opt(theory=mm, 
          algorithm="lbfgs", tolerance=0.0003, trust_radius="energy",
          maxcycle=400, maxene=300).run()

ecalc = opt.result.energy

# Test result
eref = 0.01715176


testutils.validate(ecalc, eref)
