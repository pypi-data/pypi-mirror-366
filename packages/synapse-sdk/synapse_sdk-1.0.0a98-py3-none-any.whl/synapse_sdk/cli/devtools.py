import os
import sys

import click

from synapse_sdk.i18n import gettext as _


@click.command()
@click.option('--host', default=None, help='Host to bind the devtools server')
@click.option('--port', default=None, type=int, help='Port to bind the devtools server')
@click.option('--debug', is_flag=True, help='Run in debug mode')
def devtools(host, port, debug):
    """Start the Synapse devtools web interface"""

    try:
        from synapse_sdk.devtools.config import get_server_config
        from synapse_sdk.devtools.server import create_devtools_server
        from synapse_sdk.devtools.utils import find_available_port, is_port_available

    except ImportError:
        click.echo(
            click.style(
                _('Devtools dependencies not installed. Install with: pip install synapse-sdk[devtools]'), fg='red'
            ),
            err=True,
        )
        sys.exit(1)

    click.echo('Building assets...')
    from synapse_sdk.cli import build_frontend

    if not build_frontend():
        click.echo(click.style('Build failed, continuing with existing assets...', fg='yellow'))

    if debug:
        click.echo(_('Starting devtools in debug mode...'))
        os.environ['UVICORN_LOG_LEVEL'] = 'debug'

    click.echo('Starting Synapse Devtools...')

    # Get server configuration from config file
    server_config = get_server_config()

    # Use CLI arguments if provided, otherwise use config defaults
    final_host = host if host is not None else server_config['host']
    final_port = port if port is not None else server_config['port']

    # Check if the port is available, fallback to next available port if not
    if not is_port_available(final_host, final_port):
        try:
            fallback_port = find_available_port(final_host, final_port + 1)
            click.echo(click.style(f'Port {final_port} is in use, falling back to port {fallback_port}', fg='yellow'))
            final_port = fallback_port
        except RuntimeError as e:
            click.echo(click.style(f'Failed to find available port: {e}', fg='red'), err=True)
            sys.exit(1)

    # Create and start the devtools server
    # Pass the current working directory as the plugin directory
    plugin_directory = os.getcwd()
    server = create_devtools_server(host=final_host, port=final_port, plugin_directory=plugin_directory)

    try:
        server.start_server()
    except KeyboardInterrupt:
        click.echo(_('\nDevtools stopped.'))
    except Exception as e:
        click.echo(click.style(f'Failed to start devtools: {e}', fg='red'), err=True)
        sys.exit(1)
