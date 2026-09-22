@echo off
setlocal
REM Soonpage - Local dev server (Windows)
REM Usage: dev-server.bat [port]
REM   port   default: 8000
REM
REM Static site, nothing to build - this just serves the directory locally
REM so you can preview index.html the way GitHub Pages will serve it.

set "DIR=%~dp0"
set "PORT=8000"
if not "%~1"=="" set "PORT=%~1"

echo Soonpage running at http://127.0.0.1:%PORT%
php -S 127.0.0.1:%PORT% -t "%DIR%"
