""" Make a 3D visualization of the restarts saved in a h5 file 
    Ovito is used for the visualization, and needs to be present

    Usage:

    python3 visualize.py filename
"""

import gamdpy as gp
import numpy as np
import sys
import uuid
import os

argv = sys.argv.copy()
argv.pop(0)  # remove scriptname
executable = None
if __name__ == "__main__":
    if argv:
        filename = argv.pop(0) # get filename 
        executable = "ovito"
    else:
        filename = 'Data/KABLJ_Rho1.200_T0.400_toread.h5' # Used in testing
else:
    filename = 'Data/KABLJ_Rho1.200_T0.400_toread.h5' # Used in testing

# make a filename from UUID based on the host ID and current time
data_file = '/tmp/' + str(uuid.uuid1()) + '.lammps'
dump_file = '/tmp/' + str(uuid.uuid1()) + '.dump'

# Load existing data and save 
output = gp.tools.TrajectoryIO(filename).get_h5()

configuration = gp.Configuration.from_h5(output, 'initial_configuration', include_topology=True)
with open(data_file, 'w') as f:
    print(gp.configuration_to_lammps_data(configuration), file=f)

configuration = gp.Configuration.from_h5(output, 'restarts/restart0000')
with open(dump_file, 'w') as f:
    print(gp.configuration_to_lammps(configuration, timestep=0), file=f)
num_restarts = len(output['restarts'])

print(f'Unpacking {num_restarts} restarts: ', end='', flush=True)
for i in range(1, num_restarts):
    configuration = gp.Configuration.from_h5(output, f'restarts/restart{i:04d}')
    with open(dump_file, 'a') as f:
        print(gp.configuration_to_lammps(configuration, timestep=i), file=f)
    if i%10==0:
        print(i, end='', flush=True)
    else:
        print('.', end='', flush=True)
print()

if executable:
    os.system(executable + ' ' + data_file + ' ' + dump_file )
    os.system('rm ' + data_file + ' ' + dump_file )

