@echo off
chcp 65001 > nul
title 创建WebPMS桌面快捷方式

echo =====================================================
echo   WebPMS 桌面快捷方式创建工具
echo =====================================================
echo.

REM 获取当前脚本路径
set "SCRIPT_PATH=%~dp0"
set "HTML_PATH=%SCRIPT_PATH%frontend-proxy.html"
set "SHORTCUT_NAME=WebPMS智能入口.url"
set "DESKTOP_PATH=%USERPROFILE%\Desktop"

echo 正在创建桌面快捷方式...

REM 创建快捷方式到桌面
echo [InternetShortcut] > "%DESKTOP_PATH%\%SHORTCUT_NAME%"
echo URL=file://%HTML_PATH% >> "%DESKTOP_PATH%\%SHORTCUT_NAME%"
echo IconIndex=0 >> "%DESKTOP_PATH%\%SHORTCUT_NAME%"
echo HotKey=0 >> "%DESKTOP_PATH%\%SHORTCUT_NAME%"
echo IDList= >> "%DESKTOP_PATH%\%SHORTCUT_NAME%"

echo.
echo 快捷方式已创建: "%DESKTOP_PATH%\%SHORTCUT_NAME%"
echo.
echo 您现在可以通过桌面上的"WebPMS智能入口"图标访问系统，
echo 无论系统端口如何变化，此快捷方式都能智能检测并访问正确的端口。
echo.

pause 