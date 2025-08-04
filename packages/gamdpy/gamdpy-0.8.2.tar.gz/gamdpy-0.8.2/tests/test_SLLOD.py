""" Example of a Simulation using gamdpy, using explicit blocks.

Simulation of a Lennard-Jones crystal in the NVT ensemble followed by shearing with SLLOD 
and Lees-Edwards boundary conditions

"""


def test_SLLOD(run_NVT=False):
    from pathlib import Path

    import h5py
    import numpy as np
    import matplotlib.pyplot as plt

    import gamdpy as gp

    # Setup pair potential: Single component 12-6 Lennard-Jones
    pairfunc = gp.apply_shifted_force_cutoff(gp.LJ_12_6_sigma_epsilon)
    sig, eps, cut = 1.0, 1.0, 2.5
    pairpot = gp.PairPotential(pairfunc, params=[sig, eps, cut], max_num_nbs=1000)

    temperature = 0.700
    gridsync = True

    # read reference configuration
    configuration = None
    possible_file_paths = ['reference_data/conf_LJ_N2048_rho0.973_T0.700.h5', 'tests/reference_data/conf_LJ_N2048_rho0.973_T0.700.h5']
    for path in possible_file_paths:
        if Path(path).is_file():
            with h5py.File(path, "r") as fin:
                configuration = gp.Configuration.from_h5(fin, "configuration", compute_flags={'stresses':True, 'Vol':True})
            break
    if configuration is None:
        raise FileNotFoundError(f'Could not find configuration file in {possible_file_paths}')

    compute_plan = gp.get_default_compute_plan(configuration)
    compute_plan['gridsync'] = gridsync
    sc_output = 1
    sr = 0.1
    dt = 0.01

    configuration.simbox = gp.LeesEdwards(configuration.D, configuration.simbox.get_lengths())

    integrator_SLLOD = gp.integrators.SLLOD(shear_rate=sr, dt=dt)

    # Test get_kernel
    integrator_SLLOD.get_kernel(configuration=configuration,
                                compute_plan = gp.get_default_compute_plan(configuration),
                                compute_flags = gp.get_default_compute_flags(),
                                interactions_kernel=None,
                                verbose=True)

    # set the kinetic temperature to the exact value associated with the desired
    # temperature since SLLOD uses an isokinetic thermostat
    configuration.set_kinetic_temperature(temperature, ndofs=configuration.N*3-4) # remove one DOF due to constraint on total KE

    runtime_actions = [gp.MomentumReset(100), 
                   gp.TrajectorySaver(include_simbox=True),
                   gp.StressSaver(sc_output),
                   gp.ScalarSaver(sc_output, {'stresses':True}), ]

    # Setup Simulation. Total number of timesteps: num_blocks * steps_per_block
    sim_SLLOD = gp.Simulation(configuration, pairpot, integrator_SLLOD, runtime_actions,
                            num_timeblocks=3, steps_per_timeblock=128,
                            storage='memory', compute_plan=compute_plan)

    # To generate Data/sllod_data.h5 for use in testing calc_dynamics with LEBC, set storage='Data/sllod_data.h5'
    # and set num_timeblocks=30

    # Run simulation one block at a time
    for block in sim_SLLOD.run_timeblocks():
        print(sim_SLLOD.status(per_particle=True))
        configuration.simbox.copy_to_host()
        box_shift = configuration.simbox.box_shift
        lengths = configuration.simbox.get_lengths()
        print(f'box-shift={box_shift:.4f}, strain = {box_shift/lengths[1]:.4f}')
    print(sim_SLLOD.summary())

    sxy = gp.StressSaver.extract(sim_SLLOD.output)[:,0,1]
    sxy_mean = np.mean(sxy)
    print(f'{sr:.2g} {sxy_mean:.6f}')
    assert np.isclose(sxy_mean, 2.71, atol=0.005 ), f"sxy_mean should be 2.71 but is {sxy_mean}"
    assert np.isclose(pairpot.nblist.d_nbflag[2], 51, atol=1), f"pairpot.nblist.d_nbflag[2] should be 51 but is {pairpot.nblist.d_nbflag[2]}"


if __name__ == '__main__':
    test_SLLOD()
