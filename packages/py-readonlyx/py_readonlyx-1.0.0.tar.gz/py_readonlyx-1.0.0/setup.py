from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-readonlyx",
    version="1.0.0",
    author="py-readonlyx",
    author_email="info@py-readonlyx.com",
    description="Lightweight Python Read-Only Property Decorator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/py-readonlyx",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/py-readonlyx/issues",
    },
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
        "Programming Language :: Python :: 3.12+",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    keywords="readonly, property, decorator, immutable, python",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
)
