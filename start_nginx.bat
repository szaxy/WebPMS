@echo off
chcp 65001 > nul
REM WebPMS Nginx Start Script

echo 正在启动Nginx服务...

REM 检查Nginx是否已安装
IF NOT EXIST "G:\LJT\TD\WebPMS_comp\nginx-1.26.3\nginx.exe" (
    echo 错误: 未找到Nginx安装. 请安装Nginx到 G:\LJT\TD\WebPMS_comp\nginx-1.26.3
    echo 您可以从 http://nginx.org/en/download.html 下载
    pause
    exit /b 1
)

REM 检查配置文件是否存在
IF NOT EXIST "G:\LJT\TD\WebPMS_comp\nginx-1.26.3\conf\nginx.conf" (
    echo 错误: 未找到nginx.conf配置文件
    pause
    exit /b 1
)

REM 先检查是否有Nginx进程运行
tasklist /FI "IMAGENAME eq nginx.exe" | find "nginx.exe" > nul
IF %ERRORLEVEL% == 0 (
    echo 发现正在运行的Nginx进程，正在停止...
    cd /d G:\LJT\TD\WebPMS_comp\nginx-1.26.3
    nginx -s stop
    ping 127.0.0.1 -n 3 > nul
)

REM 复制项目nginx.conf到Nginx安装目录
echo 正在复制项目配置文件...
copy /Y "%~dp0nginx.conf" "G:\LJT\TD\WebPMS_comp\nginx-1.26.3\conf\nginx.conf"

REM 检查日志目录是否存在，若不存在则创建
IF NOT EXIST "G:\LJT\TD\WebPMS_comp\nginx-1.26.3\logs" (
    echo 创建日志目录...
    mkdir "G:\LJT\TD\WebPMS_comp\nginx-1.26.3\logs"
)

REM 启动Nginx
echo 正在启动Nginx...
cd /d G:\LJT\TD\WebPMS_comp\nginx-1.26.3
start nginx

REM 检查Nginx是否成功启动
ping 127.0.0.1 -n 3 > nul
tasklist /FI "IMAGENAME eq nginx.exe" | find "nginx.exe" > nul
IF %ERRORLEVEL% == 0 (
    echo Nginx启动成功!
    echo 您现在可以通过以下地址访问WebPMS:
    echo   - 本地访问: http://localhost:8754
    echo   - 局域网访问: http://172.16.10.12:8754
    echo.
    echo 如果您的应用服务未启动，请确保:
    echo   - 前端服务在9527端口运行
    echo   - 后端服务在9803端口运行
) ELSE (
    echo Nginx启动失败，请检查错误信息.
    echo 检查日志文件: G:\LJT\TD\WebPMS_comp\nginx-1.26.3\logs\error.log
)

pause 