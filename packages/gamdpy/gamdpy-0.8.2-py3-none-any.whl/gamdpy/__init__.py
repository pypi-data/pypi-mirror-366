""" The gamdpy main module """

# Setting to make gamdpy run on google.colab:
from numba import config
config.CUDA_ENABLE_PYNVJITLINK = 1

# Objects which are imported here will be in the main namespace and can be called are gamdpy.object
# Objects which are imported in the __init__.py of subpackages are called as gamdpy.subpackage.object

# Import from configuration subpackage
# The configuration subpackage contains details about the configuration (positions, energies, etc)
# The (abstract base) class SimulationBox, and derived classes Orthrhombic and LeesEdwards have information about the simulation box
from .configuration.Configuration import Configuration
from .configuration.old_input_output import configuration_to_rumd3, configuration_from_rumd3
from .configuration.old_input_output import configuration_to_lammps, configuration_to_lammps_data
from .configuration.Configuration import replicate_molecules
from .simulation_boxes.orthorhombic import Orthorhombic
from .simulation_boxes.lees_edwards import LeesEdwards
from .configuration.topology import Topology
from .configuration.topology import bonds_from_positions, angles_from_bonds, dihedrals_from_angles, molecules_from_bonds, duplicate_topology, replicate_topologies
from .configuration.colarray import colarray 
from .configuration import unit_cells
# make_lattice is imported in configuration/__init__.py

# Import from simulation subpackage
from .simulation.Simulation import Simulation
from .simulation.get_default_sim import get_default_sim
from .simulation.get_default_compute_plan import get_default_compute_plan
from .simulation.get_default_compute_flags import get_default_compute_flags

# Import from integrators subpackage
from .integrators import integrator, NVE, NVT, NVT_Langevin, Brownian, NPT_Atomic, NPT_Langevin, SLLOD, NVU_RT, GradientDescent

# Import from interactions subpackage
from .interactions import interaction, add_interactions_list, NbList2, NbListLinkedLists
from .interactions import PairPotential, TabulatedPairPotential
from .interactions import Bonds, Angles, Dihedrals
from .interactions import make_fixed_interactions, make_planar_calculator, setup_planar_interactions
from .interactions import Gravity, Relaxtemp, Tether
from .interactions.potential_functions import *

# Import from runtime_actions subpackage (Actions that can be inserted into the stimulation  kernel)
from .runtime_actions import RuntimeAction, add_runtime_actions_list, TrajectorySaver, RestartSaver, ScalarSaver, MomentumReset, StressSaver
from .runtime_actions.time_scheduler import *

# Import from calculators subpackage
from .calculators import CalculatorHydrodynamicCorrelations, CalculatorHydrodynamicProfile, CalculatorWidomInsertion
from .calculators import CalculatorRadialDistribution, CalculatorStructureFactor

# Import from tools subpackage
# To make type checking work (e.g. pylance): 
from .tools import TrajectoryIO, calc_dynamics, save_configuration, calc_conductivity
# Side effect gp.calc_dynamics does also work! Same problem for integrators
# TrajectoryIO, save_configuration and calc_dynamics are not directly imported and are called via gp.tools.*

# Tools/Evaluator are runtime actions with do not interact with the kernel
from .tools.Evaluator import Evaluator

# Import from misc
# Misc folder contains scripts that have no better place in the code
from .misc.select_gpu import select_gpu
from .misc.plot_scalars import plot_scalars
from .misc.make_function import make_function_constant, make_function_ramp, make_function_sin, make_function_cos
from .misc.extract_scalars import extract_scalars
from .misc.plot_molecule import plot_molecule

# Import from visualization 
#from .visualization import *

__version__ = "0.8.2"
