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

echo [Step 3] Checking if start-frontend-new.sh exists...
if not exist "start-frontend-new.sh" (
    echo Creating enhanced frontend startup script...
    (
        echo #!/bin/sh
        echo # Ensure directory exists
        echo cd /app
        echo.
        echo # Check if node_modules needs to be rebuilt
        echo if [ ! -d "/app/node_modules" ] ^|^| [ ! -f "/app/node_modules/.package-lock.json" ]; then
        echo   echo "Setting up node_modules..."
        echo.  
        echo   # If offline package exists, use it
        echo   if [ -f "/npm-packages/node_modules.tar.gz" ]; then
        echo     echo "Extracting node_modules from offline package..."
        echo     tar -xzf /npm-packages/node_modules.tar.gz -C /app
        echo.     
        echo     # Check if extraction was successful
        echo     if [ ! -d "/app/node_modules/vite" ]; then
        echo       echo "Warning: Vite not found in offline package, will try npm install..."
        echo       npm install
        echo     fi
        echo   else
        echo     echo "Installing dependencies with npm..."
        echo     npm install
        echo   fi
        echo.   
        echo   # Create marker file
        echo   touch /app/node_modules/.package-lock.json
        echo else
        echo   echo "node_modules already exists, checking dependencies..."
        echo.   
        echo   # Check if critical dependencies exist
        echo   if [ ! -d "/app/node_modules/vite" ]; then
        echo     echo "Critical dependency 'vite' is missing, reinstalling..."
        echo     npm install vite
        echo   fi
        echo fi
        echo.
        echo # Start Vite development server
        echo echo "Starting Vite development server..."
        echo if [ -f "/app/node_modules/.bin/vite" ]; then
        echo   /app/node_modules/.bin/vite --host 0.0.0.0
        echo else
        echo   echo "ERROR: Vite executable not found!"
        echo.   
        echo   # Show all available bin files
        echo   echo "Available executables in node_modules/.bin:"
        echo   ls -la /app/node_modules/.bin ^|^| echo "No .bin directory found"
        echo.   
        echo   # Try using npx
        echo   echo "Trying to start with npx..."
        echo   npx vite --host 0.0.0.0
        echo fi
    ) > start-frontend-new.sh
    echo Enhanced frontend script created.
)

echo [Step 4] Updating docker-compose configuration...
set "COMPOSE_FILE=docker-compose.postgres.yml"
type "%COMPOSE_FILE%" | findstr "start-frontend-new.sh" > nul
if errorlevel 1 (
    echo Backup original docker-compose file...
    copy "%COMPOSE_FILE%" "%COMPOSE_FILE%.bak" > nul
    
    echo Updating frontend command in docker-compose file...
    powershell -Command "(Get-Content '%COMPOSE_FILE%') -replace 'command: sh /start-frontend.sh', 'command: sh /start-frontend-new.sh' -replace './start-frontend.sh:/start-frontend.sh', './start-frontend-new.sh:/start-frontend-new.sh' | Set-Content '%COMPOSE_FILE%'"
    
    echo Docker compose configuration updated.
)

echo [Step 5] Stopping any running containers...
docker-compose -f docker-compose.postgres.yml down 2>nul
timeout /t 2 /nobreak > nul

echo [Step 6] Starting database container...
docker-compose -f docker-compose.postgres.yml up -d db redis
echo Waiting for database to initialize...
timeout /t 15 /nobreak > nul

echo [Step 7] Starting backend container and running migrations...
docker-compose -f docker-compose.postgres.yml up -d backend
echo Waiting for backend to start...
timeout /t 15 /nobreak > nul

echo [Step 8] Running database migrations...
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

echo [Step 9] Starting frontend container...
docker-compose -f docker-compose.postgres.yml up -d frontend
echo Waiting for frontend to start...
timeout /t 30 /nobreak > nul

echo [Step 10] Checking container status...
docker-compose -f docker-compose.postgres.yml ps

echo =====================================================
echo   WebPMS Platform is now running!
echo   - Frontend: http://localhost:3000
echo   - API: http://localhost:8000/api
echo   - Admin: http://localhost:8000/admin
echo   - Database: localhost:15432 (PostgreSQL)
echo =====================================================
echo Note: If frontend shows connection issues, check logs with:
echo       docker-compose -f docker-compose.postgres.yml logs frontend
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