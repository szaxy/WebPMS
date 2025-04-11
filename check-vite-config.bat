@echo off
echo =====================================================
echo   WebPMS Vite Config Checker/Fixer
echo =====================================================

:: 检查Docker
echo [Step 1] Checking Docker environment...
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    goto END
)

:: 检查前端容器
echo [Step 2] Checking frontend container...
docker ps | findstr webpms-frontend-1 >nul
if errorlevel 1 (
    echo [WARNING] Frontend container is not running!
    echo Starting frontend container...
    docker-compose -f docker-compose.postgres.yml up -d frontend
    
    echo Waiting for container to start...
    timeout /t 10 /nobreak >nul
    
    docker ps | findstr webpms-frontend-1 >nul
    if errorlevel 1 (
        echo [ERROR] Failed to start frontend container!
        goto END
    )
)

:: 检查vite配置
echo [Step 3] Checking current Vite configuration...
echo Current vite.config.js content:
echo -------------------------------------------
docker exec webpms-frontend-1 cat /app/vite.config.js
echo -------------------------------------------
echo.

:: 检查是否有localhost绑定问题
echo [Step 4] Checking if Vite is binding correctly...
docker exec webpms-frontend-1 sh -c "grep -E \"host:|server:\" /app/vite.config.js" > tmp_config.txt

findstr /i "localhost 127.0.0.1" tmp_config.txt >nul
if not errorlevel 1 (
    echo [FOUND] Vite may be restrictively binding to localhost/127.0.0.1
    echo This could prevent connections from outside the container.
    
    set /p FIX_CONFIG="Would you like to fix the Vite configuration to bind to all interfaces? (Y/N): "
    if /i "%FIX_CONFIG%"=="Y" (
        echo [Step 5] Creating updated Vite configuration...
        
        echo import { defineConfig } from 'vite' > fixed_vite_config.js
        echo import vue from '@vitejs/plugin-vue' >> fixed_vite_config.js
        echo. >> fixed_vite_config.js
        echo export default defineConfig({ >> fixed_vite_config.js
        echo   plugins: [vue()], >> fixed_vite_config.js
        echo   server: { >> fixed_vite_config.js
        echo     host: '0.0.0.0', >> fixed_vite_config.js
        echo     port: 3000, >> fixed_vite_config.js
        echo   }, >> fixed_vite_config.js
        echo }) >> fixed_vite_config.js
        
        echo [Step 6] Backing up original configuration...
        docker exec webpms-frontend-1 sh -c "cp /app/vite.config.js /app/vite.config.js.bak"
        
        echo [Step 7] Uploading new configuration...
        docker cp fixed_vite_config.js webpms-frontend-1:/app/vite.config.js
        del fixed_vite_config.js
        
        echo [Step 8] Restarting frontend service...
        docker-compose -f docker-compose.postgres.yml restart frontend
        
        echo Waiting for frontend to restart...
        timeout /t 15 /nobreak >nul
        
        echo Configuration updated and service restarted!
    )
) else (
    echo [OK] No restrictive binding found in Vite configuration.
)

del tmp_config.txt

:: 检查服务是否可访问
echo.
echo [Step 9] Testing service accessibility...
powershell -Command "try { $client = New-Object System.Net.Sockets.TcpClient('localhost', 3000); $client.Close(); Write-Host 'Connection successful! Frontend is accessible.' } catch { Write-Host 'Connection failed! Frontend is still not accessible.' }"

:: 检查前端日志
echo.
echo [Step 10] Checking frontend logs after configuration update...
docker logs --tail 20 webpms-frontend-1

echo.
echo =====================================================
echo   Configuration Check/Fix Completed
echo =====================================================
echo.
echo If you still cannot connect:
echo 1. Try accessing with a different browser
echo 2. Check if port 3000 is blocked by firewall
echo 3. Try explicitly accessing http://localhost:3000
echo 4. Check the Docker network configuration with:
echo    docker network inspect webpms_default
echo.
echo Run 'fix-connection.bat' for a more comprehensive diagnosis.
echo =====================================================

:END
pause 