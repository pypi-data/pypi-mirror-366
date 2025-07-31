import os
import tempfile
import time
from typing import Optional

import click
import requests

from ..utils.code_packager import CodePackager
from ..utils.yaml_parser import ConfigParser


@click.command()
@click.option(
    "--deployment-server",
    "-d",
    default="http://159.69.38.8:8081",
    help="Deployment server URL (default: http://159.69.38.8:8081)",
)
@click.option(
    "--config",
    "-c",
    default="agent.yaml",
    help="Agent configuration file (default: agent.yaml)",
)
@click.option(
    "--check", is_flag=True, help="Check connection and package without uploading"
)
def push_command(deployment_server: str, config: str, check: bool) -> None:
    """Push agent code to deployment server"""

    def show_spinner(message: str, duration: float = 1.0):
        """Show animated spinner with message"""
        spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        start_time = time.time()
        i = 0
        click.echo(f"\r{spinner_chars[i]} {message}", nl=False)
        while time.time() - start_time < duration:
            i = (i + 1) % len(spinner_chars)
            click.echo(f"\r{spinner_chars[i]} {message}", nl=False)
            time.sleep(0.1)
        click.echo(f"\r✓ {message}")

    def show_progress_stage(stage: str, emoji: str = "📦"):
        """Show progress stage with emoji"""
        click.echo(f"{emoji} {stage}")

    # Check deployment server connectivity
    if check:
        show_spinner("Checking deployment server connection...")
        try:
            response = requests.get(f"{deployment_server}/health", timeout=10)
            if response.status_code == 200:
                click.echo("✓ Deployment server connection successful")
                return
            else:
                click.echo(
                    f"✗ Deployment server returned status {response.status_code}",
                    err=True,
                )
                raise click.Abort()
        except requests.exceptions.RequestException as e:
            click.echo(f"✗ Failed to connect to deployment server: {e}", err=True)
            raise click.Abort()

    try:
        # Get agent name from CLI args or agent.yaml
        config_data = ConfigParser.load_config(config)
        agent_name = config_data.platform.name

        # Initialize packager and check package
        show_progress_stage("Validating package", "🔍")
        packager = CodePackager()
        package_info = packager.get_package_info()

        if not package_info["valid"]:
            click.echo(f"✗ Error: {package_info['error']}", err=True)
            raise click.Abort()

        click.echo(
            f"✓ Package validated: {package_info['file_count']} files, {package_info['total_size']} bytes"
        )

        # Create temporary package
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
            temp_package_path = temp_file.name

        try:
            # Package the code
            show_progress_stage("Packaging code", "📦")
            show_spinner("Creating package...", 2.0)
            packager.create_package(temp_package_path)

            # Upload to deployment server
            show_progress_stage("Uploading to deployment server", "🚀")
            show_spinner("Uploading package...", 1.5)

            try:
                with open(temp_package_path, "rb") as f:
                    files = {"file": (f"{agent_name}.zip", f, "application/zip")}
                    response = requests.post(
                        f"{deployment_server}/push",
                        files=files,
                        timeout=300,  # 5 minutes timeout for build and deploy
                    )

                if response.status_code == 200:
                    result = response.json()

                    show_progress_stage("Deployment completed", "🎉")
                    click.echo(f"✓ Agent deployed successfully!")
                    click.echo(f"📍 Deployment URL: {result['url']}")
                    click.echo(f"🏷️  Agent Name: {result['agent_name']}")
                    click.echo(f"🔢 Version: v{result['version']}")
                    click.echo(f"🐳 Container ID: {result['container_id'][:12]}...")
                    click.echo(f"🖼️  Image: {result['image_tag']}")

                else:
                    error_msg = response.text
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", error_msg)
                    except:
                        pass
                    click.echo(f"✗ Deployment failed: {error_msg}", err=True)
                    raise click.Abort()

            except requests.exceptions.RequestException as e:
                click.echo(f"✗ Failed to connect to deployment server: {e}", err=True)
                raise click.Abort()
            except Exception as e:
                click.echo(f"✗ Unexpected error: {str(e)}", err=True)
                raise click.Abort()

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_package_path)
            except:
                pass

    except Exception as e:
        if not isinstance(e, click.Abort):
            click.echo(f"Error: {e}", err=True)
        raise click.Abort()


# Export for CLI registration
push = push_command
