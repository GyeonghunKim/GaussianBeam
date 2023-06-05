import numpy as np
from numpy.typing import *
from typing import *
from scipy.integrate import dblquad
from ..components.lens import BaseLens


class GaussianBeam:
    def __init__(
        self,
        z_center: Union[float, NDArray[np.float64]],
        waist: Union[float, NDArray[np.float64]],
        rotation: float,
        power: float,
        wavelength: float,
    ):
        if isinstance(z_center, float):
            self.z_center = np.array([z_center, z_center])
        else:
            self.z_center = np.array(z_center)
            
        if isinstance(waist, float):
            self.waist = np.array([waist, waist])
        else:
            self.waist = np.array(waist)
            
        self.rotation = rotation
        self.power = power
        self.wavelength = wavelength
        self.I_0 = 2 * self.power / (np.pi * self.waist[0] * self.waist[1])
        self.z_R = np.pi * self.waist**2 / wavelength

    def radius_one_over_e_sq(self, z):
        return self.waist * np.sqrt(1 + ((z - self.z_center) / self.z_R) ** 2)

    def radius_fwhm(self, z):
        return self.radius_one_over_e_sq(z) * np.sqrt(2 * np.log(2))

    def wavefront_curvature(self, z):
        if np.abs(z - self.z_center) < 1e-12:
            return np.inf
        else:
            return z * (1 + (self.z_R / (z - self.z_center)) ** 2)

    def divergence(self):
        return self.wavelength / (np.pi * self.waist)

    def intensity(self, z):
        w_z = self.radius_one_over_e_sq(z)
        return (
            lambda x, y: self.I_0
            * (self.waist[0] / w_z[0])
            * (self.waist[1] / w_z[1])
            * np.exp(-2 * (x**2 / w_z[0] ** 2 + y**2 / w_z[1] ** 2))
        )

    def power_through_aperture(self, z: float, R: float, rough_mode: bool = False):
        intensity_func = lambda y, x: self.intensity(z)(x, y) * (
            x**2 + y**2 < R**2
        )
        w_z = self.radius_one_over_e_sq(z)
        if rough_mode:
            x_list = np.linspace(-w_z[0] * 10, w_z[0] * 10, 101)
            y_list = np.linspace(-w_z[1] * 10, w_z[1] * 10, 101)
            X, Y = np.meshgrid(x_list, y_list)
            I = intensity_func(X, Y)
            return np.sum(I) * (x_list[1] - x_list[0]) * (y_list[1] - y_list[0])
        else:
            return dblquad(
                intensity_func, -w_z[0] * 10, w_z[0] * 10, -w_z[1] * 10, w_z[1] * 10
            )[0]

    def pass_lens(self, lens: BaseLens):
        z = lens.z - self.z_center
        r = self.z_R / (z - lens.f)
        M_r = np.abs(lens.f / (z - lens.f))
        M = M_r / np.sqrt(1 + r**2)

        new_waist = self.waist * M  # self.waist / np.sqrt(1 + (self.z_R / lens.f)**2)
        new_z_center = (
            lens.z + lens.f + M**2 * (z - lens.f)
        )  # lens.z + lens.f / (1 + (lens.f / self.z_R)**2)
        return GaussianBeam(
            new_z_center,
            new_waist,
            self.rotation,
            self.power,
            self.wavelength,
        )
