FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json（如果存在）
COPY package*.json ./

# 安装项目依赖
RUN npm install

# 复制项目文件
COPY . .

# 设置默认命令
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 