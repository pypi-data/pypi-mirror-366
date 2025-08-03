from typing import Dict
import os
import click
from postomc import DepletionResults
import h5py
import pandas as pd
from pathlib import Path

@click.command()
@click.argument("file", type=str)
@click.option(
    "--split-nuclides",
    "-s",
    is_flag=True,
    default=False,
    show_default=True,
    help="Wether to create a nuclide indexed table or an (Element, A, I) indexed table.",
)
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
    "--output",
    "-o",
    default=None,
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
@click.option(
    "--material",
    "-m",
    default=None,
    type=int,
    help="Id of the desired material",
    show_default=True,
)
def export(file, split_nuclides, unit, time_unit, output, chain, material):
    """
    Converts depletion_result.h5 files to various output formats.
    """

    if not h5py.is_hdf5(file):
        raise ValueError(f"{file} is not an HDF5 file")
    if h5py.File(file)["/"].attrs["filetype"] != b"depletion results":
        raise ValueError(f"{file} is not a depletion result file.")
    if chain is None:
        chain = os.environ.get("OPENMC_CHAIN_FILE")

    if output is None:
        to_console(file, split_nuclides, unit, time_unit, chain, material)
    elif output.split(".")[-1] == "csv":
        to_csv(file, split_nuclides, unit, time_unit, output, chain, material)
    elif output.split(".")[-1] == "xlsx":
        to_excel(file, split_nuclides, unit, time_unit, output, chain, material)
    else:
        to_console(file, split_nuclides, unit, time_unit, chain, material)


def to_console(file, split_nuclides, unit, time_unit, chain, material):
    """
    Displays depletion results to the console for specified materials and nuclides.

    Parameters:
        file (str): Path to the depletion results file.
        split_nuclides (bool): Whether to split nuclides in the output DataFrame.
        unit (str): Unit for the depletion results (e.g., 'W', 'g').
        time_unit (str): Unit for time (e.g., 's', 'd', 'a').
        chain (str): Path to the depletion chain file.
        material (str or None): Material ID to display. If None, displays all materials or the only material present.

    Raises:
        ValueError: If the specified material ID does not exist in the results file.

    Outputs:
        Prints the depletion results DataFrame(s) to the console using click.echo().
    """
    res = DepletionResults(file, chain)
    materials = build_material_dict(file)

    dfs = res(unit, multiindex=split_nuclides, time_unit=time_unit, squeeze=False)
    if material is None and len(res.materials) == 1:
        material = list(dfs.keys())[0]
        click.echo(dfs[material].to_string())
    elif material is None and len(res.materials) != 1:
        for matid, df in dfs.items():
            click.echo(materials.get(matid, matid))
            click.echo(df.to_string())
            click.echo()
    else:
        if material not in dfs:
            raise ValueError(
                f"Material id {material} does not exist in file. Available: {list(dfs.keys())}"
            )
        else:
            click.echo(dfs[material].to_string())


def to_csv(file, split_nuclides, unit, time_unit, output, chain, material):
    """
    Converts depletion results from a file to a CSV format.

    Parameters:
        file (str): Path to the depletion results file.
        split_nuclides (bool): Whether to split nuclides in the output DataFrame's index.
        unit (str): The unit to use for the results (e.g., 'W', 'g', etc.).
        time_unit (str): The unit to use for time (e.g., 's', 'd', etc.).
        output (str): Path to the output CSV file.
        chain (str): Path to the depletion chain file.
        material (str or None): Material ID to extract results for. If None, uses the only material present or raises an error if multiple materials exist.

    Raises:
        NotImplementedError: If multiple materials are present and no material is specified.
        ValueError: If the specified material does not exist in the results file.

    Returns:
        None
    """
    res = DepletionResults(file, chain)

    dfs = res(unit, multiindex=split_nuclides, time_unit=time_unit, squeeze=False)
    if material is None and len(res.materials) == 1:
        material = dfs.keys()[0]
        dfs[material].to_csv(output)
    elif material is None and len(res.materials) != 1:
        raise NotImplementedError(
            f"Can't convert multi-material result file to csv. Available materials {list(dfs.keys())}"
        )
    else:
        if material not in dfs:
            raise ValueError(
                f"Material id {material} does not exist in file. Available: {list(dfs.keys())}"
            )
        else:
            dfs[material].to_csv(output)


def to_excel(file, split_nuclides, unit, time_unit, output, chain, material):
    """
    Export depletion results to an Excel file, with each material's data in a separate sheet.

    Parameters:
        file (str): Path to the depletion results file.
        split_nuclides (bool): Whether to split nuclides in the output DataFrame's index.
        unit (str): Unit for the depletion results (e.g., 'g/cm**3', 'g', etc.).
        time_unit (str): Unit for time (e.g., 's', 'd', 'y').
        output (str): Path to the output Excel file.
        chain (str): Path to the depletion chain file.
        material (str or None): Material ID to export. If None, exports all materials.

    Raises:
        ValueError: If the specified material does not exist in the results file.

    Notes:
        - If only one material is present and `material` is None, exports that material.
        - If multiple materials are present and `material` is None, exports all materials, each to a separate sheet.
        - If `material` is specified, exports only that material.
    """
    res = DepletionResults(file, chain)
    materials = build_material_dict(file)

    dfs = res(unit, multiindex=split_nuclides, time_unit=time_unit, squeeze=False)
    if material is None and len(res.materials) == 1:
        material = list(dfs.keys())[0]
        name = build_sheet_name(materials, material)
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            dfs[material].to_excel(writer, sheet_name=name)
    elif material is None and len(res.materials) != 1:
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            for matid, df in dfs.items():
                name = build_sheet_name(materials, matid)
                df.to_excel(writer, sheet_name=name)
    else:
        if material not in dfs:
            raise ValueError(
                f"Material id {material} does not exist in file. Available: {list(dfs.keys())}"
            )
        else:
            name = build_sheet_name(materials, material)
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                dfs[material].to_excel(writer, sheet_name=name)


def build_material_dict(file: Path | str):
    """
    Builds a dictionary mapping material IDs to their names from a summary HDF5 file.

    Given a file path, this function locates the corresponding 'summary.h5' file in the same directory.
    It reads the 'materials' group from the HDF5 file, filtering out non-depletable materials.
    For each depletable material, it extracts the material ID and name, and adds them to the dictionary.

    Args:
        file (str or Path): Path to a file in the target directory containing 'summary.h5'.

    Returns:
        dict: A dictionary where keys are material IDs (int) and values are material names (str).
              Returns an empty dictionary if 'summary.h5' does not exist.
    """
    summary = Path(file).parent / "summary.h5"
    if summary.exists():
        with h5py.File(summary, mode="r") as f:
            materials = {}
            for material in f["materials"]:
                if f[f"materials/{material}"].attrs["depletable"] == 0:
                    continue
                id = int(material.split()[-1])
                name = f[f"materials/{material}/name"][()].decode("utf-8")
                materials[id] = name
        return materials
    else:
        return {}


def build_sheet_name(materials: Dict[int, str], material: int) -> str:
    """
    Generates a valid Excel sheet name for a given material.

    Parameters:
        materials (dict): A dictionary mapping material identifiers to their names.
        material (str): The identifier of the material to generate the sheet name for.

    Returns:
        str: A sanitized sheet name for the material, ensuring it does not exceed 31 characters
             and does not contain forbidden characters (/, \\, *, ?, [, ]) as per Excel's requirements.
             If the name is too long, returns a default name in the format "Material <material>".
    """
    name = materials.get(material, f"Material {material}")
    forbidden_mapping = {"/": "-", "\\": "-", "*": "x", "?": " ", "[": "(", "]": ")"}
    if len(name) > 31:
        return f"Material {material}"
    for k, v in forbidden_mapping.items():
        name = name.replace(k, v)
    return name
