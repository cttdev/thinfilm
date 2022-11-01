import numpy as np
from materials import Material
from utils import Y


def get_complex_index_of_refraction(material, wavelengths):
    """
    Returns the complex index of refraction at given wavelengths.

    N = n - ik
    """
    return material.get_n(wavelengths) - 1j * material.get_k(wavelengths)  # 2.19


def calculate_eta(material, angle_of_incidence, model_with_p_waves, wavelengths):
    """
    Calculates the tilted optical admittance (eta) for a given material, angle of incidence, and wavelengths.
    """
    N = get_complex_index_of_refraction(material, wavelengths)

    # Calculate the characteristic optical admittance of the medium
    y = N * Y  # 2.29

    # Calculate the tilted optical admittance (eta)
    if model_with_p_waves:
        # p-waves
        eta = y / np.cos(angle_of_incidence)  # 2.68
    else:
        # s-waves
        eta = y * np.cos(angle_of_incidence)  # 2.69

    return eta


class OpticalAssembly:
    """
    Repreents a thin film optical assembly consisting of a substrate with multiple thin films stacked on top.

    Parameters:
    wavelengths (float or list): wavelengths of light in nm
    substrate_material (Material): material of the substrate
    angle_of_incidence (float): angle of incidence in radians
    model_with_p_waves (bool): whether to model the assembly with p-waves or s-waves

    """

    def __init__(
        self,
        wavelengths,
        substrate_material,
        angle_of_incidence,
        model_with_p_waves=False,
    ):
        self.wavelengths = wavelengths
        self.angle_of_incidence = angle_of_incidence
        self.model_with_p_waves = model_with_p_waves

        # Calculate the substrate's chracteristic matrix
        substrate_eta = calculate_eta(
            substrate_material, angle_of_incidence, model_with_p_waves, wavelengths
        )

        self.char_mat = np.array(
            [[np.full(len(substrate_eta), 1)], [substrate_eta]]
        )  # 2.99

        # Transpose matrix to make it easier to multiply
        self.char_mat = np.transpose(self.char_mat, (2, 0, 1))

    def stack_thin_film(self, material, thickness):
        """
        Stacks a thin film on top of the optical assembly.

        Parameters:
        material (Material): material of the thin film
        thickness (float): thickness of the thin film in nm

        """
        # Calculate the thin film's chracteristic matrix
        thin_film_eta = calculate_eta(
            material, self.angle_of_incidence, self.model_with_p_waves, self.wavelengths
        )
        thin_film_N = get_complex_index_of_refraction(material, self.wavelengths)

        # Calculate delta
        delta = (
            2 * np.pi * thin_film_N * thickness * np.cos(self.angle_of_incidence)
        ) / self.wavelengths  # After 2.95

        # Calculate the thin film's characteristic matrix
        # [cos(delta)               (i * sin(delta)) / eta_1]
        # [(i * eta_1 * sin(delta)) cos(delta)              ]
        thin_film_char_mat = np.array(
            [
                [np.cos(delta), (1j * np.sin(delta)) / thin_film_eta],
                [(1j * thin_film_eta * np.sin(delta)), np.cos(delta)],
            ]
        )

        # Calculate the new characteristic matrix of the assembly
        # Transposes the thin film's characteristic matrix to make it easier to multiply
        self.char_mat = np.matmul(
            np.transpose(thin_film_char_mat, (2, 0, 1)), self.char_mat
        )  # 2.99

        return thin_film_char_mat

    def calculate_assembly_reflectance(self, incident_medium_material):
        """
        Calculates the reflectance of the optical assembly. Assumes the incident medium is stacked on top of the optical assembly.

        Parameters:
        incident_medium_material (Material): material of the incident medium
        """
        incident_medium_eta = calculate_eta(
            incident_medium_material,
            self.angle_of_incidence,
            self.model_with_p_waves,
            self.wavelengths,
        )

        # Extract values from the characteristic matrix
        B = self.char_mat[:, 0].flatten()  # 2.99
        C = self.char_mat[:, 1].flatten()  # 2.99

        # Calculate the input optical addmittance of the assembly (gamma)
        gamma = C / B  # 2.100

        # Calculate the reflectance
        R = (incident_medium_eta - gamma) / (incident_medium_eta + gamma)  # 2.102
        R *= np.conj(R)

        return R


if __name__ == "__main__":
    wavelengths = np.arange(400, 800, 1)

    # Create materials
    substrate_material = Material("materials/Si.txt", "materials/Si.txt")
    thin_film_material = Material("materials/Si3N4.txt", "materials/Si3N4.txt")
    air_material = Material(1.0, 0.0)

    # Create optical assembly
    assembly = OpticalAssembly(wavelengths, substrate_material, 0, False)

    # Stack thin film
    assembly.stack_thin_film(thin_film_material, 84)

    # Calculate reflectance
    R = assembly.calculate_assembly_reflectance(air_material)

    # Plot reflectance
    import matplotlib.pyplot as plt

    plt.title("Reflectance vs. Wavelength of 84nm Si3N4 film on Si Substrate")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Reflectance")

    plt.plot(wavelengths, R)
    plt.show()
