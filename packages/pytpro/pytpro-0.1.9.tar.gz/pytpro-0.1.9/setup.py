from setuptools import setup, find_packages
import sys

if sys.version_info < (3, 6):
    print("❌ To use this module, you need Python 3.6 or newer.")
    sys.exit(1)

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pytpro",
    version="0.1.9",
    description="A simple Python tools package by Ibrahim Akhlaq",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ibrahim Akhlaq",
    author_email="ibakhlaq@gmail.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)