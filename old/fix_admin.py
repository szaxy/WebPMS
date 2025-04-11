#!/usr/bin/env python
print("开始修复管理员账户...")

from django.contrib.auth import get_user_model
User = get_user_model()

# 查找管理员账户
try:
    # 尝试查找用户名为'admin'的账户
    admin = User.objects.get(username='admin')
    print(f"找到管理员账户: {admin.username}")
    
    # 更新管理员状态为已批准
    admin.registration_status = 'approved'
    admin.save()
    print("管理员账户已更新为已批准状态")
    
except User.DoesNotExist:
    print("未找到用户名为'admin'的账户，尝试查找超级用户...")
    
    # 尝试查找任何超级用户账户
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        for su in superusers:
            su.registration_status = 'approved'
            su.save()
            print(f"超级用户 {su.username} 已更新为已批准状态")
    else:
        print("未找到任何超级用户账户，将创建新的管理员账户...")
        
        # 创建一个新的超级用户
        User.objects.create_superuser(
            username='newadmin',
            email='admin@example.com',
            password='admin123',
            registration_status='approved'
        )
        print("创建了新的超级管理员账户: newadmin (密码: admin123)")

print("修复完成。") 