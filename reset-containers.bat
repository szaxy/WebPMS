@echo off
REM ===================================================
REM   WebPMS Container Reset & Cleanup Tool
REM ===================================================

set "COMPOSE_FILE=docker-compose.postgres.yml"

echo [Step 1] Stopping all running containers...
docker-compose -f %COMPOSE_FILE% down

echo [Step 2] Checking for orphaned containers...
for /f "tokens=*" %%i in ('docker ps -a ^| findstr webpms') do (
    for /f "tokens=1" %%j in ("%%i") do (
        echo Removing container: %%j
        docker rm -f %%j
    )
)

echo [Step 3] Cleaning up Docker networks...
for /f "tokens=*" %%i in ('docker network ls ^| findstr webpms') do (
    for /f "tokens=1" %%j in ("%%i") do (
        echo Removing network: %%j
        docker network rm %%j 2>nul
    )
)

echo [Step 4] Restoring original docker-compose file...
if exist "%COMPOSE_FILE%.original" (
    echo Restoring from original backup...
    copy "%COMPOSE_FILE%.original" "%COMPOSE_FILE%" /y
) else if exist "%COMPOSE_FILE%.bak" (
    echo Restoring from backup...
    copy "%COMPOSE_FILE%.bak" "%COMPOSE_FILE%" /y
)

echo [Step 5] Checking container status...
docker ps -a | findstr webpms

echo.
echo ===================================================
echo   Container reset complete!
echo ===================================================
echo All WebPMS containers have been stopped and removed.
echo You can now run start-webpms-optimized.bat for a fresh start.
echo ===================================================

pause 