FROM registry.cn-hangzhou.aliyuncs.com/library/postgres:14

# 添加初始化脚本
COPY ./init-scripts/ /docker-entrypoint-initdb.d/

# 设置时区
ENV TZ=Asia/Shanghai

# 设置字符集
ENV LANG zh_CN.utf8 