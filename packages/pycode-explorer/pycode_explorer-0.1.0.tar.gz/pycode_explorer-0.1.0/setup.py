from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pycode-explorer",
    version="0.1.0",
    author="Krishna Sagar P",
    author_email="ktorres9917@gmail.com",
    description="A Python package for analyzing scripts and exploring package functionalities - perfect for busy team leads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sagar7973/pycode-explorer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only built-in Python libraries
    ],
    entry_points={
        "console_scripts": [
            "pyexplorer=pyexplorer.cli:main",
        ],
    },
)