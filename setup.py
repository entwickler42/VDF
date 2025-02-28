from setuptools import setup, find_packages

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