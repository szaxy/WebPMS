@echo off
echo =====================================================
echo   WebPMS node_modules Backup Tool
echo   (For Offline Deployment)
echo =====================================================

:: 设置变量
set "OUTPUT_DIR=offline-resources\npm-packages"
set "PACKAGES_FILE=package-list.txt"

:: 检查Docker
echo [1] Checking Docker environment...
docker ps >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running!
    echo Please start Docker and try again.
    goto END
)

:: 检查前端容器
echo [2] Checking frontend container...
docker ps | findstr webpms-frontend-1 >nul
if errorlevel 1 (
    echo Frontend container is not running, starting it...
    docker-compose -f docker-compose.postgres.yml up -d frontend
    
    echo Waiting for container to start...
    timeout /t 10 /nobreak >nul
    
    docker ps | findstr webpms-frontend-1 >nul
    if errorlevel 1 (
        echo Error: Cannot start frontend container!
        goto END
    )
)

:: 创建输出目录
echo [3] Creating output directory...
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
)

:: 保存依赖列表
echo [4] Saving package dependency list...
docker exec webpms-frontend-1 sh -c "cd /app && npm list --depth=0" > "%OUTPUT_DIR%\%PACKAGES_FILE%"
echo Package list saved to %OUTPUT_DIR%\%PACKAGES_FILE%

:: 备份node_modules目录
echo [5] Creating complete node_modules backup...
echo This might take a while for large node_modules...
docker exec webpms-frontend-1 sh -c "cd /app && tar -czf /tmp/node_modules.tar.gz node_modules"
docker cp webpms-frontend-1:/tmp/node_modules.tar.gz "%OUTPUT_DIR%\"
echo Node modules backup saved to %OUTPUT_DIR%\node_modules.tar.gz

:: 创建离线安装脚本
echo [6] Creating offline installation script...
(
    echo @echo off
    echo echo =====================================================
    echo echo   WebPMS Offline node_modules Installer
    echo echo =====================================================
    echo.
    echo :: Check if Docker is running
    echo docker ps ^>nul 2^>^&1
    echo if errorlevel 1 ^(
    echo     echo Error: Docker is not running!
    echo     echo Please start Docker and try again.
    echo     goto END
    echo ^)
    echo.
    echo :: Check frontend container
    echo docker ps ^| findstr webpms-frontend-1 ^>nul
    echo if errorlevel 1 ^(
    echo     echo Frontend container is not running, starting it...
    echo     docker-compose -f docker-compose.postgres.yml up -d frontend
    echo     timeout /t 10 /nobreak ^>nul
    echo     
    echo     docker ps ^| findstr webpms-frontend-1 ^>nul
    echo     if errorlevel 1 ^(
    echo         echo Error: Cannot start frontend container!
    echo         goto END
    echo     ^)
    echo ^)
    echo.
    echo echo [1] Restoring node_modules directory...
    echo if exist "%OUTPUT_DIR%\node_modules.tar.gz" ^(
    echo     echo Copying node_modules backup to container...
    echo     docker cp "%OUTPUT_DIR%\node_modules.tar.gz" webpms-frontend-1:/app/
    echo     
    echo     echo Extracting node_modules inside container...
    echo     docker exec webpms-frontend-1 sh -c "cd /app && rm -rf node_modules && tar -xzf node_modules.tar.gz && rm node_modules.tar.gz"
    echo     echo Node modules restored successfully.
    echo ^) else ^(
    echo     echo Error: node_modules.tar.gz not found in %OUTPUT_DIR%
    echo     goto END
    echo ^)
    echo.
    echo :: Restart container
    echo echo [2] Restarting frontend container...
    echo docker-compose -f docker-compose.postgres.yml restart frontend
    echo echo Waiting for container to restart...
    echo timeout /t 15 /nobreak ^>nul
    echo.
    echo echo =====================================================
    echo echo   node_modules restored successfully!
    echo echo =====================================================
    echo echo.
    echo echo Please refresh your browser to see the changes.
    echo.
    echo :END
    echo pause
) > "offline-restore-modules.bat"

:: 完成
echo.
echo =====================================================
echo   Backup completed!
echo =====================================================
echo.
echo Complete node_modules directory has been backed up to:
echo %cd%\%OUTPUT_DIR%\node_modules.tar.gz
echo.
echo For offline deployment:
echo 1. Copy the entire '%OUTPUT_DIR%' directory to your target environment
echo 2. Run 'offline-restore-modules.bat' on the target system
echo.
echo This approach ensures ALL dependencies are available in the exact
echo same state as your current development environment.
echo =====================================================

:END
pause 