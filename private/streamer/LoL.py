import subprocess

from DirectInput import *

def LoL_start_spectate (url, gameId, encryptionKey, platformId):
	subprocess.call(['spectate.bat', url, str(gameId), encryptionKey, platformId])
	
def LoL_modify_ui():
	toggleKey(0x18) #toggle u
	toggleKey(0x16) #toggle o
	
def LoL_stop():
	subprocess.call(['kill.bat', 'League of Legends.exe'])