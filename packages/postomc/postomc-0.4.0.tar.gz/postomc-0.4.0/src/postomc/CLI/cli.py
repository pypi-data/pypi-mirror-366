import click
from postomc.CLI.export import export
from postomc.CLI.info import info
from postomc.CLI.plot import plot

@click.group()
def cli():
    """Command line utility for post-processing OpenMC depletion results."""
    pass

cli.add_command(export)
cli.add_command(info)
cli.add_command(plot)