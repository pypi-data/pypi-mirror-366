"""Code-server integration for remote plugin development."""

from typing import Optional

import click

from synapse_sdk.cli.config import fetch_agents_from_backend, get_agent_config
from synapse_sdk.devtools.config import get_backend_config


@click.command()
@click.option('--agent', help='Agent name or ID')
@click.option('--open-browser/--no-open-browser', default=True, help='Open in browser')
def code_server(agent: Optional[str], open_browser: bool):
    """Connect to web-based code-server on an agent for plugin development."""

    # Get current agent configuration
    agent_config = get_agent_config()
    backend_config = get_backend_config()

    if not backend_config:
        click.echo("❌ No backend configured. Run 'synapse config' first.")
        return

    # If no agent specified, use current agent or let user choose
    if not agent:
        if agent_config and agent_config.get('id'):
            agent = agent_config['id']
            click.echo(f'Using current agent: {agent_config.get("name", agent)}')
        else:
            # List available agents
            agents, error = fetch_agents_from_backend()
            if not agents:
                click.echo('❌ No agents available. Check your backend configuration.')
                return

            if len(agents) == 1:
                # If only one agent, use it
                agent = agents[0]['id']
                click.echo(f'Using agent: {agents[0].get("name", agent)}')
            else:
                # Let user choose
                click.echo('Available agents:')
                for i, agent_info in enumerate(agents, 1):
                    status = agent_info.get('status_display', 'Unknown')
                    name = agent_info.get('name', agent_info['id'])
                    click.echo(f'  {i}. {name} ({status})')

                try:
                    choice = click.prompt('Select agent', type=int)
                    if 1 <= choice <= len(agents):
                        agent = agents[choice - 1]['id']
                    else:
                        click.echo('❌ Invalid selection')
                        return
                except (ValueError, EOFError, KeyboardInterrupt):
                    click.echo('\n❌ Cancelled')
                    return

    # Connect to agent and get code-server info
    try:
        # Get agent details from backend to get the agent URL
        from synapse_sdk.clients.backend import BackendClient

        backend_client = BackendClient(backend_config['host'], access_token=backend_config['token'])

        # Get agent information
        try:
            agent_info = backend_client._get(f'agents/{agent}/')
        except Exception as e:
            click.echo(f'❌ Failed to get agent information for: {agent}')
            click.echo(f'Error: {e}')
            return

        if not agent_info or not agent_info.get('url'):
            click.echo(f'❌ Agent {agent} does not have a valid URL')
            click.echo(f'Agent info: {agent_info}')
            return

        # Get the agent token from local configuration
        agent_token = agent_config.get('token')
        if not agent_token:
            click.echo('❌ No agent token found in configuration')
            click.echo("Run 'synapse config' to configure the agent")
            return

        # Create agent client
        from synapse_sdk.clients.agent import AgentClient

        client = AgentClient(base_url=agent_info['url'], agent_token=agent_token, user_token=backend_config['token'])

        # Get code-server information
        try:
            info = client.get_code_server_info()
        except AttributeError:
            # Fallback to direct API call if method doesn't exist
            response = client._get('code-server/info/')
            info = response if isinstance(response, dict) else {}
        except Exception as e:
            # Handle other errors
            click.echo(f'❌ Failed to get code-server info: {e}')
            click.echo(f'Agent URL: {agent_info.get("url")}')
            click.echo('\nNote: The agent might not have code-server endpoint implemented yet.')
            return

        if not info or not info.get('available', False):
            message = info.get('message', 'Code-server is not available') if info else 'Failed to get code-server info'
            click.echo(f'❌ {message}')
            click.echo('\nTo enable code-server, reinstall the agent with code-server support.')
            return

        # Display connection information
        click.echo('\n✅ Code-Server is available!')

        workspace = info.get('workspace', '/home/coder/workspace')

        # Show web browser access
        click.echo('\n🌐 Web-based VS Code:')
        click.echo(f'   URL: {info["url"]}')
        password = info.get('password')
        if password:
            click.echo(f'   Password: {password}')
        else:
            click.echo('   Password: Not required (passwordless mode)')

        click.echo(f'\n📁 Workspace: {workspace}')

        # Optionally open in browser
        if open_browser and info.get('url'):
            import subprocess

            click.echo('\nAttempting to open in browser...')

            # Try to open browser, suppressing stderr to avoid xdg-open noise
            try:
                # Use subprocess to suppress xdg-open errors
                result = subprocess.run(['xdg-open', info['url']], capture_output=True, text=True, timeout=2)
                if result.returncode != 0:
                    click.echo('⚠️  Could not open browser automatically (no display?)')
                    click.echo(f'👉 Please manually open: {info["url"]}')
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # xdg-open not available or timed out
                click.echo('⚠️  Could not open browser (headless environment)')
                click.echo(f'👉 Please manually open: {info["url"]}')
            except Exception:
                # Fallback for other errors
                click.echo(f'👉 Please manually open: {info["url"]}')

        # Show additional instructions
        click.echo('\n📝 Quick Start:')
        click.echo('1. Open the URL in your browser')
        click.echo('2. Enter the password if prompted')
        click.echo('3. Start coding in the web-based VS Code!')

    except Exception as e:
        import traceback

        click.echo(f'❌ Failed to connect to agent: {e}')

        # Show more detailed error in debug mode
        if '--debug' in click.get_current_context().params:
            click.echo('\nDebug trace:')
            click.echo(traceback.format_exc())

        click.echo('\nTroubleshooting:')
        click.echo('1. Check if agent is running and accessible')
        click.echo('2. Verify the agent has code-server support (may need agent update)')
        click.echo('3. Check agent logs for more details')
        click.echo('4. Try running with --no-open-browser to see connection details')
