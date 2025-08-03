#!/usr/bin/env python3
"""
Setup script for QuantaThread framework.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "QuantaThread: Quantum-Inspired Computing Framework"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="quanta-thread",
    version="1.0.0",
    author="QuantaThread Team",
    author_email="contact@quantathread.com",
    description="Quantum-Inspired Computing Framework for Classical Hardware",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/quantathread/quanta-thread",
    project_urls={
        "Bug Tracker": "https://github.com/quantathread/quanta-thread/issues",
        "Documentation": "https://quantathread.readthedocs.io/",
        "Source Code": "https://github.com/quantathread/quanta-thread",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "pre-commit>=2.20.0",
        ],
        "quantum": [
            "qiskit>=0.40.0",
            "cirq>=1.0.0",
            "pennylane>=0.20.0",
        ],
        "ml": [
            "tensorflow>=2.8.0",
            "torch>=1.12.0",
            "scikit-learn>=1.1.0",
        ],
        "viz": [
            "plotly>=5.10.0",
            "matplotlib>=3.5.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipywidgets>=7.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "quanta-thread=quanta_thread.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "quanta_thread": [
            "examples/*.py",
            "config/*.yaml",
            "config/*.json",
        ],
    },
    keywords=[
        "quantum computing",
        "quantum algorithms",
        "machine learning",
        "artificial intelligence",
        "optimization",
        "parallel computing",
        "threading",
    ],
    license="MIT",
    platforms=["any"],
    zip_safe=False,
) 