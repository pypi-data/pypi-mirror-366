"""
命令行工具

提供配置诊断、验证和管理功能。
"""

import sys
from typing import Optional

import click

from .common.config import get_config_manager
from .common.config_validator import ConfigValidator, diagnose_configuration_issues, print_config_report


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug mode')
def cli(debug: bool):
    """MCP ImageUtils 命令行工具"""
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)


@cli.command()
def config():
    """显示当前配置"""
    print_config_report()


@cli.command()
def diagnose():
    """诊断配置问题"""
    diagnose_configuration_issues()


@cli.command()
@click.option('--generator', help='指定生成器名称 (bfl, openai, etc.)')
def validate(generator: Optional[str]):
    """验证配置"""
    from .generation import get_registry
    
    validator = ConfigValidator()
    registry = get_registry()
    
    if generator:
        # 验证特定生成器
        if generator not in registry.list_registered_classes():
            click.echo(f"❌ Generator '{generator}' not found")
            click.echo(f"Available generators: {', '.join(registry.list_registered_classes())}")
            sys.exit(1)
        
        gen_instance = registry.get_generator(generator)
        if gen_instance and hasattr(gen_instance, 'config'):
            required_keys = []
            if hasattr(gen_instance.config, 'get_required_keys'):
                required_keys = gen_instance.config.get_required_keys()
            
            is_valid, errors = validator.validate_generator_config(generator, required_keys)
            
            click.echo(f"{generator.upper()} Generator Configuration:")
            if is_valid:
                click.echo("✅ Valid")
            else:
                click.echo("❌ Invalid")
                for error in errors:
                    click.echo(f"  - {error}")
        else:
            click.echo(f"❌ Generator '{generator}' not properly configured")
    else:
        # 验证所有生成器
        from .common.config_validator import validate_all_generators
        
        results = validate_all_generators()
        if not results:
            click.echo("No generators found to validate")
            return
        
        all_valid = True
        for gen_name, (is_valid, errors) in results.items():
            click.echo(f"{gen_name.upper()} Generator:")
            if is_valid:
                click.echo("  ✅ Valid")
            else:
                all_valid = False
                click.echo("  ❌ Invalid")
                for error in errors:
                    click.echo(f"    - {error}")
        
        if all_valid:
            click.echo("\n🎉 All configurations are valid!")
        else:
            click.echo("\n⚠️  Some configurations have issues")


@cli.command()
@click.argument('key')
@click.argument('value')
@click.option('--sensitive', is_flag=True, help='Mark as sensitive information')
def set_config(key: str, value: str, sensitive: bool):
    """设置配置值"""
    from .common.config import set_config as _set_config
    
    _set_config(key, value, sensitive)
    click.echo(f"✅ Set {key} = {'***' if sensitive else value}")


@cli.command()
@click.argument('key')
def get_config(key: str):
    """获取配置值"""
    from .common.config import get_config as _get_config
    
    value = _get_config(key)
    if value is not None:
        click.echo(f"{key} = {value}")
    else:
        click.echo(f"❌ Configuration key '{key}' not found")


@cli.command()
def list_generators():
    """列出所有生成器"""
    from .generation import get_registry, initialize_generators
    
    # 初始化生成器
    initialize_generators()
    
    registry = get_registry()
    
    click.echo("Registered Generators:")
    for gen_name in registry.list_registered_classes():
        status = "✅ Enabled" if registry.is_enabled(gen_name) else "❌ Disabled"
        click.echo(f"  {gen_name}: {status}")
        
        # 显示生成器信息
        info = registry.get_generator_info(gen_name)
        if info:
            click.echo(f"    Display Name: {info['display_name']}")
            click.echo(f"    Description: {info['description']}")


@cli.command()
def create_example_config():
    """创建示例配置文件"""
    import shutil
    from pathlib import Path
    
    current_dir = Path.cwd()
    example_file = Path(__file__).parent.parent.parent / "mcp-imgutils.example.json"
    target_file = current_dir / "mcp-imgutils.json"
    
    if target_file.exists():
        if not click.confirm(f"Configuration file {target_file} already exists. Overwrite?"):
            click.echo("Cancelled")
            return
    
    try:
        shutil.copy2(example_file, target_file)
        click.echo(f"✅ Created configuration file: {target_file}")
        click.echo("Please edit the file and add your API keys")
    except Exception as e:
        click.echo(f"❌ Failed to create configuration file: {e}")


@cli.command()
def version():
    """显示版本信息"""
    try:
        import importlib.metadata
        version = importlib.metadata.version("mcp-imgutils")
        click.echo(f"MCP ImageUtils v{version}")
    except Exception:
        click.echo("MCP ImageUtils (development version)")


if __name__ == "__main__":
    cli()
