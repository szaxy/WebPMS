@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

title WebPMS一键启动脚本

echo ========================================================
echo                WebPMS 一键启动脚本
echo ========================================================
echo.

REM 定义路径变量
set "WEBPMS_ROOT=%~dp0"
set "BACKEND_DIR=%WEBPMS_ROOT%backend"
set "FRONTEND_DIR=%WEBPMS_ROOT%frontend"
set "NGINX_DIR=%WEBPMS_ROOT%nginx-1.26.3"
set "VENV_ACTIVATE=%BACKEND_DIR%\venv\Scripts\activate.bat"

REM 检查必要文件是否存在
if not exist "%VENV_ACTIVATE%" (
    echo [错误] 找不到Python虚拟环境: %VENV_ACTIVATE%
    echo 请确保已正确设置虚拟环境
    pause
    exit /b 1
)

if not exist "%NGINX_DIR%\nginx.exe" (
    echo [错误] 找不到Nginx: %NGINX_DIR%\nginx.exe
    echo 请确保Nginx已正确安装
    pause
    exit /b 1
)

REM 加载端口配置
if exist "%WEBPMS_ROOT%\.env.ports" (
    echo 正在读取端口配置...
    for /f "tokens=1,* delims==" %%a in (%WEBPMS_ROOT%\.env.ports) do (
        if not "%%a"=="" (
            if not "%%a:~0,1%"=="#" (
                set "%%a=%%b"
            )
        )
    )
) else (
    echo [警告] 未找到端口配置文件，使用默认端口
    set "FRONTEND_PORT=9527"
    set "BACKEND_PORT=9803"
    set "REDIS_PORT=6379"
)

echo.
echo 当前服务端口配置:
echo - 前端服务: %FRONTEND_PORT%
echo - 后端服务: %BACKEND_PORT%
echo - Redis服务: %REDIS_PORT%
echo.

REM 检查端口占用
echo 正在检查端口占用情况...

set FRONTEND_BUSY=0
set BACKEND_BUSY=0
set REDIS_BUSY=0

REM 检查前端端口
netstat -ano | findstr ":%FRONTEND_PORT% " > nul
if %errorlevel% equ 0 (
    set FRONTEND_BUSY=1
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%FRONTEND_PORT% "') do (
        set FRONTEND_PID=%%p
        echo [警告] 前端端口 %FRONTEND_PORT% 被PID为 !FRONTEND_PID! 的进程占用
    )
) else (
    echo [正常] 前端端口 %FRONTEND_PORT% 可用
)

REM 检查后端端口
netstat -ano | findstr ":%BACKEND_PORT% " > nul
if %errorlevel% equ 0 (
    set BACKEND_BUSY=1
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%BACKEND_PORT% "') do (
        set BACKEND_PID=%%p
        echo [警告] 后端端口 %BACKEND_PORT% 被PID为 !BACKEND_PID! 的进程占用
    )
) else (
    echo [正常] 后端端口 %BACKEND_PORT% 可用
)

REM 检查Redis端口
netstat -ano | findstr ":%REDIS_PORT% " > nul
if %errorlevel% equ 0 (
    set REDIS_BUSY=1
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%REDIS_PORT% "') do (
        set REDIS_PID=%%p
        echo [警告] Redis端口 %REDIS_PORT% 被PID为 !REDIS_PID! 的进程占用
    )
) else (
    echo [正常] Redis端口 %REDIS_PORT% 可用
)

echo.

REM 处理端口占用
if %FRONTEND_BUSY%==1 (
    choice /c yn /m "是否终止占用前端端口的进程(PID:!FRONTEND_PID!)?"
    if errorlevel 2 (
        echo 请手动修改前端端口配置后重试
        goto port_error
    ) else (
        echo 正在终止进程PID:!FRONTEND_PID!...
        taskkill /f /pid !FRONTEND_PID!
        if !errorlevel! neq 0 (
            echo [错误] 无法终止进程!
            goto port_error
        ) else (
            echo 进程已终止
        )
    )
)

if %BACKEND_BUSY%==1 (
    choice /c yn /m "是否终止占用后端端口的进程(PID:!BACKEND_PID!)?"
    if errorlevel 2 (
        echo 请手动修改后端端口配置后重试
        goto port_error
    ) else (
        echo 正在终止进程PID:!BACKEND_PID!...
        taskkill /f /pid !BACKEND_PID!
        if !errorlevel! neq 0 (
            echo [错误] 无法终止进程!
            goto port_error
        ) else (
            echo 进程已终止
        )
    )
)

if %REDIS_BUSY%==1 (
    choice /c yn /m "是否终止占用Redis端口的进程(PID:!REDIS_PID!)?"
    if errorlevel 2 (
        echo 请手动修改Redis端口配置后重试
        goto port_error
    ) else (
        echo 正在终止进程PID:!REDIS_PID!...
        taskkill /f /pid !REDIS_PID!
        if !errorlevel! neq 0 (
            echo [错误] 无法终止进程!
            goto port_error
        ) else (
            echo 进程已终止
        )
    )
)

echo.
echo 所有端口检查完毕，继续启动服务...
echo.

REM 更新Nginx配置文件中的端口
echo 正在更新Nginx配置...
set "NGINX_CONF=%WEBPMS_ROOT%nginx.conf"
set "NGINX_CONF_TEMP=%WEBPMS_ROOT%nginx.conf.temp"

if exist "%NGINX_CONF%" (
    type nul > "%NGINX_CONF_TEMP%"
    for /f "usebackq delims=" %%a in ("%NGINX_CONF%") do (
        set "line=%%a"
        
        REM 替换前端端口
        set "line=!line:proxy_pass http://localhost:9527=proxy_pass http://localhost:%FRONTEND_PORT%!"
        
        REM 替换后端端口
        set "line=!line:proxy_pass http://localhost:9803=proxy_pass http://localhost:%BACKEND_PORT%!"
        set "line=!line:proxy_pass http://localhost:9803/ws/=proxy_pass http://localhost:%BACKEND_PORT%/ws/!"
        
        echo !line!>> "%NGINX_CONF_TEMP%"
    )
    
    REM 替换原配置文件
    move /y "%NGINX_CONF_TEMP%" "%NGINX_CONF%" > nul
    echo Nginx配置已更新为使用前端端口%FRONTEND_PORT%和后端端口%BACKEND_PORT%
)

REM 停止可能运行的Nginx
echo 正在检查并停止运行中的Nginx...
tasklist /fi "imagename eq nginx.exe" | find "nginx.exe" > nul
if %errorlevel% equ 0 (
    cd /d "%NGINX_DIR%"
    "%NGINX_DIR%\nginx.exe" -s stop
    timeout /t 2 > nul
)

echo.
echo ========================================================
echo                  正在启动所有服务...
echo ========================================================
echo.

REM 启动Redis服务
echo [1/4] 正在启动Redis服务...
start "WebPMS Redis" redis-server --port %REDIS_PORT%
timeout /t 2 > nul

REM 启动Django后端
echo [2/4] 正在启动Django后端服务(端口:%BACKEND_PORT%)...
start "WebPMS 后端" cmd /c "cd /d "%BACKEND_DIR%" && call "%VENV_ACTIVATE%" && python manage.py runserver %BACKEND_PORT%"
timeout /t 5 > nul

REM 启动前端
echo [3/4] 正在启动Vue前端服务(端口:%FRONTEND_PORT%)...
start "WebPMS 前端" cmd /c "cd /d "%FRONTEND_DIR%" && npm run dev -- --port %FRONTEND_PORT% --host 0.0.0.0"
timeout /t 5 > nul

REM 启动Nginx
echo [4/4] 正在启动Nginx反向代理...
echo 复制Nginx配置...
copy /y "%NGINX_CONF%" "%NGINX_DIR%\conf\nginx.conf" > nul
cd /d "%NGINX_DIR%"
start "" "%NGINX_DIR%\nginx.exe"

REM 检查Nginx是否成功启动
timeout /t 2 > nul
tasklist /fi "imagename eq nginx.exe" | find "nginx.exe" > nul
if %errorlevel% equ 0 (
    echo Nginx已成功启动
) else (
    echo [错误] Nginx启动失败，请检查配置或日志
    goto nginx_error
)

echo.
echo ========================================================
echo                WebPMS 服务已全部启动
echo ========================================================
echo.
echo 您可以通过以下地址访问WebPMS:
echo   * 本地访问: http://localhost:8754
echo   * 局域网访问: http://172.16.10.12:8754
echo.
echo 服务端口信息:
echo   * 前端服务: %FRONTEND_PORT%
echo   * 后端服务: %BACKEND_PORT%
echo   * Redis服务: %REDIS_PORT%
echo   * Nginx代理: 8754
echo.
echo 提示: 按任意键退出此窗口不会关闭已启动的服务
echo 如需停止服务，请运行 stop-webpms.bat 或关闭各服务窗口
echo ========================================================
echo.
goto end

:port_error
echo.
echo [错误] 端口占用问题未解决，无法启动服务
echo 请检查端口配置或手动结束占用进程后重试
echo.
pause
exit /b 1

:nginx_error
echo.
echo [错误] Nginx启动失败
echo 请检查Nginx配置文件或错误日志: %NGINX_DIR%\logs\error.log
echo.
pause
exit /b 1

:end
pause
exit /b 0 