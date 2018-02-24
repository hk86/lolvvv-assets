@echo off
ping 127.0.0.1 -n 8

SET mypath=%~dp0
SET script_path=%mypath:~0,-1%
cd /d %script_path%

cd ..\..
git pull

cd %script_path%
python main.py