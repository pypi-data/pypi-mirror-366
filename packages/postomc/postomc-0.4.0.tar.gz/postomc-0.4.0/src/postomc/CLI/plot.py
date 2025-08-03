import click
import os
import h5py
import matplotlib.pyplot as plt
from postomc.depletion_results import ureg
from postomc.depletion_results import DepletionResults

dimensions = {
    "atom": [ureg("atom").dimensionality, ureg("atom/cm**3").dimensionality],
    "mass": [ureg("g").dimensionality, ureg("g/cm**3").dimensionality],
    "activity": [ureg("Bq").dimensionality, ureg("Bq/cm**3").dimensionality],
    "heat": [ureg("W").dimensionality, ureg("W/cm**3").dimensionality],
}

DIMENSIONS = {
    ureg("atom").dimensionality: "Atom Number",
    ureg("atom/cm**3").dimensionality: "Atom Density",
    ureg("g").dimensionality: "Mass",
    ureg("g/cm**3").dimensionality: "Mass Density",
    ureg("Bq").dimensionality: "Activity",
    ureg("Bq/cm**3").dimensionality: "Activity Density",
    ureg("W").dimensionality: "Power",
    ureg("W/cm**3").dimensionality: "Power Density",
}

@click.command()
@click.argument("file", type=str)
@click.option("--nuclides", "-n", type=str)
@click.option(
    "--unit",
    "-u",
    default="g/cm**3",
    type=str,
    help="The desired unit.",
    show_default=True,
)
@click.option(
    "--time-unit",
    "-t",
    default="d",
    type=str,
    help="The desired time unit.",
    show_default=True,
)
@click.option(
    "--material",
    "-m",
    default=None,
    type=int,
    help="Id of the desired material",
    show_default=True,
)
@click.option(
    "--output",
    "-o",
    default="depletion.png",
    type=str,
    help="Path to the output file.",
    show_default=True,
)
@click.option(
    "--chain",
    "-c",
    default=None,
    type=str,
    help="Path to a depletion chain file.",
    show_default=True,
)
def plot(file, nuclides, unit, time_unit, material, output, chain):
    if not h5py.is_hdf5(file):
        raise ValueError(f"{file} is not an HDF5 file")
    if h5py.File(file)["/"].attrs["filetype"] != b"depletion results":
        raise ValueError(f"{file} is not a depletion result file.")

    if chain is None:
        chain = os.environ.get("OPENMC_CHAIN_FILE")
    res = DepletionResults(file, chain_file=chain)
    nmat = len(res.materials)
    if material is None and nmat > 1:
        raise ValueError(f"Multiple materials found ({nmat}), please specify a material with --material.")
    elif material is None and nmat == 1:
        material = list(res.materials.keys())[0]
    else:
        assert material in res.materials, f"Material {material} not found in the depletion results."

    if nuclides is None:
        raise ValueError("No nuclides specified for plotting.")
    nuclides = nuclides.split()
    fig, ax = plt.subplots()
    for nuclide in nuclides:
        df = res(unit, time_unit=time_unit, squeeze=False)[material]
        if nuclide not in df.index:
            raise ValueError(f"Nuclide {nuclide} not found in the depletion results.")
        series = df.loc[nuclide]
        ax.plot(series.index, series.values, label=nuclide)
    ax.legend()
    ax.grid()
    ax.set_xlabel(f"Time [{time_unit}]")
    ax.set_ylabel(f"{DIMENSIONS[ureg(unit).dimensionality]} [{unit}]")
    ax.set_title("Depletion Results")
    fig.tight_layout()
    plt.savefig(output)
