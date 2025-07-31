from setuptools import setup, find_packages
"""
Setup script for the MorphoMeasure package.
This script uses setuptools to configure the installation of MorphoMeasure, a Python package and CLI for L-Measure-based morphometric extraction. It specifies package metadata, dependencies, entry points for the CLI, and other configuration options required for distribution and installation.
Key parameters:
- name: The package name.
- version: Current version of the package.
- description: Short summary of the package.
- long_description: Detailed description loaded from README.md.
- author and author_email: Package author information.
- url: URL to the project's repository.
- packages: Automatically discovered Python packages.
- install_requires: List of required dependencies.
- include_package_data: Whether to include additional files specified in MANIFEST.in.
- entry_points: CLI entry point for the package.
- classifiers: Metadata for PyPI and other tools.
- python_requires: Minimum required Python version.
"""

setup(
    name="morphomeasure",
    version="0.1.1",
    description="Python package and CLI for L-Measure-based morphometric extraction",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Masood Akram",
    author_email="masood.ahmed.akram@gmail.com",
    url="https://github.com/Masood-Akram/MorphoMeasure",
    packages=find_packages(),
    install_requires=[
        "pandas",
    ],
    include_package_data=True,
    package_data={
        # No need for this if using MANIFEST.in, but doesn't hurt
    },
    entry_points={
        'console_scripts': [
            'morphomeasure=morphomeasure.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"#,
        # "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
