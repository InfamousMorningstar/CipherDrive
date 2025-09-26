import socket
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

def check_port_available(port: int, host: str = "localhost") -> bool:
    """
    Check if a port is available for binding.
    Returns True if available, False if in use.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Set socket options to avoid "Address already in use" errors
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            result = sock.bind((host, port))
            return True
    except OSError:
        return False
    except Exception as e:
        logger.error(f"Error checking port {port}: {e}")
        return False

def find_available_port(start_port: int, end_port: int, host: str = "localhost") -> Optional[int]:
    """
    Find the first available port in the given range.
    Returns port number if found, None if no ports available.
    """
    for port in range(start_port, end_port + 1):
        if check_port_available(port, host):
            logger.info(f"Found available port: {port}")
            return port
    
    logger.error(f"No available ports found in range {start_port}-{end_port}")
    return None

def get_required_ports() -> dict:
    """
    Get the required ports for CipherDrive services.
    Automatically selects available ports to avoid conflicts.
    """
    port_config = {
        "backend": None,
        "frontend": None,
        "db": None
    }
    
    # Backend port (FastAPI/Uvicorn)
    backend_port = find_available_port(8000, 8100)
    if backend_port is None:
        raise RuntimeError("No available ports for backend service (8000-8100)")
    port_config["backend"] = backend_port
    
    # Frontend port (React/Vite)
    frontend_port = find_available_port(3000, 3100)
    if frontend_port is None:
        raise RuntimeError("No available ports for frontend service (3000-3100)")
    port_config["frontend"] = frontend_port
    
    # Database port (PostgreSQL)
    db_port = find_available_port(5432, 5500)
    if db_port is None:
        raise RuntimeError("No available ports for database service (5432-5500)")
    port_config["db"] = db_port
    
    logger.info(f"Port configuration: {port_config}")
    return port_config

def validate_port_configuration(ports: dict) -> bool:
    """
    Validate that all configured ports are still available.
    Returns True if all ports are available, False otherwise.
    """
    for service, port in ports.items():
        if not check_port_available(port):
            logger.error(f"Port {port} for {service} is no longer available")
            return False
    
    return True

def check_network_connectivity() -> dict:
    """
    Check network connectivity and port binding capabilities.
    Returns status dictionary.
    """
    status = {
        "localhost_reachable": False,
        "external_binding_ok": False,
        "port_range_available": False
    }
    
    # Test localhost connectivity
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", 80))  # Test connection
            status["localhost_reachable"] = True
    except Exception as e:
        logger.warning(f"Localhost connectivity test failed: {e}")
    
    # Test external binding (0.0.0.0)
    try:
        test_port = find_available_port(8080, 8090, "0.0.0.0")
        if test_port:
            status["external_binding_ok"] = True
    except Exception as e:
        logger.warning(f"External binding test failed: {e}")
    
    # Test port range availability
    available_ports = 0
    for port in range(8000, 8010):
        if check_port_available(port):
            available_ports += 1
    
    status["port_range_available"] = available_ports >= 3
    
    return status