"""
Main Entry Point - Secure Audio Steganography System
====================================================
Project FYP - Degree Level

This is the main entry point of the system. Run this file to launch the program.
Simply press "F5" or "Run" to start the application.

Author: Student FYP (Jazzy)
Date: 2024
"""

import sys
import os
import importlib

# ======================================================================
# GLOBAL CONFIGURATION - Must be set BEFORE any other imports
# ======================================================================
# Force CPU and Torch backend to prevent CUDA OOM on limited hardware
os.environ["KERAS_BACKEND"] = "torch"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Specify the python directory path (to allow importing other modules)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)  # Change to app directory for relative paths


from gui import main as gui_main # type: ignore


def print_banner():
    """
    Print an introductory banner in the terminal upon execution.
    This gives the system a professional appearance during demonstrations.
    """
    banner = """
    +--------------------------------------------------------------+
    |                                                              |
    |       SECURE AUDIO STEGANOGRAPHY SYSTEM                      |
    |                                                              |
    |       Echo Hiding + AES-256-CBC Encryption                   |
    |       Final Year Project                                     |
    |                                                              |
    +--------------------------------------------------------------+
    
    Features:
    - AES-256-CBC Encryption
    - Echo Hiding Steganography
    - CNN-based Analysis
    - User-friendly GUI
    
    Starting application...
    """
    print(banner)


def check_dependencies():
    """
    Perform a system health check before starting.
    Verifies that all required libraries are installed.
    Displays a warning and prompts for installation if any are missing,
    preventing application crashes during runtime.
    """
    required_modules = [
        'numpy',
        'scipy',
        'librosa',
        'soundfile',
        'Crypto',
        # 'tensorflow', # Skipped for Python 3.14 compatibility
        'sklearn',
        'matplotlib',
        'tkinter'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'tkinter':
                import tkinter
            else:
                importlib.import_module(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("ERROR: Missing required dependencies!")
        print("\nMissing modules:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install dependencies using:")
        print("  pip install -r requirements.txt")
        return False
    
    return True


def main():
    """
    The main execution function.
    All operations begin here.
    1. Print banner
    2. Check dependencies
    3. Launch GUI
    """
    print_banner()
    
    # Check if all requirements are met
    if not check_dependencies():
        sys.exit(1)
    
    # Start the application
    try:
        gui_main()
    except KeyboardInterrupt:
        print("\n\nGoodbye! (App closed by user)")
    except Exception as e:
        print(f"\n\nCRITICAL ERROR: {str(e)}")
        print("\nPlease check the following:")
        print("  1. Are all dependencies installed? (pip install -r requirements.txt)")
        print("  2. Is the audio file format FLAC?")
        print("  3. Do you have necessary write permissions?")
        sys.exit(1)


if __name__ == "__main__":
    main()
