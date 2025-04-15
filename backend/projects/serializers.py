from rest_framework import serializers
from .models import Project, ProjectDepartment
import re

class ProjectDepartmentSerializer(serializers.ModelSerializer):
    """项目部门关联序列化器"""
    
    department_display = serializers.CharField(source='get_department_display', read_only=True)
    
    class Meta:
        model = ProjectDepartment
        fields = ['id', 'department', 'department_display']
        
class ProjectSerializer(serializers.ModelSerializer):
    """项目序列化器，用于API数据交换"""
    
    departments = ProjectDepartmentSerializer(source='project_departments', many=True, read_only=True)
    department_ids = serializers.ListField(
        child=serializers.CharField(), 
        write_only=True, 
        required=True,
        error_messages={'required': '请至少选择一个部门'}
    )
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'code', 'status', 'start_date',
            'recsubmit_date', 'end_date', 'description',
            'cgtw_project_id', 'created_at', 'updated_at',
            'departments', 'department_ids'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_start_date(self, value):
        """验证开始日期，允许为空"""
        # 如果日期为空，直接返回None
        if value is None or value == '':
            return None
        return value
    
    def validate_end_date(self, value):
        """验证结束日期，允许为空"""
        # 如果日期为空，直接返回None
        if value is None or value == '':
            return None
        return value
    
    def validate_code(self, value):
        """
        验证项目代号格式是否符合规范
        规范：2-10个字符，只允许字母、数字和连字符，必须以字母开头
        """
        # 检查长度
        if len(value) < 2 or len(value) > 10:
            raise serializers.ValidationError("项目代号长度必须在2-10个字符之间")
        
        # 检查格式：字母开头，只允许字母、数字和连字符
        if not re.match(r'^[A-Za-z][A-Za-z0-9\-]*$', value):
            raise serializers.ValidationError("项目代号必须以字母开头，只允许包含字母、数字和连字符")
        
        # 检查项目代号唯一性（创建时）
        if self.instance is None or self.instance.code != value:
            if Project.objects.filter(code=value).exists():
                raise serializers.ValidationError("项目代号已被使用")
                
        return value
    
    def create(self, validated_data):
        departments = validated_data.pop('department_ids', [])
        project = Project.objects.create(**validated_data)
        
        # 创建项目部门关联
        for department in departments:
            ProjectDepartment.objects.create(project=project, department=department)
            
        return project
    
    def update(self, instance, validated_data):
        departments = validated_data.pop('department_ids', None)
        
        # 更新项目基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 如果提供了部门信息，则更新部门关联
        if departments is not None:
            # 删除现有关联
            instance.project_departments.all().delete()
            
            # 创建新的关联
            for department in departments:
                ProjectDepartment.objects.create(project=instance, department=department)
        
        return instance

class ProjectListSerializer(serializers.ModelSerializer):
    """项目列表序列化器，用于列表显示，包含较少字段"""
    
    departments = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'code', 'status', 
            'start_date', 'end_date', 'updated_at',
            'departments'
        ]
    
    def get_departments(self, obj):
        """获取项目关联的部门列表"""
        return [
            {
                'department': dept.department,
                'department_display': dept.get_department_display()
            }
            for dept in obj.project_departments.all()
        ] 