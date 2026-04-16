"""
系统功能技能
负责处理系统级别的功能，如权限管理、任务管理、配置管理等
"""
from backend.skills.base_skill import BaseSkill
from typing import Dict, Any, List
import logging
import requests

logger = logging.getLogger(__name__)


class SystemSkill(BaseSkill):
    """系统功能技能"""
    
    def __init__(self):
        super().__init__(
            skill_id='system_skill',
            name='系统功能',
            description='处理系统级别的功能，如权限管理、任务管理、配置管理等'
        )
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行系统功能
        
        Args:
            params: 输入参数字典，包含：
                - action: 操作类型
                - intent: 意图类型
                - 其他参数
        
        Returns:
            执行结果
        """
        logger.info(f"执行系统功能，参数：{params}")
        
        action = params.get('action')
        intent = params.get('intent')
        
        try:
            if intent == 'permission_manage':
                return self._handle_permission_manage(params)
            elif intent == 'task_manage':
                return self._handle_task_manage(params)
            elif intent == 'config_manage':
                return self._handle_config_manage(params)
            elif intent == 'file_retrieval':
                return self._handle_file_retrieval(params)
            elif intent == 'integration_manage':
                return self._handle_integration_manage(params)
            else:
                return {
                    'success': False,
                    'message': f'不支持的系统功能：{intent}'
                }
        except Exception as e:
            logger.error(f"执行系统功能失败：{str(e)}")
            return {
                'success': False,
                'message': f'执行系统功能时遇到错误：{str(e)}'
            }
    
    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        验证输入参数
        
        Args:
            params: 输入参数字典
            
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        if 'intent' not in params:
            errors.append('缺少 intent 参数')
        
        return len(errors) == 0, errors
    
    def _handle_permission_manage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理权限管理功能"""
        from backend.services.permission_service import permission_service
        from backend.services.permission_service import RoleType
        
        action = params.get('action')
        username = params.get('username')
        role_str = params.get('role')
        
        if action == 'create_user':
            if not username:
                return {
                    'success': False,
                    'message': '缺少用户名参数'
                }
            
            # 创建用户
            password = '123456'  # 默认密码
            role = RoleType.USER  # 默认角色
            
            if role_str:
                role_str = role_str.lower()
                if role_str == 'admin':
                    role = RoleType.ADMIN
                elif role_str == 'guest':
                    role = RoleType.GUEST
            
            try:
                user = permission_service.create_user(username, password, role)
                return {
                    'success': True,
                    'message': f'用户 {username} 创建成功，默认密码：123456',
                    'data': user.to_dict()
                }
            except Exception as e:
                logger.error(f"创建用户失败：{str(e)}")
                return {
                    'success': False,
                    'message': f'创建用户失败：{str(e)}'
                }
        
        elif action == 'delete_user':
            if not username:
                return {
                    'success': False,
                    'message': '缺少用户名参数'
                }
            
            # 查找用户ID
            users = permission_service.list_users()
            user_id_to_delete = None
            for user in users:
                if user['username'] == username:
                    user_id_to_delete = user['user_id']
                    break
            
            if not user_id_to_delete:
                return {
                    'success': False,
                    'message': f'用户 {username} 不存在'
                }
            
            try:
                success = permission_service.delete_user(user_id_to_delete)
                if success:
                    return {
                        'success': True,
                        'message': f'用户 {username} 删除成功'
                    }
                else:
                    return {
                        'success': False,
                        'message': f'用户 {username} 删除失败'
                    }
            except Exception as e:
                logger.error(f"删除用户失败：{str(e)}")
                return {
                    'success': False,
                    'message': f'删除用户失败：{str(e)}'
                }
        
        elif action == 'update_user_role':
            if not username or not role_str:
                return {
                    'success': False,
                    'message': '缺少用户名或角色参数'
                }
            
            # 查找用户ID
            users = permission_service.list_users()
            user_id_to_update = None
            for user in users:
                if user['username'] == username:
                    user_id_to_update = user['user_id']
                    break
            
            if not user_id_to_update:
                return {
                    'success': False,
                    'message': f'用户 {username} 不存在'
                }
            
            # 解析角色
            role = RoleType.USER
            role_str = role_str.lower()
            if role_str == 'admin':
                role = RoleType.ADMIN
            elif role_str == 'guest':
                role = RoleType.GUEST
            
            try:
                success = permission_service.update_user_role(user_id_to_update, role)
                if success:
                    return {
                        'success': True,
                        'message': f'用户 {username} 角色更新为 {role.value} 成功'
                    }
                else:
                    return {
                        'success': False,
                        'message': f'用户 {username} 角色更新失败'
                    }
            except Exception as e:
                logger.error(f"更新用户角色失败：{str(e)}")
                return {
                    'success': False,
                    'message': f'更新用户角色失败：{str(e)}'
                }
        
        else:
            # 查看用户和角色列表
            try:
                users = permission_service.list_users()
                roles = permission_service.list_roles()
                return {
                    'success': True,
                    'message': f'当前系统有 {len(users)} 个用户，{len(roles)} 个角色',
                    'data': {
                        'users': users,
                        'roles': roles
                    }
                }
            except Exception as e:
                logger.error(f"获取用户和角色列表失败：{str(e)}")
                return {
                    'success': False,
                    'message': f'获取用户和角色列表失败：{str(e)}'
                }
    
    def _handle_task_manage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务管理功能"""
        action = params.get('action', 'list')
        period = params.get('period', 'week')
        task_id = params.get('task_id')
        
        try:
            if action == 'work_summary':
                # 生成工作总结
                url = f"http://localhost:5000/api/tasks/work-summary?period={period}"
                response_data = requests.get(url).json()
                
                if response_data.get('success'):
                    summary = response_data['data']
                    # 生成简洁的工作总结
                    stats = summary['statistics']
                    message = f"{summary['period_label']}工作总结：\n"
                    message += f"总任务数：{stats['total_tasks']}\n"
                    message += f"已完成：{stats['completed_count']}（{stats['completion_rate']}%）\n"
                    message += f"进行中：{stats['in_progress_count']}\n"
                    message += f"待处理：{stats['pending_count']}\n"
                    message += f"超期任务：{stats['overdue_count']}\n"
                    
                    if summary['risks']:
                        message += "\n风险事项：\n"
                        for risk in summary['risks'][:3]:
                            message += f"- {risk['title']}：{risk['description']}\n"
                    
                    if summary['next_plan']:
                        message += "\n下周计划：\n"
                        for plan in summary['next_plan'][:3]:
                            message += f"- {plan['title']}\n"
                            for item in plan['items'][:2]:
                                message += f"  · {item}\n"
                    
                    return {
                        'success': True,
                        'message': message,
                        'data': summary
                    }
                else:
                    return {
                        'success': False,
                        'message': '生成工作总结失败'
                    }
            
            elif action == 'list_tasks':
                # 获取任务列表
                url = "http://localhost:5000/api/tasks"
                response_data = requests.get(url).json()
                
                if response_data.get('success'):
                    tasks = response_data['data']
                    message = f"当前系统共有 {len(tasks)} 个任务：\n"
                    for task in tasks[:5]:  # 只显示前5个
                        message += f"- {task['title']}（状态：{task['status']}，优先级：{task['priority']}）\n"
                    if len(tasks) > 5:
                        message += f"... 还有 {len(tasks) - 5} 个任务"
                    
                    return {
                        'success': True,
                        'message': message,
                        'data': tasks
                    }
                else:
                    return {
                        'success': False,
                        'message': '获取任务列表失败'
                    }
            
            elif action == 'task_summary':
                # 任务汇总
                url = "http://localhost:5000/api/tasks/summary"
                response_data = requests.get(url).json()
                
                if response_data.get('success'):
                    summary = response_data['data']
                    message = "任务汇总：\n"
                    message += f"总任务数：{summary['total']}\n"
                    message += f"待处理：{summary['pending']}\n"
                    message += f"进行中：{summary['in_progress']}\n"
                    message += f"已完成：{summary['completed']}\n"
                    message += f"超期：{summary['overdue']}\n"
                    message += f"高优先级：{summary['high_priority']}\n"
                    
                    return {
                        'success': True,
                        'message': message,
                        'data': summary
                    }
                else:
                    return {
                        'success': False,
                        'message': '获取任务汇总失败'
                    }
            
            else:
                return {
                    'success': False,
                    'message': f'不支持的任务管理操作：{action}'
                }
        except Exception as e:
            logger.error(f"处理任务管理功能失败：{str(e)}")
            return {
                'success': False,
                'message': f'处理任务管理功能失败：{str(e)}'
            }
    
    def _handle_config_manage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理配置管理功能"""
        from backend.services.config_service import config_service
        
        action = params.get('action', 'get')
        config_name = params.get('config_name', 'default')
        user_id = params.get('user_id')
        
        try:
            if action == 'get':
                # 获取配置
                config = config_service.get_config('user_preference', config_name, user_id)
                if config:
                    return {
                        'success': True,
                        'message': f'获取配置 {config_name} 成功',
                        'data': config
                    }
                else:
                    return {
                        'success': False,
                        'message': f'配置 {config_name} 不存在'
                    }
            
            else:
                return {
                    'success': False,
                    'message': f'不支持的配置管理操作：{action}'
                }
        except Exception as e:
            logger.error(f"处理配置管理功能失败：{str(e)}")
            return {
                'success': False,
                'message': f'处理配置管理功能失败：{str(e)}'
            }
    
    def _handle_file_retrieval(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理文件检索功能"""
        return {
            'success': True,
            'message': '文件检索功能正在开发中，敬请期待'
        }
    
    def _handle_integration_manage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理系统集成功能"""
        return {
            'success': True,
            'message': '系统集成功能正在开发中，敬请期待'
        }
