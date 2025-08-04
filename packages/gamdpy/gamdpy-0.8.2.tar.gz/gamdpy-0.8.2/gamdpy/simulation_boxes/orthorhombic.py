#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 11:41:24 2024

@author: nbailey
"""

import numpy as np
import numba
from numba import cuda
from .simulationbox import SimulationBox

class Orthorhombic(SimulationBox):
    """ Standard rectangular simulation box class 

    Parameters
    ----------
    D: int
        Spatial dimension

    lengths: list of floats
        The box lengths in each spatial dimension.

    Raises
    ------
    ValueError
        If the length of ``lengths`` is not equal to ``D``.

    Example
    -------

    >>> import gamdpy as gp
    >>> simbox = gp.Orthorhombic(D=3, lengths=[3, 4, 5])

    """
    def __init__(self, D: int, lengths: list):
        if len(lengths) != D:
            raise ValueError("Length of lengths must be equal to D")

        self.D = D  # This parameter is not needed, since it is determined by the length of the box
        self.data_array = np.array(lengths, dtype=np.float32) # ensure single precision
        self.len_sim_box_data = D # not true for other Simbox classes. Want to remove this and just use len(self.data_array)

        return

    def get_name(self) -> str:
        return "Orthorhombic"

    def copy_to_device(self) -> None:
        # Copy data from host to device memory (CPU to GPU).
        self.d_data = cuda.to_device(self.data_array)

    def copy_to_host(self) -> None:
        # Copy data from device to host memory (GPU to CPU).
        self.data_array = self.d_data.copy_to_host()

    def get_dist_sq_dr_function(self) -> callable:
        D = self.D
        # A function which computes displacement and distance squared for one neighbor
        def dist_sq_dr_function(ri, rj, sim_box, dr):

            ''' Returns the squared distance between ri and rj applying MIC and saves ri-rj in dr '''
            dist_sq = numba.float32(0.0)
            for k in range(D):
                dr[k] = ri[k] - rj[k]
                box_k = sim_box[k]
                dr[k] += (-box_k if numba.float32(2.0) * dr[k] > +box_k else
                          (+box_k if numba.float32(2.0) * dr[k] < -box_k else numba.float32(0.0)))  # MIC
                dist_sq = dist_sq + dr[k] * dr[k]
            return dist_sq

        return dist_sq_dr_function

    def get_dist_sq_function(self) -> callable:
        D = self.D
        # Generates function dist_sq_function which computes distance squared for one neighbor
        def dist_sq_function(ri, rj, sim_box):
            ''' Returns the squared distance between ri and rj applying MIC'''
            dist_sq = numba.float32(0.0)
            for k in range(D):
                dr_k = ri[k] - rj[k]
                box_k = sim_box[k]
                dr_k += (-box_k if numba.float32(2.0) * dr_k > +box_k else
                         (+box_k if numba.float32(2.0) * dr_k < -box_k else numba.float32(0.0)))  # MIC
                dist_sq = dist_sq + dr_k * dr_k
            return dist_sq

        return dist_sq_function

    def get_apply_PBC(self):
        D = self.D
        def apply_PBC(r, image, sim_box):
            for k in range(D):
                if r[k] * numba.float32(2.0) > +sim_box[k]:
                    r[k] -= sim_box[k]
                    image[k] += 1
                if r[k] * numba.float32(2.0) < -sim_box[k]:
                    r[k] += sim_box[k]
                    image[k] -= 1
            return
        return apply_PBC

    def get_lengths(self) -> np.ndarray:
        """ Return the box lengths as a numpy array

         Returns
         -------
         numpy.ndarray
            The box lengths in each spatial dimension.

         """
        return self.data_array.copy()

    def get_volume(self) -> float:
        r""" Return the box volume, :math:`V = \prod_{i=1}^{D} L_i`

        Returns
        -------
        float
            Volume of the box.

        """
        #self.copy_to_host() # not necessary if volume is fixed and if not fixed then presumably stuff like normalizing stress by volume should be done in the device anyway
        return float(self.get_volume_function()(self.data_array))

    def get_volume_function(self):
        D = self.D
        def volume(sim_box):
            ''' Returns volume of the rectangular box '''
            vol = sim_box[0]
            for i in range(1,D):
                vol *= sim_box[i]
            return vol
        return volume

    def scale(self, scale_factor: float) -> None:
        """ Scale the box lengths by scale_factor """
        self.data_array *= scale_factor

    #def get_dist_moved_sq_function(self):
    #    D = self.D
    #    def dist_moved_sq_function(r_current, r_last, sim_box, sim_box_last):
    #        ''' Returns squared distance between vectors r_current and r_last '''
    #        dist_sq = numba.float32(0.0)
    #        for k in range(D):
    #            dr_k = r_current[k] - r_last[k]
    #            box_k = sim_box[k]
    #            dr_k += (-box_k if numba.float32(2.0) * dr_k > +box_k else
    #                     (+box_k if numba.float32(2.0) * dr_k < -box_k else numba.float32(0.0)))  # MIC
    #            dist_sq = dist_sq + dr_k * dr_k

    #        return dist_sq
    #    return dist_moved_sq_function

    def get_dist_moved_exceeds_limit_function(self):
        D = self.D

        def dist_moved_exceeds_limit_function(r_current, r_last, sim_box, sim_box_last, skin, cut):
            """ Returns True if squared distance between r_current and r_last exceeds half skin.
            Parameters sim_box_last and cut are not used here, but are needed for the Lees-Edwards type of Simbox"""
            dist_sq = numba.float32(0.0)
            for k in range(D):
                dr_k = r_current[k] - r_last[k]
                box_k = sim_box[k]
                dr_k += (-box_k if numba.float32(2.0) * dr_k > +box_k else
                         (+box_k if numba.float32(2.0) * dr_k < -box_k else numba.float32(0.0)))  # MIC
                dist_sq = dist_sq + dr_k * dr_k

            return dist_sq > skin*skin*numba.float32(0.25)
        return dist_moved_exceeds_limit_function

    def get_loop_x_addition(self):
        return 0

    def get_loop_x_shift_function(self):

       def loop_x_shift_function(sim_box, cell_length_x): # pragma: no cover
            return 0
       return loop_x_shift_function
