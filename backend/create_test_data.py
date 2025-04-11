import os
import django
import random
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from projects.models import Project
from shots.models import Shot

User = get_user_model()

# 获取或创建动画部门用户
def get_or_create_animator_users():
    # 检查是否有动画部门的用户
    animator_users = User.objects.filter(department='DH').order_by('?')
    
    # 如果没有，创建两个
    if not animator_users.exists():
        print("创建动画部门测试用户...")
        usernames = ['animator1', 'animator2']
        users = []
        for i, username in enumerate(usernames):
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password="testpassword",
                department='DH',  # 动画部门
                role='artist',    # 艺术家角色
            )
            users.append(user)
        return users
    else:
        print(f"发现已有{animator_users.count()}个动画部门用户")
        return list(animator_users[:2])  # 返回最多两个用户

# 创建测试项目
def create_test_projects():
    project_names = [
        "荷和年-星罗棋布",
        "荷和年-无垠星辰"
    ]
    
    projects = []
    for i, name in enumerate(project_names):
        project, created = Project.objects.get_or_create(
            name=name,
            defaults={
                'code': f'HHY{i+1}',
                'status': 'active',
                'start_date': timezone.now().date(),
                'end_date': (timezone.now() + datetime.timedelta(days=180)).date(),
                'description': f"{name}项目描述"
            }
        )
        
        if created:
            print(f"创建新项目: {name}")
        else:
            print(f"项目已存在: {name}")
        
        projects.append(project)
    
    return projects

# 创建测试镜头
def create_test_shots(projects, artists):
    stages = ['LAY', 'BLK', 'ANI', 'PASS']
    statuses = ['waiting', 'in_progress', 'submit_review', 'revising', 
                'internal_approved', 'client_review']
    
    total_created = 0
    
    for project in projects:
        # 检查项目下已有多少镜头
        existing_shots = Shot.objects.filter(project=project).count()
        if existing_shots >= 10:
            print(f"项目 {project.name} 已有 {existing_shots} 个镜头，跳过")
            continue
            
        shots_to_create = 10 - existing_shots
        print(f"为项目 {project.name} 创建 {shots_to_create} 个镜头")
        
        for i in range(shots_to_create):
            shot_num = existing_shots + i + 1
            
            # 随机选择一个艺术家
            artist = random.choice(artists) if random.random() > 0.3 else None
            
            # 随机生成日期
            today = timezone.now().date()
            deadline = today + datetime.timedelta(days=random.randint(10, 60))
            
            # 有50%概率有提交日期
            has_submission = random.random() > 0.5
            last_submit_date = today - datetime.timedelta(days=random.randint(1, 10)) if has_submission else None
            
            # 创建镜头
            shot = Shot.objects.create(
                project=project,
                shot_code=f"SC_{shot_num:03d}",
                department='DH',  # 动画部门
                prom_stage=random.choice(stages),
                status=random.choice(statuses),
                artist=artist,
                duration_frame=random.randint(50, 300),
                deadline=deadline,
                last_submit_date=last_submit_date,
                description=f"测试镜头 {shot_num} 描述",
                metadata={
                    'test_data': True,
                    'created_at': str(timezone.now()),
                }
            )
            total_created += 1
    
    return total_created

if __name__ == "__main__":
    print("开始创建测试数据...")
    
    # 获取或创建动画部门用户
    artists = get_or_create_animator_users()
    print(f"找到艺术家: {[a.username for a in artists]}")
    
    # 创建项目
    projects = create_test_projects()
    
    # 创建镜头
    total_shots = create_test_shots(projects, artists)
    
    print(f"创建完成！总共创建了 {len(projects)} 个项目和 {total_shots} 个镜头") 