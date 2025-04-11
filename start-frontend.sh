#!/bin/sh
cd /app

# 检查node_modules是否已经存在
if [ ! -d "/app/node_modules" ] || [ ! -f "/app/node_modules/.package-lock.json" ]; then
  echo "Extracting node_modules..."
  tar -xzf /npm-packages/node_modules.tar.gz -C /app
else
  echo "node_modules already exists, skipping extraction"
fi

echo 'Starting Vite server...'
export PATH=/app/node_modules/.bin:$PATH

# 检查vite是否存在
if [ -f "/app/node_modules/vite/bin/vite.js" ]; then
  echo "Starting Vite development server on port 3000..."
  exec node /app/node_modules/vite/bin/vite.js --host 0.0.0.0
else
  echo "ERROR: Vite not found in node_modules!"
  exit 1
fi