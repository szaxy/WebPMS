@echo off
chcp 65001 > nul
echo =====================================================
echo   WebPMS Platform - 清理工具
echo =====================================================

echo [Step 1] 停止并删除所有容器...
docker-compose -f docker-compose.postgres.yml down -v
echo 已移除所有WebPMS容器和相关卷。

echo [Step 2] 清理前端依赖...
set FRONTEND_FOLDER=frontend
if exist "%FRONTEND_FOLDER%\node_modules" (
    echo 删除 %FRONTEND_FOLDER%\node_modules 文件夹...
    rd /s /q "%FRONTEND_FOLDER%\node_modules"
    if exist "%FRONTEND_FOLDER%\node_modules" (
        echo 警告: 无法完全删除node_modules文件夹，请手动删除。
    ) else (
        echo 成功删除node_modules文件夹。
    )
)

echo [Step 3] 清理Docker缓存(可选)...
choice /C YN /M "是否清理Docker构建缓存? 这将释放磁盘空间但会使下次构建变慢"
if errorlevel 1 (
    if errorlevel 2 (
        echo 跳过清理Docker缓存。
    ) else (
        echo 正在清理Docker构建缓存...
        docker builder prune -f
        echo Docker构建缓存已清理。
    )
)

echo =====================================================
echo   WebPMS Platform 清理完成!
echo   您可以通过运行start-webpms.bat重新启动系统。
echo =====================================================

pause 