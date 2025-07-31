import click
import os
from pathlib import Path
from typing import Optional
import re
from jinja2 import Environment, FileSystemLoader

@click.command()
@click.option('--name', help='Agent name (will prompt if not provided)')
@click.option('--description', help='Agent description (will prompt if not provided)')
@click.option('--version', help='Agent version (will prompt if not provided)')
@click.option('--force', is_flag=True, help='Overwrite existing files')
def init_command(name: Optional[str], description: Optional[str], version: Optional[str], force: bool) -> None:
    """Initialize a new agent project"""
    current_dir = Path.cwd()
    
    # Check if files already exist
    files_to_create = ['main.py', 'agent.yaml', '.agentignore', 'README.md']
    existing_files = [f for f in files_to_create if (current_dir / f).exists()]
    
    if existing_files and not force:
        click.echo(f"⚠️  Files already exist: {', '.join(existing_files)}")
        click.echo("Use --force to overwrite existing files")
        raise click.Abort()
    
    # Get agent details
    if name:
        agent_name = name
    else:
        agent_name = click.prompt('Agent name', default='demo-agent')
    
    # Validate agent name
    if not _is_valid_agent_name(agent_name):
        click.echo("❌ Agent name must contain only letters, numbers, and hyphens")
        raise click.Abort()
    
    if description:
        agent_description = description
    else:
        agent_description = click.prompt('Description', default='A simple demo agent')
    
    if version:
        agent_version = version
    else:
        agent_version = click.prompt('Version', default='1.0.0')
    
    # Generate class name from agent name
    class_name = _agent_name_to_class_name(agent_name)
    
    # Template variables
    template_vars = {
        'agent_name': agent_name,
        'class_name': class_name,
        'description': agent_description,
        'version': agent_version
    }
    
    try:
        # Setup Jinja2 environment
        template_dir = Path(__file__).parent.parent / "templates" / "init"
        env = Environment(loader=FileSystemLoader(template_dir))
        
        # Create files from templates
        _render_template_to_file(env, 'main.py.jinja2', current_dir / 'main.py', template_vars)
        click.echo("✓ Created main.py")
        
        _render_template_to_file(env, 'agent.yaml.jinja2', current_dir / 'agent.yaml', template_vars)
        click.echo("✓ Created agent.yaml")
        
        _render_template_to_file(env, 'agentignore.jinja2', current_dir / '.agentignore', template_vars)
        click.echo("✓ Created .agentignore")
        
        _render_template_to_file(env, 'README.md.jinja2', current_dir / 'README.md', template_vars)
        click.echo("✓ Created README.md")
        
        # Success message with next steps
        click.echo("\n🎉 Agent project initialized successfully!")
        click.echo("\nNext steps:")
        click.echo("  1. Edit main.py to implement your agent logic")
        click.echo("  2. Run: definable serve")
        click.echo(f"  3. Test: curl http://localhost:8000/{agent_name}/v1/info")
        
    except Exception as e:
        click.echo(f"❌ Failed to create agent: {e}", err=True)
        raise click.Abort()

def _is_valid_agent_name(name: str) -> bool:
    """Validate agent name - only letters, numbers, hyphens"""
    return re.match(r'^[a-zA-Z0-9-]+$', name) is not None

def _agent_name_to_class_name(agent_name: str) -> str:
    """Convert agent-name to AgentName class name"""
    # Split by hyphens and capitalize each part
    parts = agent_name.split('-')
    class_name = ''.join(word.capitalize() for word in parts)
    return class_name

def _render_template_to_file(env: Environment, template_name: str, output_path: Path, template_vars: dict) -> None:
    """Render a Jinja2 template to a file"""
    template = env.get_template(template_name)
    content = template.render(**template_vars)
    output_path.write_text(content)

# Export for CLI registration
init = init_command