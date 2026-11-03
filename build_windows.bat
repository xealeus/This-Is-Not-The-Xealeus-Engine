@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Build - This Is Not The Xealeus Engine

echo ===============================================
echo   THIS IS NOT THE XEALEUS ENGINE - EXE BUILDER
echo ===============================================
echo.

rem Find a usable Python command.
set "PY="
where py >nul 2>nul
if not errorlevel 1 set "PY=py"

if not defined PY (
  where python >nul 2>nul
  if not errorlevel 1 set "PY=python"
)

if not defined PY (
  echo ERROR: Python was not found on PATH.
  echo.
  echo Close this window, reinstall Python from python.org,
  echo and make sure Python / the launcher is added to PATH.
  echo.
  pause
  exit /b 1
)

echo Using Python:
%PY% --version
if errorlevel 1 goto :fail

echo.
echo Checking pip...
%PY% -m pip --version >nul 2>nul
if errorlevel 1 (
  echo pip was not available. Attempting to enable it...
  %PY% -m ensurepip --upgrade
  if errorlevel 1 goto :fail
)

echo.
echo Checking PyInstaller...
%PY% -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
  echo PyInstaller is not installed yet.
  echo Installing PyInstaller now...
  %PY% -m pip install --upgrade pyinstaller
  if errorlevel 1 goto :fail
) else (
  echo PyInstaller is already installed.
)

echo.
echo Building terminal-free Windows executable...
echo.
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name This_Is_Not_The_Xealeus_Engine ^
  --add-data "assets;assets" ^
  --add-data "data;data" ^
  voynich_guided_demo.py

if errorlevel 1 goto :fail

echo.
echo ===============================================
echo BUILD COMPLETE!
echo ===============================================
echo.
echo Your EXE is here:
echo   %CD%\dist\This_Is_Not_The_Xealeus_Engine.exe
echo.
echo Press any key to close this builder.
pause >nul
exit /b 0

:fail
echo.
echo ===============================================
echo BUILD FAILED - the error is printed above.
echo ===============================================
echo.
echo Leave this window open and copy the last error lines if you need help.
echo.
pause
exit /b 1
