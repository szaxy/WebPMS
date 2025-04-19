@echo off
chcp 65001 > nul
REM WebPMS Nginx Start Script

echo Starting Nginx service...

REM Check if Nginx is installed
IF NOT EXIST "G:\LJT\TD\WebPMS_comp\nginx-1.26.3\nginx.exe" (
    echo Error: Nginx installation not found. Please install Nginx to G:\LJT\TD\WebPMS_comp\nginx-1.26.3
    echo You can download it from http://nginx.org/en/download.html
    pause
    exit /b 1
)

REM Check if config file exists
IF NOT EXIST "G:\LJT\TD\WebPMS_comp\nginx-1.26.3\conf\nginx.conf" (
    echo Error: nginx.conf configuration file not found
    pause
    exit /b 1
)

REM Copy project nginx.conf to Nginx installation directory
echo Copying project configuration file...
copy /Y "%~dp0nginx.conf" "G:\LJT\TD\WebPMS_comp\nginx-1.26.3\conf\nginx.conf"

REM Start Nginx
echo Starting Nginx...
cd /d G:\LJT\TD\WebPMS_comp\nginx-1.26.3
start nginx

REM Check if Nginx started successfully
ping 127.0.0.1 -n 3 > nul
tasklist /FI "IMAGENAME eq nginx.exe" | find "nginx.exe" > nul
IF %ERRORLEVEL% == 0 (
    echo Nginx started successfully!
    echo You can now access WebPMS at:
    echo   - Local access: http://localhost:8754
    echo   - LAN access: http://172.16.10.12:8754
) ELSE (
    echo Nginx startup failed, please check for errors.
)

pause 