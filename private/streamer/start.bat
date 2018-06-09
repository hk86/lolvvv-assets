@echo off

:: Wait for Connection to the Internet established
powershell.exe -noprofile -command "while((Test-Connection -ComputerName 'www.google.de' -Quiet) -eq $False) {Start-Sleep -s 10}"
SET mypath=%~dp0
SET script_path=%mypath:~0,-1%
cd /d %script_path%

cd ..\..
git pull

cd %script_path%
python main.py