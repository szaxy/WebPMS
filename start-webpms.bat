@echo off
echo =====================================================
echo   WebPMS Platform - Offline Startup
echo =====================================================

echo [Step 1] Checking for required packages...
if not exist "offline-resources\python-packages\py3\tomli-2.0.0-py3-none-any.whl" (
    echo ERROR: tomli package not found in correct location!
    echo Please make sure you have the tomli-2.0.0-py3-none-any.whl in your offline-resources\python-packages\py3 directory.
    pause
    exit /b 1
)

echo [Step 2] Loading Docker images if needed...
echo Checking PostgreSQL image...
docker images | findstr postgres:14.15 > nul
if errorlevel 1 (
    echo Loading PostgreSQL image...
    docker load -i docker\images\postgres-14.15.tar
)

echo Checking Redis image...
docker images | findstr redis:alpine > nul
if errorlevel 1 (
    echo Loading Redis image...
    docker load -i docker\images\redis-alpine.tar
)

echo Checking Python image...
docker images | findstr python:3.10-slim > nul
if errorlevel 1 (
    echo Loading Python image...
    docker load -i docker\images\python-slim.tar
)

echo Checking Node.js image...
docker images | findstr node:18-alpine > nul
if errorlevel 1 (
    echo Loading Node.js image...
    docker load -i docker\images\node-alpine.tar
)

echo [Step 3] Stopping any running containers...
docker-compose -f docker-compose.postgres.yml down 2>nul
timeout /t 2 /nobreak > nul

echo [Step 4] Starting database container...
docker-compose -f docker-compose.postgres.yml up -d db redis
echo Waiting for database to initialize...
timeout /t 15 /nobreak > nul

echo [Step 5] Starting backend container and running migrations...
docker-compose -f docker-compose.postgres.yml up -d backend
echo Waiting for backend to start...
timeout /t 15 /nobreak > nul

echo [Step 6] Running database migrations...
echo - Checking for conflicting migrations...
docker exec -it webpms-backend-1 sh -c "cd /app && python manage.py makemigrations --merge --noinput"
echo - Creating migrations for users app...
docker exec -it webpms-backend-1 sh -c "cd /app && python manage.py makemigrations users"
echo - Creating migrations for other apps...
docker exec -it webpms-backend-1 sh -c "cd /app && python manage.py makemigrations"
echo - Applying all migrations...
docker exec -it webpms-backend-1 sh -c "cd /app && python manage.py migrate"
echo Migrations completed.
timeout /t 5 /nobreak > nul

echo [Step 7] Starting frontend container...
docker-compose -f docker-compose.postgres.yml up -d frontend
echo Waiting for frontend to start...
timeout /t 30 /nobreak > nul

echo [Step 8] Checking container status...
docker-compose -f docker-compose.postgres.yml ps

echo =====================================================
echo   WebPMS Platform is now running!
echo   - Frontend: http://localhost:3000
echo   - API: http://localhost:8000/api
echo   - Admin: http://localhost:8000/admin
echo   - Database: localhost:15432 (PostgreSQL)
echo =====================================================
echo Note: If frontend shows "localhost didn't send any data", please wait
echo       another 30 seconds and refresh the page. The Vite server needs
echo       time to start up completely.
echo =====================================================
echo To create an admin user, run:
echo docker exec -it webpms-backend-1 sh -c "cd /app && python manage.py createsuperuser"
echo.
echo To stop services:
echo docker-compose -f docker-compose.postgres.yml down
echo.
echo To view backend logs:
echo docker-compose -f docker-compose.postgres.yml logs -f backend
echo.
echo To view frontend logs:
echo docker-compose -f docker-compose.postgres.yml logs -f frontend

pause 