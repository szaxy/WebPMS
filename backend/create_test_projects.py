import os
import django
import random
from datetime import timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from projects.models import Project, ProjectDepartment

def create_test_projects():
    """创建100个测试项目"""
    # 可能的状态
    statuses = ['in_progress', 'paused', 'archived']
    status_weights = [0.6, 0.3, 0.1]  # 60%进行中, 30%已暂停, 10%已归档
    
    # 可能的部门
    departments = ['animation', 'post', 'fx', 'producer', 'model']
    
    # 当前日期
    today = timezone.now().date()
    
    # 计数器
    created_count = 0
    
    # 清理现有数据（可选，取消注释以启用）
    # existing_projects = Project.objects.filter(code__startswith='CSXM')
    # if existing_projects.exists():
    #     print(f"删除 {existing_projects.count()} 个现有测试项目...")
    #     existing_projects.delete()
    
    # 创建100个测试项目
    for i in range(1, 101):
        # 项目代号和名称
        code = f"CSXM{str(i).zfill(3)}"
        name = f"测试项目 {str(i).zfill(3)}"
        
        # 检查项目是否已存在
        if Project.objects.filter(code=code).exists():
            print(f"项目 {code} 已存在，跳过")
            continue
        
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
            print(f"创建项目: {code} ({status}, 关联部门: {', '.join(selected_depts)})")
            
        except Exception as e:
            print(f"创建项目 {code} 失败: {str(e)}")
    
    # 输出结果
    print(f'成功创建 {created_count} 个测试项目')
    
    # 统计各状态项目数量
    for status in statuses:
        count = Project.objects.filter(status=status).count()
        print(f"状态 '{status}' 的项目数量: {count}")
    
    # 总项目数
    total = Project.objects.count()
    print(f"数据库中总项目数: {total}")

if __name__ == "__main__":
    print("开始创建测试项目...")
    create_test_projects()
    print("测试项目创建完成。") 