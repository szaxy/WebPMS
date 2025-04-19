# WebPMS Nginx反向代理配置指南

本文档说明如何使用Nginx作为反向代理，解决WebPMS系统在局域网环境中的跨域问题。

## 为什么需要Nginx反向代理？

当您在局域网环境中访问WebPMS系统时，可能会遇到以下问题：

1. 浏览器尝试连接`localhost`而非服务器IP地址
2. 前端应用中硬编码的API地址导致跨域问题
3. WebSocket连接失败

使用Nginx反向代理可以解决这些问题，通过将前端和后端服务整合到同一域和端口下提供访问。

## 安装步骤

### 1. 下载并安装Nginx

1. 访问 [http://nginx.org/en/download.html](http://nginx.org/en/download.html)
2. 下载稳定版本（如nginx-1.24.0）
3. 解压到简单路径，如`C:\nginx`（推荐）

### 2. 配置Nginx

项目目录中已包含以下文件：
- `nginx.conf` - Nginx配置文件
- `start_nginx.bat` - 启动Nginx的批处理脚本
- `stop_nginx.bat` - 停止Nginx的批处理脚本
- `reload_nginx.bat` - 重新加载配置的批处理脚本

### 3. 启动服务

1. 先启动Django后端服务（端口9803）
2. 再启动Vue前端服务（端口9528）
3. 最后运行`start_nginx.bat`启动Nginx反向代理

### 4. 访问系统

一旦Nginx启动成功，您可以通过以下地址访问WebPMS系统：

- **本地访问**：http://localhost:8765
- **局域网访问**：http://服务器IP地址:8765（如：http://172.16.10.12:8765）

## 配置说明

`nginx.conf`主要配置了以下路径的反向代理：

- `/` - 前端应用（指向本地9528端口）
- `/api/` - 后端API（指向本地9803端口）
- `/ws/` - WebSocket连接（指向本地9803端口）
- `/media/` - 媒体文件（指向本地9803端口）

## 故障排除

### 常见问题

1. **无法启动Nginx**
   - 检查端口8765是否被占用：`netstat -ano | findstr :8765`
   - 如果被占用，可以修改`nginx.conf`中的监听端口

2. **前端可以访问但API请求失败**
   - 检查后端服务是否正常运行
   - 检查`nginx.conf`中API路径配置是否正确

3. **WebSocket连接失败**
   - 确保后端WebSocket服务正常运行
   - 检查WebSocket代理配置

### 查看日志

Nginx日志文件位于：
- 错误日志：`C:\nginx\logs\error.log`
- 访问日志：`C:\nginx\logs\access.log`

## 卸载Nginx

如果您不再需要Nginx：

1. 运行`stop_nginx.bat`停止Nginx服务
2. 删除Nginx安装目录

## 其他说明

Nginx配置可能需要根据实际网络环境进行调整。如果您的计算机IP地址发生变化，需要相应更新`nginx.conf`中的`server_name`设置。 