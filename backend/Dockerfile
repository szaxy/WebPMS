FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    # Pillow依赖
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 创建媒体文件夹
RUN mkdir -p /app/@attachments/thumbnails

# 复制项目文件
COPY . /app/

# 执行迁移脚本
RUN python auto_migrate.py || echo "迁移稍后会在runserver时执行"

# 设置启动命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 