from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
from .client import CGTWClient
from .models import SyncLog
from projects.models import Project
from shots.models import Shot
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()
logger = logging.getLogger(__name__)

def send_sync_error_notification(error_message):
    """发送同步错误通知邮件"""
    if not settings.EMAIL_HOST_USER:
        logger.warning("未配置邮件发送账号，跳过发送同步错误通知")
        return
        
    subject = "CGTeamwork同步失败通知"
    message = f"同步CGTeamwork数据时发生错误：\n\n{error_message}\n\n请检查系统日志获取详细信息。"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = User.objects.filter(role='admin').values_list('email', flat=True)
    
    if recipient_list:
        try:
            send_mail(subject, message, from_email, recipient_list)
            logger.info(f"已发送同步错误通知到: {', '.join(recipient_list)}")
        except Exception as e:
            logger.error(f"发送同步错误通知邮件失败: {str(e)}")
    else:
        logger.warning("没有找到管理员用户，跳过发送同步错误通知")

@shared_task(bind=True, max_retries=3)
def sync_projects_from_cgtw(self):
    """同步项目数据任务"""
    try:
        # 创建同步日志
        sync_log = SyncLog.objects.create(
            sync_type='projects',
            status='in_progress'
        )
        
        # 从CGTeamwork获取数据
        cgtw_client = CGTWClient()
        projects_data = cgtw_client.get_projects()
        
        # 同步数据
        synced_count = 0
        for project_data in projects_data.get('data', []):
            project, created = Project.objects.update_or_create(
                cgtw_project_id=project_data['id'],
                defaults={
                    'name': project_data['name'],
                    'code': project_data['code'],
                    'status': map_project_status(project_data['status']),
                    'start_date': parse_date(project_data.get('start_date')),
                    'end_date': parse_date(project_data.get('end_date')),
                    'description': project_data.get('description')
                }
            )
            synced_count += 1
            
        # 更新同步日志
        sync_log.end_time = timezone.now()
        sync_log.status = 'success'
        sync_log.items_synced = synced_count
        sync_log.save()
        
        logger.info(f"成功同步 {synced_count} 个项目")
        return f"成功同步 {synced_count} 个项目"
        
    except Exception as e:
        # 记录错误并重试
        if sync_log:
            sync_log.status = 'failed'
            sync_log.error_message = str(e)
            sync_log.end_time = timezone.now()
            sync_log.save()
        
        # 发送邮件通知
        send_sync_error_notification(str(e))
        
        logger.error(f"同步项目数据失败: {str(e)}")
        # 重试任务
        raise self.retry(exc=e, countdown=60*5)  # 5分钟后重试

@shared_task(bind=True, max_retries=3)
def sync_shots_from_cgtw(self, project_id=None):
    """同步镜头数据任务"""
    try:
        # 获取上次同步时间
        last_sync = SyncLog.objects.filter(
            sync_type='shots', 
            status='success'
        ).order_by('-end_time').first()
        
        last_sync_time = last_sync.end_time if last_sync else None
        
        # 创建同步日志
        sync_log = SyncLog.objects.create(
            sync_type='shots',
            status='in_progress'
        )
        
        # 从CGTeamwork获取数据
        cgtw_client = CGTWClient()
        filters = {}
        
        # 如果有上次同步时间，只获取更新的数据
        if last_sync_time:
            # 将datetime转换为CGTeamwork支持的时间格式
            filters['update_time'] = {'$gt': last_sync_time.strftime('%Y-%m-%dT%H:%M:%S')}
            
        # 如果指定了项目ID，只同步该项目的镜头
        if project_id:
            filters['project_id'] = project_id
            
        shots_data = cgtw_client.get_shots(filters)
        
        # 同步数据
        synced_count = 0
        for shot_data in shots_data.get('data', []):
            try:
                project = Project.objects.get(cgtw_project_id=shot_data['project_id'])
                
                shot, created = Shot.objects.update_or_create(
                    cgtw_task_id=shot_data['id'],
                    defaults={
                        'project': project,
                        'shot_code': shot_data['code'],
                        'status': map_shot_status(shot_data['status']),
                        'deadline': parse_date(shot_data.get('deadline')),
                        'duration_frame': shot_data.get('duration_frame'),
                        'description': shot_data.get('description'),
                        'metadata': shot_data
                    }
                )
                synced_count += 1
            except Project.DoesNotExist:
                logger.warning(f"同步镜头时找不到对应的项目: {shot_data['project_id']}")
                continue
            
        # 更新同步日志
        sync_log.end_time = timezone.now()
        sync_log.status = 'success'
        sync_log.items_synced = synced_count
        sync_log.save()
        
        logger.info(f"成功同步 {synced_count} 个镜头")
        return f"成功同步 {synced_count} 个镜头"
        
    except Exception as e:
        # 记录错误并重试
        if sync_log:
            sync_log.status = 'failed'
            sync_log.error_message = str(e)
            sync_log.end_time = timezone.now()
            sync_log.save()
        
        # 发送邮件通知
        send_sync_error_notification(str(e))
        
        logger.error(f"同步镜头数据失败: {str(e)}")
        # 重试任务
        raise self.retry(exc=e, countdown=60*5)  # 5分钟后重试

@shared_task(bind=True, max_retries=3)
def sync_users_from_cgtw(self):
    """同步用户数据任务"""
    try:
        # 创建同步日志
        sync_log = SyncLog.objects.create(
            sync_type='users',
            status='in_progress'
        )
        
        # 从CGTeamwork获取数据
        cgtw_client = CGTWClient()
        users_data = cgtw_client.get_users()
        
        # 同步数据
        synced_count = 0
        for user_data in users_data.get('data', []):
            # 仅同步激活状态的用户
            if user_data.get('status') != 'active':
                continue
                
            user, created = User.objects.update_or_create(
                cgtw_id=user_data['id'],
                defaults={
                    'username': user_data['username'],
                    'email': user_data.get('email', ''),
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'department': map_department(user_data.get('department')),
                    # 如果是新创建的用户，设置一个随机密码
                    **({"is_active": True} if created else {})
                }
            )
            
            if created:
                # 为新用户生成随机密码
                password = User.objects.make_random_password()
                user.set_password(password)
                user.save()
                
                # 可以在这里发送包含初始密码的邮件给用户
                
            synced_count += 1
            
        # 更新同步日志
        sync_log.end_time = timezone.now()
        sync_log.status = 'success'
        sync_log.items_synced = synced_count
        sync_log.save()
        
        logger.info(f"成功同步 {synced_count} 个用户")
        return f"成功同步 {synced_count} 个用户"
        
    except Exception as e:
        # 记录错误并重试
        if sync_log:
            sync_log.status = 'failed'
            sync_log.error_message = str(e)
            sync_log.end_time = timezone.now()
            sync_log.save()
        
        # 发送邮件通知
        send_sync_error_notification(str(e))
        
        logger.error(f"同步用户数据失败: {str(e)}")
        # 重试任务
        raise self.retry(exc=e, countdown=60*5)  # 5分钟后重试

# 工具函数

def parse_date(date_str):
    """解析日期字符串为日期对象"""
    if not date_str:
        return None
    try:
        return timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        logger.warning(f"无法解析日期字符串: {date_str}")
        return None

def map_project_status(cgtw_status):
    """将CGTeamwork项目状态映射为系统状态"""
    status_map = {
        'active': 'in_progress',
        'pause': 'paused',
        'done': 'archived',
    }
    return status_map.get(cgtw_status, 'in_progress')

def map_shot_status(cgtw_status):
    """将CGTeamwork镜头状态映射为系统状态"""
    status_map = {
        'in_progress': 'in_progress',
        'wait_review': 'review',
        'approved': 'approved',
        'feedback': 'need_revision',
    }
    return status_map.get(cgtw_status, 'in_progress')

def map_department(cgtw_department):
    """将CGTeamwork部门映射为系统部门"""
    department_map = {
        'animation': 'animation',
        'post': 'post',
        'fx': 'fx',
        'producer': 'producer',
    }
    return department_map.get(cgtw_department, None) 