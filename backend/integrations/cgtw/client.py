import os
import json
import requests
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CGTWClient:
    """CGTeamwork API客户端封装"""
    
    def __init__(self):
        self.api_url = settings.CGTW_API_URL
        self.username = settings.CGTW_USERNAME
        self.password = settings.CGTW_PASSWORD
        self.token = None
        
    def _get_token(self):
        """获取CGTeamwork API访问令牌"""
        if self.token:
            return self.token
            
        try:
            url = f"{self.api_url}/api/login"
            data = {
                "username": self.username,
                "password": self.password
            }
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('status') == 'success':
                self.token = result.get('data', {}).get('token')
                return self.token
            else:
                logger.error(f"CGTeamwork登录失败: {result.get('message')}")
                return None
        except Exception as e:
            logger.error(f"CGTeamwork登录异常: {str(e)}")
            return None
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """发送请求到CGTeamwork API"""
        token = self._get_token()
        if not token:
            raise Exception("无法获取CGTeamwork API访问令牌")
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.api_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
                
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"CGTeamwork API请求失败: {str(e)}")
            raise
    
    def get_projects(self, filters=None):
        """获取项目列表"""
        params = {"filters": json.dumps(filters)} if filters else {}
        return self._make_request('GET', '/api/projects', params=params)
    
    def get_shots(self, filters=None):
        """获取镜头列表"""
        params = {"filters": json.dumps(filters)} if filters else {}
        return self._make_request('GET', '/api/shots', params=params)
    
    def get_users(self, filters=None):
        """获取用户列表"""
        params = {"filters": json.dumps(filters)} if filters else {}
        return self._make_request('GET', '/api/users', params=params)
        
    def update_shot_status(self, shot_id, status):
        """更新镜头状态"""
        data = {"status": status}
        return self._make_request('PUT', f'/api/shots/{shot_id}', data=data) 