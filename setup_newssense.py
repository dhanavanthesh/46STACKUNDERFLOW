#!/usr/bin/env python3
"""
NewsSense Setup Script
Sets up the NewsSense environment by:
1. Creating necessary directory structure
2. Installing the required modules
3. Setting up the Gemini API integration
"""

import os
import sys
import shutil
import logging
import subprocess

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directory_structure():
    """Create the necessary directory structure"""
    # List of directories to create
    directories = [
        "data",
        "data/scraped_news",
        "data/market_data",
        "data/analysis",
        "data/queries",
        "data/gemini_cache",
        "src",
        "src/analyzer",
        "src/news_scraper",
        "src/query_processor",
        "src/utils"
    ]
    
    # Create each directory
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    return True

def create_init_files():
    """Create necessary __init__.py files"""
    init_files = [
        "src/__init__.py",
        "src/analyzer/__init__.py",
        "src/news_scraper/__init__.py",
        "src/query_processor/__init__.py",
        "src/utils/__init__.py"
    ]
    
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write('"""NewsSense module."""\n')
        logger.info(f"Created __init__ file: {init_file}")
    
    return True

def install_dependencies():
    """Install required dependencies"""
    try:
        # Update pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install dependencies
        dependencies = [
            "yfinance>=0.2.36",
            "requests>=2.31.0",
            "pandas>=2.0.0",
            "beautifulsoup4>=4.13.3",
            "textblob>=0.17.1",
            "tabulate>=0.9.0",
            "colorama>=0.4.6",
            "numpy>=1.24.0",
            "python-dateutil>=2.8.2"
        ]
        
        for dependency in dependencies:
            logger.info(f"Installing {dependency}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dependency])
        
        logger.info("All dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing dependencies: {str(e)}")
        return False

def check_gemini_api_key():
    """Check if the Gemini API key is available"""
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        api_key = "AIzaSyDBhdcypT-HFiKaxXbuGylRS25n3vtPESo"  # Default key from the prompt
        
        # Set the environment variable
        os.environ["GEMINI_API_KEY"] = api_key
        
        # Also inform the user
        logger.info(f"Using default Gemini API key: {api_key}")
        logger.info("For better performance, you can set your own API key:")
        logger.info("  - Windows: set GEMINI_API_KEY=your_api_key")
        logger.info("  - Linux/Mac: export GEMINI_API_KEY=your_api_key")
    else:
        logger.info(f"Using provided Gemini API key: {api_key[:10]}...")
    
    return True

def test_directories_access():
    """Test that we can write to necessary directories"""
    test_dirs = ["data", "data/scraped_news", "data/queries"]
    
    for directory in test_dirs:
        test_file = os.path.join(directory, "test_access.txt")
        try:
            with open(test_file, 'w') as f:
                f.write("Testing write access")
            
            # Read it back
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Remove the test file
            os.remove(test_file)
            
            logger.info(f"Successfully verified write access to {directory}")
        except Exception as e:
            logger.error(f"Could not write to {directory}: {str(e)}")
            return False
    
    return True

def setup_gemini_helper():
    """Set up the Gemini helper configuration"""
    try:
        # Create a sample ticker mappings file
        mappings_dir = "data/gemini_cache"
        os.makedirs(mappings_dir, exist_ok=True)
        
        mappings_file = os.path.join(mappings_dir, "ticker_mappings.json")
        
        # Default mappings for common securities
        default_mappings = {
            "jyothy labs": "JYOTHYLAB.NS",
            "nifty": "^NSEI",
            "sensex": "^BSESN",
            "swiggy": "SWIGGY.NS",  # Placeholder as Swiggy is not publicly traded
            "sbi amc": "SBIAMC.NS",  # Placeholder
            "apple": "AAPL",
            "microsoft": "MSFT",
            "google": "GOOGL",
            "invesco qqq etf": "QQQ",
            "emerging markets": "EEM"
        }
        
        with open(mappings_file, 'w') as f:
            import json
            json.dump(default_mappings, f, indent=2)
        
        logger.info(f"Created ticker mappings file: {mappings_file}")
        return True
    except Exception as e:
        logger.error(f"Error setting up Gemini helper: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("Setting up NewsSense - 'Why Is My Nifty Down?'")
    print("=" * 60)
    
    # Create directory structure
    print("\nStep 1: Creating directory structure...")
    if create_directory_structure():
        print("✅ Directory structure created successfully.")
    else:
        print("❌ Error creating directory structure.")
        return
    
    # Create __init__ files
    print("\nStep 2: Creating __init__ files...")
    if create_init_files():
        print("✅ __init__ files created successfully.")
    else:
        print("❌ Error creating __init__ files.")
        return
    
    # Install dependencies
    print("\nStep 3: Installing dependencies...")
    if install_dependencies():
        print("✅ Dependencies installed successfully.")
    else:
        print("❌ Error installing dependencies. You may need to install them manually.")
        print("   See requirements.txt for the list of required packages.")
    
    # Check Gemini API key
    print("\nStep 4: Setting up Gemini API...")
    if check_gemini_api_key():
        print("✅ Gemini API key configured.")
    else:
        print("❌ Error configuring Gemini API.")
    
    # Set up Gemini helper
    print("\nStep 5: Setting up Gemini helper...")
    if setup_gemini_helper():
        print("✅ Gemini helper set up successfully.")
    else:
        print("❌ Error setting up Gemini helper.")
    
    # Test directory access
    print("\nStep 6: Testing directory access...")
    if test_directories_access():
        print("✅ Directory access verified.")
    else:
        print("❌ Error verifying directory access. Check permissions.")
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("You can now run NewsSense by executing: python main.py")
    print("=" * 60)

if __name__ == "__main__":
    main()