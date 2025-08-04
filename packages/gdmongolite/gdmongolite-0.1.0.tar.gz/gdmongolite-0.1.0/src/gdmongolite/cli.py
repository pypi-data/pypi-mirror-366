import asyncio
import click
import aioconsole
from .core import DB

@click.group()
def main():
    """gdmongolite: lightweight, auto-maintained all-in-one MongoDB toolkit."""
    pass

@main.command()
def migrate():
    """Run database migrations."""
    click.echo("Running migrations...")

@main.command()
def shell():
    """Start an interactive shell."""
    from .schema import db
    
    async def main_async():
        shell_context = {
            "db": db,
            "asyncio": asyncio,
        }
        await aioconsole.interact(locals=shell_context)

    asyncio.run(main_async())

@main.command()
@click.option('--collection', required=True, help='The name of the collection to generate the model from.')
@click.option('--out', required=True, help='The path to the output file.')
def gen_model(collection, out):
    """Generate a new model."""
    click.echo(f"Generating model from collection {collection} to {out}...")

@main.command()
def test():
    """Run tests."""
    click.echo("Running tests...")

if __name__ == '__main__':
    main()
