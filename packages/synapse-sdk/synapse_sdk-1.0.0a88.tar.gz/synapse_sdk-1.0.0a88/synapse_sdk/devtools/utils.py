import socket


def is_port_available(host: str, port: int) -> bool:
    """Check if a port is available on the given host"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0
    except (socket.error, OSError):
        return False


def find_available_port(host: str, start_port: int, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(host, port):
            return port
    raise RuntimeError(f'No available port found in range {start_port}-{start_port + max_attempts - 1}')


def get_local_ip() -> str:
    """Get the local IP address for client access"""
    try:
        # In WSL, return localhost since the server is accessible via localhost
        if _is_wsl():
            return '127.0.0.1'

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except Exception:
        # Fallback to localhost if we can't determine the local IP
        return '127.0.0.1'


def _is_wsl() -> bool:
    """Check if we're running in WSL"""
    try:
        with open('/proc/version', 'r') as f:
            content = f.read().lower()
            return 'microsoft' in content or 'wsl' in content
    except Exception:
        return False


def get_display_host(server_host: str) -> str:
    """Get the appropriate host for display and frontend access"""
    if server_host == '0.0.0.0':
        return get_local_ip()
    return server_host
