""" Minimal example for calculing rdf from existing data """

import os
import matplotlib.pyplot as plt
import gamdpy as gp
import numpy as np

file_to_read = "Data/NVT_N4000_T2.0_rho1.2_KABLJ_rumd3/TrajectoryFiles"
max_plot_points = 100_000

if not os.path.isdir(file_to_read):
    print(f"This example needs {file_to_read} to be present")
    exit()

# Load existing data
output = gp.tools.TrajectoryIO(file_to_read).get_h5()
# Read number of particles N and dimensions from data
nblocks, nconfs, N, D = output['block/positions'].shape
# Set up the configuration object
configuration = gp.Configuration(D=D, N=N)
configuration.simbox = gp.Orthorhombic(D, output.attrs['simbox_initial'])

volume = configuration.get_volume()
rho = N/volume

# Extract potential energy (U), virial (W), and kinetic energy (K)
# first_block can be used to skip the initial "equilibration".
U, W, K = gp.extract_scalars(output, ['U', 'W', 'K'], first_block=0)

mU = np.mean(U)
mW = np.mean(W)
mK = np.mean(K)

# Hack to find parts of data not valid
print(np.mean(K>0))

# Time
dt = output.attrs['dt']
time = np.arange(len(U)) * dt * output.attrs['scalar_saver/steps_between_output']

# Compute mean kinetic temperature
dof = D * N - D  # degrees of freedom
T_kin = 2 * mK / dof

# Compute mean pressure
P = rho * T_kin + mW / volume

# Compute W-U correlations
dU = U - mU
dW = W - mW
gamma = np.dot(dW,dU)/np.dot(dU,dU)
R = np.dot(dW,dU)/(np.dot(dW,dW)*np.dot(dU,dU))**0.5

# Plot 
plotindex = range(len(U))
print(len(plotindex))
if len(U)>max_plot_points:
    step = int(len(U)/max_plot_points+1)
    plotindex = plotindex[::step]
print(len(plotindex))

title = f'N={N},  rho={rho:.3f},  Tkin={np.mean(T_kin):.3f},  P={np.mean(P):.3f},  R={R:.3f},  gamma={gamma:.3f}'

fig, axs = plt.subplots(3, 1, figsize=(8, 9), sharex=True)
fig.subplots_adjust(hspace=0.00)  # Remove vertical space between axes
axs[0].set_title(title)
axs[0].set_ylabel('U/N')
axs[1].set_ylabel('W/N')
axs[2].set_ylabel('K/N')
axs[2].set_xlabel('Time')
axs[0].grid(linestyle='--', alpha=0.5)
axs[1].grid(linestyle='--', alpha=0.5)
axs[2].grid(linestyle='--', alpha=0.5)

label  = f'mean: {mU/N:.3f}   std: {np.std(U/N):.3f}'
axs[0].plot(time[plotindex], U[plotindex] / N, label=label)
axs[0].axhline(mU / N, color='k', linestyle='--')
axs[0].legend(loc=     'upper right')

label  = f'mean: {mW/N:.3f}   std: {np.std(W/N):.3f}'
axs[1].plot(time[plotindex], W[plotindex] / N, label=label)
axs[1].axhline(mW / N, color='k', linestyle='--')
axs[1].legend(loc=     'upper right')

label  = f'mean: {mK/N:.3f}   std: {np.std(K/N):.3f}'
axs[2].plot(time[plotindex], K[plotindex] / N, label=label)
axs[2].axhline(mK / N, color='k', linestyle='--')
axs[2].legend(loc=     'upper right')

fig.savefig('Data/NVT_N4000_T2.0_rho1.2_KABLJ_rumd3_thermodynamics.pdf')
plt.show(block=True)

