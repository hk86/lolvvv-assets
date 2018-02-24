import subprocess

import os

class ServerSystem:
    pass

    def terminate(self, procName):
        subprocess.call(['kill.bat', procName])

    def reboot(self):
        os.system('shutdown -t 1 -r -f') # shutdown -t 1 -r -f
