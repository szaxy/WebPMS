import os
import django
import random
from datetime import date, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from projects.models import Project
from shots.models import Shot
from users.models import User

def create_test_projects():
    """创建测试项目"""
    project_data = [
        {
            'name': '荷和年动画项目',
            'code': 'HHN-01',
            'status': 'active',
            'start_date': date.today() - timedelta(days=30),
            'end_date': date.today() + timedelta(days=180),
            'description': '荷和年首个动画项目，包含多个角色和场景。'
        },
        {
            'name': '森林奇缘',
            'code': 'SLQ-02',
            'status': 'active',
            'start_date': date.today() - timedelta(days=60),
            'end_date': date.today() + timedelta(days=90),
            'description': '森林主题的动画短片项目。'
        },
        {
            'name': '星空冒险',
            'code': 'XKMX-03',
            'status': 'planning',
            'start_date': date.today() + timedelta(days=30),
            'end_date': date.today() + timedelta(days=240),
            'description': '太空探险主题的科幻动画项目。'
        }
    ]
    
    created_projects = []
    for data in project_data:
        project, created = Project.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        if created:
            print(f"创建项目: {project.name}")
        else:
            print(f"项目已存在: {project.name}")
        created_projects.append(project)
    
    return created_projects

def create_test_shots(projects):
    """为项目创建测试镜头"""
    statuses = ['in_progress', 'review', 'approved', 'need_revision']
    
    # 获取制作者用户
    artists = list(User.objects.filter(role='artist'))
    if not artists:
        # 如果没有艺术家用户，使用管理员
        artists = list(User.objects.filter(role='admin'))
    
    # 为每个项目创建镜头
    for project in projects:
        # 创建动画部门镜头
        for i in range(1, 11):
            shot_code = f"DH_{i:03d}"
            status = random.choice(statuses)
            
            shot, created = Shot.objects.get_or_create(
                project=project,
                shot_code=shot_code,
                defaults={
                    'status': status,
                    'prom_stage': random.choice(['layout', 'blocking', 'animation', 'lighting']),
                    'deadline': date.today() + timedelta(days=random.randint(10, 60)),
                    'duration_frame': random.randint(50, 300),
                    'description': f"{project.name}的{shot_code}镜头，动画部门负责。",
                    'artist': random.choice(artists) if artists else None
                }
            )
            
            if created:
                print(f"创建镜头: {project.code} - {shot_code}")
        
        # 创建解算部门镜头
        for i in range(1, 6):
            shot_code = f"JS_{i:03d}"
            status = random.choice(statuses)
            
            shot, created = Shot.objects.get_or_create(
                project=project,
                shot_code=shot_code,
                defaults={
                    'status': status,
                    'prom_stage': random.choice(['simulation', 'effects', 'cloth']),
                    'deadline': date.today() + timedelta(days=random.randint(10, 60)),
                    'duration_frame': random.randint(50, 300),
                    'description': f"{project.name}的{shot_code}镜头，解算部门负责。",
                    'artist': random.choice(artists) if artists else None
                }
            )
            
            if created:
                print(f"创建镜头: {project.code} - {shot_code}")
        
        # 创建后期部门镜头
        for i in range(1, 8):
            shot_code = f"HQ_{i:03d}"
            status = random.choice(statuses)
            
            shot, created = Shot.objects.get_or_create(
                project=project,
                shot_code=shot_code,
                defaults={
                    'status': status,
                    'prom_stage': random.choice(['compositing', 'grading', 'final']),
                    'deadline': date.today() + timedelta(days=random.randint(10, 60)),
                    'duration_frame': random.randint(50, 300),
                    'description': f"{project.name}的{shot_code}镜头，后期部门负责。",
                    'artist': random.choice(artists) if artists else None
                }
            )
            
            if created:
                print(f"创建镜头: {project.code} - {shot_code}")

if __name__ == "__main__":
    print("开始创建测试数据...")
    projects = create_test_projects()
    create_test_shots(projects)
    print("测试数据创建完成!") 