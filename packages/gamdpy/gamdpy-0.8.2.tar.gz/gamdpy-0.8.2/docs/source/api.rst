===
API
===

.. toctree::
   :maxdepth: 1

The Simulation Class
--------------------

.. autoclass:: gamdpy.Simulation
   :members:

The Configuration Class
-----------------------

.. autoclass:: gamdpy.Configuration
   :members:

Simulation boxes
~~~~~~~~~~~~~~~~

An simulation box object is attached to an configuration object.

.. autoclass:: gamdpy.Orthorhombic
   :members:

.. autoclass:: gamdpy.LeesEdwards
   :members:


.. _integrators:

Integrators
-----------

One of the below integrators should be given as a parameter to the :class:`~gamdpy.Simulation` class.

Constant energy and volume
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: gamdpy.NVE
   :members:
   :exclude-members: get_kernel, get_params

Constant temperature and volume
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: gamdpy.NVT
   :members:
   :exclude-members: get_kernel, get_params

.. autoclass:: gamdpy.NVT_Langevin
   :members:
   :exclude-members: get_kernel, get_params

.. autoclass:: gamdpy.Brownian
   :members:
   :exclude-members: get_kernel, get_params

Constant temperature and pressure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: gamdpy.NPT_Atomic
   :members:
   :exclude-members: get_kernel, get_params

.. autoclass:: gamdpy.NPT_Langevin
   :members:
   :exclude-members: get_kernel, get_params

Other integrators
~~~~~~~~~~~~~~~~~

.. autoclass:: gamdpy.SLLOD
   :members:
   :exclude-members: get_kernel, get_params

.. autoclass:: gamdpy.GradientDescent
   :members:
   :exclude-members: get_kernel, get_params

.. _interactions:

Interactions
------------

Interactions are passed in a list to the :class:`~gamdpy.Simulation` class.
This will typically include a *pair potential* and *fix interactions* like gravity and walls.

Pair potential
~~~~~~~~~~~~~~

.. autoclass:: gamdpy.PairPotential
   :members:
   :exclude-members: check_datastructure_validity, get_kernel, get_params

Pair potential functions
^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: gamdpy.LJ_12_6

.. autofunction:: gamdpy.LJ_12_6_sigma_epsilon

.. autofunction:: gamdpy.harmonic_repulsion

.. autofunction:: gamdpy.hertzian

.. autofunction:: gamdpy.SAAP

Generators
^^^^^^^^^^

Generators return a function that can be used to calculate the potential energy and the force between two particles.

.. autofunction:: gamdpy.make_LJ_m_n

.. autofunction:: gamdpy.make_IPL_n

.. autofunction:: gamdpy.add_potential_functions

.. autofunction:: gamdpy.make_potential_function_from_sympy

Modifies
^^^^^^^^

Modifies are typically used to smoothly truncate the potential at a certain distance.

.. autofunction:: gamdpy.apply_shifted_potential_cutoff

.. autofunction:: gamdpy.apply_shifted_force_cutoff

Fixed interactions
~~~~~~~~~~~~~~~~~~

Classes
^^^^^^^

.. autoclass:: gamdpy.Bonds

.. autoclass:: gamdpy.Angles

.. autoclass:: gamdpy.Tether

.. autoclass:: gamdpy.Gravity

.. autoclass:: gamdpy.Relaxtemp

Generators
^^^^^^^^^^

.. autofunction:: gamdpy.make_planar_calculator

.. autofunction:: gamdpy.setup_planar_interactions

.. autofunction:: gamdpy.make_fixed_interactions


Bond functions
^^^^^^^^^^^^^^

A *bond potential* is needed for the :class:`~gamdpy.Bonds` class.

.. autofunction:: gamdpy.harmonic_bond_function


.. _runtime_actions:

Runtime Actions
---------------

A list of runtime actions are passed as an argument to the :class:`~gamdpy.Simulation` class.

.. autoclass:: gamdpy.TrajectorySaver

.. autoclass:: gamdpy.ScalarSaver

.. autoclass:: gamdpy.RestartSaver

.. autoclass:: gamdpy.MomentumReset

.. autoclass:: gamdpy.StressSaver

Calculators
-----------

.. autoclass:: gamdpy.CalculatorRadialDistribution
   :members:

.. autoclass:: gamdpy.CalculatorStructureFactor
   :members:

.. autoclass:: gamdpy.CalculatorWidomInsertion
   :members:

.. autoclass:: gamdpy.CalculatorHydrodynamicCorrelations
   :members:

.. autoclass:: gamdpy.CalculatorHydrodynamicProfile
   :members:

Tools and helper functions
--------------------------

Input and Output
~~~~~~~~~~~~~~~~

The TrajectoryIO class
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: gamdpy.tools.TrajectoryIO
   :members:

IO functions
^^^^^^^^^^^^

.. autofunction:: gamdpy.configuration_from_rumd3

.. autofunction:: gamdpy.configuration_to_rumd3

.. autofunction:: gamdpy.configuration_to_lammps

Post-analysis tools
-------------------

.. autofunction:: gamdpy.extract_scalars

.. autofunction:: gamdpy.tools.calc_dynamics

.. autofunction:: gamdpy.tools.calculate_molecular_center_of_masses

.. autofunction:: gamdpy.tools.calculate_molecular_velocities

.. autofunction:: gamdpy.tools.calculate_molecular_dipoles

Mathematical functions
----------------------

The below returns functions that can be executed fast in a GPU kernel.
As an example, they can be used to set a time-dependent target temperature.

.. autofunction:: gamdpy.make_function_constant

.. autofunction:: gamdpy.make_function_ramp

.. autofunction:: gamdpy.make_function_sin

Miscellaneous
-------------

.. autofunction:: gamdpy.select_gpu

.. autofunction:: gamdpy.get_default_sim

.. autofunction:: gamdpy.get_default_compute_plan

.. autofunction:: gamdpy.get_default_compute_flags

.. autofunction:: gamdpy.plot_molecule

.. autofunction:: gamdpy.tools.print_h5_structure

.. autofunction:: gamdpy.tools.print_h5_attributes
