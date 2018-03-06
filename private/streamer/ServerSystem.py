import subprocess

import os

class ServerSystem:
    pass

    def setMute(self, mute):
        if mute:
            muteFlag = '1'
        else:
            muteFlag = '0'
        subprocess.call(['nircmd.exe', 'mutesysvolume', muteFlag])

    def terminate(self, procName):
        subprocess.call(['kill.bat', procName])

    def reboot(self):
        os.system('shutdown -t 1 -r -f') # shutdown -t 1 -r -f
