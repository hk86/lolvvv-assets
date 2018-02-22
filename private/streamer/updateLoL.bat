@echo off
setlocal ENABLEEXTENSIONS
setlocal EnableDelayedExpansion

set VALUE_NAME=LocalRootFolder

IF EXIST "C:\Riot Games\League of Legends\RADS" (
SET RADS="C:\Riot Games\League of Legends\RADS" 
GOTO PLAY
)

set KEY_NAME=HKCU\SOFTWARE\Riot Games\RADS
FOR /F "tokens=2*" %%A IN ('REG.EXE QUERY "%KEY_NAME%" /v "%VALUE_NAME%" 2^>NUL ^| FIND "REG_SZ"') DO SET RADS=%%B
IF NOT "!RADS!"=="" GOTO PLAY

set KEY_NAME=HKCU\Software\Classes\VirtualStore\MACHINE\SOFTWARE\Wow6432Node\Riot Games\RADS
FOR /F "tokens=2*" %%A IN ('REG.EXE QUERY "%KEY_NAME%" /v "%VALUE_NAME%" 2^>NUL ^| FIND "REG_SZ"') DO SET RADS=%%B
IF NOT "!RADS!"=="" GOTO PLAY

set KEY_NAME=HKCU\Software\Classes\VirtualStore\MACHINE\SOFTWARE\Riot Games\RADS
FOR /F "tokens=2*" %%A IN ('REG.EXE QUERY "%KEY_NAME%" /v "%VALUE_NAME%" 2^>NUL ^| FIND "REG_SZ"') DO SET RADS=%%B
IF NOT "!RADS!"=="" GOTO PLAY

set KEY_NAME=HKLM\SOFTWARE\Wow6432Node\Riot Games\RADS
FOR /F "tokens=2*" %%A IN ('REG.EXE QUERY "%KEY_NAME%" /v "%VALUE_NAME%" 2^>NUL ^| FIND "REG_SZ"') DO SET RADS=%%B
IF NOT "!RADS!"=="" GOTO PLAY

echo Could not find League of Legends installation.
@pause
goto :EOF

:PLAY
cd /D %RADS%\..

@start "" "LeagueClient.exe"