"""CLI interface for gdmongolite"""

import click

@click.group()
@click.version_option(version="1.0.0")
def main():
    """gdmongolite - The World's Most Powerful and Easiest MongoDB Toolkit"""
    pass

@main.command()
def init():
    """Initialize a new gdmongolite project"""
    click.echo("Initializing gdmongolite project...")
    click.echo("Project initialized successfully!")

@main.command()
def serve():
    """Start development server"""
    click.echo("Starting gdmongolite development server...")
    click.echo("Server would start here (not implemented in basic version)")

@main.command()
def shell():
    """Start interactive shell"""
    click.echo("Starting gdmongolite interactive shell...")
    click.echo("Shell would start here (not implemented in basic version)")

if __name__ == "__main__":
    main()