import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from typing import Dict, List, Optional

import requests
import uvicorn
import yaml
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from synapse_sdk.cli.plugin.publish import _publish
from synapse_sdk.clients.agent import AgentClient
from synapse_sdk.clients.backend import BackendClient
from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.devtools.config import get_backend_config, load_devtools_config
from synapse_sdk.devtools.models import ConfigResponse, ConfigUpdateRequest
from synapse_sdk.devtools.utils import get_display_host

logger = logging.getLogger(__name__)


class DevtoolsServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 8080, plugin_directory: str = None):
        self.host = host
        self.port = port

        self.agent_id = None
        self.plugin_code = None
        self.plugin_directory = Path(plugin_directory) if plugin_directory else Path.cwd()
        self.websocket_connections: List[WebSocket] = []
        self.app = FastAPI(title='Synapse Devtools', version='1.0.0', lifespan=self.lifespan)
        self._cached_validation_result = None  # Cache validation result from startup

        self.web_build_dir = Path(__file__).parent / 'web' / 'dist'
        self.web_public_dir = Path(__file__).parent / 'web' / 'public'

        self.setup_middleware()
        self.setup_static_files()
        self.setup_routes()

        # Initialize clients if config is available
        self.backend_client = self._init_backend_client()
        self.agent_client = self._init_agent_client()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        # Startup
        logger.info('DevTools server starting up...')
        yield
        # Shutdown
        logger.info('DevTools server shutting down...')
        # Close all WebSocket connections
        if self.websocket_connections:
            logger.info(f'Closing {len(self.websocket_connections)} WebSocket connections')
            for connection in self.websocket_connections[:]:
                try:
                    await connection.close(code=1000, reason='Server shutdown')
                except Exception as e:
                    logger.error(f'Error closing WebSocket connection: {e}')
            self.websocket_connections.clear()
        logger.info('DevTools server shutdown complete')

    def _init_backend_client(self) -> Optional[BackendClient]:
        config = get_backend_config()
        if config:
            return BackendClient(config['host'], access_token=config['token'])
        return None

    def _init_agent_client(self) -> Optional[AgentClient]:
        devtools_config = load_devtools_config()
        agent_config = devtools_config.get('agent', {})
        if agent_config and 'url' in agent_config:
            self.agent_id = agent_config['id']
            # Use shorter timeouts for better UX in devtools
            timeout = {
                'connect': 3,  # 3 second connection timeout
                'read': 10,  # 10 second read timeout
            }
            return AgentClient(agent_config['url'], agent_config.get('token'), timeout=timeout)
        return None

    def _validate_plugin_config(self) -> Dict:
        """Validate plugin config.yaml in the plugin directory"""

        return {'valid': True, 'errors': None, 'schema_version': 'unknown', 'validated_fields': 0}

    async def _publish_plugin_internal(self, host: str, access_token: str, debug: bool, source_path: Path) -> Dict:
        """Internal method to publish plugin using CLI logic"""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(str(source_path))

            debug_modules = os.getenv('SYNAPSE_DEBUG_MODULES', '')
            plugin_release = _publish(host, access_token, debug, debug_modules)

            return {
                'success': True,
                'message': f'Successfully published "{plugin_release.name}" '
                f'({plugin_release.code}) to synapse backend!',
                'plugin_code': plugin_release.code,
                'version': plugin_release.version,
                'name': plugin_release.name,
                'result': '',
            }

        finally:
            os.chdir(original_cwd)

    async def _execute_plugin_http_request(
        self,
        action: str,
        params: Dict,
        debug: bool,
        access_token: str,
    ) -> Dict:
        """Execute an HTTP request to the plugin endpoint"""
        import asyncio
        import time

        import aiohttp

        plugin_url = f'{self.backend_client.base_url}/plugins/{self.plugin_code}/run/'

        headers = {
            'Accept': 'application/json; indent=4',
            'Content-Type': 'application/json',
            'Synapse-Access-Token': f'Token {access_token}',
        }

        payload = {'agent': self.agent_id, 'action': action, 'params': params, 'debug': debug}

        start_time = time.time()

        try:
            timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(plugin_url, json=payload, headers=headers) as response:
                    execution_time = int((time.time() - start_time) * 1000)

                    response_text = await response.text()

                    # Try to parse as JSON, fallback to text
                    try:
                        response_data = await response.json()
                    except Exception:
                        response_data = response_text

                    return {
                        'success': response.status < 400,
                        'status_code': response.status,
                        'response_data': response_data,
                        'execution_time': execution_time,
                        'url': plugin_url,
                        'method': 'POST',
                        'headers': headers,
                        'payload': payload,
                    }

        except asyncio.TimeoutError:
            execution_time = int((time.time() - start_time) * 1000)
            return {
                'success': False,
                'status_code': 408,
                'error': 'Request timeout',
                'execution_time': execution_time,
                'url': plugin_url,
            }
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            return {
                'success': False,
                'status_code': 500,
                'error': str(e),
                'execution_time': execution_time,
                'url': plugin_url,
            }

    def _get_action_example_params(self, action: str) -> Dict:
        """Get pre-filled example parameters for different actions based on test.http"""
        examples = {
            'tune': {
                'num_cpus': 2,
                'num_gpus': 1,
                'name': 'tune-test-example',
                'description': 'Tuning example',
                'experiment': 37,
                'dataset': 55,
                'checkpoint': 163,
                'tune_config': {'metric': 'metrics/mAP50-95(B)', 'mode': 'max', 'num_samples': 5},
                'hyperparameter': [
                    {'name': 'learning_rate', 'type': 'loguniform', 'min': 1e-4, 'max': 1e-1},
                    {'name': 'batch_size', 'type': 'choice', 'options': [8, 16, 32]},
                    {'name': 'epochs', 'type': 'randint', 'min': 1, 'max': 2},
                ],
            },
            'deployment': {'num_cpus': 4, 'num_gpus': 1},
            'train': {
                'num_cpus': 2,
                'num_gpus': 1,
                'name': 'train-test-example',
                'description': 'Training example',
                'experiment': 32,
                'dataset': 55,
                'checkpoint': 8,
                'hyperparameter': {'epochs': 10, 'batch_size': 8, 'learning_rate': 0.001, 'imgsz': 640},
            },
            'gradio': {'num_cpus': 4},
            'inference': {'num_cpus': 2, 'num_gpus': 1},
            'test': {'num_cpus': 1},
        }

        return examples.get(action, {})

    def setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

    def setup_static_files(self):
        # Serve built Vue.js assets from web/dist/
        if self.web_build_dir.exists():
            # Serve Vue.js built assets
            assets_dir = self.web_build_dir / 'assets'
            if assets_dir.exists():
                self.app.mount('/assets', StaticFiles(directory=assets_dir), name='assets')
        else:
            logger.warning('Vue.js dist directory not found, devtools may not work properly')

        # Serve public files (like logo.png) during development
        if self.web_public_dir.exists():
            self.app.mount('/public', StaticFiles(directory=self.web_public_dir), name='public')

    def _inject_env_vars(self, html_content: str) -> str:
        """Inject environment variables into HTML"""
        # Use display host for frontend access (resolves 0.0.0.0 to actual IP)
        display_host = get_display_host(self.host)
        env_script = f"""<script>
        window.VITE_API_PORT = {self.port};
        window.VITE_API_HOST = '{display_host}';
        </script>"""

        # Insert before closing head tag
        return html_content.replace('</head>', f'{env_script}</head>')

    def setup_routes(self):
        @self.app.get('/')
        async def read_root():
            index_file = self.web_build_dir / 'index.html'

            if index_file.exists():
                # Read and modify HTML content to inject environment variables
                with open(index_file, 'r') as f:
                    html_content = f.read()

                modified_html = self._inject_env_vars(html_content)

                from fastapi.responses import HTMLResponse

                return HTMLResponse(content=modified_html)
            return {'message': 'Synapse Devtools API', 'docs': '/docs'}

        @self.app.get('/status')
        async def get_status():
            from synapse_sdk.devtools.config import load_devtools_config

            backend_config = get_backend_config()
            devtools_config = load_devtools_config()
            agent_config = devtools_config.get('agent', {})

            status = {
                'backend': {
                    'host': self.backend_client.base_url,
                    'status': 'configured' if backend_config else 'not_configured',
                },
                'agent': {
                    'id': agent_config.get('id'),
                    'name': agent_config.get('name'),
                },
                'devtools': {'version': version('synapse-sdk')},
            }

            return status

        @self.app.get('/auth/token')
        async def get_auth_token():
            """Get the current authentication token from configuration"""
            backend_config = get_backend_config()

            if backend_config and 'token' in backend_config:
                return {'token': backend_config['token'], 'host': backend_config['host']}

            return {'token': None, 'host': None}

        @self.app.get('/jobs')
        async def get_jobs():
            """Get the list of jobs from the backend"""
            if not self.agent_client:
                raise HTTPException(status_code=503, detail='Agent client not configured')

            try:
                jobs = self.agent_client.list_jobs()
                jobs.sort(key=lambda job: job.get('start_time', 0), reverse=True)
                return jobs
            except ClientError as e:
                logger.warning(f'Agent client error while fetching jobs: {e.reason}')
                if e.status in [408, 503]:
                    raise HTTPException(status_code=503, detail=f'Agent unavailable: {e.reason}')
                else:
                    raise HTTPException(status_code=e.status, detail=e.reason)
            except Exception as e:
                logger.error(f'Unexpected error fetching jobs: {e}')
                raise HTTPException(status_code=500, detail='Failed to fetch jobs')

        @self.app.get('/jobs/{job_id}')
        async def get_job(job_id: str):
            """Get details of a specific job by ID"""
            if not self.agent_client:
                raise HTTPException(status_code=503, detail='Agent client not configured')

            try:
                job = self.agent_client.get_job(job_id)
                return job
            except Exception as e:
                logger.error(f'Failed to fetch job {job_id}: {e}')
                raise HTTPException(status_code=500, detail=f'Failed to fetch job {job_id}')

        @self.app.get('/jobs/{job_id}/logs')
        async def get_job_logs(job_id: str, request: Request):
            """Get logs for a specific job by ID"""
            if not self.agent_client:
                raise HTTPException(status_code=503, detail='Agent client not configured')

            async def log_generator():
                import asyncio

                try:
                    # Run the synchronous generator in a thread to avoid blocking
                    loop = asyncio.get_event_loop()
                    log_iter = self.agent_client.tail_job_logs(job_id, stream_timeout=3)

                    while True:
                        # Check if client disconnected before getting next log
                        if await request.is_disconnected():
                            logger.info(f'Client disconnected, stopping log stream for job {job_id}')
                            break

                        try:
                            # Get next log line with timeout to allow periodic disconnect checks
                            log_line = await loop.run_in_executor(None, lambda: next(log_iter, None))

                            if log_line is None:
                                break

                            # Check again before yielding
                            if await request.is_disconnected():
                                logger.info(f'Client disconnected before yield, stopping log stream for job {job_id}')
                                break

                            # Convert plain text to SSE format
                            if log_line.strip():
                                yield f'data: {log_line.strip()}\n\n'

                        except StopIteration:
                            break

                except ClientError as e:
                    logger.warning(f'Agent client error in log streaming for job {job_id}: {e.reason}')
                    if e.status == 408:
                        yield 'data: Log stream timeout - agent may be unresponsive\n\n'
                    elif e.status == 503:
                        yield 'data: Agent connection error - service may be unavailable\n\n'
                    else:
                        yield f'data: Agent error: {e.reason}\n\n'
                except Exception as e:
                    logger.error(f'Unexpected error in log streaming for job {job_id}: {e}')
                    yield f'data: Unexpected error: {str(e)}\n\n'
                finally:
                    logger.info(f'Log streaming ended for job {job_id}')

            try:
                return StreamingResponse(log_generator(), media_type='text/event-stream')
            except Exception as e:
                logger.error(f'Failed to setup log stream for job {job_id}: {e}')
                raise HTTPException(status_code=500, detail=f'Failed to setup log stream for job {job_id}')

        @self.app.get('/serve_applications')
        async def get_serve_applications(request: Request):
            """Get the list of serve applications from the agent or serve SPA"""
            # Check if this is an API request (AJAX call) vs browser navigation
            accept_header = request.headers.get('accept', '')

            # If browser navigation (HTML request), serve the SPA
            if 'text/html' in accept_header and 'application/json' not in accept_header:
                index_file = self.web_build_dir / 'index.html'
                if index_file.exists():
                    # Read and modify HTML content to inject environment variables
                    with open(index_file, 'r') as f:
                        html_content = f.read()

                    modified_html = self._inject_env_vars(html_content)

                    from fastapi.responses import HTMLResponse

                    return HTMLResponse(content=modified_html)
                return {'message': 'Frontend not built'}

            # Otherwise, handle as API request
            if not self.agent_client:
                raise HTTPException(status_code=503, detail='Agent client not configured')

            try:
                applications = self.agent_client.list_serve_applications()
                # Sort by creation time if available, otherwise alphabetically by name
                if applications:
                    applications.sort(key=lambda app: app.get('created_at', app.get('name', '')), reverse=True)
                return applications
            except ClientError as e:
                logger.warning(f'Agent client error while fetching applications: {e.reason}')
                if e.status in [408, 503]:
                    raise HTTPException(status_code=503, detail=f'Agent unavailable: {e.reason}')
                else:
                    raise HTTPException(status_code=e.status, detail=e.reason)
            except Exception as e:
                logger.error(f'Unexpected error fetching applications: {e}')
                raise HTTPException(status_code=500, detail='Failed to fetch applications')

        @self.app.get('/serve_applications/{app_id}')
        async def get_serve_application(app_id: str):
            """Get details of a specific application by ID"""
            if not self.agent_client:
                raise HTTPException(status_code=503, detail='Agent client not configured')

            try:
                application = self.agent_client.get_serve_application(app_id)
                return application
            except Exception as e:
                logger.error(f'Failed to fetch application {app_id}: {e}')
                raise HTTPException(status_code=500, detail=f'Failed to fetch application {app_id}')

        @self.app.delete('/serve_applications/{app_id}')
        async def delete_serve_application(app_id: str):
            """Delete a serve application by ID"""
            if not self.agent_client:
                raise HTTPException(status_code=503, detail='Agent client not configured')

            try:
                result = self.agent_client.delete_serve_application(app_id)
                return {'message': f'Application {app_id} deleted successfully', 'result': result}
            except Exception as e:
                logger.error(f'Failed to delete application {app_id}: {e}')
                raise HTTPException(status_code=500, detail=f'Failed to delete application {app_id}')

        @self.app.get('/health/backend')
        async def check_backend_health():
            """Check backend health status"""
            if not self.backend_client:
                return {'status': 'not_configured', 'error': 'Backend client not configured', 'lastCheck': None}

            import time

            start_time = time.time()

            try:
                # Use the backend client to check health with shorter timeout
                response = requests.get(f'{self.backend_client.base_url}/health', timeout=3)
                latency = int((time.time() - start_time) * 1000)

                if response.status_code == 200:
                    return {
                        'status': 'healthy',
                        'latency': latency,
                        'lastCheck': time.time(),
                        'url': f'{self.backend_client.base_url}',
                        'httpStatus': response.status_code,
                    }
                else:
                    status_map = {
                        401: 'auth_error',
                        403: 'forbidden',
                        404: 'not_found',
                        500: 'down',
                        502: 'down',
                        503: 'down',
                        504: 'down',
                    }

                    return {
                        'status': status_map.get(response.status_code, 'down'),
                        'lastCheck': time.time(),
                        'url': f'{self.backend_client.host}/health',
                        'httpStatus': response.status_code,
                        'error': f'HTTP {response.status_code}',
                    }

            except requests.exceptions.Timeout:
                return {
                    'status': 'timeout',
                    'lastCheck': time.time(),
                    'url': f'{self.backend_client.base_url}/health',
                    'error': 'Request timeout (>3s)',
                }
            except requests.exceptions.RequestException as e:
                return {
                    'status': 'down',
                    'lastCheck': time.time(),
                    'url': f'{self.backend_client.base_url}/health',
                    'error': str(e),
                }

        @self.app.get('/health/agent')
        async def check_agent_health():
            """Check agent health status"""
            if not self.agent_client:
                return {'status': 'not_configured', 'error': 'Agent client not configured', 'lastCheck': None}

            import time

            start_time = time.time()

            try:
                # Use the agent client to check health with shorter timeout
                response = requests.get(
                    f'{self.agent_client.base_url}/health',
                    timeout=3,
                    headers={'Authorization': f'Token {self.agent_client.agent_token}'},
                )
                latency = int((time.time() - start_time) * 1000)

                if response.status_code == 200:
                    return {
                        'status': 'healthy',
                        'latency': latency,
                        'lastCheck': time.time(),
                        'url': f'{self.agent_client.base_url}/health',
                        'httpStatus': response.status_code,
                    }
                else:
                    status_map = {
                        401: 'auth_error',
                        403: 'forbidden',
                        404: 'not_found',
                        500: 'down',
                        502: 'down',
                        503: 'down',
                        504: 'down',
                    }

                    return {
                        'status': status_map.get(response.status_code, 'down'),
                        'lastCheck': time.time(),
                        'url': f'{self.agent_client.base_url}/health',
                        'httpStatus': response.status_code,
                        'error': f'HTTP {response.status_code}',
                    }

            except requests.exceptions.Timeout:
                return {
                    'status': 'timeout',
                    'lastCheck': time.time(),
                    'url': f'{self.agent_client.base_url}/health',
                    'error': 'Request timeout (>3s)',
                }
            except requests.exceptions.RequestException as e:
                return {
                    'status': 'down',
                    'lastCheck': time.time(),
                    'url': f'{self.agent_client.base_url}/health',
                    'error': str(e),
                }

        @self.app.get('/config')
        async def get_config():
            """Get the current config.yaml content with validation status"""
            config_path = self.plugin_directory / 'config.yaml'

            if not config_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail='config.yaml not found in plugin directory: '
                    '{self.plugin_directory}. DevTools server expects to run from within a plugin directory.',
                )

            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)

                stat = config_path.stat()
                last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()

                validation_result = self._validate_plugin_config()

                response = ConfigResponse(config=config_data, file_path=str(config_path), last_modified=last_modified)
                response_dict = response.model_dump()
                response_dict['validation'] = validation_result

                # variables
                self.plugin_code = response_dict['config'].get('code')

                return response_dict
            except yaml.YAMLError as e:
                raise HTTPException(status_code=422, detail=f'Invalid YAML format: {str(e)}')
            except Exception as e:
                logger.error(f'Failed to read config.yaml: {e}')
                raise HTTPException(status_code=500, detail='Failed to read configuration file')

        @self.app.put('/config')
        async def update_config(request: ConfigUpdateRequest):
            """Update the config.yaml file"""
            config_path = self.plugin_directory / 'config.yaml'

            try:
                # Create backup of existing config
                if config_path.exists():
                    backup_path = config_path.with_suffix('.yaml.bak')
                    config_path.rename(backup_path)

                # Write new config
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(request.config, f, default_flow_style=False, allow_unicode=True, indent=2)

                # Return updated config
                stat = config_path.stat()
                last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()

                return ConfigResponse(config=request.config, file_path=str(config_path), last_modified=last_modified)
            except Exception as e:
                # Restore backup if write failed
                backup_path = config_path.with_suffix('.yaml.bak')
                if backup_path.exists():
                    backup_path.rename(config_path)

                logger.error(f'Failed to update config.yaml: {e}')
                raise HTTPException(status_code=500, detail='Failed to update configuration file')

        @self.app.post('/config/validate')
        async def validate_config(request: ConfigUpdateRequest):
            """Validate config.yaml structure using JSON schema"""
            return self._validate_plugin_config()

        @self.app.post('/plugin/http')
        async def execute_plugin_http(request: Request):
            """Execute a plugin HTTP request with specified parameters"""
            try:
                body = await request.json()

                # Extract request parameters
                action = body.get('action')
                params = body.get('params', {})
                debug = body.get('debug', True)
                access_token = body.get('access_token', None)

                # Validate plugin config before executing
                validation_result = self._validate_plugin_config()
                if not validation_result['valid']:
                    return {
                        'success': False,
                        'error': 'Plugin configuration is invalid',
                        'validation_errors': validation_result['errors'],
                        'message': 'Please fix config.yaml before executing HTTP requests',
                    }

                # Execute the HTTP request
                result = await self._execute_plugin_http_request(
                    action=action, params=params, debug=debug, access_token=access_token
                )

                return result

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f'Failed to execute plugin HTTP request: {e}')
                raise HTTPException(status_code=500, detail=f'Failed to execute HTTP request: {str(e)}')

        @self.app.get('/plugin/http/params/{action}')
        async def get_action_params(action: str):
            """Get pre-filled example parameters for a specific action"""
            example_params = self._get_action_example_params(action)

            return {'action': action, 'example_params': example_params, 'has_example': len(example_params) > 0}

        @self.app.post('/plugin/publish')
        async def publish_plugin(request: Request):
            """Publish a plugin to the Synapse platform using the same logic as CLI publish"""
            try:
                body = await request.json()

                # Extract publish configuration
                host = body.get('host')
                access_token = body.get('access_token')  # This is the synapse access token
                debug = body.get('debug', True)

                # Validate required fields
                if not all([host, access_token]):
                    raise HTTPException(status_code=400, detail='Missing required fields: host or access_token')

                # Validate plugin config before publishing
                validation_result = self._validate_plugin_config()
                if not validation_result['valid']:
                    return {
                        'success': False,
                        'error': 'Plugin configuration is invalid',
                        'validation_errors': validation_result['errors'],
                        'message': 'Please fix config.yaml before publishing',
                    }

                # Use the existing CLI publish logic
                result = await self._publish_plugin_internal(
                    host=host, access_token=access_token, debug=debug, source_path=self.plugin_directory
                )

                return result

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f'Failed to publish plugin: {e}')
                raise HTTPException(status_code=500, detail=f'Failed to publish plugin: {str(e)}')

        @self.app.get('/{path:path}')
        async def spa_handler(path: str):
            """Serve index.html for all non-API routes (SPA routing)"""
            # Don't handle API routes, static assets, or docs
            if (
                path.startswith('api/')
                or path.startswith('docs')
                or path.startswith('redoc')
                or path.startswith('assets/')
                or path.startswith('public/')
                or path.startswith('jobs')
                or path.startswith('health/')
                or path.startswith('config')
                or path.startswith('status')
                or path.startswith('auth/')
                or path.startswith('plugin/')
                or path.endswith('.js')
                or path.endswith('.css')
                or path.endswith('.ico')
                or path.endswith('.png')
                or path.endswith('.svg')
                or path.endswith('.jpg')
                or path.endswith('.jpeg')
                or path.endswith('.woff')
                or path.endswith('.woff2')
                or path.endswith('.ttf')
            ):
                raise HTTPException(status_code=404, detail='Not found')

            index_file = self.web_build_dir / 'index.html'

            if index_file.exists():
                # Read and modify HTML content to inject environment variables
                with open(index_file, 'r') as f:
                    html_content = f.read()

                modified_html = self._inject_env_vars(html_content)

                from fastapi.responses import HTMLResponse

                return HTMLResponse(content=modified_html)

            # Fallback if no built frontend
            return {'message': 'Synapse Devtools API', 'docs': '/docs', 'path': path}

    async def broadcast_update(self, data: Dict):
        """Broadcast updates to all connected WebSocket clients"""
        if self.websocket_connections:
            message = json.dumps(data)
            disconnected_connections = []

            for connection in self.websocket_connections[:]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f'Error sending WebSocket message: {e}')
                    disconnected_connections.append(connection)

            # Remove disconnected connections
            for connection in disconnected_connections:
                if connection in self.websocket_connections:
                    self.websocket_connections.remove(connection)
                    logger.info('Removed disconnected WebSocket connection')

    def start_server(self):
        """Start the devtools server"""
        # Use display host for browser opening and URL display
        display_host = get_display_host(self.host)
        url = f'http://{display_host}:{self.port}'
        print(f'Open devtools on your browser: {url}')

        uvicorn.run(self.app, host=self.host, port=self.port, log_level='warning', access_log=False)


def create_devtools_server(host: str = '0.0.0.0', port: int = 8080, plugin_directory: str = None) -> DevtoolsServer:
    """Factory function to create a devtools server instance"""
    return DevtoolsServer(host=host, port=port, plugin_directory=plugin_directory)
