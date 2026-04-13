"""
权限管理服务
支持用户认证、权限检查、角色管理等功能
"""
import os
import json
import logging
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class RoleType(Enum):
    """角色类型"""
    ADMIN = 'admin'  # 管理员
    USER = 'user'    # 普通用户
    GUEST = 'guest'  # 访客


class PermissionType(Enum):
    """权限类型"""
    # 系统级权限
    SYSTEM_MANAGE = 'system:manage'           # 系统管理
    USER_MANAGE = 'user:manage'               # 用户管理
    ROLE_MANAGE = 'role:manage'               # 角色管理
    
    # 配置权限
    CONFIG_VIEW = 'config:view'               # 查看配置
    CONFIG_EDIT = 'config:edit'               # 编辑配置
    CONFIG_IMPORT_EXPORT = 'config:import_export'  # 导入导出配置
    
    # Skill 权限
    SKILL_VIEW = 'skill:view'                 # 查看技能
    SKILL_CREATE = 'skill:create'             # 创建技能
    SKILL_EDIT = 'skill:edit'                 # 编辑技能
    SKILL_PUBLISH = 'skill:publish'           # 发布技能
    
    # 任务权限
    TASK_VIEW = 'task:view'                 # 查看任务
    TASK_CREATE = 'task:create'             # 创建任务
    TASK_EDIT = 'task:edit'                 # 编辑任务
    TASK_DELETE = 'task:delete'             # 删除任务
    
    # 系统集成权限
    INTEGRATION_VIEW = 'integration:view'     # 查看系统集成
    INTEGRATION_EDIT = 'integration:edit'     # 编辑系统集成
    
    # WPS 集成权限
    WPS_ACCESS = 'wps:access'               # 访问 WPS 集成
    WPS_EDIT = 'wps:edit'                   # 编辑 WPS 文档
    
    # 文件检索权限
    FILE_RETRIEVAL = 'file:retrieval'         # 文件检索
    FILE_ACCESS = 'file:access'             # 文件访问


class User:
    """用户类"""
    
    def __init__(self, user_id: str, username: str, password_hash: str, role: RoleType):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_login = None
    
    def check_password(self, password: str) -> bool:
        """检查密码"""
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return self.password_hash == hashed
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建"""
        user = cls(
            data['user_id'],
            data['username'],
            data['password_hash'],
            RoleType(data['role'])
        )
        user.created_at = datetime.fromisoformat(data['created_at'])
        user.updated_at = datetime.fromisoformat(data['updated_at'])
        if data.get('last_login'):
            user.last_login = datetime.fromisoformat(data['last_login'])
        return user


class Role:
    """角色类"""
    
    def __init__(self, role_type: RoleType, permissions: List[PermissionType]):
        self.role_type = role_type
        self.permissions = permissions
    
    def has_permission(self, permission: PermissionType) -> bool:
        """检查是否有指定权限"""
        return permission in self.permissions
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'role_type': self.role_type.value,
            'permissions': [p.value for p in self.permissions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Role':
        """从字典创建"""
        permissions = [PermissionType(p) for p in data['permissions']]
        return cls(RoleType(data['role_type']), permissions)


class PermissionService:
    """权限管理服务"""
    
    def __init__(self, storage_path: str = 'backend/data/security'):
        self.storage_path = storage_path
        self.users: Dict[str, User] = {}
        self.roles: Dict[RoleType, Role] = {}
        self._ensure_storage_dir()
        self._load_roles()
        self._load_users()
        self._init_default_roles()
        self._init_default_users()
    
    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _init_default_roles(self):
        """初始化默认角色"""
        # 管理员角色
        admin_permissions = [p for p in PermissionType]
        admin_role = Role(RoleType.ADMIN, admin_permissions)
        self.roles[RoleType.ADMIN] = admin_role
        
        # 普通用户角色
        user_permissions = [
            PermissionType.CONFIG_VIEW,
            PermissionType.SKILL_VIEW,
            PermissionType.SKILL_CREATE,
            PermissionType.TASK_VIEW,
            PermissionType.TASK_CREATE,
            PermissionType.TASK_EDIT,
            PermissionType.INTEGRATION_VIEW,
            PermissionType.WPS_ACCESS,
            PermissionType.FILE_RETRIEVAL,
            PermissionType.FILE_ACCESS
        ]
        user_role = Role(RoleType.USER, user_permissions)
        self.roles[RoleType.USER] = user_role
        
        # 访客角色
        guest_permissions = [
            PermissionType.SKILL_VIEW,
            PermissionType.TASK_VIEW
        ]
        guest_role = Role(RoleType.GUEST, guest_permissions)
        self.roles[RoleType.GUEST] = guest_role
        
        self._save_roles()
    
    def _init_default_users(self):
        """初始化默认用户"""
        # 管理员用户
        if 'admin' not in self.users:
            admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
            admin = User('admin', 'admin', admin_password, RoleType.ADMIN)
            self.users['admin'] = admin
        
        # 测试用户
        if 'test' not in self.users:
            test_password = hashlib.sha256('test123'.encode()).hexdigest()
            test_user = User('test', 'test', test_password, RoleType.USER)
            self.users['test'] = test_user
        
        self._save_users()
    
    def _load_roles(self):
        """加载角色"""
        roles_path = os.path.join(self.storage_path, 'roles.json')
        if os.path.exists(roles_path):
            try:
                with open(roles_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for role_data in data:
                        role = Role.from_dict(role_data)
                        self.roles[role.role_type] = role
            except Exception as e:
                logger.error(f"加载角色失败: {str(e)}")
    
    def _save_roles(self):
        """保存角色"""
        roles_path = os.path.join(self.storage_path, 'roles.json')
        try:
            with open(roles_path, 'w', encoding='utf-8') as f:
                roles_data = [role.to_dict() for role in self.roles.values()]
                json.dump(roles_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存角色失败: {str(e)}")
    
    def _load_users(self):
        """加载用户"""
        users_path = os.path.join(self.storage_path, 'users.json')
        if os.path.exists(users_path):
            try:
                with open(users_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_data in data:
                        user = User.from_dict(user_data)
                        self.users[user.user_id] = user
            except Exception as e:
                logger.error(f"加载用户失败: {str(e)}")
    
    def _save_users(self):
        """保存用户"""
        users_path = os.path.join(self.storage_path, 'users.json')
        try:
            with open(users_path, 'w', encoding='utf-8') as f:
                users_data = [user.to_dict() for user in self.users.values()]
                json.dump(users_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存用户失败: {str(e)}")
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        for user in self.users.values():
            if user.username == username and user.check_password(password):
                user.last_login = datetime.now()
                user.updated_at = datetime.now()
                self._save_users()
                logger.info(f"用户登录成功: {username}")
                return user
        logger.warning(f"用户登录失败: {username}")
        return None
    
    def check_permission(self, user_id: str, permission: PermissionType) -> bool:
        """检查用户是否有指定权限"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        role = self.roles.get(user.role)
        if not role:
            return False
        
        return role.has_permission(permission)
    
    def get_user_roles(self, user_id: str) -> Optional[RoleType]:
        """获取用户角色"""
        user = self.users.get(user_id)
        if user:
            return user.role
        return None
    
    def create_user(self, username: str, password: str, role: RoleType) -> User:
        """创建用户"""
        user_id = f"user_{len(self.users) + 1}"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = User(user_id, username, password_hash, role)
        self.users[user_id] = user
        self._save_users()
        logger.info(f"创建用户: {username}")
        return user
    
    def update_user_role(self, user_id: str, role: RoleType) -> bool:
        """更新用户角色"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        user.role = role
        user.updated_at = datetime.now()
        self._save_users()
        logger.info(f"更新用户角色: {user_id} -> {role.value}")
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        if user_id in self.users:
            del self.users[user_id]
            self._save_users()
            logger.info(f"删除用户: {user_id}")
            return True
        return False
    
    def list_users(self) -> List[Dict[str, Any]]:
        """列出所有用户"""
        return [user.to_dict() for user in self.users.values()]
    
    def list_roles(self) -> List[Dict[str, Any]]:
        """列出所有角色"""
        return [role.to_dict() for role in self.roles.values()]
    
    def update_role_permissions(self, role_type: RoleType, permissions: List[PermissionType]) -> bool:
        """更新角色权限"""
        if role_type not in self.roles:
            return False
        
        role = self.roles[role_type]
        role.permissions = permissions
        self._save_roles()
        logger.info(f"更新角色权限: {role_type.value}")
        return True


# 全局权限管理服务实例
permission_service = PermissionService()


def init_permission_service() -> PermissionService:
    """初始化权限管理服务"""
    global permission_service
    return permission_service
