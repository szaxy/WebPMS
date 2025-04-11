@echo off
REM ===================================================
REM   WebPMS NPM Package Extractor (From Real Project)
REM ===================================================

REM Set paths
set NPM_DEPS_DIR=offline-resources\npm-packages
set TEMP_CONTAINER_NAME=webpms-npm-extractor

REM Create required directories
if not exist "%NPM_DEPS_DIR%" mkdir "%NPM_DEPS_DIR%"

echo.
echo [Step 1] Stopping any existing container...
docker rm -f %TEMP_CONTAINER_NAME% 2>nul

echo [Step 2] Creating temporary container to extract existing dependencies...
echo This will extract dependencies from your frontend container

REM First check if frontend container is running
docker ps | findstr webpms-frontend > nul
if errorlevel 1 (
    echo [WARNING] WebPMS frontend container not running!
    echo Please run start-webpms-optimized.bat first to start the containers
    echo or use download-npm-packages-fixed.bat to download packages directly.
    pause
    exit /b 1
)

echo [Step 3] Extracting node_modules from running frontend container...
docker exec webpms-frontend-1 sh -c "cd /app && tar -czf /tmp/node_modules.tar.gz node_modules && echo 'Node modules archived successfully'"

echo [Step 4] Copying archive from container to host...
docker cp webpms-frontend-1:/tmp/node_modules.tar.gz "%NPM_DEPS_DIR%\node_modules.tar.gz"

echo [Step 5] Cleaning up temporary files in container...
docker exec webpms-frontend-1 sh -c "rm /tmp/node_modules.tar.gz"

echo [Step 6] Checking extraction success...
if exist "%NPM_DEPS_DIR%\node_modules.tar.gz" (
    echo [SUCCESS] Successfully extracted node_modules from running project
    
    REM Create package list from package.json for future reference
    echo [Step 7] Creating package list from active project...
    docker exec webpms-frontend-1 sh -c "cd /app && npm list --depth=0" > "%NPM_DEPS_DIR%\package-list.txt"
    
    echo.
    echo ===================================================
    echo   NPM packages extracted successfully!
    echo ===================================================
    echo NPM packages tar file saved to: %NPM_DEPS_DIR%\node_modules.tar.gz
    echo Package list saved to: %NPM_DEPS_DIR%\package-list.txt
    echo.
    echo You can now use these files with start-webpms-optimized.bat
) else (
    echo [ERROR] Failed to extract node_modules
    echo Please check Docker permissions and container status
)
echo ===================================================

pause 