import numpy as np
from scipy.integrate import dblquad
class GaussianBeam:
    def __init__(self, z_center: float, waist_1: float, waist_2: float, rotation: float, power: float, wavelength: float):
        self.z_center = z_center
        self.waist = np.array([waist_1, waist_2])
        self.rotation = rotation
        self.power = power
        self.wavelength = wavelength
        self.I_0 = 2 * self.power / (np.pi * self.waist[0] * self.waist[1])
        self.z_R = np.pi * self.waist**2 / wavelength
        
    def radius_one_over_e_sq(self, z):
        return self.waist * np.sqrt(1 + ((z - self.z_center) / self.z_R)**2)
    
    def radius_fwhm(self, z):
        return self.radius_one_over_e_sq(z) * np.sqrt(2 * np.log(2))
    
    def wavefront_curvature(self, z):
        if np.abs(z - self.z_center) < 1e-12:
            return np.inf
        else:
            return z * (1 + (self.z_R / (z - self.z_center))**2)
        
    def divergence(self):
        return self.wavelength / (np.pi * self.waist)
    
    def intensity(self, z):
        w_z = self.radius_one_over_e_sq(z)
        return (
            lambda x, y: 
                self.I_0 * (self.waist[0] / w_z[0]) * (self.waist[1] / w_z[1]) * np.exp(-2 * (x**2 / w_z[0]**2 + y**2 / w_z[1]**2))
        )
    
    def power_through_aperture(self, z: float, R: float):
        intensity_func = lambda y, x: self.intensity(z)(x, y) * float(x**2 + y**2 < R**2)
        w_z = self.radius_one_over_e_sq(z)
        return dblquad(intensity_func, -w_z[0] * 10, w_z[0] * 10, -w_z[1] * 10, w_z[1] * 10)[0]
    
    def pass_lens(self, z: float, f: float):
        new_waist = self.waist / np.sqrt(1 + (self.z_R / f)**2)
        new_z_center = z + f / (1 + (self.z_R / f)**2)
        return GaussianBeam(new_z_center, new_waist[0], new_waist[1], self.rotation, self.power, self.wavelength)
    