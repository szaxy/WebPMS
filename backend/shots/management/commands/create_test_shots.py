from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from shots.models import Shot
from projects.models import Project
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = '创建测试镜头数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project',
            type=str,
            help='项目代号，如果不指定，将使用第一个可用项目'
        )
        
    def handle(self, *args, **options):
        # 检查项目
        project_code = options.get('project')
        
        if project_code:
            try:
                project = Project.objects.get(code=project_code)
            except Project.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'项目 "{project_code}" 不存在'))
                return
        else:
            try:
                project = Project.objects.first()
                if not project:
                    self.stdout.write(self.style.ERROR('没有可用的项目，请先创建一个项目'))
                    return
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'获取项目失败: {str(e)}'))
                return
        
        # 获取制作人员（按部门）
        animation_artists = list(User.objects.filter(department='animation', role='artist'))
        fx_artists = list(User.objects.filter(department='fx', role='artist'))
        post_artists = list(User.objects.filter(department='post', role='artist'))
        
        # 创建动画部门镜头
        self.create_department_shots(
            project, 
            'DH', 
            'DH_EP001_SC', 
            range(1, 11), 
            animation_artists
        )
        
        # 创建解算部门镜头
        self.create_department_shots(
            project, 
            'JS', 
            'JS_EP001_SC', 
            range(1, 11), 
            fx_artists
        )
        
        # 创建后期部门镜头
        self.create_department_shots(
            project, 
            'HQ', 
            'HQ_EP001_SC', 
            range(1, 11), 
            post_artists
        )
        
        self.stdout.write(self.style.SUCCESS('成功创建测试镜头数据'))
    
    def create_department_shots(self, project, dept_code, prefix, scene_range, artists):
        """创建指定部门的测试镜头"""
        today = timezone.now().date()
        
        # 可能的状态
        statuses = ['waiting', 'in_progress', 'submit_review', 'revising', 'internal_approved', 'client_review']
        
        # 可能的推进阶段
        stages = ['LAY', 'BLK', 'ANI', 'PASS']
        
        # 镜头数量计数
        count = 0
        
        # 为每个场景创建10个镜头
        for scene in scene_range:
            scene_code = f"{prefix}{str(scene).zfill(3)}"
            
            for shot_num in range(10, 101, 10):
                shot_code = f"{scene_code}_Shot{str(shot_num).zfill(4)}"
                
                # 随机选择状态和推进阶段
                status = random.choice(statuses)
                stage = random.choice(stages)
                
                # 随机选择制作人
                artist = random.choice(artists) if artists else None
                
                # 随机设置截止日期（当前日期的前后30天内）
                deadline = today + timedelta(days=random.randint(-15, 30))
                
                # 是否有提交日期？50%的概率
                last_submit_date = None
                if random.random() > 0.5:
                    last_submit_date = today - timedelta(days=random.randint(1, 10))
                
                # 帧数（60-300之间随机）
                duration_frame = random.randint(60, 300)
                
                # 创建镜头
                shot = Shot.objects.create(
                    project=project,
                    shot_code=shot_code,
                    department=dept_code,
                    prom_stage=stage,
                    status=status,
                    artist=artist,
                    deadline=deadline,
                    last_submit_date=last_submit_date,
                    duration_frame=duration_frame,
                    description=f"测试镜头 {shot_code}"
                )
                
                count += 1
                
                self.stdout.write(f"创建镜头: {shot_code} ({dept_code})")
        
        self.stdout.write(self.style.SUCCESS(f'部门 {dept_code} 创建了 {count} 个测试镜头')) 