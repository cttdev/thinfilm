from enum import Enum
import os
import numpy as np
import pandas

from utils import make_interpolator


class Material:
    """
    Represents a material with an index of refraction n and and extinction coefficent k.

    Parameters:
    n (callable): returns the index of refraction as a float at a given wavelength
    k (callable): extinction coefficient as a float at a given wavelength

    """

    def __init__(self, n, k):
        """
        Creates a material with a constant index of refraction and extinction coefficient.

        Parameters:
        n (float or csv name): index of refraction
        k (float or csv name): extinction coefficient

        If a float is given, the material will have a constant index of refraction and extinction coefficient.
        If a csv name is given, the material will be created from the csv file.

        NOTE: The csv file must have columns "Wavelength(nm)", "n", and "k".

        """
        if isinstance(n, float):
            # Constant index of refraction
            self.n = lambda wavelength: np.full(len(wavelength), n) if isinstance(wavelength, list) or isinstance(wavelength, np.ndarray) else n
        elif os.path.isfile(n):
            # If a file is given, try to load the material and generate an interpolator
            data = pandas.read_csv(n, sep=self.FileFormat.SEPERATOR.value)
            self.n = make_interpolator(
                data[self.FileFormat.WAVELENGTH.value], data[self.FileFormat.N.value]
            )
        else:
            raise TypeError("n must be a float or a csv name!")

        if isinstance(k, float):
            # Constant extinction coefficient
            self.k = lambda wavelength: np.full(len(wavelength), k) if isinstance(wavelength, list) or isinstance(wavelength, np.ndarray) else k
        elif os.path.isfile(k):
            # If a file is given, try to load the material and generate an interpolator
            data = pandas.read_csv(k, sep=self.FileFormat.SEPERATOR.value)
            self.k = make_interpolator(
                data[self.FileFormat.WAVELENGTH.value], data[self.FileFormat.K.value]
            )
        else:
            raise TypeError("k must be a float or a csv name!")

    def get_n(self, wavelength):
        """
        Returns the index of refraction at a given wavelength.

        """
        return self.n(wavelength)

    def get_k(self, wavelength):
        """
        Returns the extinction coefficient at a given wavelength.

        """
        return self.k(wavelength)

    class FileFormat(Enum):
        """
        Enum for the file format of the csv files.

        """

        SEPERATOR = "\t"
        WAVELENGTH = "Wavelength(nm)"
        N = "n"
        K = "k"


if __name__ == "__main__":
    # Test the Material class
    material = Material(1.5, 0.0)
    print(material.get_n(500))
    print(material.get_k(500))

    material = Material("materials/Si.txt", "materials/Si.txt")
    print(material.get_n(500))
    print(material.get_k(500))
