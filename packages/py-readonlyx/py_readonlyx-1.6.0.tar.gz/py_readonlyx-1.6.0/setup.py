"""
Setup file for py-readonlyx package.
Modern Python packaging uses pyproject.toml, but this setup.py is provided
for compatibility with older tools.
"""

from setuptools import setup, find_packages

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-readonlyx",
    version="1.6.0",
    author="firatmio",
    author_email="firattunaarslan@gmail.com",
    description="Lightweight Python Read-Only Property Decorator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/firatmio/py-readonlyx",
    project_urls={
        "Bug Tracker": "https://github.com/firatmio/py-readonlyx/issues",
        "Repository": "https://github.com/firatmio/py-readonlyx",
        "Documentation": "https://github.com/firatmio/py-readonlyx#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    keywords=["readonly", "property", "decorator", "immutable", "python"],
    license="Apache-2.0",
    install_requires=[],  # No dependencies
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
)