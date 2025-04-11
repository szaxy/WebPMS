print("Starting fix...")

from django.contrib.auth import get_user_model
User = get_user_model()

# 更新所有用户状态为已批准
users = User.objects.all()
for user in users:
    user.registration_status = 'approved'
    user.save()
    print(f"Updated user: {user.username}")

print("All users updated to approved status.") 