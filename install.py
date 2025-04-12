#!/usr/bin/env python3
"""
NewsSense - Installation Script
This script installs all dependencies and sets up the project structure.
"""

import subprocess
import sys
import os
from pathlib import Path
import platform
import time

def print_colored(text, color=None, style=None):
    """Print colored text if colorama is available"""
    try:
        from colorama import init, Fore, Style
        init()
        
        color_map = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE
        }
        
        style_map = {
            'normal': Style.NORMAL,
            'bright': Style.BRIGHT,
            'dim': Style.DIM
        }
        
        color_code = color_map.get(color, '')
        style_code = style_map.get(style, '')
        
        print(f"{color_code}{style_code}{text}{Style.RESET_ALL}")
    except ImportError:
        print(text)

def check_python_version():
    """Check if Python version is sufficient"""
    print_colored("Checking Python version...", "blue")
    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
        print_colored("Error: Python 3.8 or higher is required.", "red", "bright")
        print_colored(f"Current version: {sys.version}", "red")
        return False
    print_colored(f"✓ Python version {version_info.major}.{version_info.minor}.{version_info.micro} detected.", "green")
    return True

def create_directory_structure():
    """Create necessary directories for the project"""
    print_colored("Creating directory structure...", "blue")
    
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
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_colored(f"  Created directory: {directory}", "cyan")
    
    # Create __init__.py files
    init_files = [
        "src/__init__.py",
        "src/analyzer/__init__.py",
        "src/news_scraper/__init__.py",
        "src/query_processor/__init__.py",
        "src/utils/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = Path(init_file)
        if not init_path.exists():
            init_path.write_text('"""NewsSense module."""\n')
            print_colored(f"  Created file: {init_file}", "cyan")
    
    print_colored("✓ Directory structure created successfully", "green")
    return True

def install_dependencies():
    """Install required dependencies"""
    print_colored("Starting installation of dependencies...", "blue")
    
    # Try to install colorama first for prettier output
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "colorama"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE,
                      check=True)
        from colorama import init, Fore, Style
        init()
    except:
        pass
    
    # Ensure pip is up to date
    print_colored("Upgrading pip...", "cyan")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      check=True)
    except subprocess.CalledProcessError:
        print_colored("Warning: Failed to upgrade pip, but continuing installation.", "yellow")
    
    # Read requirements from file
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        with open(requirements_file, "r") as f:
            requirements = f.read().splitlines()
    else:
        # Default requirements if file doesn't exist
        requirements = [
            "requests>=2.31.0",
            "yfinance>=0.2.36",
            "pandas>=2.0.0",
            "beautifulsoup4>=4.11.2",
            "textblob>=0.17.1",
            "tabulate>=0.9.0",
            "colorama>=0.4.6",
            "tqdm>=4.66.0",
            "python-dateutil>=2.8.2",
            "numpy>=1.24.0"
        ]
        
        # Write requirements to file
        with open(requirements_file, "w") as f:
            f.write("\n".join(requirements))
    
    # Filter out any empty lines or comments
    requirements = [req for req in requirements if req and not req.startswith("#")]
    
    # Install packages with progress indication
    successful = []
    failed = []
    
    print_colored("Installing packages:", "blue")
    for i, package in enumerate(requirements):
        package_name = package.split(">=")[0].split("==")[0].strip()
        print_colored(f"  [{i+1}/{len(requirements)}] Installing {package_name}...", "cyan")
        
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 check=False)
            
            if result.returncode == 0:
                successful.append(package_name)
                print_colored(f"    ✓ {package_name} installed successfully", "green")
            else:
                failed.append(package_name)
                print_colored(f"    ✗ Error installing {package_name}", "red")
                print_colored(f"    {result.stderr.decode('utf-8', errors='replace')}", "red")
        except Exception as e:
            failed.append(package_name)
            print_colored(f"    ✗ Error installing {package_name}: {str(e)}", "red")
    
    # Install NLTK data for TextBlob
    try:
        print_colored("Installing NLTK data for TextBlob...", "cyan")
        import nltk
        nltk.download('punkt', quiet=True)
        print_colored("    ✓ NLTK data installed successfully", "green")
    except:
        print_colored("    ✗ Failed to install NLTK data, but continuing installation", "yellow")
    
    # Installation summary
    print_colored("\nInstallation Summary:", "blue", "bright")
    print_colored(f"  Successfully installed: {len(successful)}/{len(requirements)} packages", "green" if len(failed) == 0 else "yellow")
    
    if failed:
        print_colored("  Failed installations:", "red")
        for package in failed:
            print_colored(f"    - {package}", "red")
        
        print_colored("\nSuggestions for failed installations:", "yellow")
        print_colored("  - Try installing the failed packages manually:", "yellow")
        for package in failed:
            print_colored(f"    pip install {package}", "cyan")
        print_colored("  - Check your internet connection", "yellow")
        print_colored("  - Make sure you have the necessary permissions", "yellow")
        
        return False
    
    return True

def check_optional_dependencies():
    """Check for optional dependencies and provide information"""
    print_colored("\nChecking optional dependencies:", "blue")
    
    # Check for Gemini API key
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if gemini_api_key:
        print_colored("  ✓ Gemini API key found in environment variables", "green")
    else:
        print_colored("  ℹ Gemini API key not found. For enhanced natural language processing:", "yellow")
        print_colored("    1. Get an API key from https://ai.google.dev/", "yellow")
        print_colored("    2. Set it as an environment variable:", "yellow")
        print_colored("       export GEMINI_API_KEY=your_api_key (Linux/macOS)", "cyan")
        print_colored("       set GEMINI_API_KEY=your_api_key (Windows CMD)", "cyan")
        print_colored("       $env:GEMINI_API_KEY=\"your_api_key\" (Windows PowerShell)", "cyan")
    
    return True

def test_installation():
    """Run a simple test to verify installation"""
    print_colored("\nTesting installation...", "blue")
    
    # Test importing key modules
    modules_to_test = [
        ("requests", "HTTP requests"),
        ("pandas", "Data analysis"),
        ("bs4", "Web scraping"),
        ("textblob", "Natural language processing"),
        ("yfinance", "Financial data"),
        ("tabulate", "Data display"),
        ("colorama", "Terminal colors")
    ]
    
    all_passed = True
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print_colored(f"  ✓ {module_name} ({description}) - Successfully imported", "green")
        except ImportError as e:
            all_passed = False
            print_colored(f"  ✗ {module_name} ({description}) - Import failed: {str(e)}", "red")
    
    if all_passed:
        print_colored("\n✓ All modules imported successfully!", "green", "bright")
    else:
        print_colored("\n✗ Some modules failed to import. You may need to install them manually.", "red", "bright")
    
    return all_passed

def finished_message():
    """Display completion message"""
    print_colored("\n" + "="*70, "blue", "bright")
    print_colored("NewsSense Installation Complete!", "green", "bright")
    print_colored("="*70, "blue", "bright")
    
    print_colored("\nTo start the application, run:", "cyan")
    print_colored("  python main.py", "white", "bright")
    
    print_colored("\nQuick start guide:", "cyan")
    print_colored("1. Ask questions like:", "cyan")
    print_colored("   - Why is Apple up today?", "white")
    print_colored("   - What happened to Nifty this week?", "white")
    print_colored("   - How is QQQ performing compared to the market?", "white")
    
    print_colored("\n2. Analyze specific securities using ticker symbols:", "cyan")
    print_colored("   - AAPL (Apple)", "white")
    print_colored("   - NIFTY50 or ^NSEI (Nifty 50 Index)", "white")
    print_colored("   - RELIANCE.NS (Reliance Industries - Indian stock)", "white")
    
    print_colored("\nFor more information, see the README.md file.", "cyan")
    print_colored("="*70, "blue", "bright")

def main():
    """Main installation function"""
    try:
        print_colored("\n" + "="*70, "blue", "bright")
        print_colored("NewsSense Installation", "magenta", "bright")
        print_colored("="*70, "blue", "bright")
        
        # Display system information
        print_colored(f"System: {platform.system()} {platform.release()}", "cyan")
        print_colored(f"Python: {sys.version.split()[0]}", "cyan")
        print_colored(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}", "cyan")
        print_colored("="*70, "blue", "bright")
        
        # Run installation steps
        steps = [
            ("Checking Python version", check_python_version),
            ("Creating directory structure", create_directory_structure),
            ("Installing dependencies", install_dependencies),
            ("Checking optional dependencies", check_optional_dependencies),
            ("Testing installation", test_installation)
        ]
        
        all_successful = True
        
        for step_name, step_func in steps:
            print_colored(f"\n[STEP] {step_name}", "magenta", "bright")
            try:
                success = step_func()
                if not success:
                    all_successful = False
                    print_colored(f"✗ {step_name} failed.", "red", "bright")
            except Exception as e:
                all_successful = False
                print_colored(f"✗ {step_name} failed with error: {str(e)}", "red", "bright")
        
        if all_successful:
            finished_message()
            return 0
        else:
            print_colored("\nInstallation completed with some issues. Please review the errors above.", "yellow", "bright")
            return 1
    except KeyboardInterrupt:
        print_colored("\n\nInstallation interrupted by user.", "yellow", "bright")
        return 130
    except Exception as e:
        print_colored(f"\nUnexpected error during installation: {str(e)}", "red", "bright")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)