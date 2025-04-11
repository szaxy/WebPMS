@echo off
echo =====================================================
echo   WebPMS Environment Cleanup Utility
echo =====================================================

echo [1] Stopping all running Docker containers...
for /f "tokens=*" %%i in ('docker ps -q') do (
    docker stop %%i
)
docker-compose -f docker-compose.postgres.yml down 2>nul

echo [2] Removing all containers related to WebPMS...
docker ps -a | findstr webpms
for /f "tokens=1" %%i in ('docker ps -a -q --filter "name=webpms"') do (
    docker rm %%i
)

echo [3] Checking for any remaining containers...
docker ps -a

echo [4] Cleaning up unused containers...
docker container prune -f

echo [5] Cleaning up unused networks...
docker network prune -f

echo [6] Cleaning up unused volumes...
docker volume prune -f

echo [7] Checking if services are completely stopped...
echo Checking PostgreSQL...
netstat -ano | findstr 5432
netstat -ano | findstr 15432
echo Checking Redis...
netstat -ano | findstr 6379
echo Checking backend service...
netstat -ano | findstr 8000
echo Checking frontend service...
netstat -ano | findstr 3000

echo =====================================================
echo Cleanup complete! Environment has been fully reset.
echo =====================================================

pause 