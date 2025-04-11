@echo off
chcp 65001 > nul
title WebPMS Frontend Dependencies Packager
echo =====================================================
echo   WebPMS Frontend Dependencies Packager
echo =====================================================

:: 检查目录存在
if not exist "frontend" (
    echo ERROR: 前端目录不存在!
    echo 请确保脚本在项目根目录运行。
    pause
    exit /b 1
)

if not exist "offline-resources\npm-packages" (
    echo 创建离线资源目录...
    mkdir "offline-resources\npm-packages"
)

:: 检查Docker是否在运行
docker info > nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker不在运行状态!
    echo 请先启动Docker Desktop然后再运行此脚本。
    pause
    exit /b 1
)

echo Step 1: 停止运行中的容器...
docker-compose -f docker-compose.postgres.yml down

echo Step 2: 创建临时容器打包依赖...
echo 正在安装和打包依赖，这可能需要几分钟时间...

:: 使用绝对路径避免路径问题
set "CURRENT_DIR=%CD%"
set "FRONTEND_DIR=%CURRENT_DIR%\frontend"
set "OUTPUT_DIR=%CURRENT_DIR%\offline-resources\npm-packages"

echo 前端目录: %FRONTEND_DIR%
echo 输出目录: %OUTPUT_DIR%

:: 使用单行命令避免Windows批处理特殊字符问题
docker run --rm -v "%FRONTEND_DIR%:/app" -v "%OUTPUT_DIR%:/output" swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/node:18-alpine sh -c "cd /app && npm config set strict-ssl false && npm config set registry https://registry.npmjs.org/ && npm install --legacy-peer-deps && tar -czf /output/node_modules.tar.gz -C /app node_modules && cp -f /app/package-lock.json /output/ && npm ls --depth=0 > /output/package-list.txt"

:: 检查是否成功打包
if exist "%OUTPUT_DIR%\node_modules.tar.gz" (
    echo Step 3: 依赖打包成功!
    echo node_modules.tar.gz 大小:
    dir "%OUTPUT_DIR%\node_modules.tar.gz" | findstr "node_modules"
) else (
    echo ERROR: 依赖打包失败，未找到输出文件!
    pause
    exit /b 1
)

echo 重新启动服务...
docker-compose -f docker-compose.postgres.yml up -d

echo =====================================================
echo   前端依赖已成功打包到离线目录!
echo   可以通过start-webpms.bat启动服务尝试离线加载
echo =====================================================

pause 