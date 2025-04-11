import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User

# 获取所有超级用户或管理员
admin_users = User.objects.filter(is_superuser=True) | User.objects.filter(is_staff=True)

for user in admin_users:
    # 设置角色为admin
    user.role = 'admin'
    # 设置部门为producer (制片部门，通常具有查看所有内容的权限)
    user.department = 'producer'
    user.save()
    print(f"已更新用户 {user.username} 的角色为管理员，部门为制片")

print("管理员用户更新完成") 