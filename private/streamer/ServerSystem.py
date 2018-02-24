import subprocess

class ServerSystem:
    pass

    def terminate(self, procName):
        subprocess.call(['kill.bat', procName])

    def reboot(self):
        subprocess.call(['shutdown', '-t 1', '-r', '-f']) # shutdown -t 1 -r -f
