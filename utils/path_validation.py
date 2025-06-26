import os
import logging

logger = logging.getLogger(__name__)

def validate_path(path, working_dir):
    """Ensure path is within working directory"""
    full_path = os.path.abspath(os.path.join(working_dir, path))
    safe_dir = os.path.abspath(working_dir)
    
    if not full_path.startswith(safe_dir):
        logger.error(f"Path traversal attempt: {path}")
        raise ValueError(f"Path {path} is outside working directory")
    
    return full_path