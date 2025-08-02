import click

@click.command()
@click.argument('name', default='you')

def hello(name):
    """Greet the person specified by name."""
    click.echo(f"Hello {name}!")