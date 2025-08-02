#!/usr/bin/env python3
"""
Fallback setup.py for isoprompt package.
Modern installations should use pyproject.toml, but this provides compatibility.
"""

from setuptools import setup, find_packages
import os


# Read the README file
def read_readme():
    """Read README.md file."""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "AI-powered prompt generation and processing tool"


setup(
    name="isoprompt",
    version="1.0.3",
    author="Aditya Patange (AdiPat)",
    author_email="zero@thehackersplaybook.org",
    description="AI-powered prompt generation and processing tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/thehackersplaybook/isoprompt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "isoprompt=isoprompt.cli:main",
        ],
    },
    keywords="python ai prompt llm-ops research openai gpt nlp cli",
    project_urls={
        "Documentation": "https://github.com/thehackersplaybook/isoprompt/blob/main/docs/getting_started.md",
        "Source": "https://github.com/thehackersplaybook/isoprompt",
        "Tracker": "https://github.com/thehackersplaybook/isoprompt/issues",
    },
    include_package_data=True,
    zip_safe=False,
)
