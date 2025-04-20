@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

title WebPMS Service Stop Script

echo ========================================================
echo                WebPMS Service Stop Script
echo ========================================================
echo.

REM Define path variables
set "WEBPMS_ROOT=%~dp0"
set "NGINX_DIR=%WEBPMS_ROOT%nginx-1.26.3"

echo Stopping all WebPMS services...

REM Stop Nginx
echo [1/4] Stopping Nginx service...
tasklist /fi "imagename eq nginx.exe" | find "nginx.exe" > nul
if %errorlevel% equ 0 (
    cd /d "%NGINX_DIR%"
    "%NGINX_DIR%\nginx.exe" -s stop
    echo Nginx service stopped
) else (
    echo Nginx service not running
)

REM Stop frontend service
echo [2/4] Stopping frontend service...
for /f "tokens=2" %%p in ('tasklist /fi "windowtitle eq WebPMS Frontend*" /fo list ^| findstr "PID:"') do (
    echo Terminating frontend process: %%p
    taskkill /f /pid %%p > nul 2>&1
)

REM Stop backend service
echo [3/4] Stopping backend service...
for /f "tokens=2" %%p in ('tasklist /fi "windowtitle eq WebPMS Backend*" /fo list ^| findstr "PID:"') do (
    echo Terminating backend process: %%p
    taskkill /f /pid %%p > nul 2>&1
)

REM Stop Redis service
echo [4/4] Stopping Redis service...
for /f "tokens=2" %%p in ('tasklist /fi "windowtitle eq WebPMS Redis*" /fo list ^| findstr "PID:"') do (
    echo Terminating Redis process: %%p
    taskkill /f /pid %%p > nul 2>&1
)

REM Find and terminate possible node.js processes (frontend service)
for /f "tokens=1" %%p in ('tasklist /fi "imagename eq node.exe" /fo list ^| findstr "PID:"') do (
    set "line=%%p"
    set "pid=!line:~4!"
    echo Terminating Node.js process: !pid!
    taskkill /f /pid !pid! > nul 2>&1
)

REM Find and terminate possible Python processes (backend service)
echo Checking and terminating remaining Python processes...
for /f "tokens=1" %%p in ('tasklist /fi "imagename eq python.exe" /fo list ^| findstr "PID:"') do (
    set "line=%%p"
    set "pid=!line:~4!"
    echo Terminating Python process: !pid!
    taskkill /f /pid !pid! > nul 2>&1
)

REM Find and terminate Redis processes
echo Checking and terminating remaining Redis processes...
for /f "tokens=1" %%p in ('tasklist /fi "imagename eq redis-server.exe" /fo list ^| findstr "PID:"') do (
    set "line=%%p"
    set "pid=!line:~4!"
    echo Terminating Redis process: !pid!
    taskkill /f /pid !pid! > nul 2>&1
)

echo.
echo ========================================================
echo             All WebPMS services stopped
echo ========================================================

pause
exit /b 0 