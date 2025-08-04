import numpy as np
import numba
import math
from numba import cuda, config
import json

from .runtime_action import RuntimeAction
from .time_scheduler import Lin


class StressSaver(RuntimeAction):
    """ Runtime action for saving stress tensor(a D x D matrix) during a timeblock
    every `steps_between_output` time steps.
    """
    def __init__(self, steps_between_output:int = 16, compute_flags = None, verbose=False) -> None:
        if type(steps_between_output) != int or steps_between_output < 0:
            raise ValueError(f'steps_between_output ({steps_between_output}) should be non-negative integer.')

        # For now only to put the scheduler information in the h5 file
        self.scheduler = Lin(steps_between=steps_between_output)

        self.steps_between_output = steps_between_output
        self.compute_flags = compute_flags
        self.verbose = verbose

    def get_compute_flags(self):
        return self.compute_flags


    def setup(self, configuration, num_timeblocks:int, steps_per_timeblock:int, output, verbose=False) -> None:

        self.configuration = configuration
        D = configuration.D

        if type(num_timeblocks) != int or num_timeblocks < 0:
            raise ValueError(f'num_timeblocks ({num_timeblocks}) should be non-negative integer.')
        self.num_timeblocks = num_timeblocks

        if type(steps_per_timeblock) != int or steps_per_timeblock < 0:
            raise ValueError(f'steps_per_timeblock ({steps_per_timeblock}) should be non-negative integer.')
        self.steps_per_timeblock = steps_per_timeblock

        if self.steps_between_output >= steps_per_timeblock:
            raise ValueError(f'scalar_output ({self.steps_between_output}) must be less than steps_per_timeblock ({steps_per_timeblock})')

        # per block saving of stress tensor
        if not configuration.compute_flags['stresses']:
            raise RuntimeError('stresses not set in compute_flags')

        self.stress_saves_per_block = self.steps_per_timeblock//self.steps_between_output

        # Setup output
        shape = (self.num_timeblocks, self.stress_saves_per_block, D, D)
        if 'stresses' in output.keys():
            del output['stresses']
        output.create_group('stresses')
        output.create_dataset('stresses/stress_tensor', shape=shape,
                chunks=(1, self.stress_saves_per_block, D, D), dtype=np.float32)
        output['stresses'].attrs['steps_between_output'] = self.steps_between_output # LC: This should be removed because it's above already

        # Setup scheduler, and write the relevant information to the h5 file
        self.scheduler.setup(stepmax=self.steps_per_timeblock, ntimeblocks=self.num_timeblocks)
        self.scheduler.info_to_h5(output['stresses'])

        #output['stresses'].attrs['scheduler'] = 'Lin' #self.scheduler.__class__.__name__        
        #output['stresses'].attrs['scheduler'] = self.scheduler.__class__.__name__
        #output['stresses'].attrs['scheduler_info'] = json.dumps(self.scheduler.kwargs)
        #output['stresses'].attrs['scheduler_info'] = json.dumps({'Dt':self.steps_between_output}) #json.dumps(self.scheduler.kwargs)
        #output['stresses'].create_dataset('steps', data=self.scheduler.steps, dtype=np.int32)

        
        flag = config.CUDA_LOW_OCCUPANCY_WARNINGS
        config.CUDA_LOW_OCCUPANCY_WARNINGS = False
        self.zero_kernel = self.make_zero_kernel_3()
        config.CUDA_LOW_OCCUPANCY_WARNINGS = flag



    def make_zero_kernel_3(self):
        """ Returns a kernel that can zero an array with three axes """
        def zero_kernel(array):
            Nx, Ny, Nz = array.shape
            #i, j = cuda.grid(2) # doing simple 1 thread kernel for now ...
            for i in range(Nx):
                for j in range(Ny):
                    for k in range(Nz):
                        array[i,j,k] = numba.float32(0.0)

        zero_kernel = cuda.jit(zero_kernel)
        return zero_kernel[1,1]


    def get_params(self, configuration, compute_plan):
        D = configuration.D
        self.output_array = np.zeros((self.stress_saves_per_block, D, D), dtype=np.float32)
        self.d_output_array = cuda.to_device(self.output_array)
        self.params = (self.steps_between_output, self.d_output_array)
        return self.params

    def initialize_before_timeblock(self, timeblock: int, output_reference):
        self.zero_kernel(self.d_output_array)

    def update_at_end_of_timeblock(self, timeblock: int, output_reference):
        volume = self.configuration.get_volume()
        output_reference['stresses/stress_tensor'][timeblock, :] = self.d_output_array.copy_to_host() / volume


    def get_prestep_kernel(self, configuration, compute_plan):
        # Unpack parameters from configuration and compute_plan
        D, num_part = configuration.D, configuration.N
        pb, tp, gridsync = [compute_plan[key] for key in ['pb', 'tp', 'gridsync']] 
        num_blocks = (num_part - 1) // pb + 1


        m_id = configuration.sid['m']
        v_id = configuration.vectors.indices['v']
        sx_id = configuration.vectors.indices['sx']
        sy_id = configuration.vectors.indices['sy']
        if D > 2:
            sz_id = configuration.vectors.indices['sz']
        if D > 3:
            sw_id = configuration.vectors.indices['sw']

        #volume_function = numba.njit(configuration.simbox.get_volume_function())

        def kernel(grid, vectors, scalars, r_im, sim_box, step, runtime_action_params):
            """     
            """
            steps_between_output, output_array = runtime_action_params # Needs to be compatible with get_params above
            if step%steps_between_output==0:
                save_index = step//steps_between_output
                if save_index < output_array.shape[0]:
                    global_id, my_t = cuda.grid(2)
                    if global_id < num_part and my_t == 0:
                        my_m = scalars[global_id][m_id]
                        for k in range(D):
                            cuda.atomic.add(output_array, (save_index, 0, k), vectors[sx_id][global_id][k] -
                                            my_m * vectors[v_id][global_id][0]*vectors[v_id][global_id][k])

                            cuda.atomic.add(output_array, (save_index, 1, k), vectors[sy_id][global_id][k] -
                                            my_m * vectors[v_id][global_id][1]*vectors[v_id][global_id][k])
                            if D > 2:
                                cuda.atomic.add(output_array, (save_index, 2, k), vectors[sz_id][global_id][k] -
                                                my_m * vectors[v_id][global_id][2]*vectors[v_id][global_id][k])
                            if D > 3:
                                cuda.atomic.add(output_array, (save_index, 3, k), vectors[sw_id][global_id][k] -
                                                my_m * vectors[v_id][global_id][3]*vectors[v_id][global_id][k])
            return

        kernel = cuda.jit(device=gridsync)(kernel)

        if gridsync:
            return kernel  # return device function
        else:
            return kernel[num_blocks, (pb, 1)]  # return kernel, incl. launch parameters

    #### CONSIDER USING POSTSTEP TO GET CORRECT VELOCITIES ###############
    def get_poststep_kernel(self, configuration, compute_plan, verbose=False):
        pb, tp, gridsync = [compute_plan[key] for key in ['pb', 'tp', 'gridsync']]
        if gridsync:
            def kernel(grid, vectors, scalars, r_im, sim_box, step, conf_saver_params):
                pass
                return
            return cuda.jit(device=gridsync)(kernel)
        else:
            def kernel(grid, vectors, scalars, r_im, sim_box, step, conf_saver_params):
                pass
            return kernel

    # Class functions to read data

    def extract(h5file, first_block=0, last_block=None, subsample=1):

        #stress_data = h5file['stress_saver/stress_tensor']
        h5grp = h5file['stresses']
        nblocks, per_block, D, D2 = h5grp['stress_tensor'].shape
        assert D == D2
        final_rows = (nblocks-first_block) * per_block
        return h5grp['stress_tensor'][first_block:last_block,:,:, :].reshape(final_rows, D, D)[::subsample]

    def get_times(h5file, first_block=0, last_block=None, reset_time=True, subsample=1):
        num_timeblock, saves_per_timeblock = h5file['stresses/stress_tensor'][first_block:last_block,:,0,0].shape
        times_array = np.arange(0,num_timeblock*saves_per_timeblock, step=subsample)*h5file.attrs['dt']
        return times_array
