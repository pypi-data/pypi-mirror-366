import click
import subprocess
import sys
import os
from typing import Optional
from ..utils.config_manager import ConfigManager
from ..base.models import UserConfig


@click.group(invoke_without_command=True)
@click.pass_context
def config_command(ctx) -> None:
    """Manage Definable configuration"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@config_command.command('set')
@click.argument('key')
@click.argument('value')
def set_config(key: str, value: str) -> None:
    """Set a configuration value"""
    try:
        config_manager = ConfigManager()
        config_manager.set(key, value)
        
        # Show masked value for sensitive keys
        if 'api_key' in key.lower() or 'token' in key.lower() or 'password' in key.lower():
            masked_value = f"{'*' * (len(value) - 4)}{value[-4:]}" if len(value) > 4 else "****"
            click.echo(f"✓ Set {key} = {masked_value}")
        else:
            click.echo(f"✓ Set {key} = {value}")
            
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Failed to set config: {e}", err=True)
        raise click.Abort()


@config_command.command('get')
@click.argument('key')
def get_config(key: str) -> None:
    """Get a configuration value"""
    try:
        config_manager = ConfigManager()
        value = config_manager.get(key)
        
        if value is None:
            click.echo(f"Key '{key}' not found")
            return
        
        # Show masked value for sensitive keys
        if 'api_key' in key.lower() or 'token' in key.lower() or 'password' in key.lower():
            masked_value = f"{'*' * (len(value) - 4)}{value[-4:]}" if len(value) > 4 else "****"
            click.echo(f"{key} = {masked_value}")
        else:
            click.echo(f"{key} = {value}")
            
    except Exception as e:
        click.echo(f"Failed to get config: {e}", err=True)
        raise click.Abort()


@config_command.command('list')
def list_config() -> None:
    """List all configuration values"""
    try:
        config_manager = ConfigManager()
        config_data = config_manager.list_config()
        
        if not config_data:
            click.echo("No configuration found")
            return
        
        click.echo("Current configuration:")
        for key, value in config_data.items():
            click.echo(f"  {key} = {value}")
            
    except Exception as e:
        click.echo(f"Failed to list config: {e}", err=True)
        raise click.Abort()


@config_command.command('delete')
@click.argument('key')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
def delete_config(key: str, yes: bool) -> None:
    """Delete a configuration value"""
    try:
        config_manager = ConfigManager()
        
        # Check if key exists
        current_value = config_manager.get(key)
        if current_value is None:
            click.echo(f"Key '{key}' not found")
            return
        
        # Confirm deletion unless --yes flag is used
        if not yes:
            if not click.confirm(f"Delete '{key}'?"):
                click.echo("Cancelled")
                return
        
        success = config_manager.delete(key)
        if success:
            click.echo(f"✓ Deleted {key}")
        else:
            click.echo(f"Key '{key}' not found")
            
    except Exception as e:
        click.echo(f"Failed to delete config: {e}", err=True)
        raise click.Abort()


@config_command.command('edit')
def edit_config() -> None:
    """Edit configuration file directly"""
    try:
        config_manager = ConfigManager()
        config_file = config_manager.get_config_file_path()
        
        # Get editor from config or environment
        editor = config_manager.get('editor') or os.getenv('EDITOR', 'nano')
        
        # Create config file if it doesn't exist
        if not config_manager.config_exists():
            config_manager.save_config(UserConfig())
            click.echo(f"Created new config file: {config_file}")
        
        # Open editor
        try:
            subprocess.run([editor, config_file], check=True)
            click.echo("✓ Config file updated")
        except subprocess.CalledProcessError:
            click.echo(f"Failed to open editor '{editor}'", err=True)
            click.echo(f"Config file location: {config_file}")
        except FileNotFoundError:
            click.echo(f"Editor '{editor}' not found", err=True)
            click.echo(f"Config file location: {config_file}")
            
    except Exception as e:
        click.echo(f"Failed to edit config: {e}", err=True)
        raise click.Abort()


@config_command.command('reset')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
def reset_config(yes: bool) -> None:
    """Reset all configuration"""
    try:
        config_manager = ConfigManager()
        
        if not config_manager.config_exists():
            click.echo("No configuration to reset")
            return
        
        # Confirm reset unless --yes flag is used
        if not yes:
            if not click.confirm("Reset all configuration?"):
                click.echo("Cancelled")
                return
        
        config_manager.reset()
        click.echo("✓ Configuration reset")
        
    except Exception as e:
        click.echo(f"Failed to reset config: {e}", err=True)
        raise click.Abort()


@config_command.command('show-keys')
def show_keys() -> None:
    """Show available configuration keys"""
    click.echo("Available configuration keys:")
    for field_name, field_info in UserConfig.__fields__.items():
        # Handle different Pydantic versions
        if hasattr(field_info, 'type_'):
            field_type = field_info.type_
        elif hasattr(field_info, 'annotation'):
            field_type = field_info.annotation
        else:
            field_type = str
        
        if hasattr(field_type, '__args__') and len(field_type.__args__) > 0:
            # Handle Optional types
            inner_type = field_type.__args__[0]
            type_name = getattr(inner_type, '__name__', str(inner_type))
        else:
            type_name = getattr(field_type, '__name__', str(field_type))
        
        description = ""
        if field_name == 'api_key':
            description = " - API key for authentication"
        elif field_name == 'default_endpoint':
            description = " - Default API endpoint URL"
        elif field_name == 'default_name':
            description = " - Default agent name"
        elif field_name == 'editor':
            description = " - Preferred text editor"
        
        click.echo(f"  {field_name} ({type_name}){description}")


# Export for CLI registration
config = config_command