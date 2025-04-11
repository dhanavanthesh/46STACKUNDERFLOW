"""
Path helper utilities for NewsSense.
Ensures correct paths for data files and directories.
"""

import os
import sys
import logging

logger = logging.getLogger(__name__)

def fix_path_issues():
    """Fix common path issues by ensuring all required directories exist"""
    # Define required directories
    directories = [
        "data",
        "data/scraped_news",
        "data/market_data",
        "data/analysis",
        "data/queries"
    ]
    
    # Create directories if they don't exist
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Add src directory to Python path if not already there
    src_path = os.path.abspath("src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
        logger.info(f"Added {src_path} to Python path")
    
    return True

def ensure_data_directory(data_type=None):
    """Ensure data directory exists and return its path"""
    if data_type:
        directory = os.path.join("data", data_type)
    else:
        directory = "data"
    
    os.makedirs(directory, exist_ok=True)
    return directory

def get_absolute_path(relative_path):
    """Convert relative path to absolute path"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, relative_path)