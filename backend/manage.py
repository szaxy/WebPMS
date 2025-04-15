#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import django
from django.core.management import call_command


def main():
    """Run administrative tasks."""
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
        
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    # 如果命令是runserver，先执行迁移
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        try:
            django.setup()
            print("自动执行数据库迁移...")
            call_command('migrate')
            print("迁移完成。")
        except Exception as e:
            print(f"迁移过程中出错: {e}")
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main() 