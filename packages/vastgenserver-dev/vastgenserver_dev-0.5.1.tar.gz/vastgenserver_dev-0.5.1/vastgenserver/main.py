# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
import click
from typing import List, Optional
import yaml
from pathlib import Path
from vastgenserver.schema.config import DeploymentConfig, AppConfig
from vastgenserver.api.frontend import FastApiFrontend
from vastgenserver.engine.ray.importer import get_all_services

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_LOG_LEVEL = "info"
DEFAULT_ALLOW_CORS = "enable"


def common_service_options(func):
    """Decorator for common service options shared by all services"""
    func = click.option(
        "--host",
        default=DEFAULT_HOST,
        help=f"Host to run the server on. Default: {DEFAULT_HOST}",
    )(func)
    func = click.option(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to run the server on. Default: {DEFAULT_PORT}",
    )(func)
    func = click.option(
        "--log-level",
        type=click.Choice(["debug", "info", "warning", "error", "critical"]),
        default=DEFAULT_LOG_LEVEL,
        help=f"Logging level for the server. Default: {DEFAULT_LOG_LEVEL}",
    )(func)
    func = click.option(
        "--allow-cors",
        type=click.Choice(["enable", "disable"]),
        default=DEFAULT_ALLOW_CORS,
        help=f"Control CORS: enable|disable. Default: {DEFAULT_ALLOW_CORS}",
    )(func)
    func = click.option("--model-path", required=True, help="Path to the model")(func)
    func = click.option(
        "--device", help="Device to run the model (e.g. 'cpu', 'cuda:0')"
    )(func)
    return func


def start_service(service_type: str, **kwargs):
    """Start a service with the given configuration"""
    click.echo(f"Starting {service_type} service with config: {kwargs}")

    config = AppConfig()
    config.host = kwargs.get("host", DEFAULT_HOST)
    config.port = kwargs.get("port", DEFAULT_PORT)
    config.log_level = kwargs.get("log_level", DEFAULT_LOG_LEVEL)
    config.allow_cors = kwargs.get("allow_cors", DEFAULT_ALLOW_CORS)

    # Extract service-specific config
    extract_method = getattr(config, f"extract_{service_type}_config")
    extract_method(kwargs["model_path"], kwargs.get("device"))

    app = FastApiFrontend(config)
    app.start()


@click.group()
def cli():
    """One-click deploy service management system for vastgenserver."""
    pass


@cli.command()
def list():
    """List all supported services"""
    click.echo("Supported services:")
    for service in get_all_services():
        click.echo(f"  - {service}")


@cli.command()
@click.option(
    "--gen-config",
    type=click.Path(),
    required=False,
    default="default_config.yaml",
    help="Generate a service config template file",
)
@click.option(
    "--service-list",
    type=str,
    required=False,
    help="Comma-separated service to include (e.g., --service-list ASR,TTS)",
)
@click.option(
    "--run-config",
    type=click.Path(exists=True),
    required=False,
    help="Path to the service configuration file",
)
def service(gen_config, service_list, run_config):
    """service management commands \n
    Two mutually exclusive modes: \n
    1. Generate config: vastgenserver.service --list ASR,TTS [--gen-config your_conf.yaml] \n
    2. Run services: vastgenserver.service --run-config your_conf.yaml \n
    """
    if run_config and service_list:
        raise click.UsageError("Cannot specify both --run-config and --service-list")

    if not run_config and not service_list:
        raise click.UsageError("Must specify either --run-config or --service-list")

    if service_list:
        services = [s.strip() for s in service_list.split(",")]
        invalid_services = [s for s in services if s not in get_all_services()]
        if invalid_services:
            raise click.UsageError(
                f"Unsupported services: {', '.join(invalid_services)}\n"
                f"Supported services: {', '.join(get_all_services())}\n"
                # "Use 'vastgenserver.list' to see all supported services."
            )
        app_config = AppConfig()
        conf_file = Path(gen_config)
        app_config.get_registry(services).to_yaml(conf_file)
        click.echo(f"Configuration template generated at: {gen_config}")
        click.echo(f"Included services: {service_list}")
        return

    if run_config:
        click.echo(f"Running services with config: {run_config}")
        app_config = AppConfig.from_yaml(run_config)
        app = FastApiFrontend(app_config)
        app.start()


# # Dynamically create service commands for all supported services
# for service in SUPPORTED_SERVICES:
#     @cli.command(name=service)
#     @common_service_options
#     def service_command(**kwargs):
#         """Service management command"""
#         # Get the service name from the click context
#         service_name = click.get_current_context().info_name
#         start_service(service_name, **kwargs)
#
#     # Update the docstring for each service
#     service_command.__doc__ = f"{service.upper()} service management commands"
#
#     # Add the command to the CLI
#     cli.add_command(service_command)

if __name__ == "__main__":
    cli()
