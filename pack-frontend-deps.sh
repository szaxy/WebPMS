#!/bin/sh

# 停止已经运行的容器
echo "==== 停止运行中的容器 ===="
docker-compose -f docker-compose.postgres.yml down

# 创建临时容器来打包依赖
echo "==== 创建临时容器打包依赖 ===="
docker run -it --rm \
  -v ${PWD}/frontend:/app \
  -v ${PWD}/offline-resources/npm-packages:/output \
  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/node:18-alpine \
  sh -c "cd /app && \
         echo '安装最新依赖...' && \
         npm config set strict-ssl false && \
         npm config set registry https://registry.npmjs.org/ && \
         npm install --legacy-peer-deps && \
         echo '打包node_modules...' && \
         tar -czf /output/node_modules.tar.gz -C /app node_modules && \
         echo '保存package-lock.json...' && \
         cp /app/package-lock.json /output/package-lock.json && \
         echo '记录安装包版本信息...' && \
         npm ls --depth=0 > /output/package-list.txt && \
         echo '完成! 依赖包已保存到 offline-resources/npm-packages 目录'"

# 显示完成信息
echo "==== 依赖打包完成 ===="
echo "node_modules.tar.gz 文件大小："
du -h offline-resources/npm-packages/node_modules.tar.gz

# 重新启动服务
echo "==== 重新启动服务 ===="
docker-compose -f docker-compose.postgres.yml up -d 