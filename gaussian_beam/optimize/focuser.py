from typing import *

from scipy.optimize import minimize_scalar
from scipy.optimize import Bounds
from ..components.sequence import Sequence
from copy import deepcopy
from ..utils.units import *

class Focuser:
    def __init__(self, 
                 sequence: Sequence, 
                 free_component_index: int, 
                 focus_beam_index: int, 
                 focus_position: float,
                 optimization_axis: Optional[int]=0
                 ):
        self.sequence = sequence
        self.free_component_index = free_component_index
        self.collimation_beam_index = focus_beam_index
        self.optimization_axis = optimization_axis
        self.focus_position = focus_position
        
        self.target_beam = sequence.beams[focus_beam_index]
        self.target_component = sequence.lens_list[free_component_index]
        
        if (
            (self.sequence.z_lens[self.free_component_index] > focus_position)
            or
            (self.sequence.z_lens[self.free_component_index+2] < focus_position)
        ):
            raise Exception("Invalid focus position")
                
    def run(self):
        
        def cost_func(z):
            new_lens_list = deepcopy(self.sequence.lens_list)
            new_lens_list[self.free_component_index].z = z
            sequence = Sequence(
                new_lens_list, 
                (self.sequence.z_lens[0], self.sequence.z_lens[-1]), 
                self.sequence.beams[0]
                )
            return (
                sequence.beams[self.collimation_beam_index].z_center[self.optimization_axis]
                - self.focus_position
            ) ** 2
        
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