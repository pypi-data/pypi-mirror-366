"""
AMPGen: A de novo Generation Pipeline Leveraging Evolutionary Information for Broad-Spectrum Antimicrobial Peptide Design

A comprehensive pipeline for generating and evaluating novel antimicrobial peptide (AMP) sequences using EvoDiff framework.
"""

import os
from setuptools import setup, find_packages

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ampgen",
    version="0.1.12",
    author="nicholexiong",
    author_email="",  # Add your email here
    description="A de novo generation pipeline leveraging evolutionary information for broad-spectrum antimicrobial peptide design",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AMPGen",  # Add your repository URL
    project_urls={
        "Bug Reports": "https://github.com/yourusername/AMPGen/issues",
        "Source": "https://github.com/yourusername/AMPGen",
        "Documentation": "https://github.com/yourusername/AMPGen#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",  # Change to your license
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "ampgen-generate=util.unconditional_generation:main",
            "ampgen-generate-msa=util.unconditional_generation_msa:main",
            "ampgen-generate-conditional=util.conditional_generation_msa:main",
            "ampgen-calculate-properties=util.CalProperties:main",
            "ampgen-classify=model.Discriminator:main",
            "ampgen-score=model.MICscorer:main",
            "ampgen-train-discriminator=model.train_discriminator:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ampgen": [
            "Scorer_model/*.pkl",
            "model/iFeature/*",
        ],
    },
    keywords="bioinformatics, antimicrobial-peptides, protein-design, machine-learning, evodiff",
    zip_safe=False,
)