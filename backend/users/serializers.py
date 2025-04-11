from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器，用于API数据交换"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'device_code', 'first_name', 'last_name',
            'role', 'department', 'cgtw_id', 'avatar',
            'is_active', 'date_joined', 'last_login',
            'registration_status', 'approval_date', 'registration_notes'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'approval_date']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class UserListSerializer(serializers.ModelSerializer):
    """用户列表序列化器，用于列表显示，包含较少字段"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'device_code', 'role', 
            'department', 'avatar', 'is_active',
            'registration_status'
        ]

class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器，用于新用户注册"""
    
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'device_code', 'password', 'password2', 
            'first_name', 'last_name', 'role', 'department',
            'registration_notes'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({"password": "两次输入的密码不匹配"})
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            device_code=validated_data.get('device_code', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'artist'),
            department=validated_data.get('department'),
            registration_notes=validated_data.get('registration_notes', '')
        )
        return user

class UserApprovalSerializer(serializers.ModelSerializer):
    """用户审批序列化器，用于管理员审核用户注册"""
    
    class Meta:
        model = User
        fields = ['registration_status', 'registration_notes']
    
    def update(self, instance, validated_data):
        instance.registration_status = validated_data.get('registration_status', instance.registration_status)
        instance.registration_notes = validated_data.get('registration_notes', instance.registration_notes)
        
        if instance.registration_status == 'approved':
            instance.approved_by = self.context['request'].user
            instance.approval_date = timezone.now()
        
        instance.save()
        return instance

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """自定义Token序列化器，在Token中添加用户信息"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # 添加自定义声明
        token['username'] = user.username
        token['device_code'] = user.device_code
        token['role'] = user.role
        token['department'] = user.department
        token['is_approved'] = user.is_approved
        
        return token
        
    def validate(self, attrs):
        # 首先使用父类的验证方法获取token
        data = super().validate(attrs)
        
        # 检查用户是否已经通过审核
        user = self.user
        if not user.is_approved and not user.is_admin:
            raise serializers.ValidationError(
                {"detail": "您的账号尚未通过审核，请联系管理员。"}
            )
            
        return data 