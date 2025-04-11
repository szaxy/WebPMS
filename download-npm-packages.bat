@echo off
REM ===================================================
REM   WebPMS NPM Package Downloader (Docker Container)
REM ===================================================

REM Set paths
set NPM_DEPS_DIR=offline-resources\npm-packages
set TEMP_CONTAINER_NAME=webpms-npm-downloader

REM Create required directories
if not exist "%NPM_DEPS_DIR%" mkdir "%NPM_DEPS_DIR%"

REM Create package list if not exists
if not exist "%NPM_DEPS_DIR%\package-list.txt" (
  echo vue@3.3.4 > "%NPM_DEPS_DIR%\package-list.txt"
  echo pinia@2.1.6 >> "%NPM_DEPS_DIR%\package-list.txt"
  echo vite@4.4.9 >> "%NPM_DEPS_DIR%\package-list.txt"
  echo axios@1.5.0 >> "%NPM_DEPS_DIR%\package-list.txt"
  echo element-plus@2.3.12 >> "%NPM_DEPS_DIR%\package-list.txt"
  echo @element-plus/icons-vue@2.1.0 >> "%NPM_DEPS_DIR%\package-list.txt"
  echo vue-router@4.2.4 >> "%NPM_DEPS_DIR%\package-list.txt"
  echo date-fns@2.30.0 >> "%NPM_DEPS_DIR%\package-list.txt"
  echo lodash@4.17.21 >> "%NPM_DEPS_DIR%\package-list.txt"
)

REM Create temp script to run inside docker container
echo #!/bin/sh > npm-download.sh
echo mkdir -p /temp-project >> npm-download.sh
echo cd /temp-project >> npm-download.sh
echo echo "{\"name\":\"webpms-temp\",\"version\":\"1.0.0\",\"dependencies\":{}}" ^> package.json >> npm-download.sh
echo echo "Installing NPM packages..." >> npm-download.sh
echo xargs npm install --save --no-fund --no-audit < /package-list/package-list.txt >> npm-download.sh
echo echo "Creating archive of node_modules..." >> npm-download.sh
echo tar -czf /package-list/node_modules.tar.gz node_modules >> npm-download.sh
echo echo "Package download complete" >> npm-download.sh

echo.
echo [Step 1] Stopping any existing container...
docker rm -f %TEMP_CONTAINER_NAME% 2>nul

echo [Step 2] Creating temporary container to download NPM packages...
docker run --name %TEMP_CONTAINER_NAME% -v "%CD%\%NPM_DEPS_DIR%:/package-list" -v "%CD%\npm-download.sh:/npm-download.sh" node:18-alpine /bin/sh -c "chmod +x /npm-download.sh && /npm-download.sh"

echo [Step 3] Cleaning up...
docker rm -f %TEMP_CONTAINER_NAME% 2>nul
del npm-download.sh 2>nul

echo.
echo ===================================================
echo   NPM packages downloaded successfully!
echo ===================================================
echo NPM packages tar file saved to: %NPM_DEPS_DIR%\node_modules.tar.gz
echo.
echo You can now run start-webpms-optimized.bat to start the project
echo ===================================================

pause 