import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from projects.models import Project
from shots.models import Shot, ShotNote
from comments.models import Comment

User = get_user_model()

class Command(BaseCommand):
    help = '创建测试镜头数据'
    
    def add_arguments(self, parser):
        parser.add_argument('--project', type=str, help='项目代号')
        parser.add_argument('--count', type=int, default=100, help='每个部门创建的镜头数量')
        
    def handle(self, *args, **options):
        project_code = options.get('project')
        count = options.get('count')
        
        if not project_code:
            # 获取第一个项目
            project = Project.objects.first()
            if not project:
                self.stdout.write(self.style.ERROR('没有找到项目，请先创建项目'))
                return
        else:
            try:
                project = Project.objects.get(code=project_code)
            except Project.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'项目 {project_code} 不存在'))
                return
        
        self.stdout.write(f'开始为项目 {project.code} 创建测试镜头...')
        
        # 获取或创建部门用户
        users = self._get_or_create_department_users()
        
        # 创建三个部门的镜头
        with transaction.atomic():
            # 动画部门镜头
            self._create_department_shots(
                project, 'DH_EP001_SC', count, 
                users.get('animation', []), 
                users.get('all', [])
            )
            
            # 解算部门镜头
            self._create_department_shots(
                project, 'JS_EP001_SC', count, 
                users.get('fx', []), 
                users.get('all', [])
            )
            
            # 后期部门镜头
            self._create_department_shots(
                project, 'HQ_EP001_SC', count, 
                users.get('post', []), 
                users.get('all', [])
            )
        
        self.stdout.write(self.style.SUCCESS(f'成功创建 {count * 3} 个测试镜头'))
    
    def _get_or_create_department_users(self):
        """获取或创建各部门的用户"""
        # 获取现有用户并按部门分组
        users_by_dept = {
            'animation': list(User.objects.filter(department='animation')),
            'fx': list(User.objects.filter(department='fx')),
            'post': list(User.objects.filter(department='post')),
            'producer': list(User.objects.filter(department='producer')),
            'admin': list(User.objects.filter(role='admin'))
        }
        
        # 合并管理员和制片部门的用户
        users_by_dept['all'] = users_by_dept['admin'] + users_by_dept['producer']
        
        # 如果某个部门没有用户，创建测试用户
        if not users_by_dept['animation']:
            user = User.objects.create_user(
                username='animation_user',
                password='password',
                department='animation',
                role='artist',
                registration_status='approved'
            )
            users_by_dept['animation'].append(user)
            
        if not users_by_dept['fx']:
            user = User.objects.create_user(
                username='fx_user',
                password='password',
                department='fx',
                role='artist',
                registration_status='approved'
            )
            users_by_dept['fx'].append(user)
            
        if not users_by_dept['post']:
            user = User.objects.create_user(
                username='post_user',
                password='password',
                department='post',
                role='artist',
                registration_status='approved'
            )
            users_by_dept['post'].append(user)
        
        if not users_by_dept['producer']:
            user = User.objects.create_user(
                username='producer_user',
                password='password',
                department='producer',
                role='producer',
                registration_status='approved'
            )
            users_by_dept['producer'].append(user)
            users_by_dept['all'].append(user)
            
        if not users_by_dept['admin']:
            user = User.objects.create_user(
                username='admin_user',
                password='password',
                role='admin',
                registration_status='approved'
            )
            users_by_dept['admin'].append(user)
            users_by_dept['all'].append(user)
        
        return users_by_dept
    
    def _create_department_shots(self, project, prefix, count, department_users, admin_users):
        """为指定部门创建测试镜头"""
        if not department_users:
            self.stdout.write(self.style.WARNING(f'没有 {prefix} 部门的用户，跳过创建镜头'))
            return
        
        # 状态列表
        statuses = ['in_progress', 'review', 'approved', 'need_revision']
        # 推进阶段列表
        stages = ['layout', 'animation', 'lighting', 'rendering']
        
        # 当前日期
        now = timezone.now().date()
        
        shots = []
        # 创建镜头
        for i in range(1, count + 1):
            # 镜头编号, 如: DH_EP001_SC001_Shot0010
            shot_num = i * 10
            shot_code = f"{prefix}{shot_num//100:03d}_Shot{shot_num:04d}"
            
            # 随机选择状态、推进阶段和制作者
            status = random.choice(statuses)
            artist = random.choice(department_users)
            
            # 生成随机的截止日期（当前日期前后15天内）
            days_delta = random.randint(-15, 15)
            deadline = now + timedelta(days=days_delta)
            
            # 随机决定是否有最近提交日期
            last_submit_date = None
            if random.random() > 0.3:  # 70%几率有提交日期
                submit_days = random.randint(-10, 5)
                last_submit_date = now + timedelta(days=submit_days)
            
            # 创建镜头
            shot = Shot(
                project=project,
                shot_code=shot_code,
                prom_stage=random.choice(stages),
                status=status,
                deadline=deadline,
                last_submit_date=last_submit_date,
                artist=artist,
                duration_frame=random.randint(24, 240)
            )
            shots.append(shot)
        
        # 批量创建镜头
        Shot.objects.bulk_create(shots)
        
        # 为一些镜头添加备注和反馈
        created_shots = Shot.objects.filter(project=project, shot_code__startswith=prefix)
        
        # 约20%的镜头添加重要备注
        for shot in random.sample(list(created_shots), int(count * 0.2)):
            ShotNote.objects.create(
                shot=shot,
                user=random.choice(department_users),
                content=f"重要备注：{shot.shot_code} 需要特别注意光照效果",
                is_important=True
            )
        
        # 约30%的镜头添加一般备注
        for shot in random.sample(list(created_shots), int(count * 0.3)):
            ShotNote.objects.create(
                shot=shot,
                user=random.choice(department_users),
                content=f"{shot.shot_code} 制作中的注意事项",
                is_important=False
            )
        
        # 约40%的镜头添加反馈
        for shot in random.sample(list(created_shots), int(count * 0.4)):
            # 添加1-3条反馈
            for _ in range(random.randint(1, 3)):
                Comment.objects.create(
                    shot=shot,
                    user=random.choice(admin_users),
                    content=f"{shot.shot_code} 的反馈：{random.choice(['动画效果需要调整', '角色表情不够生动', '场景光照有问题'])}"
                ) 