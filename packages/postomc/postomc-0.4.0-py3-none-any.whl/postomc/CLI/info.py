import click
from pathlib import Path
import h5py
from postomc.depletion_results import ureg
from rich.console import Console
from rich.table import Table

@click.command()
@click.argument("file", type=str)
def info(file):
    """
    Displays information about the depletion result file.
    """
    console = Console()
    if not h5py.is_hdf5(file):
        raise ValueError(f"{file} is not an HDF5 file")

    p = Path(file)
    summary_path = p.parent / "summary.h5"
    
    
    with h5py.File(file, 'r') as f:
        if f["/"].attrs.get("filetype") != b"depletion results":
            raise ValueError(f"{file} is not a depletion result file.")

        console.print(f"{'Depletion File':<20} [italic]{file}[/italic]")
        if summary_path.exists():
            console.print(f"{'Summary File':<20} [italic]{summary_path}[/italic]")
        console.print()

        table = Table(title="Depletion Steps", show_header=True, header_style="bold")
        table.add_column("Step #", justify="left")
        table.add_column(r"t(i) \[days]", justify="left")
        table.add_column(r"t(i+1) \[days]", justify="left")
        table.add_column(r"Power \[W]", justify="left")

        time = f["/time"][...]
        power = f["/source_rate"][...].flatten()
        for istep, (left, right) in enumerate(time):
            table.add_row(
                f"{istep + 1}",
                f"{left * ureg('s').to('d').m:.2f}",
                f"{right * ureg('s').to('d').m:.2f}",
                f"{power[istep]:.2f}"
            )
            
        console.print(table)

        material_table = Table(title="Materials", show_header=True, header_style="bold")
        material_table.add_column("Id", justify="left")
        material_table.add_column("Name", justify="left")
        material_table.add_column("Nuclides", justify="left")
        material_table.add_column(r"Atom Density \[atom/b/cm]", justify="left")

        mat_ids = sorted(list(f["/materials"].keys()), key=int)
        if summary_path.exists():
            with h5py.File(summary_path, 'r') as summary:
                for mat_id in mat_ids:
                    mat = summary[f"/materials/material {mat_id}"]
                    name = mat["name"][()].decode("utf-8")
                    n_nuclides = len(mat["nuclides"][...])
                    atom_density = mat["atom_density"][()]
                    material_table.add_row(
                        mat_id,
                        name,
                        f"{n_nuclides}",
                        f"{atom_density:.2e}"
                    )

        console.print(material_table)
