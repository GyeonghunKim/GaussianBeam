import numpy as np
from numpy.typing import *
import matplotlib.pyplot as plt

from typing import *
from ..components.lens import BaseLens
from ..beam.beam import GaussianBeam
from ..utils.units import *

class Sequence:
    def __init__(
        self,
        lens_list: Iterable[BaseLens],
        z_span: Iterable[float],
        initial_beam: GaussianBeam,
    ):
        self.lens_list = lens_list
        self.z_lens = [z_span[0]] + [lens.z for lens in self.lens_list] + [z_span[1]]
        if (sorted(self.z_lens) != self.z_lens):
            raise ValueError("Lens sequence should be in position order.")

        self.beams = [initial_beam]
        for lens in self.lens_list:
            self.beams.append(self.beams[-1].pass_lens(lens=lens))

    def plot_xz(self, overlap: bool = True):
        fig = plt.figure(figsize=(12, 5))
        ax = fig.add_subplot(111)
        z_lists = np.array(
            [
                np.linspace(z1, z2, 101)[:-1]
                for z1, z2 in zip(self.z_lens[:-1], self.z_lens[1:])
            ]
        )
        waist_list = np.array(
            [
                [beam.radius_one_over_e_sq(z) for z in z_list]
                for beam, z_list in zip(self.beams, z_lists)
            ]
        )
        w_plot = waist_list.reshape((waist_list.shape[0] * waist_list.shape[1], 2))
        z_plot = z_lists.reshape((z_lists.shape[0] * z_lists.shape[1],))
        
        ax.plot(z_plot / mm, w_plot[:, 0] / mm, c="r", label = 'axis 1')
        ax.plot(z_plot / mm, -w_plot[:, 0] / mm, c="r")

        ax.plot(z_plot / mm, w_plot[:, 1] / mm, c="b", label = 'axis 2')
        ax.plot(z_plot / mm, -w_plot[:, 1] / mm, c="b")


        lens_radi = np.max(w_plot) * 1.2
        for lens in self.lens_list:
            ax.plot([lens.z/mm, lens.z/mm], [-lens_radi/mm, lens_radi/mm], "--", c="k")
            
        ax.legend()
        ax.set_xlabel('z (mm)')
        ax.set_ylabel('x, y (mm)')
        return fig, ax
