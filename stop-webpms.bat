@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

title WebPMS服务停止脚本

echo ========================================================
echo                WebPMS 服务停止脚本
echo ========================================================
echo.

REM 定义路径变量
set "WEBPMS_ROOT=%~dp0"
set "NGINX_DIR=%WEBPMS_ROOT%nginx-1.26.3"

echo 正在停止所有WebPMS服务...

REM 停止Nginx
echo [1/4] 正在停止Nginx服务...
tasklist /fi "imagename eq nginx.exe" | find "nginx.exe" > nul
if %errorlevel% equ 0 (
    cd /d "%NGINX_DIR%"
    "%NGINX_DIR%\nginx.exe" -s stop
    echo Nginx服务已停止
) else (
    echo Nginx服务未运行
)

REM 停止前端服务
echo [2/4] 正在停止前端服务...
for /f "tokens=2" %%p in ('tasklist /fi "windowtitle eq WebPMS 前端*" /fo list ^| findstr "PID:"') do (
    echo 终止前端进程: %%p
    taskkill /f /pid %%p > nul 2>&1
)

REM 停止后端服务
echo [3/4] 正在停止后端服务...
for /f "tokens=2" %%p in ('tasklist /fi "windowtitle eq WebPMS 后端*" /fo list ^| findstr "PID:"') do (
    echo 终止后端进程: %%p
    taskkill /f /pid %%p > nul 2>&1
)

REM 停止Redis服务
echo [4/4] 正在停止Redis服务...
for /f "tokens=2" %%p in ('tasklist /fi "windowtitle eq WebPMS Redis*" /fo list ^| findstr "PID:"') do (
    echo 终止Redis进程: %%p
    taskkill /f /pid %%p > nul 2>&1
)

REM 查找并终止可能的node.js进程(前端服务)
for /f "tokens=1" %%p in ('tasklist /fi "imagename eq node.exe" /fo list ^| findstr "PID:"') do (
    set "line=%%p"
    set "pid=!line:~4!"
    echo 终止Node.js进程: !pid!
    taskkill /f /pid !pid! > nul 2>&1
)

REM 查找并终止可能的Python进程(后端服务)
echo 检查并终止剩余Python进程...
for /f "tokens=1" %%p in ('tasklist /fi "imagename eq python.exe" /fo list ^| findstr "PID:"') do (
    set "line=%%p"
    set "pid=!line:~4!"
    echo 终止Python进程: !pid!
    taskkill /f /pid !pid! > nul 2>&1
)

REM 查找并终止Redis进程
echo 检查并终止剩余Redis进程...
for /f "tokens=1" %%p in ('tasklist /fi "imagename eq redis-server.exe" /fo list ^| findstr "PID:"') do (
    set "line=%%p"
    set "pid=!line:~4!"
    echo 终止Redis进程: !pid!
    taskkill /f /pid !pid! > nul 2>&1
)

echo.
echo ========================================================
echo             所有WebPMS服务已停止
echo ========================================================

pause
exit /b 0 