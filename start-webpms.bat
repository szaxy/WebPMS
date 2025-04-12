@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo =====================================================
echo   WebPMS Platform - 智能启动程序
echo =====================================================

echo [步骤 1] 运行端口管理器检查端口占用情况...
call port-manager.bat check
if errorlevel 1 (
    echo 端口管理器出错，将使用默认端口配置继续...
) else (
    echo 端口配置已更新.
)

REM 加载端口配置
for /f "tokens=1,* delims==" %%a in (.env.ports) do (
    if not "%%a"=="" (
        set "%%a=%%b"
    )
)

echo 当前端口配置:
echo - 前端端口: %FRONTEND_PORT%
echo - 后端端口: %BACKEND_PORT%
echo - 数据库端口: %DB_PORT%
echo - Redis端口: %REDIS_PORT%

echo [步骤 2] 检查必要的离线资源...
if not exist "offline-resources\python-packages\py3\tomli-2.0.0-py3-none-any.whl" (
    echo 错误: Python离线包不存在!
    echo 请确保离线资源目录结构正确。
    pause
    exit /b 1
)

if not exist "offline-resources\npm-packages\node_modules.tar.gz" (
    echo 警告: 前端离线依赖包不存在!
    echo 将尝试在线安装，可能会失败。
    echo 建议先运行pack-frontend-deps.bat创建离线包。
    echo.
    choice /C YN /M "是否继续?"
    if errorlevel 2 (
        exit /b 0
    )
) else (
    echo 前端离线依赖包检查通过。
)

echo [步骤 3] 加载Docker镜像(如需)...
echo 检查PostgreSQL镜像...
docker images | findstr postgres:14.15 > nul
if errorlevel 1 (
    echo 加载PostgreSQL镜像...
    docker load -i docker\images\postgres-14.15.tar
)

echo 检查Redis镜像...
docker images | findstr redis:alpine > nul
if errorlevel 1 (
    echo 加载Redis镜像...
    docker load -i docker\images\redis-alpine.tar
)

echo 检查Python镜像...
docker images | findstr python:3.10-slim > nul
if errorlevel 1 (
    echo 加载Python镜像...
    docker load -i docker\images\python-slim.tar
)

echo 检查Node.js镜像...
docker images | findstr node:18-alpine > nul
if errorlevel 1 (
    echo 加载Node.js镜像...
    docker load -i docker\images\node-alpine.tar
)

echo [步骤 4] 设置环境变量...
set "FRONTEND_PORT_ENV=FRONTEND_PORT=%FRONTEND_PORT%"
set "BACKEND_PORT_ENV=BACKEND_PORT=%BACKEND_PORT%"
set "DB_PORT_ENV=DB_PORT=%DB_PORT%"
set "REDIS_PORT_ENV=REDIS_PORT=%REDIS_PORT%"

echo [步骤 5] 停止运行中的容器...
docker-compose -f docker-compose.postgres.yml down 2>nul
timeout /t 2 /nobreak > nul

echo [步骤 6] 启动后端服务(数据库, redis, 后端)...
set "COMPOSE_COMMAND=docker-compose -f docker-compose.postgres.yml"
%COMPOSE_COMMAND% up -d db redis backend
echo 等待后端服务初始化...
timeout /t 15 /nobreak > nul

echo [步骤 7] 启动前端服务...
%COMPOSE_COMMAND% up -d frontend
echo 等待前端初始化(可能需要1-2分钟)...
echo 正在解压前端依赖包并启动Vite服务器...
timeout /t 90 /nobreak > nul

echo [步骤 8] 检查容器状态...
%COMPOSE_COMMAND% ps

echo =====================================================
echo   WebPMS平台现已启动!
echo   - 前端: http://localhost:%FRONTEND_PORT%
echo   - API: http://localhost:%BACKEND_PORT%/api
echo   - 管理后台: http://localhost:%BACKEND_PORT%/admin
echo   - 数据库: localhost:%DB_PORT% (PostgreSQL)
echo =====================================================
echo 注意: 如果前端显示"localhost未发送任何数据"，Vite服务器
echo       可能仍在启动中。请再等待30-60秒并刷新页面。
echo =====================================================
echo 查看前端启动进度:
echo docker logs -f webpms-frontend-1
echo.
echo 创建管理员用户:
echo docker exec -it webpms-backend-1 sh -c "cd /app && python manage.py createsuperuser"
echo.
echo 停止所有服务:
echo docker-compose -f docker-compose.postgres.yml down
echo.
echo 查看后端日志:
echo docker-compose -f docker-compose.postgres.yml logs -f backend
echo.
echo 查看前端日志:
echo docker-compose -f docker-compose.postgres.yml logs -f frontend
echo.
echo 端口管理:
echo port-manager.bat
echo.
echo 创建固定入口:
echo 如果您希望创建一个固定访问入口(不会随端口变化)，请输入 'y'
choice /C YN /M "是否创建固定入口? [Y/N]: "
if errorlevel 2 goto :skip_shortcut
if errorlevel 1 (
    echo 正在创建固定入口...
    call create-shortcut.bat
)

:skip_shortcut

pause 