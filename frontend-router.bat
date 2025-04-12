@echo off
chcp 65001 > nul
title WebPMS 固定入口代理

echo =====================================================
echo   WebPMS 固定入口代理 - 端口转发服务
echo   固定入口: http://localhost:9000
echo =====================================================
echo.

REM 检查Node.js是否安装
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Node.js。此工具需要Node.js支持。
    echo 请安装Node.js后再试。
    pause
    exit /b 1
)

REM 创建临时目录
if not exist "temp" mkdir temp

REM 获取当前实际端口
set ACTUAL_PORT=3000
if exist .env.ports (
    for /f "tokens=1,* delims==" %%a in (.env.ports) do (
        if "%%a"=="FRONTEND_PORT" (
            set ACTUAL_PORT=%%b
        )
    )
)

echo 当前WebPMS前端实际端口: %ACTUAL_PORT%
echo 将创建从固定端口9000到实际端口%ACTUAL_PORT%的转发...
echo.

REM 创建临时的代理服务器
echo 正在创建代理服务器代码...
(
    echo const http = require('http');
    echo const httpProxy = require('http-proxy');
    echo.
    echo // 如果http-proxy不存在，提示安装
    echo try {
    echo     require.resolve('http-proxy');
    echo } catch (e) {
    echo     console.error('缺少http-proxy模块。正在安装...');
    echo     require('child_process').execSync('npm install http-proxy');
    echo     console.log('http-proxy已安装');
    echo }
    echo.
    echo const FRONTEND_PORT = %ACTUAL_PORT%;
    echo const PROXY_PORT = 9000;
    echo.
    echo // 创建代理服务器
    echo const proxy = httpProxy.createProxyServer({});
    echo.
    echo // 处理代理错误
    echo proxy.on('error', function (err, req, res) {
    echo     console.error('代理错误:', err);
    echo     res.writeHead(500, {
    echo         'Content-Type': 'text/plain'
    echo     });
    echo     res.end('代理错误: 无法连接到实际服务');
    echo });
    echo.
    echo // 创建HTTP服务器
    echo const server = http.createServer(function(req, res) {
    echo     // 代理到实际服务器
    echo     proxy.web(req, res, { target: `http://localhost:${FRONTEND_PORT}` });
    echo });
    echo.
    echo // 监听固定端口
    echo server.listen(PROXY_PORT, function() {
    echo     console.log('=====================================================');
    echo     console.log(' WebPMS固定入口代理正在运行');
    echo     console.log(` 固定访问地址: http://localhost:${PROXY_PORT}`);
    echo     console.log(` 转发到实际地址: http://localhost:${FRONTEND_PORT}`);
    echo     console.log('=====================================================');
    echo     console.log(' 请保持此窗口打开。关闭窗口将停止代理服务。');
    echo     console.log('=====================================================');
    echo });
) > temp\proxy-server.js

echo 正在启动代理服务...
echo.
echo 请使用 http://localhost:9000 访问WebPMS
echo 此地址不会随着系统端口变化而改变。
echo.
echo 注意：请保持此窗口开启，关闭窗口将停止代理服务。
echo.

node temp\proxy-server.js 