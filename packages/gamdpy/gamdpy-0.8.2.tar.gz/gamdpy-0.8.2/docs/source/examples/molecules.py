import numpy as np
import gamdpy as gp

gp.select_gpu()

# Simulation params 
rho, temperature = 0.85, 1.5
N_A, N_B, N_C = 8, 4, 4  # Number of atoms of each tyoe
particles_per_molecule = N_A + N_B + N_C
filename = 'Data/chains'
num_timeblocks = 64
steps_per_timeblock = 1 * 1024 # 8 * 1024 to show reliable pattern formation

positions = []
particle_types = []
masses = []

# A particles
for i in range(N_A):
    positions.append( [ i*1.0, (i%2)*.1, 0. ] ) # x, y, z for this particle
    particle_types.append( 0 )
    masses.append( 1.0 )  

# B particles
for i in range(N_B):
    positions.append( [ 0, (i+1)*1.0, ((i+1)%2)*.1 ] ) # x, y, z for this particle
    particle_types.append( 1 )
    masses.append( 1.0 )  

# C particles
for i in range(N_C):
    positions.append( [ ((i+1)%2)*.1, 0, (i+1)*1.0 ] ) # x, y, z for this particle
    particle_types.append( 2 )
    masses.append( 1.0 )  

# Setup configuration: Single molecule first, then duplicate
top = gp.Topology(['MyMolecule', ])
top.bonds = gp.bonds_from_positions(positions, cut_off=1.1, bond_type=0)
top.angles = gp.angles_from_bonds(top.bonds, angle_type=0)
top.dihedrals = gp.dihedrals_from_angles(top.angles, dihedral_type=0)
top.molecules['MyMolecule'] = gp.molecules_from_bonds(top.bonds)


dict_this_mol = {"positions" : positions,
                 "particle_types" : particle_types,
                 "masses" : masses,
                 "topology" : top}

print(dict_this_mol)
print(dict_this_mol['topology'])

print('Initial Positions:')
for position in positions:
    print('\t\t', position)
print('Particle types:\t', particle_types)
print('Bonds:         \t', top.bonds)
print('Angles:        \t', top.angles)
print('Dihedrals:     \t', top.dihedrals)
print()

# This call creates the pdf "molecule.pdf" with a drawing of the molecule 
# Use block=True to visualize the molecule before running the simulation
gp.plot_molecule(top, positions, particle_types, filename="molecule.pdf", block=False)

configuration = gp.replicate_molecules([dict_this_mol], [216], safety_distance=2.0, compute_flags={"stresses":True})

configuration.randomize_velocities(temperature=temperature)

print(f'Number of molecules: {len(configuration.topology.molecules["MyMolecule"])}')
print(f'Number of particles: {configuration.N}\n')

# Make bond interactions
bond_potential = gp.harmonic_bond_function
bond_params = [[0.8, 1000.], ]
bonds = gp.Bonds(bond_potential, bond_params, configuration.topology.bonds)

# Make angle interactions
angle_potential = gp.cos_angle_function
angle0, k = 2.0, 500.0
angles = gp.Angles(angle_potential, configuration.topology.angles, parameters=[[k, angle0],])

# Make dihedral interactions
dihedral_potential = gp.ryckbell_dihedral
rbcoef=[.0, 5.0, .0, .0, .0, .0]    
dihedrals = gp.Dihedrals(dihedral_potential, configuration.topology.dihedrals, parameters=[rbcoef, ])

# Exlusion list
exclusions = dihedrals.get_exclusions(configuration)
#exclusions = bonds.get_exclusions(configuration)

# Make pair potential
pair_func = gp.apply_shifted_force_cutoff(gp.LJ_12_6_sigma_epsilon)
sig = [[1.00, 1.00, 1.00],
       [1.00, 1.00, 1.00],
       [1.00, 1.00, 1.00],]
eps = [[1.00, 1.00, 1.00],
       [1.00, 1.00, 0.80],
       [1.00, 0.80, 1.00],]
cut = [[2.50, 1.12, 1.12],
       [1.12, 2.50, 2.50],
       [1.12, 2.50, 2.50]]

pair_pot = gp.PairPotential(pair_func, params=[sig, eps, cut], exclusions=exclusions, max_num_nbs=1000)

# Make integrator
integrator = gp.integrators.NVT(temperature=temperature, tau=0.1, dt=0.004)

# Setup runtime actions, i.e. actions performed during simulation of timeblocks
runtime_actions = [gp.TrajectorySaver(),
                   gp.RestartSaver(),
                   gp.ScalarSaver(32),
                   gp.StressSaver(32, compute_flags={'stresses':True}),
                   gp.MomentumReset(100)]

# Setup simulation
sim = gp.Simulation(configuration, [pair_pot, bonds, angles, dihedrals], integrator, runtime_actions,
                    num_timeblocks=num_timeblocks, steps_per_timeblock=steps_per_timeblock,
                    storage=filename+'_compress.h5')

print('\nCompression and equilibration: ')
initial_rho = configuration.N / configuration.get_volume()
for block in sim.run_timeblocks():
    volume = configuration.get_volume()
    N = configuration.N
    current_rho = N/volume
    print(sim.status(per_particle=True), f'rho= {current_rho:.3}', end='\t')
    print(f'P= {(N*temperature + np.sum(configuration["W"]))/volume:.3}') # pV = NkT + W
    
    # Scale configuration to get closer to final density, rho
    if block<sim.num_blocks/2:
        desired_rho = (block+1)/(sim.num_blocks/2)*(rho - initial_rho) + initial_rho
        if desired_rho > 1.5*current_rho:
            desired_rho = 1.5*current_rho 
        configuration.atomic_scale(density=desired_rho)
        configuration.copy_to_device() # Since we altered configuration, we need to copy it back to device
print(sim.summary()) 
print(configuration)

sim = gp.Simulation(configuration, [pair_pot, bonds, angles, dihedrals], integrator, runtime_actions,
                    num_timeblocks=num_timeblocks, steps_per_timeblock=steps_per_timeblock,
                    compute_plan=sim.compute_plan, storage=filename+'.h5')

print('\nProduction: ')
for block in sim.run_timeblocks():
    print(sim.status(per_particle=True))
print(sim.summary()) 
print(configuration)

W = gp.ScalarSaver.extract(sim.output, columns=['W'])
full_stress_tensor = gp.StressSaver.extract(sim.output)
mean_diagonal_sts = (full_stress_tensor[:,0,0] + full_stress_tensor[:,1,1] + full_stress_tensor[:,2,2])/3

print("Mean diagonal stress", np.mean(mean_diagonal_sts) )
print("Pressure", np.mean(W)*rho/N + temperature*rho)


print('\nAnalyse the saved simulation with scripts found in "examples"')
print('(visualize requires that ovito is installed):')
print('   python3 analyze_structure.py Data/chains')
print('   python3 analyze_dynamics.py Data/chains')
print('   python3 analyze_thermodynamics.py Data/chains')
print('   python3 visualize.py Data/chains.h5')