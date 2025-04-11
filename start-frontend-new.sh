#!/bin/sh
# 确保目录存在
cd /app

# 检查 node_modules 是否需要重建
if [ ! -d "/app/node_modules" ] || [ ! -f "/app/node_modules/.package-lock.json" ]; then
  echo "Setting up node_modules..."
  
  # 如果存在离线包则使用离线包
  if [ -f "/npm-packages/node_modules.tar.gz" ]; then
    echo "Extracting node_modules from offline package..."
    tar -xzf /npm-packages/node_modules.tar.gz -C /app
    
    # 检查是否成功解压
    if [ ! -d "/app/node_modules/vite" ]; then
      echo "Warning: Vite not found in offline package, will try npm install..."
      npm install
    fi
  else
    echo "Installing dependencies with npm..."
    npm install
  fi
  
  # 创建标记文件
  touch /app/node_modules/.package-lock.json
else
  echo "node_modules already exists, checking dependencies..."
  
  # 检查关键依赖是否存在
  if [ ! -d "/app/node_modules/vite" ]; then
    echo "Critical dependency 'vite' is missing, reinstalling..."
    npm install vite
  fi
fi

# 启动 Vite 开发服务器
echo "Starting Vite development server..."
if [ -f "/app/node_modules/.bin/vite" ]; then
  /app/node_modules/.bin/vite --host 0.0.0.0
else
  echo "ERROR: Vite executable not found!"
  
  # 显示所有可用的bin文件
  echo "Available executables in node_modules/.bin:"
  ls -la /app/node_modules/.bin || echo "No .bin directory found"
  
  # 尝试使用 npx
  echo "Trying to start with npx..."
  npx vite --host 0.0.0.0
fi 