#!/usr/bin/env python
"""
自动执行迁移的脚本，可以在应用程序启动时运行
"""
import os
import django
import sys

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# 导入必要的模块
from django.core.management import call_command
from django.db import connection

def main():
    print("开始执行数据库迁移...")
    
    # 执行迁移
    call_command('migrate')
    
    # 记录已应用的迁移
    cursor = connection.cursor()
    cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
    applied_migrations = cursor.fetchall()
    
    print("已应用的迁移:")
    for app, name in applied_migrations:
        print(f"  {app}: {name}")
    
    print("迁移完成。")

if __name__ == "__main__":
    main() 