@echo off
chcp 65001 > nul
echo =====================================================
echo   WebPMS Platform - Offline Startup
echo =====================================================

echo [Step 1] 检查必要的离线资源...
if not exist "offline-resources\python-packages\py3\tomli-2.0.0-py3-none-any.whl" (
    echo ERROR: Python离线包不存在!
    echo 请确保离线资源目录结构正确。
    pause
    exit /b 1
)

if not exist "offline-resources\npm-packages\node_modules.tar.gz" (
    echo WARNING: 前端离线依赖包不存在!
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

echo [Step 2] 加载Docker镜像(如需)...
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

echo [Step 3] 停止运行中的容器...
docker-compose -f docker-compose.postgres.yml down 2>nul
timeout /t 2 /nobreak > nul

echo [Step 4] 启动后端服务(数据库, redis, 后端)...
docker-compose -f docker-compose.postgres.yml up -d db redis backend
echo 等待后端服务初始化...
timeout /t 15 /nobreak > nul

echo [Step 5] 启动前端服务...
docker-compose -f docker-compose.postgres.yml up -d frontend
echo 等待前端初始化(可能需要1-2分钟)...
echo 正在解压前端依赖包并启动Vite服务器...
timeout /t 90 /nobreak > nul

echo [Step 6] 检查容器状态...
docker-compose -f docker-compose.postgres.yml ps

echo =====================================================
echo   WebPMS平台现已启动!
echo   - 前端: http://localhost:3000
echo   - API: http://localhost:8000/api
echo   - 管理后台: http://localhost:8000/admin
echo   - 数据库: localhost:15432 (PostgreSQL)
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

pause 