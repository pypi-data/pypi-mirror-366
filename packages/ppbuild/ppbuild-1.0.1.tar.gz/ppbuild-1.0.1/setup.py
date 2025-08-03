#!/usr/bin/env python3
"""Setup script for pp tool."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ppbuild",
    version="1.0.1",
    author="Josh Caponigro",
    description="A declarative, language-agnostic build system and utility manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JoshCap20/pp",
    project_urls={
        "Bug Tracker": "https://github.com/JoshCap20/pp/issues",
        "Documentation": "https://github.com/JoshCap20/pp/blob/main/TEMPLATE.md",
        "Source Code": "https://github.com/JoshCap20/pp",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    keywords="build-system, developer-tools, automation, cli, yaml, cross-platform",
    py_modules=["pp"],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pp=pp:main",
        ],
    },
    install_requires=[
        "pyyaml>=5.1",
        "python-dotenv>=0.19.0",
    ],
    python_requires=">=3.9",
    include_package_data=True,
    zip_safe=False,
)
