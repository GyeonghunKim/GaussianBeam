import numpy as np

from typing import *
from ...utils.units import *
from .base_lens import BaseLens

class ThinLens(BaseLens):
    def __init__(self, z: float, f: float, name: Optional[str] = None):
        if name is  None:
            name = f"ThinLens f={f/mm}mm at z={z/mm}mm"
            
        super().__init__(z, f, name)
        self.ABCD = np.array([[1, 0], [-1/self.f, 1]]) 