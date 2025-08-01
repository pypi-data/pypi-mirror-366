#!/usr/bin/env python3
"""
Setup script for psst: Prompt Symbol Standard Technology
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README_PSST.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="psst-toolkit",
    version="3.0.0",
    author="Marc Goldstein",
    author_email="marcgoldstein@example.edu",
    description="Prompt Symbol Standard Technology - 88.6% token reduction with perfect semantic fidelity",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/goldsteinmarcmd/psst",
    py_modules=[
        "psst_compiler",
        "psst_ultimate", 
        "dynamic_psst_compiler",
        "enhanced_psst_compiler",
        "psst_hybrid_integration"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Compilers",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "jellyfish>=0.9.0",
        "numpy>=1.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "openai": [
            "openai>=1.0.0",
        ],
    },
    scripts=[
        "psst-learn",
        "psst-hybrid",
    ],
    package_data={
        "": [
            "*.json",
            "examples/*.txt", 
            "examples/*.psst"
        ]
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "psst=psst_ultimate:main",
            "psst-ultimate=psst_ultimate:main",
            "psst-dynamic=dynamic_psst_compiler:main",
            "psst-enhanced=enhanced_psst_compiler:main",
            "psst-hybrid=psst_hybrid_integration:main",
        ],
    },
    keywords=[
        "ai", "prompting", "compression", "tokens", "openai", 
        "gpt", "llm", "efficiency", "cost-optimization"
    ],
    project_urls={
        "Bug Reports": "https://github.com/goldsteinmarcmd/psst/issues",
        "Source": "https://github.com/goldsteinmarcmd/psst",
        "Documentation": "https://github.com/goldsteinmarcmd/psst/blob/main/PSST_USER_MANUAL.md",
    },
) 