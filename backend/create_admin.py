#!/usr/bin/env python
"""
WebPMS 管理员账户创建脚本
用于在本地环境中快速创建系统管理员账户
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

def create_admin():
    """创建超级管理员账户"""
    
    username = 'admin'
    password = 'admin123'
    device_code = 'admin'
    
    # 检查是否已存在管理员账户
    if User.objects.filter(username=username).exists():
        print(f"管理员账户 '{username}' 已存在")
        admin = User.objects.get(username=username)
        
        # 确保角色是管理员
        if admin.role != 'admin':
            admin.role = 'admin'
            admin.department = 'admin'
            admin.save()
            print(f"已将用户 '{username}' 的角色更新为系统管理员")
            
        # 确保账户状态为已批准
        if admin.registration_status != 'approved':
            admin.registration_status = 'approved'
            admin.save()
            print(f"已将管理员账户 '{username}' 状态更新为已批准")
            
        # 确保是超级用户
        if not admin.is_superuser or not admin.is_staff:
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
            print(f"已将管理员账户 '{username}' 设置为超级用户")
    else:
        # 创建新的超级管理员账户
        User.objects.create_superuser(
            username=username,
            email='admin@example.com',
            password=password,
            device_code=device_code,
            role='admin',
            department='admin',
            registration_status='approved',
            is_staff=True,
            is_superuser=True
        )
        print(f"已创建新的超级管理员账户: {username} (密码: {password})")
        print("请使用此账户登录系统并尽快修改密码")

if __name__ == '__main__':
    print("开始创建管理员账户...")
    create_admin()
    print("管理员账户创建/更新完成") 