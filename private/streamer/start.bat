@echo off

SET mypath=%~dp0
SET script_path=%mypath:~0,-1%
cd /d %script_path%

cd ..\..
git pull

cd %script_path%
python main.py