import click

@click.command
def version():
    """Print version and exit
    """
    print(f"Facet v. 1.1.9 (August 1, 2025)")
