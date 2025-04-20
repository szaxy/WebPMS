@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

title WebPMS Quick Start Script

echo ========================================================
echo                WebPMS Quick Start Script
echo ========================================================
echo.

REM Define path variables
set "WEBPMS_ROOT=%~dp0"
set "BACKEND_DIR=%WEBPMS_ROOT%backend"
set "FRONTEND_DIR=%WEBPMS_ROOT%frontend"
set "NGINX_DIR=%WEBPMS_ROOT%nginx-1.26.3"
set "VENV_ACTIVATE=%BACKEND_DIR%\venv\Scripts\activate.bat"

REM Check if required files exist
if not exist "%VENV_ACTIVATE%" (
    echo [ERROR] Python virtual environment not found: %VENV_ACTIVATE%
    echo Please make sure the virtual environment is set up correctly
    pause
    exit /b 1
)

if not exist "%NGINX_DIR%\nginx.exe" (
    echo [ERROR] Nginx not found: %NGINX_DIR%\nginx.exe
    echo Please make sure Nginx is installed correctly
    pause
    exit /b 1
)

REM Load port configuration
if exist "%WEBPMS_ROOT%\.env.ports" (
    echo Reading port configuration...
    for /f "tokens=1,* delims==" %%a in (%WEBPMS_ROOT%\.env.ports) do (
        if not "%%a"=="" (
            if not "%%a:~0,1%"=="#" (
                set "%%a=%%b"
            )
        )
    )
) else (
    echo [WARNING] Port configuration file not found, using default ports
    set "FRONTEND_PORT=9527"
    set "BACKEND_PORT=9803"
    set "REDIS_PORT=6379"
)

echo.
echo Current service port configuration:
echo - Frontend: %FRONTEND_PORT%
echo - Backend: %BACKEND_PORT%
echo - Redis: %REDIS_PORT%
echo.

REM Check port availability
echo Checking port availability...

set FRONTEND_BUSY=0
set BACKEND_BUSY=0
set REDIS_BUSY=0

REM Check frontend port
netstat -ano | findstr ":%FRONTEND_PORT% " > nul
if %errorlevel% equ 0 (
    set FRONTEND_BUSY=1
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%FRONTEND_PORT% "') do (
        set FRONTEND_PID=%%p
        echo [WARNING] Frontend port %FRONTEND_PORT% is in use by process PID !FRONTEND_PID!
    )
) else (
    echo [OK] Frontend port %FRONTEND_PORT% is available
)

REM Check backend port
netstat -ano | findstr ":%BACKEND_PORT% " > nul
if %errorlevel% equ 0 (
    set BACKEND_BUSY=1
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%BACKEND_PORT% "') do (
        set BACKEND_PID=%%p
        echo [WARNING] Backend port %BACKEND_PORT% is in use by process PID !BACKEND_PID!
    )
) else (
    echo [OK] Backend port %BACKEND_PORT% is available
)

REM Check Redis port
netstat -ano | findstr ":%REDIS_PORT% " > nul
if %errorlevel% equ 0 (
    set REDIS_BUSY=1
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%REDIS_PORT% "') do (
        set REDIS_PID=%%p
        echo [WARNING] Redis port %REDIS_PORT% is in use by process PID !REDIS_PID!
    )
) else (
    echo [OK] Redis port %REDIS_PORT% is available
)

echo.

REM Handle port conflicts
if %FRONTEND_BUSY%==1 (
    choice /c yn /m "Terminate process using frontend port (PID:!FRONTEND_PID!)?"
    if errorlevel 2 (
        echo Please manually change the frontend port configuration and try again
        goto port_error
    ) else (
        echo Terminating process PID:!FRONTEND_PID!...
        taskkill /f /pid !FRONTEND_PID!
        if !errorlevel! neq 0 (
            echo [ERROR] Could not terminate process!
            goto port_error
        ) else (
            echo Process terminated
        )
    )
)

if %BACKEND_BUSY%==1 (
    choice /c yn /m "Terminate process using backend port (PID:!BACKEND_PID!)?"
    if errorlevel 2 (
        echo Please manually change the backend port configuration and try again
        goto port_error
    ) else (
        echo Terminating process PID:!BACKEND_PID!...
        taskkill /f /pid !BACKEND_PID!
        if !errorlevel! neq 0 (
            echo [ERROR] Could not terminate process!
            goto port_error
        ) else (
            echo Process terminated
        )
    )
)

if %REDIS_BUSY%==1 (
    choice /c yn /m "Terminate process using Redis port (PID:!REDIS_PID!)?"
    if errorlevel 2 (
        echo Please manually change the Redis port configuration and try again
        goto port_error
    ) else (
        echo Terminating process PID:!REDIS_PID!...
        taskkill /f /pid !REDIS_PID!
        if !errorlevel! neq 0 (
            echo [ERROR] Could not terminate process!
            goto port_error
        ) else (
            echo Process terminated
        )
    )
)

echo.
echo All port checks completed, continuing startup...
echo.

REM Update Nginx configuration
echo Updating Nginx configuration...
set "NGINX_CONF=%WEBPMS_ROOT%nginx.conf"
set "NGINX_CONF_TEMP=%WEBPMS_ROOT%nginx.conf.temp"

if exist "%NGINX_CONF%" (
    type nul > "%NGINX_CONF_TEMP%"
    for /f "usebackq delims=" %%a in ("%NGINX_CONF%") do (
        set "line=%%a"
        
        REM Replace frontend port
        set "line=!line:proxy_pass http://localhost:9527=proxy_pass http://localhost:%FRONTEND_PORT%!"
        
        REM Replace backend port
        set "line=!line:proxy_pass http://localhost:9803=proxy_pass http://localhost:%BACKEND_PORT%!"
        set "line=!line:proxy_pass http://localhost:9803/ws/=proxy_pass http://localhost:%BACKEND_PORT%/ws/!"
        
        echo !line!>> "%NGINX_CONF_TEMP%"
    )
    
    REM Replace original config file
    move /y "%NGINX_CONF_TEMP%" "%NGINX_CONF%" > nul
    echo Nginx configuration updated to use frontend port %FRONTEND_PORT% and backend port %BACKEND_PORT%
)

REM Stop any running Nginx
echo Checking and stopping any running Nginx...
tasklist /fi "imagename eq nginx.exe" | find "nginx.exe" > nul
if %errorlevel% equ 0 (
    cd /d "%NGINX_DIR%"
    "%NGINX_DIR%\nginx.exe" -s stop
    timeout /t 2 > nul
)

echo.
echo ========================================================
echo                Starting all services...
echo ========================================================
echo.

REM Start Redis service
echo [1/4] Starting Redis service...
start "WebPMS Redis" redis-server --port %REDIS_PORT%
timeout /t 2 > nul

REM Start Django backend
echo [2/4] Starting Django backend service (port:%BACKEND_PORT%)...
start "WebPMS Backend" cmd /c "cd /d "%BACKEND_DIR%" && call "%VENV_ACTIVATE%" && python manage.py runserver %BACKEND_PORT%"
timeout /t 5 > nul

REM Start frontend
echo [3/4] Starting Vue frontend service (port:%FRONTEND_PORT%)...
start "WebPMS Frontend" cmd /c "cd /d "%FRONTEND_DIR%" && npm run dev -- --port %FRONTEND_PORT% --host 0.0.0.0"
timeout /t 5 > nul

REM Start Nginx
echo [4/4] Starting Nginx reverse proxy...
echo Copying Nginx configuration...
copy /y "%NGINX_CONF%" "%NGINX_DIR%\conf\nginx.conf" > nul
cd /d "%NGINX_DIR%"
start "" "%NGINX_DIR%\nginx.exe"

REM Check if Nginx started successfully
timeout /t 2 > nul
tasklist /fi "imagename eq nginx.exe" | find "nginx.exe" > nul
if %errorlevel% equ 0 (
    echo Nginx started successfully
) else (
    echo [ERROR] Failed to start Nginx, please check configuration or logs
    goto nginx_error
)

echo.
echo ========================================================
echo                WebPMS services started
echo ========================================================
echo.
echo You can access WebPMS at:
echo   * Local: http://localhost:8754
echo   * LAN: http://172.16.10.12:8754
echo.
echo Service port information:
echo   * Frontend: %FRONTEND_PORT%
echo   * Backend: %BACKEND_PORT%
echo   * Redis: %REDIS_PORT%
echo   * Nginx proxy: 8754
echo.
echo Note: Closing this window will not stop the services
echo To stop services, run stop-webpms.bat or close each service window
echo ========================================================
echo.
goto end

:port_error
echo.
echo [ERROR] Port conflict not resolved, cannot start services
echo Please check port configuration or manually end processes and try again
echo.
pause
exit /b 1

:nginx_error
echo.
echo [ERROR] Failed to start Nginx
echo Please check Nginx configuration or error logs: %NGINX_DIR%\logs\error.log
echo.
pause
exit /b 1

:end
pause
exit /b 0 