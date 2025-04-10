#!/bin/bash
echo "加载PostgreSQL镜像..."
docker load -i ../images/postgres-14.tar

echo "加载Redis镜像..."
docker load -i ../images/redis-alpine.tar

echo "加载Python镜像..."
docker load -i ../images/python-3.10-slim.tar

echo "加载Node.js镜像..."
docker load -i ../images/node-18-alpine.tar

echo "所有镜像加载完成!"
docker images
