from rest_framework import serializers
from .models import Project, ProjectDepartment

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
        required=False
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