import click
import uvicorn
from ..server.app import AgentServer

@click.command()
@click.option('-p', '--port', default=8000, help='Port to serve on')
@click.option('-f', '--file', default='agent.yaml', help='Agent configuration file')
@click.option('--host', default='0.0.0.0', help='Host to bind to')
def serve_command(port: int, file: str, host: str) -> None:
    """Serve agent locally"""
    try:
        # TODO: to pass debug mode to the server
        server = AgentServer(file)
        click.echo(f"Starting agent server on {host}:{port}")
        uvicorn.run(server.app, host=host, port=port)
    except Exception as e:
        click.echo(f"Server failed to start: {e}", err=True)
        raise click.Abort()

# Export for CLI registration
serve = serve_command