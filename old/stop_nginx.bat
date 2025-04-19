@echo off
chcp 65001 > nul
REM WebPMS Nginx Stop Script

echo Stopping Nginx service...

REM Check if Nginx is installed
IF NOT EXIST "G:\LJT\TD\WebPMS_comp\nginx-1.26.3\nginx.exe" (
    echo Error: Nginx installation not found
    pause
    exit /b 1
)

REM Stop Nginx
cd /d G:\LJT\TD\WebPMS_comp\nginx-1.26.3
nginx -s stop

REM Check if Nginx has stopped
ping 127.0.0.1 -n 3 > nul
tasklist /FI "IMAGENAME eq nginx.exe" | find "nginx.exe" > nul
IF %ERRORLEVEL% == 0 (
    echo Warning: Nginx processes still running, attempting to force terminate...
    taskkill /F /IM nginx.exe
) ELSE (
    echo Nginx successfully stopped
)

pause 