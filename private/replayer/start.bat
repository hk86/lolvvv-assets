@echo off
SET mypath=%~dp0
SET script_path=%mypath:~0,-1%
cd /d %script_path%
../prepend_script.bat
:: start node js replay server
start app.bat
:: start clipper
main.bat