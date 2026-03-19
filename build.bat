@echo off
title Verba Build Tool
color 0B

echo ===================================================
echo               VERBA BUILD SYSTEM
echo ===================================================
echo.
echo [*] Starting build process for verba.exe...
echo [*] Running PyInstaller...
echo.

pyinstaller verba.spec --clean

echo.
echo ===================================================
echo [+] Build Complete!
echo [+] Standalone binary located at: dist\verba.exe
echo ===================================================
echo.
pause