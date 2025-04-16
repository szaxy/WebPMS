from django.core.management.base import BaseCommand
from django.utils import timezone
from projects.models import Project, ProjectDepartment
import random
from datetime import timedelta

class Command(BaseCommand):
    help = '创建10个特定项目数据'

    def handle(self, *args, **options):
        # 当前日期
        today = timezone.now().date()
        
        # 特定项目信息
        projects_data = [
            {"code": "DEMO001", "name": "演示项目01", "status": "in_progress", "departments": ["animation", "post"]},
            {"code": "DEMO002", "name": "演示项目02", "status": "in_progress", "departments": ["fx", "model"]},
            {"code": "DEMO003", "name": "演示项目03", "status": "paused", "departments": ["producer"]},
            {"code": "DEMO004", "name": "演示项目04", "status": "archived", "departments": ["animation", "post", "fx"]},
            {"code": "DEMO005", "name": "演示项目05", "status": "in_progress", "departments": ["model", "animation"]},
            {"code": "DEMO006", "name": "演示项目06", "status": "paused", "departments": ["post"]},
            {"code": "DEMO007", "name": "演示项目07", "status": "in_progress", "departments": ["producer", "fx"]},
            {"code": "DEMO008", "name": "演示项目08", "status": "archived", "departments": ["model"]},
            {"code": "DEMO009", "name": "演示项目09", "status": "in_progress", "departments": ["animation"]},
            {"code": "DEMO010", "name": "演示项目10", "status": "paused", "departments": ["post", "producer"]}
        ]
        
        # 计数器
        created_count = 0
        
        # 创建项目
        for project_data in projects_data:
            code = project_data["code"]
            name = project_data["name"]
            status = project_data["status"]
            departments = project_data["departments"]
            
            # 检查项目是否已存在
            if Project.objects.filter(code=code).exists():
                self.stdout.write(f"项目 {code} 已存在，跳过")
                continue
            
            # 随机日期
            start_date = today - timedelta(days=random.randint(10, 100))
            end_date = None
            if random.random() > 0.3:  # 70%的项目有结束日期
                end_date = start_date + timedelta(days=random.randint(30, 120))
            
            # 创建项目描述
            description = f"这是演示项目 {code}，用于展示如何创建和管理项目。"
            
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
                
                # 添加部门关联
                for dept in departments:
                    ProjectDepartment.objects.create(
                        project=project,
                        department=dept
                    )
                
                created_count += 1
                self.stdout.write(f"创建项目: {code} ({status}, 关联部门: {', '.join(departments)})")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"创建项目 {code} 失败: {str(e)}"))
        
        # 输出结果
        self.stdout.write(self.style.SUCCESS(f'成功创建 {created_count} 个演示项目')) 