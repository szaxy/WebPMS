@echo off
chcp 65001 > nul
REM WebPMS Nginx Configuration Reload Script

echo Updating Nginx configuration...

REM Check if Nginx is installed
IF NOT EXIST "C:\nginx\nginx.exe" (
    echo Error: Nginx installation not found
    pause
    exit /b 1
)

REM Copy project nginx.conf to Nginx installation directory
echo Copying project configuration file...
copy /Y "%~dp0nginx.conf" "C:\nginx\conf\nginx.conf"

REM Check configuration syntax
echo Checking configuration syntax...
cd /d C:\nginx
nginx -t
IF %ERRORLEVEL% NEQ 0 (
    echo Configuration file has syntax errors, please fix before continuing
    pause
    exit /b 1
)

REM Reload configuration
echo Reloading Nginx configuration...
nginx -s reload

echo Configuration updated!

pause 