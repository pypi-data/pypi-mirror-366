#!/usr/bin/env python3
"""
Setup script for the hello-greetings package.
"""

import os

from setuptools import find_packages, setup


# Read the README file
def read_readme():
    """Read the README.md file for the long description."""
    here = os.path.abspath(os.path.dirname(__file__))
    readme_path = os.path.join(here, "README.md")
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "A simple command line tool that greets the user."


# Read the version from the package
def get_version():
    """Get version from the package __init__.py file."""
    here = os.path.abspath(os.path.dirname(__file__))
    version_file = os.path.join(here, "src", "hello_greetings", "__init__.py")
    version = {}
    try:
        with open(version_file, "r", encoding="utf-8") as f:
            exec(f.read(), version)
        return version["__version__"]
    except (FileNotFoundError, KeyError):
        return "1.0.0"


setup(
    name="hello-greetings",
    version=get_version(),
    author="Aaron Hsu",
    author_email="aaronhsu@mail.ntou.edu.tw",
    description="A simple command line tool that greets the user",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/AaronOET/hello-greetings",
    project_urls={
        "Homepage": "https://github.com/AaronOET/hello-greetings",
        "Repository": "https://github.com/AaronOET/hello-greetings",
        "Issues": "https://github.com/AaronOET/hello-greetings/issues",
        "Changelog": "https://github.com/AaronOET/hello-greetings/blob/main/CHANGELOG.md",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Add any runtime dependencies here
        # For example: "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "build>=0.10.0",
            "twine>=4.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hello-greetings=hello_greetings.cli:main",
        ],
    },
    keywords=["greeting", "cli", "tool"],
    include_package_data=True,
    zip_safe=False,
)
