from setuptools import setup, find_packages
import os
import subprocess
import sys

# Create and setup virtual environment if it doesn't exist
def setup_virtual_environment():
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv")
    
    # Check if venv already exists
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment at {venv_path}...")
        try:
            # Create the virtual environment
            subprocess.check_call([sys.executable, "-m", "venv", venv_path])
            
            # Determine the pip path
            if sys.platform == "win32":
                pip_path = os.path.join(venv_path, "Scripts", "pip")
            else:
                pip_path = os.path.join(venv_path, "bin", "pip")
            
            # Upgrade pip and install the package in development mode
            subprocess.check_call([pip_path, "install", "--upgrade", "pip"])
            subprocess.check_call([pip_path, "install", "-e", "."])
            
            print(f"Virtual environment setup complete. Activate with 'source {os.path.join('.venv', 'bin', 'activate')}' on macOS/Linux")
            print(f"or '{os.path.join('.venv', 'Scripts', 'activate')}' on Windows")
        except subprocess.CalledProcessError as e:
            print(f"Error setting up virtual environment: {e}")
            # Continue with setup even if venv creation fails
    else:
        print(f"Virtual environment already exists at {venv_path}")

# Setup the virtual environment before installing the package
setup_virtual_environment()

setup(
    name="steam-macos-shortcut-creator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Pillow",  # For image processing
        "vdf",     # For parsing and writing Steam VDF files
    ],
    entry_points={
        "console_scripts": [
            "steam-shortcuts=steam_macos_shortcut_creator.fixicons:main",
            "find-steam-apps=steam_macos_shortcut_creator.find_apps:main",
        ],
    },
    author="Steam macOS Shortcut Creator Contributors",
    author_email="example@example.com",
    description="A tool to add macOS applications to Steam with proper icons",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/steam-macos-shortcut-creator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.6",
) 