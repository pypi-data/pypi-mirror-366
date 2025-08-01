import os

import click
import inquirer
import requests

from .config import config
from .devtools import devtools
from .plugin import plugin


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def check_backend_status():
    """Check backend connection status and token validity"""
    from synapse_sdk.devtools.config import get_backend_config

    backend_config = get_backend_config()
    if not backend_config:
        return 'not_configured', 'No backend configured'

    try:
        # Try an authenticated endpoint to verify token validity
        # Use /users/me/ which requires authentication
        response = requests.get(
            f'{backend_config["host"]}/users/me/',
            headers={'Synapse-Access-Token': f'Token {backend_config["token"]}'},
            timeout=5,
        )

        if response.status_code == 200:
            return 'healthy', f'Connected to {backend_config["host"]}'
        elif response.status_code == 401:
            return 'auth_error', 'Invalid token (401)'
        elif response.status_code == 403:
            return 'forbidden', 'Access forbidden (403)'
        elif response.status_code == 404:
            # If /users/me/ doesn't exist, try /health as fallback
            try:
                health_response = requests.get(
                    f'{backend_config["host"]}/health',
                    headers={'Synapse-Access-Token': f'Token {backend_config["token"]}'},
                    timeout=3,
                )
                if health_response.status_code == 200:
                    return 'healthy', f'Connected to {backend_config["host"]}'
                elif health_response.status_code == 401:
                    return 'auth_error', 'Invalid token (401)'
                elif health_response.status_code == 403:
                    return 'forbidden', 'Access forbidden (403)'
                else:
                    return 'error', f'HTTP {health_response.status_code}'
            except:  # noqa: E722
                return 'error', 'Endpoint not found (404)'
        else:
            return 'error', f'HTTP {response.status_code}'

    except requests.exceptions.Timeout:
        return 'timeout', 'Connection timeout (>5s)'
    except requests.exceptions.ConnectionError:
        return 'connection_error', 'Connection failed'
    except Exception as e:
        return 'error', f'Connection error: {str(e)}'


def check_agent_status():
    """Check agent configuration status"""
    from synapse_sdk.devtools.config import load_devtools_config

    config = load_devtools_config()
    agent_config = config.get('agent', {})

    if not agent_config.get('id'):
        return 'not_configured', 'No agent selected'

    return 'configured', f'{agent_config.get("name", "")} (ID: {agent_config["id"]})'


def display_connection_status():
    """Display connection status for backend and agent"""
    click.echo(click.style('Connection Status:', fg='white', bold=True))

    # Check backend status (async with timeout)
    backend_status, backend_msg = check_backend_status()

    # Backend status with specific handling for auth errors
    if backend_status == 'healthy':
        click.echo(f'🟢 Backend: {click.style(backend_msg, fg="green")}')
    elif backend_status == 'not_configured':
        click.echo(f'🔴 Backend: {click.style(backend_msg, fg="yellow")}')
    elif backend_status in ['auth_error', 'forbidden']:
        click.echo(f'🔴 Backend: {click.style(backend_msg, fg="red", bold=True)}')
    else:
        click.echo(f'🔴 Backend: {click.style(backend_msg, fg="red")}')

    # Agent status (config check only, no network call)
    agent_status, agent_msg = check_agent_status()
    if agent_status == 'configured':
        click.echo(f'🟢 Agent: {click.style(agent_msg, fg="green")}')
    else:
        click.echo(f'🔴 Agent: {click.style(agent_msg, fg="yellow")}')

    click.echo()  # Empty line for spacing


def run_devtools(build=True):
    """Run devtools with default settings"""
    try:
        from synapse_sdk.devtools.config import get_server_config
        from synapse_sdk.devtools.server import create_devtools_server
        from synapse_sdk.devtools.utils import find_available_port, is_port_available

        if build:
            click.echo('Building...')
            build_frontend()

        click.echo('Starting Synapse Devtools...')

        # Get server configuration defaults
        server_config = get_server_config()
        host = server_config['host']
        port = server_config['port']

        # Check if the port is available, fallback to next available port if not
        if not is_port_available(host, port):
            try:
                fallback_port = find_available_port(host, port + 1)
                click.echo(click.style(f'Port {port} is in use, falling back to port {fallback_port}', fg='yellow'))
                port = fallback_port
            except RuntimeError as e:
                click.echo(click.style(f'Failed to find available port: {e}', fg='red'), err=True)
                return

        server = create_devtools_server(host=host, port=port)
        server.start_server()
    except ImportError:
        click.echo(
            click.style(
                'Devtools dependencies not installed. Install with: pip install synapse-sdk[dashboard]', fg='red'
            ),
            err=True,
        )
    except KeyboardInterrupt:
        click.echo('\nDevtools stopped.')
    except Exception as e:
        click.echo(click.style(f'Failed to start devtools: {e}', fg='red'), err=True)


def build_frontend():
    """Build the frontend assets"""
    import subprocess
    from pathlib import Path

    # Find the web directory
    devtools_dir = Path(__file__).parent.parent / 'devtools' / 'web'

    if not devtools_dir.exists():
        click.echo(click.style(f'Frontend directory not found: {devtools_dir}', fg='red'), err=True)
        return False

    try:
        # Check if npm is available
        subprocess.run(['npm', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.echo(click.style('npm not found. Please install Node.js and npm.', fg='red'), err=True)
        return False

    try:
        # Install dependencies if node_modules doesn't exist
        if not (devtools_dir / 'node_modules').exists():
            click.echo('Installing dependencies...')
            result = subprocess.run(['npm', 'install'], cwd=devtools_dir, capture_output=True, text=True)
            if result.returncode != 0:
                click.echo(click.style(f'npm install failed:\n{result.stderr}', fg='red'), err=True)
                return False

        # Build the frontend
        result = subprocess.run(['npm', 'run', 'build'], cwd=devtools_dir, capture_output=True, text=True)

        if result.returncode != 0:
            click.echo(click.style(f'Frontend build failed:\n{result.stderr}', fg='red'), err=True)
            return False

        click.echo(click.style('Build completed successfully!', fg='green'))
        return True

    except Exception as e:
        click.echo(click.style(f'Build failed: {e}', fg='red'), err=True)
        return False


def run_config():
    """Run the configuration menu"""
    from .config import interactive_config

    interactive_config()


@click.group(invoke_without_command=True)
@click.option('--dev-tools', is_flag=True, help='Start devtools immediately')
@click.pass_context
def cli(ctx, dev_tools):
    """Synapse SDK - Interactive CLI"""

    # Handle --dev-tools flag
    if dev_tools:
        run_devtools()
        return

    if ctx.invoked_subcommand is None:
        while True:
            clear_screen()  # Always clear screen at start of main menu loop
            click.echo(click.style('🚀 Synapse SDK', fg='cyan', bold=True))
            click.echo()
            display_connection_status()

            try:
                questions = [
                    inquirer.List(
                        'choice',
                        message='Select an option:',
                        choices=[
                            ('🌐 Run Dev Tools', 'devtools'),
                            ('⚙️  Configuration', 'config'),
                            ('🔌 Plugin Management', 'plugin'),
                            ('🚪 Exit', 'exit'),
                        ],
                    )
                ]

                answers = inquirer.prompt(questions)
                if not answers or answers['choice'] == 'exit':
                    clear_screen()
                    click.echo(click.style('👋 Goodbye!', fg='green'))
                    break

                if answers['choice'] == 'devtools':
                    run_devtools()
                    break  # Exit after devtools finishes
                elif answers['choice'] == 'config':
                    run_config()
                    # Config menu returned, continue to main menu loop
                elif answers['choice'] == 'plugin':
                    click.echo(click.style('🔌 Plugin Management', fg='cyan', bold=True))
                    click.echo('For plugin management, use: synapse plugin --help\n')
                    click.echo('Press Enter to return to main menu...')
                    input()
                    # Don't break - continue to main menu loop

            except (KeyboardInterrupt, EOFError):
                clear_screen()
                click.echo(click.style('👋 Goodbye!', fg='yellow'))
                break


cli.add_command(plugin)
cli.add_command(config)
cli.add_command(devtools)
