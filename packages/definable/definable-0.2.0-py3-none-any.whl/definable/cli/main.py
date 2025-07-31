import click
from .build import build_command
from .serve import serve_command
from .init import init_command
from .push import push_command
from .config import config_command

BANNER = """
██████╗ ███████╗███████╗██╗███╗   ██╗ █████╗ ██████╗ ██╗     ███████╗
██╔══██╗██╔════╝██╔════╝██║████╗  ██║██╔══██╗██╔══██╗██║     ██╔════╝
██║  ██║█████╗  █████╗  ██║██╔██╗ ██║███████║██████╔╝██║     █████╗  
██║  ██║██╔══╝  ██╔══╝  ██║██║╚██╗██║██╔══██║██╔══██╗██║     ██╔══╝  
██████╔╝███████╗██║     ██║██║ ╚████║██║  ██║██████╔╝███████╗███████╗
╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝

Build and deploy AI agents with ease
"""

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx) -> None:
    """Definable CLI - Build and deploy AI agents"""
    click.echo(BANNER)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

cli.add_command(init_command, name='init')
cli.add_command(build_command, name='build')
cli.add_command(serve_command, name='serve')
cli.add_command(push_command, name='push')
cli.add_command(config_command, name='config')

if __name__ == "__main__":
    cli()