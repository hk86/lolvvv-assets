@echo off
:: currently not working!
goto :eof
SET mypath=%~dp0
SET script_path=%mypath:~0,-1%
cd /d %script_path%
../prepend_script.bat
python main.py