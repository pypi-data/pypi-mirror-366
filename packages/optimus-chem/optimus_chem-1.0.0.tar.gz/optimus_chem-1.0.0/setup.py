#!/usr/bin/env python3
"""
Optimus - Comprehensive Chemical Analysis Package
A Python package for accurate molecular property calculations and ADMET rules analysis
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="optimus-chem",
    version="1.0.0",
    author="Pritam Kumar Panda",
    author_email="pritam@stanford.edu",
    description="Comprehensive Chemical Analysis Package for Drug Discovery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pritampanda15/Optimus_Chemical_Analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.7",
    install_requires=[
        "rdkit>=2022.3.5",
        "numpy>=1.19.0",
        "pandas>=1.3.0",
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
        "tqdm>=4.62.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
        "viz": [
            "plotly>=5.0.0",
            "bokeh>=2.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "optimus=optimus.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "optimus": ["data/*.json", "data/*.csv"],
    },
    zip_safe=False,
)