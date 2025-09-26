import os
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Required directories for CipherDrive
REQUIRED_DIRECTORIES = [
    "/mnt/app-pool/cipherdrive/config",
    "/mnt/app-pool/cipherdrive/database", 
    "/mnt/app-pool/cipherdrive/logs",
    "/mnt/Centauri/cipherdrive/users",
    "/mnt/Centauri/cipherdrive/shares",
    "/mnt/Centauri/cipherdrive/uploads",
    "/data/movies",  # For cipher user
    "/data/tv"       # For cipher user
]

def check_and_create_directories() -> Tuple[bool, List[str]]:
    """
    Check if required directories exist and create them if missing.
    Returns (success, failed_directories)
    """
    failed_dirs = []
    
    for directory in REQUIRED_DIRECTORIES:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory ensured: {directory}")
        except PermissionError:
            logger.error(f"Permission denied creating directory: {directory}")
            failed_dirs.append(directory)
        except OSError as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            failed_dirs.append(directory)
        except Exception as e:
            logger.error(f"Unexpected error creating directory {directory}: {e}")
            failed_dirs.append(directory)
    
    success = len(failed_dirs) == 0
    return success, failed_dirs

def check_directory_permissions() -> Tuple[bool, List[str]]:
    """
    Check if we have read/write permissions to required directories.
    Returns (success, inaccessible_directories)
    """
    inaccessible_dirs = []
    
    for directory in REQUIRED_DIRECTORIES:
        try:
            # Check if directory exists
            if not os.path.exists(directory):
                inaccessible_dirs.append(f"{directory} (does not exist)")
                continue
            
            # Check read permission
            if not os.access(directory, os.R_OK):
                inaccessible_dirs.append(f"{directory} (no read access)")
                continue
            
            # Check write permission
            if not os.access(directory, os.W_OK):
                inaccessible_dirs.append(f"{directory} (no write access)")
                continue
                
            logger.debug(f"Directory accessible: {directory}")
            
        except Exception as e:
            logger.error(f"Error checking permissions for {directory}: {e}")
            inaccessible_dirs.append(f"{directory} (check failed: {e})")
    
    success = len(inaccessible_dirs) == 0
    return success, inaccessible_dirs

def initialize_user_directory(username: str) -> bool:
    """
    Initialize user's home directory structure.
    Returns True if successful, False otherwise.
    """
    user_home = f"/data/users/{username}"
    
    try:
        # Create user's home directory
        Path(user_home).mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        subdirs = ["documents", "images", "videos", "archives"]
        for subdir in subdirs:
            subdir_path = os.path.join(user_home, subdir)
            Path(subdir_path).mkdir(exist_ok=True)
        
        # Set appropriate permissions (755 for directories)
        os.chmod(user_home, 0o755)
        for subdir in subdirs:
            subdir_path = os.path.join(user_home, subdir)
            os.chmod(subdir_path, 0o755)
        
        logger.info(f"User directory initialized: {user_home}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize user directory {user_home}: {e}")
        return False

def get_available_space(path: str) -> int:
    """
    Get available disk space in bytes for the given path.
    Returns -1 if unable to determine.
    """
    try:
        statvfs = os.statvfs(path)
        # Available space = fragment_size * available_fragments
        available_bytes = statvfs.f_frsize * statvfs.f_bavail
        return available_bytes
    except Exception as e:
        logger.error(f"Failed to get disk space for {path}: {e}")
        return -1

def validate_storage_paths() -> dict:
    """
    Validate all storage paths and return status information.
    """
    status = {
        "directories_created": False,
        "permissions_ok": False,
        "failed_directories": [],
        "inaccessible_directories": [],
        "disk_space": {}
    }
    
    # Check and create directories
    dirs_created, failed_dirs = check_and_create_directories()
    status["directories_created"] = dirs_created
    status["failed_directories"] = failed_dirs
    
    # Check permissions
    perms_ok, inaccessible_dirs = check_directory_permissions()
    status["permissions_ok"] = perms_ok
    status["inaccessible_directories"] = inaccessible_dirs
    
    # Check disk space for key paths
    key_paths = ["/mnt/app-pool/cipherdrive", "/mnt/Centauri/cipherdrive", "/data"]
    for path in key_paths:
        if os.path.exists(path):
            space = get_available_space(path)
            status["disk_space"][path] = space
    
    return status

def startup_directory_check():
    """
    Perform directory checks at startup and log results.
    Raises exception if critical directories are not accessible.
    """
    logger.info("Performing startup directory checks...")
    
    status = validate_storage_paths()
    
    # Log results
    if status["directories_created"]:
        logger.info("All required directories are available")
    else:
        logger.warning(f"Failed to create directories: {status['failed_directories']}")
    
    if status["permissions_ok"]:
        logger.info("All directory permissions are correct")
    else:
        logger.error(f"Directory permission issues: {status['inaccessible_directories']}")
    
    # Log disk space
    for path, space in status["disk_space"].items():
        if space > 0:
            space_gb = space / (1024 ** 3)
            logger.info(f"Available space in {path}: {space_gb:.2f} GB")
        else:
            logger.warning(f"Could not determine disk space for {path}")
    
    # Check if critical paths are accessible
    critical_failures = []
    if not status["directories_created"]:
        critical_failures.extend(status["failed_directories"])
    if not status["permissions_ok"]:
        critical_failures.extend(status["inaccessible_directories"])
    
    if critical_failures:
        error_msg = f"Critical directory failures: {critical_failures}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    logger.info("Directory initialization completed successfully")