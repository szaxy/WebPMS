from django.core.management.base import BaseCommand
from django.utils import timezone
from projects.models import Project, ProjectDepartment
import random
from datetime import timedelta

class Command(BaseCommand):
    help = '创建100个测试项目数据'

    def handle(self, *args, **options):
        # 可能的状态
        statuses = ['in_progress', 'paused', 'archived']
        status_weights = [0.6, 0.3, 0.1]  # 60%进行中, 30%已暂停, 10%已归档
        
        # 可能的部门
        departments = ['animation', 'post', 'fx', 'producer', 'model']
        
        # 当前日期
        today = timezone.now().date()
        
        # 计数器
        created_count = 0
        
        # 创建100个测试项目
        for i in range(1, 101):
            # 项目代号和名称
            code = f"CSXM{str(i).zfill(3)}"
            name = f"测试项目 {str(i).zfill(3)}"
            
            # 随机状态
            status = random.choices(statuses, weights=status_weights, k=1)[0]
            
            # 随机日期
            start_date = today - timedelta(days=random.randint(30, 365))
            end_date = None
            if random.random() > 0.3:  # 70%的项目有结束日期
                end_date = start_date + timedelta(days=random.randint(60, 300))
            
            # 随机描述
            description = f"这是测试项目 {code} 的描述内容，用于测试项目管理功能。"
            
            try:
                # 创建项目
                project = Project.objects.create(
                    name=name,
                    code=code,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                    description=description
                )
                
                # 随机关联1-3个部门
                dept_count = random.randint(1, 3)
                selected_depts = random.sample(departments, dept_count)
                
                for dept in selected_depts:
                    ProjectDepartment.objects.create(
                        project=project,
                        department=dept
                    )
                
                created_count += 1
                self.stdout.write(f"创建项目: {code} ({status}, 关联部门: {', '.join(selected_depts)})")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"创建项目 {code} 失败: {str(e)}"))
        
        # 输出结果
        self.stdout.write(self.style.SUCCESS(f'成功创建 {created_count} 个测试项目')) 