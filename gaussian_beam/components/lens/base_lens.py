import numpy as np

from typing import *
from ...utils.units import *


class BaseLens:
    def __init__(self, z: float, f: float, name: Optional[str] = None):
        self.z = z
        self.f = f
        if name is not None:
            self.name = name
        else:
            self.name = f"Lens f={f/mm}mm at z={z/mm}mm"
        