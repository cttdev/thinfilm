import numpy as np
from materials import Material
from thinfilm import OpticalAssembly

# Materials
si = Material("materials/Si.txt", "materials/Si.txt")
si3n4 = Material("materials/Si3N4.txt", "materials/Si3N4.txt")
sio2 = Material("materials/SiO2.txt", "materials/SiO2.txt")
air = Material(1.0, 0.0)

# Wavelengths
wavelengths = np.arange(400, 800, 1)

# Assembly Setup
thickness_step = 4 # nm
thicknesses_si3n4 = np.arange(0, 100, thickness_step) # nm
thicknesses_sio2 = np.arange(0, 100, thickness_step) # nm

# Create optical assembly
for thickness_si3n4 in thicknesses_si3n4:
    for thickness_sio2 in thicknesses_sio2:
        assembly = OpticalAssembly(wavelengths, si, 0, False)

        # Add thin films
        assembly.stack_thin_film(si3n4, thickness_si3n4)
        assembly.stack_thin_film(sio2, thickness_sio2)

        # Calculate reflectance
        reflectance = assembly.calculate_assembly_reflectance(air)

        