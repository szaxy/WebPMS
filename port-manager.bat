@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo =====================================================
echo   WebPMS 智能端口管理器
echo =====================================================

REM 防止窗口闪退
if "%1"=="" (
    echo 正在初始化端口管理器...
    echo.
    cmd /k "%~f0" run
    exit /b
)

if "%1"=="run" (
    echo 端口管理器已启动
    echo.
)

REM 加载当前端口配置
if exist .env.ports (
    echo 读取端口配置文件 .env.ports...
    for /f "tokens=1,* delims==" %%a in (.env.ports) do (
        if not "%%a"=="" (
            set "%%a=%%b"
        )
    )
) else (
    echo 创建默认端口配置文件...
    (
        echo # WebPMS 端口配置文件
        echo # 修改此文件以自定义服务端口
        echo.
        echo # 前端服务端口
        echo FRONTEND_PORT=3000
        echo FRONTEND_ALT_PORT=3001
        echo.
        echo # 后端服务端口
        echo BACKEND_PORT=8000
        echo BACKEND_ALT_PORT=8001
        echo.
        echo # 数据库端口
        echo DB_PORT=15432
        echo.
        echo # Redis端口
        echo REDIS_PORT=6379
        echo.
        echo # 是否允许自动切换端口(0=禁用, 1=启用^)
        echo AUTO_PORT_SWITCH=1
        echo.
        echo # 可用的前端端口池(用空格分隔^)
        echo FRONTEND_PORT_POOL="3000 3001 3002 8080 8081 9527 9528"
        echo.
        echo # 可用的后端端口池(用空格分隔^)
        echo BACKEND_PORT_POOL="8000 8001 8002 8003 9000 9001"
    ) > .env.ports
    
    set FRONTEND_PORT=3000
    set FRONTEND_ALT_PORT=3001
    set BACKEND_PORT=8000
    set BACKEND_ALT_PORT=8001
    set DB_PORT=15432
    set REDIS_PORT=6379
    set AUTO_PORT_SWITCH=1
    set FRONTEND_PORT_POOL="3000 3001 3002 8080 8081 9527 9528"
    set BACKEND_PORT_POOL="8000 8001 8002 8003 9000 9001"
)

echo.
echo 当前端口配置:
echo - 前端端口: %FRONTEND_PORT%
echo - 后端端口: %BACKEND_PORT%
echo - 数据库端口: %DB_PORT%
echo - Redis端口: %REDIS_PORT%
echo.

if "%1"=="check" goto :check_ports
if "%1"=="reset" goto :reset_ports
if "%1"=="save" goto :save_ports

goto :main_menu

:main_menu
echo 请选择操作:
echo [1] 检查端口占用情况
echo [2] 自动分配可用端口
echo [3] 手动设置端口
echo [4] 恢复默认端口设置
echo [5] 退出
choice /c 12345 /n /m "请选择操作 [1-5]: "

if errorlevel 5 goto :end
if errorlevel 4 goto :reset_ports
if errorlevel 3 goto :manual_config
if errorlevel 2 goto :auto_assign
if errorlevel 1 goto :check_ports

:check_ports
echo.
echo 正在检查端口占用情况...
echo.

set FRONTEND_BUSY=0
set BACKEND_BUSY=0
set DB_BUSY=0
set REDIS_BUSY=0

netstat -ano | findstr ":%FRONTEND_PORT% " > nul
if %errorlevel% equ 0 (
    echo [警告] 前端端口 %FRONTEND_PORT% 已被占用
    set FRONTEND_BUSY=1
) else (
    echo [正常] 前端端口 %FRONTEND_PORT% 可用
)

netstat -ano | findstr ":%BACKEND_PORT% " > nul
if %errorlevel% equ 0 (
    echo [警告] 后端端口 %BACKEND_PORT% 已被占用
    set BACKEND_BUSY=1
) else (
    echo [正常] 后端端口 %BACKEND_PORT% 可用
)

netstat -ano | findstr ":%DB_PORT% " > nul
if %errorlevel% equ 0 (
    echo [警告] 数据库端口 %DB_PORT% 已被占用
    set DB_BUSY=1
) else (
    echo [正常] 数据库端口 %DB_PORT% 可用
)

netstat -ano | findstr ":%REDIS_PORT% " > nul
if %errorlevel% equ 0 (
    echo [警告] Redis端口 %REDIS_PORT% 已被占用
    set REDIS_BUSY=1
) else (
    echo [正常] Redis端口 %REDIS_PORT% 可用
)

echo.
if %FRONTEND_BUSY%==1 (
    if "%AUTO_PORT_SWITCH%"=="1" (
        echo 自动端口切换已启用，尝试为前端分配新端口...
        call :find_available_port "FRONTEND_PORT_POOL" "FRONTEND_PORT"
    ) else (
        echo 自动端口切换已禁用，请手动设置端口
    )
)

if %BACKEND_BUSY%==1 (
    if "%AUTO_PORT_SWITCH%"=="1" (
        echo 自动端口切换已启用，尝试为后端分配新端口...
        call :find_available_port "BACKEND_PORT_POOL" "BACKEND_PORT"
    ) else (
        echo 自动端口切换已禁用，请手动设置端口
    )
)

echo.
if "%1"=="check" (
    goto :save_ports
) else (
    pause
    goto :main_menu
)

:find_available_port
set PORT_POOL=!%~1!
set PORT_VAR=%~2

REM 移除引号
set PORT_POOL=!PORT_POOL:"=!

echo 尝试端口池: !PORT_POOL!
for %%p in (!PORT_POOL!) do (
    netstat -ano | findstr ":%%p " > nul
    if !errorlevel! neq 0 (
        echo 找到可用端口: %%p
        set %PORT_VAR%=%%p
        goto :eof
    )
)

REM 如果所有预定义端口都被占用，使用随机端口
set /a RANDOM_PORT=10000 + %random% %% 20000
echo 所有预定义端口都被占用，使用随机端口: !RANDOM_PORT!
set %PORT_VAR%=!RANDOM_PORT!

goto :eof

:auto_assign
echo.
echo 正在自动分配可用端口...

call :find_available_port "FRONTEND_PORT_POOL" "FRONTEND_PORT"
call :find_available_port "BACKEND_PORT_POOL" "BACKEND_PORT"

echo 新的端口配置:
echo - 前端端口: %FRONTEND_PORT%
echo - 后端端口: %BACKEND_PORT%
echo - 数据库端口: %DB_PORT%
echo - Redis端口: %REDIS_PORT%

echo.
choice /c YN /m "是否保存这些设置? [Y/N]: "
if errorlevel 2 goto :main_menu
if errorlevel 1 goto :save_ports

:manual_config
echo.
echo 手动端口配置 (直接回车使用当前值)

set /p NEW_FRONTEND_PORT=前端端口 [%FRONTEND_PORT%]: 
if not "%NEW_FRONTEND_PORT%"=="" set FRONTEND_PORT=%NEW_FRONTEND_PORT%

set /p NEW_BACKEND_PORT=后端端口 [%BACKEND_PORT%]: 
if not "%NEW_BACKEND_PORT%"=="" set BACKEND_PORT=%NEW_BACKEND_PORT%

set /p NEW_DB_PORT=数据库端口 [%DB_PORT%]: 
if not "%NEW_DB_PORT%"=="" set DB_PORT=%NEW_DB_PORT%

set /p NEW_REDIS_PORT=Redis端口 [%REDIS_PORT%]: 
if not "%NEW_REDIS_PORT%"=="" set REDIS_PORT=%NEW_REDIS_PORT%

echo.
echo 新的端口配置:
echo - 前端端口: %FRONTEND_PORT%
echo - 后端端口: %BACKEND_PORT%
echo - 数据库端口: %DB_PORT%
echo - Redis端口: %REDIS_PORT%

echo.
choice /c YN /m "是否保存这些设置? [Y/N]: "
if errorlevel 2 goto :main_menu
if errorlevel 1 goto :save_ports

:save_ports
echo.
echo 正在保存端口配置...

(
    echo # WebPMS 端口配置文件
    echo # 修改此文件以自定义服务端口
    echo.
    echo # 前端服务端口
    echo FRONTEND_PORT=%FRONTEND_PORT%
    echo FRONTEND_ALT_PORT=%FRONTEND_ALT_PORT%
    echo.
    echo # 后端服务端口
    echo BACKEND_PORT=%BACKEND_PORT%
    echo BACKEND_ALT_PORT=%BACKEND_ALT_PORT%
    echo.
    echo # 数据库端口
    echo DB_PORT=%DB_PORT%
    echo.
    echo # Redis端口
    echo REDIS_PORT=%REDIS_PORT%
    echo.
    echo # 是否允许自动切换端口(0=禁用, 1=启用^)
    echo AUTO_PORT_SWITCH=%AUTO_PORT_SWITCH%
    echo.
    echo # 可用的前端端口池(用空格分隔^)
    echo FRONTEND_PORT_POOL=%FRONTEND_PORT_POOL%
    echo.
    echo # 可用的后端端口池(用空格分隔^)
    echo BACKEND_PORT_POOL=%BACKEND_PORT_POOL%
) > .env.ports

echo 端口配置已保存到 .env.ports 文件

if "%1"=="check" (
    exit /b 0
) else (
    echo.
    pause
    goto :main_menu
)

:reset_ports
echo.
echo 正在恢复默认端口设置...

set FRONTEND_PORT=3000
set FRONTEND_ALT_PORT=3001
set BACKEND_PORT=8000
set BACKEND_ALT_PORT=8001
set DB_PORT=15432
set REDIS_PORT=6379

goto :save_ports

:end
echo.
echo 结束端口管理
if "%1"=="run" (
    pause
)
exit /b 0 