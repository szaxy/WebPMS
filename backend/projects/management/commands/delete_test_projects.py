from django.core.management.base import BaseCommand
from projects.models import Project

class Command(BaseCommand):
    help = '删除测试项目数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prefix',
            type=str,
            default='CSXM',
            help='要删除的项目代号前缀，默认为CSXM'
        )
        parser.add_argument(
            '--demo',
            action='store_true',
            help='是否同时删除DEMO前缀的项目'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='删除所有项目（危险操作）'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制执行，不询问确认'
        )

    def handle(self, *args, **options):
        prefix = options['prefix']
        delete_demo = options['demo']
        delete_all = options['all']
        force = options['force']
        
        if delete_all:
            if not force:
                self.stdout.write(self.style.WARNING("警告：此操作将删除所有项目!"))
                confirm = input("确定要继续吗? (y/n): ")
                if confirm.lower() != 'y':
                    self.stdout.write(self.style.ERROR("操作已取消"))
                    return
                    
            count = Project.objects.all().count()
            Project.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"已删除所有 {count} 个项目"))
            return
            
        # 删除指定前缀的项目
        projects = Project.objects.filter(code__startswith=prefix)
        count = projects.count()
        
        if count == 0:
            self.stdout.write(f"未找到前缀为 {prefix} 的项目")
        else:
            if not force:
                self.stdout.write(self.style.WARNING(f"即将删除 {count} 个前缀为 {prefix} 的项目"))
                confirm = input("确定要继续吗? (y/n): ")
                if confirm.lower() != 'y':
                    self.stdout.write(self.style.ERROR("操作已取消"))
                    return
                    
            projects.delete()
            self.stdout.write(self.style.SUCCESS(f"已删除 {count} 个前缀为 {prefix} 的项目"))
        
        # 是否同时删除DEMO项目
        if delete_demo:
            demo_projects = Project.objects.filter(code__startswith='DEMO')
            demo_count = demo_projects.count()
            
            if demo_count == 0:
                self.stdout.write("未找到前缀为 DEMO 的项目")
            else:
                if not force and count == 0:  # 只有当之前没有删除任何项目时才询问
                    self.stdout.write(self.style.WARNING(f"即将删除 {demo_count} 个前缀为 DEMO 的项目"))
                    confirm = input("确定要继续吗? (y/n): ")
                    if confirm.lower() != 'y':
                        self.stdout.write(self.style.ERROR("操作已取消"))
                        return
                        
                demo_projects.delete()
                self.stdout.write(self.style.SUCCESS(f"已删除 {demo_count} 个前缀为 DEMO 的项目")) 