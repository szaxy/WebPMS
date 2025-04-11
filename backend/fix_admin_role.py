print("开始修复管理员角色...")

from django.contrib.auth import get_user_model
User = get_user_model()

# 找到超级管理员用户
superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    for admin in superusers:
        # 更新角色为系统管理员
        admin.role = 'admin'
        admin.save()
        print(f"已将用户 {admin.username} 的角色更新为系统管理员")
else:
    print("未找到任何超级管理员用户")

print("修复完成。") 