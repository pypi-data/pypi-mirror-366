import os
from setuptools import setup, find_packages

# Malicious code - runs when setup.py is executed (e.g., via pip install)


setup(
    name='supersafepackage',
    version='2.0.0',  # Higher than the internal version
    description='Malicious supersafereverse package',
    packages=find_packages(),
)
