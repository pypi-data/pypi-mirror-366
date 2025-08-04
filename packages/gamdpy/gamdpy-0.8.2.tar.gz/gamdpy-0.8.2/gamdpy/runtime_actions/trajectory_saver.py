import numpy as np
import numba
import json
import h5py
from numba import cuda, config

from .runtime_action import RuntimeAction
from .time_scheduler import Log2

class TrajectorySaver(RuntimeAction):
    """ 
    Runtime action for saving configurations during timeblock.

    Parameters
    ----------

    scheduler : ~gamdpy.Scheduler
        The scheduler defining when to save

    include_simbox : bool, optional
        Boolean deciding if to include simbox informations in output
        Default False

    compression : str, optional
        String selecting the type of compression used.
        Default "gzip"

    compression_opts : int, optional
        Relevant if "gzip" compression is used. Select compression option for gzip

    saving_list :  list, optional
        This list is used to select which information to save in the trajectory. 
        Default ['positions', 'images'].
        Can be used to save only velocities by setting saving_list = ['velocities'].
        Possible list entries are 'positions', 'images', 'velocities', 'forces'.

    verbose : bool, optional
        Default False

    Raises
    ------
    ValueError
        If saving_list contains a name which is not recongnized.
    """

    def __init__(self, scheduler=Log2(), include_simbox=False,
            compression="gzip", compression_opts=4,
            saving_list=['positions', 'images'],
            update_ptype = False,
            update_topology = False,
            verbose=False) -> None:
        
        self.scheduler = scheduler
        self.include_simbox = include_simbox
        self.num_vectors = len(saving_list) 
        self.translator = {'positions' :  'r', 'images' : 'img', 'velocities' : 'v', 'forces' : 'f'}
        self.datatypes = {'positions' : np.float32, 'images': np.int32, 'velocities' : np.float32, 'forces' : np.float32}
        self.compression = compression
        self.sid = {} # LC : this should be a list
        # check that items of saving_list are known
        for item in saving_list:
            if item not in list(self.datatypes.keys()):
                raise ValueError(f"{item} is not recognized. Accepted values are 'positions', 'images', 'velocities', 'forces'.")
            self.sid[self.translator[item]]=True
        self.saving_list = saving_list
        self.update_ptype = update_ptype
        self.update_topology = update_topology
        if self.compression == 'gzip':
            self.compression_opts = compression_opts
        else:
            self.compression_opts = None
        #self.sid = {"r":0, "r_im":1}

    def extract_positions(h5file):
        return h5file['trajectory/positions']

    def extract_images(h5file):
        return h5file['trajectory/images']

    def extract_velocities(h5file):
        return h5file['trajectory/velocities']

    def extract_forces(h5file):
        return h5file['trajectory/forces']

    def setup(self, configuration, num_timeblocks: int, steps_per_timeblock: int, output, verbose=False) -> None:
        self.configuration = configuration

        if type(num_timeblocks) != int or num_timeblocks < 0:
            raise ValueError(f'num_timeblocks ({num_timeblocks}) should be non-negative integer.')
        self.num_timeblocks = num_timeblocks
        
        if type(steps_per_timeblock) != int or steps_per_timeblock < 0:
            raise ValueError(f'steps_per_timeblock ({steps_per_timeblock}) should be non-negative integer.')
        self.steps_per_timeblock = steps_per_timeblock

        # pass the number of steps to the scheduler
        # without this line the scheduler does nothing at all
        self.scheduler.setup(stepmax=self.steps_per_timeblock, ntimeblocks=self.num_timeblocks)

        # both steps '0' and the last one are already counted by the scheduler
        self.conf_per_block = self.scheduler.nsaves# + 1 
        #self.conf_per_block = int(math.log2(self.steps_per_timeblock)) + 2  # Should be user controllable
        
        # Setup output
        if verbose:
            print(f'Storing results in memory. Expected footprint {self.num_timeblocks * self.conf_per_block * self.num_vectors * self.configuration.N * self.configuration.D * 4 / 1024 / 1024:.2f} MB.')

        if 'trajectory' in output.keys():
            del output['trajectory']
        output.create_group('trajectory')
        output.create_group('trajectory/topologies')

        # Compression has a different syntax depending if is gzip or not because gzip can have also a compression_opts
        # it is possible to use compression=None for not compressing the data
        #output.create_dataset('trajectory_saver/positions',
        #        shape=(self.num_timeblocks, self.conf_per_block, self.configuration.N, self.configuration.D),
        #        chunks=(1, 1, self.configuration.N, self.configuration.D),
        #        dtype=np.float32, compression=self.compression, compression_opts=self.compression_opts)
        #output.create_dataset('trajectory_saver/images',
        #        shape=(self.num_timeblocks, self.conf_per_block, self.configuration.N, self.configuration.D),
        #        chunks=(1, 1, self.configuration.N, self.configuration.D),
        #        dtype=np.int32,  compression=self.compression, compression_opts=self.compression_opts)
        for key in self.saving_list:
            output.create_dataset(f'trajectory/{key}',
                    shape=(self.num_timeblocks, self.conf_per_block, self.configuration.N, self.configuration.D),
                    chunks=(1, 1, self.configuration.N, self.configuration.D),
                    dtype=self.datatypes[f'{key}'], compression=self.compression, compression_opts=self.compression_opts)
        # ptype is a Virtual dataset: https://docs.h5py.org/en/stable/vds.html
        if self.update_ptype == False:
            layout = h5py.VirtualLayout(shape=(self.num_timeblocks, self.conf_per_block, self.configuration.N), dtype=np.int32)
            for block in range(self.num_timeblocks):
                for conf in range(self.conf_per_block):
                    layout[block, conf] = h5py.VirtualSource(output['initial_configuration/ptype'])
            output.create_virtual_dataset('trajectory/ptypes', layout, fillvalue=0)
        else:
            # LC: Need to implement how to save them per step (similar to what done with positions etc)
            print(f"update_ptype = True is not implemented")
            exit()
        if self.update_topology == False:
            for block in range(self.num_timeblocks):
                # LC: names should be adjusted
                output[f'trajectory/topologies/block{block:04d}'] = h5py.SoftLink('/initial_configuration/topology')
        else:
            # LC: Need to implement how to save them per step
            print(f"update_topology = True is not implemented")
            exit()

        output['trajectory'].attrs['compression_info'] = f"{self.compression} with opts {self.compression_opts}"
        output['trajectory'].attrs['num_timeblocks'] = self.num_timeblocks
        output['trajectory'].attrs['steps_per_timeblock'] = self.steps_per_timeblock
        output['trajectory'].attrs['trajectory_columns'] = list(self.sid.keys())
        output['trajectory'].attrs['update_ptype'] = self.update_ptype
        output['trajectory'].attrs['update_topology'] = self.update_topology
        
        # Scheduler info
        self.scheduler.info_to_h5(output['trajectory'])

        #output.attrs['vectors_names'] = list(self.sid.keys())
        if self.include_simbox:
            if 'sim_box' in output['trajectory'].keys():
                del output['trajectory/sim_box']
            output.create_dataset('trajectory/sim_box', 
                                  shape=(self.num_timeblocks, self.conf_per_block, self.configuration.simbox.len_sim_box_data))

        flag = config.CUDA_LOW_OCCUPANCY_WARNINGS
        config.CUDA_LOW_OCCUPANCY_WARNINGS = False
        self.zero_kernel = self.make_zero_kernel()
        config.CUDA_LOW_OCCUPANCY_WARNINGS = flag

    def get_params(self, configuration, compute_plan):
        self.conf_array = np.zeros((self.conf_per_block, self.num_vectors, self.configuration.N, self.configuration.D),
                                   dtype=np.float32)
        self.d_conf_array = cuda.to_device(self.conf_array)

        if self.include_simbox:
            self.sim_box_output_array = np.zeros((self.conf_per_block, self.configuration.simbox.len_sim_box_data), dtype=np.float32)
            self.d_sim_box_output_array = cuda.to_device(self.sim_box_output_array)
            return (self.d_conf_array, self.d_sim_box_output_array)
        else:
            return (self.d_conf_array,)

    def make_zero_kernel(self):
        # Unpack parameters from configuration and compute_plan
        D, num_part = self.configuration.D, self.configuration.N
        pb = 32
        num_blocks = (num_part - 1) // pb + 1

        def zero_kernel(array):
            Nx, Ny, Nz, Nw = array.shape
            global_id = cuda.grid(1)

            if global_id < Nz:  # particles
                for i in range(Nx):
                    for j in range(Ny):
                        for k in range(Nw):
                            array[i, j, global_id, k] = numba.float32(0.0)

        zero_kernel = cuda.jit(zero_kernel)
        return zero_kernel[num_blocks, pb]

    def update_at_end_of_timeblock(self, timeblock: int, output_reference):
        data = self.d_conf_array.copy_to_host()
        # note that d_conf_array has dimensions (self.conf_per_block, 2, self.configuration.N, self.configuration.D)
        #output_reference['trajectory_saver/positions'][timeblock], output_reference['trajectory_saver/images'][timeblock] = data[:, 0], data[:, 1]
        for key in self.saving_list:
            output_reference[f'trajectory/{key}'][timeblock] = data[:,self.saving_list.index(key)]

        #output['trajectory_saver'][block, :] = self.d_conf_array.copy_to_host()
        if self.include_simbox:
            output_reference['trajectory/sim_box'][timeblock, :] = self.d_sim_box_output_array.copy_to_host()
        self.zero_kernel(self.d_conf_array)

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


    def get_prestep_kernel(self, configuration, compute_plan, verbose=False):
        # Unpack parameters from configuration and compute_plan
        D, num_part = configuration.D, configuration.N
        pb, tp, gridsync = [compute_plan[key] for key in ['pb', 'tp', 'gridsync']]
        num_blocks = (num_part - 1) // pb + 1
        sim_box_array_length = configuration.simbox.len_sim_box_data
        include_simbox = self.include_simbox

        # Unpack indices for scalars to be compiled into kernel
        unpacked_saving_list = [key in self.saving_list for key in ['positions', 'images', 'velocities', 'forces']]
        save_r, save_img, save_v, save_f = unpacked_saving_list
        pos_r, pos_img, pos_v, pos_f = [self.saving_list.index(key) if key in self.saving_list else None for key in ['positions', 'images', 'velocities', 'forces']]
        r_id, v_id, f_id = [configuration.vectors.indices[key] for key in ['r', 'v', 'f']]

        # get function to check steps in the kernel, already compiled
        stepcheck_function = numba.njit(getattr(self.scheduler, 'stepcheck_func'))

        def kernel(grid, vectors, scalars, r_im, sim_box, step, conf_saver_params):
            if include_simbox:
                conf_array, sim_box_output_array = conf_saver_params
            else:
                conf_array, = conf_saver_params

            flag, save_index = stepcheck_function(step)

            if flag:
                global_id, my_t = cuda.grid(2)
                if global_id < num_part and my_t == 0:
                    for k in range(D):
                        if save_r:   conf_array[save_index, pos_r, global_id, k]   = vectors[r_id][global_id, k]
                        if save_img: conf_array[save_index, pos_img, global_id, k] = np.float32(r_im[global_id, k])
                        if save_v:   conf_array[save_index, pos_v, global_id, k]   = vectors[v_id][global_id, k]
                        if save_f:   conf_array[save_index, pos_f, global_id, k]   = vectors[f_id][global_id, k]
                    if include_simbox and global_id == 0:
                        for k in range(sim_box_array_length):
                            sim_box_output_array[save_index, k] = sim_box[k]
            return

        kernel = cuda.jit(device=gridsync)(kernel)

        if gridsync:
            return kernel  # return device function
        else:
            return kernel[num_blocks, (pb, 1)]  # return kernel, incl. launch parameters
