import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import docker
from jinja2 import Environment, FileSystemLoader

from ..utils.yaml_parser import ConfigParser


class DockerBuilder:
    def __init__(self, config_path: str = "agent.yaml") -> None:
        self.config = ConfigParser.load_config(config_path)
        self.docker_client = docker.from_env()

    def build_image(self, tag: str, context_path: str = ".") -> Any:
        """Build Docker image for the agent using docker-compose"""
        # Create temporary build context
        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_dir = temp_dir_obj.name

        try:
            # Copy source files
            self._copy_source_files(context_path, temp_dir)

            # Generate Dockerfile
            dockerfile_content = self._generate_dockerfile()
            dockerfile_path = Path(temp_dir) / "Dockerfile"
            dockerfile_path.write_text(dockerfile_content)

            # Generate requirements.txt
            requirements_content = self._generate_requirements()
            requirements_path = Path(temp_dir) / "requirements.txt"
            requirements_path.write_text(requirements_content)

            # Generate docker-compose.yml
            docker_compose_content = self._generate_docker_compose(tag)
            docker_compose_path = Path(temp_dir) / "docker-compose.yml"
            docker_compose_path.write_text(docker_compose_content)

            # Copy .dockerignore
            dockerignore_path = (
                Path(__file__).parent.parent / "templates" / ".dockerignore"
            )
            if dockerignore_path.exists():
                shutil.copy2(dockerignore_path, Path(temp_dir) / ".dockerignore")

            # Build image using docker-compose
            print(f"Building Docker image with docker-compose: {tag}")
            self._run_docker_compose_build(temp_dir, tag)

            # Clean up dangling images after build
            self._cleanup_dangling_images()

            # Return a simple object with the tag (maintaining interface compatibility)
            return type('BuildResult', (), {'id': tag, 'tags': [tag]})()

        finally:
            # Clean up temporary directory
            temp_dir_obj.cleanup()

    def _cleanup_dangling_images(self) -> None:
        """Remove dangling images created during build"""
        try:
            # Get dangling images
            dangling_images = self.docker_client.images.list(filters={"dangling": True})

            if dangling_images:
                print(f"Cleaning up {len(dangling_images)} dangling images...")
                for image in dangling_images:
                    try:
                        self.docker_client.images.remove(image.id, force=True)
                    except Exception:
                        pass  # Ignore errors during cleanup

        except Exception:
            pass  # Ignore cleanup errors

    def _copy_source_files(self, source_path: str, dest_path: str) -> None:
        """Copy source files to build context"""
        source = Path(source_path)
        dest = Path(dest_path)

        # Copy Python files and YAML config
        for file_pattern in ["*.py", "*.yaml", "*.yml"]:
            for file_path in source.glob(file_pattern):
                shutil.copy2(file_path, dest / file_path.name)

        # Copy directories (like models, data, etc.)
        for item in source.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                shutil.copytree(item, dest / item.name)

    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile from template"""
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("Dockerfile.jinja2")

        return template.render(
            python_version=self.config.build.python_version,
            system_packages=self.config.build.system_packages,
            environment_variables=self.config.build.environment_variables,
            platform_name=self.config.platform.name,
        )

    def _generate_requirements(self) -> str:
        """Generate requirements.txt"""
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("requirements.txt.jinja2")

        return template.render(dependencies=self.config.build.dependencies)

    def _generate_docker_compose(self, image_tag: str) -> str:
        """Generate docker-compose.yml from template"""
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("docker-compose.yml.jinja2")

        return template.render(
            platform_name=self.config.platform.name,
            image_tag=image_tag,
            environment_variables=self.config.build.environment_variables,
        )

    def _run_docker_compose_build(self, build_dir: str, tag: str) -> None:
        """Run docker-compose build and handle output"""
        try:
            # Run docker-compose build
            process = subprocess.Popen(
                ["docker-compose", "build", "--no-cache"],
                cwd=build_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Process output in real-time
            current_step = 0
            total_steps = 0
            
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if not line:
                    continue

                # Parse docker build output from docker-compose
                if "Step " in line and "/" in line:
                    # Extract step information
                    if "Step 1/" in line:
                        total_steps = int(line.split("/")[1].split(" ")[0])
                    
                    if line.startswith("Step "):
                        step_parts = line.split(" ")
                        if len(step_parts) >= 2 and "/" in step_parts[1]:
                            current_step = int(step_parts[1].split("/")[0])
                            step_name = line.split(" : ")[1] if " : " in line else "Unknown"
                            print(f"[{current_step}/{total_steps}] {step_name}")
                        else:
                            print(line)
                    else:
                        print(line)
                
                # Show important messages
                elif any(keyword in line.upper() for keyword in ["ERROR", "SUCCESS", "BUILT", "TAGGED"]):
                    print(line)
                
                # Show warnings but make them less prominent
                elif "WARNING" in line.upper() and "pip" not in line.lower():
                    print(f"⚠️  {line}")
                
                # Show building service messages
                elif "Building" in line or "Creating" in line:
                    print(line)

            # Wait for process to complete
            process.wait()
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, "docker-compose build")
                
            print(f"✅ Successfully built {tag}")

        except subprocess.CalledProcessError as e:
            raise Exception(f"Docker compose build failed with return code {e.returncode}")
        except FileNotFoundError:
            raise Exception("docker-compose command not found. Please install Docker Compose.")
        except Exception as e:
            raise Exception(f"Build failed: {str(e)}")
