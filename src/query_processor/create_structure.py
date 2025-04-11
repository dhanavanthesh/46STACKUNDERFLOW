#!/usr/bin/env python3
"""
Create directory structure for NewsSense project.
This script ensures all required directories and files are in place.
"""

import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directory_structure():
    """Create the directory structure for the project"""
    directories = [
        "data",
        "data/scraped_news",
        "data/market_data",
        "data/analysis",
        "data/queries",
        "src",
        "src/analyzer",
        "src/news_scraper",
        "src/query_processor",
        "src/utils"
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Create __init__.py files
    init_files = [
        "src/__init__.py",
        "src/analyzer/__init__.py",
        "src/news_scraper/__init__.py",
        "src/query_processor/__init__.py",
        "src/utils/__init__.py"
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('"""NewsSense module."""\n')
            logger.info(f"Created file: {init_file}")
    
    logger.info("Directory structure created successfully")

if __name__ == "__main__":
    create_directory_structure()