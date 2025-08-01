#!/usr/bin/env python3
import click
import os
from pathlib import Path
from .deployer import WatsonXDeployer

@click.command()
@click.option('--env-file', default='.env', help='Path to environment file')
@click.option('--config-dir', default='.', help='Directory containing agent folders')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(env_file, config_dir, verbose):
    """Deploy AI agents to WatsonX.ai"""
    try:
        deployer = WatsonXDeployer(
            env_file=env_file,
            config_dir=config_dir,
            verbose=verbose
        )
        deployer.deploy_all()
        click.echo("✅ All agents deployed successfully!")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    main()