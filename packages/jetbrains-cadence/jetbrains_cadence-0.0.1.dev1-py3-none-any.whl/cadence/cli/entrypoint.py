import click


@click.group(invoke_without_command=True)
def root() -> None:
    click.echo("Hello from Cadence CLI!")
