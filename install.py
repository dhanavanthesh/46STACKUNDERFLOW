import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    print("Starting installation process...")
    
    # Ensure pip is up to date
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install packages one by one to avoid conflicts
    packages = [
        "requests>=2.31.0",
        "yfinance>=0.2.36",
        "pandas>=2.0.0",
        "beautifulsoup4>=4.11.2",
        "textblob>=0.17.1",
        "tabulate>=0.9.0",
        "colorama>=0.4.6"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    if install_dependencies():
        print("Installation completed successfully!")
    else:
        print("Installation failed. Please check the errors above.")