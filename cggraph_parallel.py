from matplotlib import pyplot as plt
import numpy as np
from materials import Material
from thinfilm import OpticalAssembly
import colour
from multiprocessing import Manager, Pool, Process
from queue import Empty

# Materials
si = Material("materials/Si.txt", "materials/Si.txt")
si3n4 = Material("materials/Si3N4.txt", "materials/Si3N4.txt")
sio2 = Material("materials/SiO2.txt", "materials/SiO2.txt")
air = Material(1.0, 0.0)

# Wavelengths
wavelengths = np.arange(400, 800, 1)

# Assembly Setup
thickness_step = 4  # nm
thicknesses_si3n4 = np.arange(0, 500, thickness_step)  # nm
thicknesses_sio2 = np.arange(0, 500, thickness_step)  # nm

# Setup Colour
cmfs = colour.MSDS_CMFS["CIE 1931 2 Degree Standard Observer"]
illuminant = colour.SDS_ILLUMINANTS["ISO 7589 Sensitometric Daylight"]
colour.set_domain_range_scale("1")  # We want to use the 0-1 scale for matplotlib


def process(thickness_si3n4, thickness_sio2, queue):
    assembly = OpticalAssembly(wavelengths, si, 0, False)

    # Add thin films
    assembly.stack_thin_film(si3n4, thickness_si3n4)
    assembly.stack_thin_film(sio2, thickness_sio2)

    # Calculate reflectances
    reflectances = assembly.calculate_assembly_reflectance(air)
    reflectances = np.real(reflectances)

    # Generate Spectrial Power Distribution from Reflectances
    sd = colour.SpectralDistribution(
        dict(zip(wavelengths, reflectances)), name="Reflectance"
    )

    # Convert to RGB with cmfs and illuminant
    xyz = colour.sd_to_XYZ(sd, cmfs, illuminant)
    rgb = colour.XYZ_to_sRGB(xyz)
    rgb = np.clip(
        rgb, 0, 1
    )  # Clip to 0-1 range to compensate for values outside of the sRGB color space

    print(
        f"Thickness Si3N4: {thickness_si3n4} nm, Thickness SiO2: {thickness_sio2} nm, RGB: {rgb}"
    )

    # Generate colored rectangle
    rectangle = plt.Rectangle(
        (thickness_si3n4, thickness_sio2),
        thickness_step,
        thickness_step,
        facecolor=rgb,
        edgecolor="none",
    )

    # Put the rectangle in the queue to be plotted
    queue.put(rectangle)

    return rgb


def plot_rectangles_from_queue(queue, event):
    # Setup Plotting
    fig, ax = plt.subplots()
    ax.set_aspect("equal")
    ax.set_xlabel("Si3N4 Thickness (nm)")
    ax.set_ylabel("SiO2 Thickness (nm)")
    ax.set_title("Color of Thin Film Stack (400-800 nm)")

    # While queue is not empty, plot rectangles
    while not event.is_set():
        try:
            rectangle = queue.get(block=False)
            ax.add_patch(rectangle)
            ax.autoscale_view()
            print("Plotting... Rectangles Left:", queue.qsize())
            queue.task_done()
        except Empty:
            pass

    plt.show()


if __name__ == "__main__":
    # Setup queue for plotting
    m = Manager()
    q = m.Queue()
    e = m.Event()

    # Generate thickness combinations
    pool_tuple = [
        (thickness_si3n4, thickness_sio2, q)
        for thickness_si3n4 in thicknesses_si3n4
        for thickness_sio2 in thicknesses_sio2
    ]

    # Start the plotting process
    plotting_process = Process(target=plot_rectangles_from_queue, args=(q, e))
    plotting_process.start()

    # Multiprocessing
    res = []
    with Pool(processes=8) as pool:
        res = pool.starmap(process, pool_tuple)

    # Wait for plotting to finish
    q.join()

    # Tell the plotting process to show the plot
    e.set()

    # Wait for the plotting process to finish
    plotting_process.join()

    # Kill the plotting process
    plotting_process.kill()
