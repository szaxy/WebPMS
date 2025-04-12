@echo off
chcp 65001 > nul
title 打包前端依赖 - 简化版

echo ===================================================
echo  前端依赖打包工具 - 简化版
echo ===================================================

:: 检查目录
if not exist "frontend" (
    echo 错误: 未找到frontend目录!
    pause
    exit /b 1
)

if not exist "offline-resources\npm-packages" mkdir "offline-resources\npm-packages"

:: 确保Docker正在运行
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker未运行!
    pause
    exit /b 1
)

:: 停止已有容器
echo 1. 停止运行中的容器...
docker-compose -f docker-compose.postgres.yml down

:: 简化的打包命令
echo 2. 开始打包依赖(请耐心等待)...

docker run --rm ^
    -v "%CD%\frontend:/frontend" ^
    -v "%CD%\offline-resources\npm-packages:/output" ^
    swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/node:18-alpine ^
    /bin/sh -c "cd /frontend && npm install && tar -czf /output/node_modules.tar.gz node_modules && cp package-lock.json /output/"

:: 检查结果
if exist "offline-resources\npm-packages\node_modules.tar.gz" (
    echo ===================================================
    echo  依赖打包成功!
    echo  文件已保存到: offline-resources\npm-packages\node_modules.tar.gz
    echo ===================================================
) else (
    echo 错误: 依赖打包失败
    pause
    exit /b 1
)

echo 3. 重启服务...
docker-compose -f docker-compose.postgres.yml up -d

echo 完成! 现在可以使用start-webpms.bat启动系统了
pause 