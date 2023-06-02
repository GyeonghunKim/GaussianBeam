from typing import *

from scipy.optimize import minimize_scalar
from scipy.optimize import Bounds
from ..components.sequence import Sequence
from copy import deepcopy
from ..utils.units import *

class Collimator:
    def __init__(self, 
                 sequence: Sequence, 
                 free_component_index: int, 
                 collimation_beam_index: int, 
                 optimization_axis: Optional[int]=0
                #  z_R_threshold: Optional[float]=100*cm
                 ):
        self.sequence = sequence
        self.free_component_index = free_component_index
        self.collimation_beam_index = collimation_beam_index
        self.optimization_axis = optimization_axis
        # self.z_R_threshold = z_R_threshold
        
        self.target_beam = sequence.beams[collimation_beam_index]
        self.target_component = sequence.lens_list[free_component_index]
        
    def run(self):
        
        def cost_func(z):
            new_lens_list = deepcopy(self.sequence.lens_list)
            new_lens_list[self.free_component_index].z = z
            sequence = Sequence(
                new_lens_list, 
                (self.sequence.z_lens[0], self.sequence.z_lens[-1]), 
                self.sequence.beams[0]
                )
            return -sequence.beams[self.collimation_beam_index].z_R[self.optimization_axis]
        
        z_init = self.sequence.lens_list[self.free_component_index].z
        bound = (
                self.sequence.z_lens[self.free_component_index], 
                self.sequence.z_lens[self.free_component_index+2]
            )
        
        
        res = minimize_scalar(
            cost_func, 
            bounds=bound, 
            method='bounded'
            )
        
        opt_lens_list = deepcopy(self.sequence.lens_list)
        opt_lens_list[self.free_component_index].z = res.x
        opt_sequence = Sequence(
            opt_lens_list, 
            (self.sequence.z_lens[0], self.sequence.z_lens[-1]), 
            self.sequence.beams[0]
            )
        return opt_sequence