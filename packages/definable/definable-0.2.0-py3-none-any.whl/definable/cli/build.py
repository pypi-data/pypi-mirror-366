import click
from typing import Any
from ..utils.docker_builder import DockerBuilder

@click.command()
@click.option('-t', '--tag', required=True, help='Docker image tag')
@click.option('-f', '--file', default='agent.yaml', help='Agent configuration file')
def build_command(tag: str, file: str) -> None:
    """Build agent Docker image"""
    try:
        builder = DockerBuilder(file)
        image = builder.build_image(tag)
        click.echo(f"Successfully built {tag}")
        click.echo(f"Image ID: {image.id}")
    except Exception as e:
        click.echo(f"Build failed: {e}", err=True)
        raise click.Abort()

# Export for CLI registration
build = build_command