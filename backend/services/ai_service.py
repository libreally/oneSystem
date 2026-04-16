"""
AI 助手服务
负责理解用户意图、调度 Skills、生成执行逻辑
"""
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class AIAssistantService:
    """AI 助手服务"""
    
    def __init__(self, skill_engine=None):
        self.skill_engine = skill_engine
        self.intent_patterns = self._build_intent_patterns()
        
    def _build_intent_patterns(self) -> Dict[str, List[re.Pattern]]:
        """构建意图识别模式"""
        logger.info("开始构建意图识别模式")
        patterns = {
            'document_convert': [
                re.compile(r'转\s*(成 | 为 | 换|到)'),
                re.compile(r'(把 | 将).*转换'),
                re.compile(r'生成.*公文'),
                re.compile(r'.*公文.*格式'),
                re.compile(r'.*转成.*公文'),
            ],
            'sensitive_word_check': [
                re.compile(r'检查.*敏感'),
                re.compile(r'检测.*敏感'),
                re.compile(r'查找.*违禁'),
                re.compile(r'敏感词'),
            ],
            'data_merge': [
                re.compile(r'合并.*(表格 | 文件 |excel| 数据)'),
                re.compile(r'比对.*(表格 | 文件 | 数据)'),
                re.compile(r'对比.*(表格 | 文件 | 数据)'),
                re.compile(r'合并.*excel', re.IGNORECASE),
                re.compile(r'合并.*表'),
            ],
            'report_generate': [
                re.compile(r'生成.*报告'),
                re.compile(r'生成.*总结'),
                re.compile(r'写.*周报'),
                re.compile(r'写.*月报'),
                re.compile(r'生成周报'),
                re.compile(r'生成月报'),
            ],
            # 权限管理相关意图
            'permission_manage': [
                re.compile(r'用户.*管理'),
                re.compile(r'角色.*管理'),
                re.compile(r'权限.*管理'),
                re.compile(r'创建.*用户'),
                re.compile(r'删除.*用户'),
                re.compile(r'修改.*用户'),
                re.compile(r'查看.*用户'),
                re.compile(r'用户.*列表'),
                re.compile(r'查看.*用户.*列表'),
                re.compile(r'查看用户列表'),
                re.compile(r'查看.*权限'),
            ],
            # 任务管理相关意图
            'task_manage': [
                re.compile(r'任务.*管理'),
                re.compile(r'查看.*任务'),
                re.compile(r'任务.*列表'),
                re.compile(r'查看.*任务.*列表'),
                re.compile(r'查看任务列表'),
                re.compile(r'任务列表'),
                re.compile(r'查看.*列表'),
                re.compile(r'任务.*汇总'),
                re.compile(r'工作总结'),
                re.compile(r'工作.*报告'),
                re.compile(r'完成.*任务'),
                re.compile(r'更新.*任务'),
            ],
            # 配置管理相关意图
            'config_manage': [
                re.compile(r'配置.*管理'),
                re.compile(r'获取.*配置'),
                re.compile(r'保存.*配置'),
                re.compile(r'删除.*配置'),
                re.compile(r'导入.*配置'),
                re.compile(r'导出.*配置'),
                re.compile(r'用户.*偏好'),
            ],
            # 定时任务管理相关意图
            'scheduler_manage': [
                re.compile(r'定时.*任务'),
                re.compile(r'调度.*任务'),
                re.compile(r'创建.*定时'),
                re.compile(r'修改.*定时'),
                re.compile(r'删除.*定时'),
                re.compile(r'查看.*定时'),
            ],
            # 文件检索相关意图
            'file_retrieval': [
                re.compile(r'查找.*文件'),
                re.compile(r'检索.*文件'),
                re.compile(r'搜索.*文件'),
                re.compile(r'文件.*检索'),
            ],
            # 系统集成相关意图
            'integration_manage': [
                re.compile(r'系统.*集成'),
                re.compile(r'集成.*管理'),
                re.compile(r'WPS.*集成'),
                re.compile(r'访问.*WPS'),
            ],
        }
        logger.info(f"意图识别模式构建完成，包含 {len(patterns)} 种意图类型")
        return patterns
    
    def analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        分析用户意图
        
        Args:
            message: 用户输入消息
            
        Returns:
            意图分析结果
        """
        logger.info(f"开始分析用户意图: {message}")
        result = {
            'intent': 'unknown',
            'confidence': 0.0,
            'skill_id': None,
            'params': {},
            'missing_params': [],
            'suggestions': []
        }
        
        # 匹配意图
        for intent, patterns in self.intent_patterns.items():
            logger.info(f"检查意图: {intent}")
            for pattern in patterns:
                logger.info(f"  检查模式: {pattern.pattern}")
                if pattern.search(message):
                    result['intent'] = intent
                    result['confidence'] = 0.8
                    logger.info(f"  匹配到意图: {intent}, 置信度: 0.8")
                    break
            if result['intent'] != 'unknown':
                break
        
        # 根据意图映射到 Skill
        intent_to_skill = {
            'document_convert': 'doc_processor',
            'sensitive_word_check': 'sensitive_word_checker',
            'data_merge': 'data_merger',
            'report_generate': 'doc_processor',
            'permission_manage': 'system_skill',
            'task_manage': 'system_skill',
            'config_manage': 'system_skill',
            'scheduler_manage': 'scheduler_manager',
            'file_retrieval': 'system_skill',
            'integration_manage': 'system_skill'
        }
        
        if result['intent'] in intent_to_skill:
            result['skill_id'] = intent_to_skill[result['intent']]
            logger.info(f"意图映射到 Skill: {result['skill_id']}")
        
        # 提取参数
        result['params'] = self._extract_params(message, result['intent'])
        logger.info(f"提取到参数: {result['params']}")
        
        # 检查缺失参数
        result['missing_params'] = self._check_missing_params(result['intent'], result['params'])
        if result['missing_params']:
            logger.info(f"检测到缺失参数: {result['missing_params']}")
        
        # 生成建议
        if result['missing_params']:
            result['suggestions'] = self._generate_suggestions(result['intent'], result['missing_params'])
            logger.info(f"生成补充建议: {result['suggestions']}")
        
        logger.info(f"意图分析完成: {result}")
        return result
    
    def _extract_params(self, message: str, intent: str) -> Dict[str, Any]:
        """从消息中提取参数"""
        logger.info(f"开始提取参数，消息: {message}, 意图: {intent}")
        params = {}
        
        # 提取文件路径
        file_patterns = [
            r'(?:文件|文档)[:：]?\s*([^\s,，]+)',
            r'([^\s,，]+\.(?:docx?|xlsx?|csv|pdf|txt))',
            r'从\s*([^\s,，]+)\s*(文件|文档)',
            r'(?:处理|打开)\s*([^\s,，]+)',
        ]
        for pattern in file_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                # 确保获取到正确的分组
                if len(match.groups()) > 1 and match.group(2) in ['文件', '文档']:
                    params['file_path'] = match.group(1)
                else:
                    params['file_path'] = match.group(1)
                logger.info(f"提取到文件路径: {params['file_path']}")
                break
        
        # 提取文档类型
        doc_type_patterns = [
            r'(通知 | 报告 | 请示 | 函 | 决定 | 公告)',
        ]
        for pattern in doc_type_patterns:
            match = re.search(pattern, message)
            if match:
                params['doc_type'] = match.group(1)
                logger.info(f"提取到文档类型: {params['doc_type']}")
                break
        
        # 提取操作类型
        if '替换' in message or '替代' in message:
            params['action'] = 'replace'
            logger.info("提取到操作类型: replace")
        elif '标记' in message:
            params['action'] = 'mark'
            logger.info("提取到操作类型: mark")
        elif '合并' in message:
            params['action'] = 'merge_files'
            logger.info("提取到操作类型: merge_files")
        elif '比对' in message or '对比' in message:
            params['action'] = 'compare_files'
            logger.info("提取到操作类型: compare_files")
        elif '转换' in message or '转成' in message or '转为' in message:
            params['action'] = 'convert_to_official'
            logger.info("提取到操作类型: convert_to_official")
        elif '生成' in message:
            params['action'] = 'generate'
            logger.info("提取到操作类型: generate")
        elif '创建' in message or '新建' in message:
            params['action'] = 'create'
            logger.info("提取到操作类型: create")
        elif '删除' in message or '移除' in message:
            params['action'] = 'delete'
            logger.info("提取到操作类型: delete")
        elif '修改' in message or '更新' in message or '编辑' in message:
            params['action'] = 'update'
            logger.info("提取到操作类型: update")
        elif '查看' in message or '检查' in message:
            params['action'] = 'view'
            logger.info("提取到操作类型: view")
        
        # 系统功能参数提取
        if intent == 'permission_manage':
            # 提取用户相关参数
            user_patterns = [
                r'(?:用户|账号)[:：]?\s*([^\s,，]+)',
                r'(?:创建|删除|修改)\s*(?:用户|账号)\s*([^\s,，]+)',
            ]
            for pattern in user_patterns:
                match = re.search(pattern, message)
                if match:
                    params['username'] = match.group(1)
                    logger.info(f"提取到用户名: {params['username']}")
                    break
            
            # 提取角色相关参数
            role_patterns = [
                r'(?:角色)[:：]?\s*([^\s,，]+)',
                r'(?:设置|修改)\s*(?:角色)\s*([^\s,，]+)',
            ]
            for pattern in role_patterns:
                match = re.search(pattern, message)
                if match:
                    params['role'] = match.group(1)
                    logger.info(f"提取到角色: {params['role']}")
                    break
        
        elif intent == 'task_manage':
            # 提取任务ID
            task_id_patterns = [
                r'(?:任务|Task)[:：]?\s*([^\s,，]+)',
                r'(?:完成|更新)\s*(?:任务|Task)\s*([^\s,，]+)',
            ]
            for pattern in task_id_patterns:
                match = re.search(pattern, message)
                if match:
                    params['task_id'] = match.group(1)
                    logger.info(f"提取到任务ID: {params['task_id']}")
                    break
            
            # 提取时间段
            period_patterns = [
                r'(周|月|季度|年)报',
                r'(本周|本月|本季度|本年)',
            ]
            for pattern in period_patterns:
                match = re.search(pattern, message)
                if match:
                    period_map = {
                        '周': 'week',
                        '月': 'month',
                        '季度': 'quarter',
                        '年': 'year',
                        '本周': 'week',
                        '本月': 'month',
                        '本季度': 'quarter',
                        '本年': 'year'
                    }
                    period = match.group(1)
                    params['period'] = period_map.get(period, 'week')
                    logger.info(f"提取到时间段: {params['period']}")
                    break
        
        elif intent == 'config_manage':
            # 提取配置类型和名称
            config_patterns = [
                r'(?:配置|设置)[:：]?\s*([^\s,，]+)',
                r'(?:获取|保存|删除)\s*(?:配置|设置)\s*([^\s,，]+)',
            ]
            for pattern in config_patterns:
                match = re.search(pattern, message)
                if match:
                    params['config_name'] = match.group(1)
                    logger.info(f"提取到配置名称: {params['config_name']}")
                    break
        
        elif intent == 'scheduler_manage':
            # 提取定时任务参数
            time_patterns = [
                r'(?:每天|每周|每月|每年)\s*(\d+):(\d+)',
                r'(?:时间|定时)[:：]?\s*(\d+):(\d+)',
            ]
            for pattern in time_patterns:
                match = re.search(pattern, message)
                if match:
                    params['hour'] = match.group(1)
                    params['minute'] = match.group(2)
                    logger.info(f"提取到定时时间: {params['hour']}:{params['minute']}")
                    break
            
            # 提取任务名称
            task_name_patterns = [
                r'(?:任务|作业)[:：]?\s*([^\s,，]+)',
                r'(?:创建|修改)\s*(?:定时|任务)\s*([^\s,，]+)',
            ]
            for pattern in task_name_patterns:
                match = re.search(pattern, message)
                if match:
                    params['task_name'] = match.group(1)
                    logger.info(f"提取到任务名称: {params['task_name']}")
                    break
        
        logger.info(f"参数提取完成: {params}")
        return params
    
    def _check_missing_params(self, intent: str, params: Dict[str, Any]) -> List[str]:
        """检查缺失的关键参数"""
        logger.info(f"开始检查缺失参数，意图: {intent}, 当前参数: {params}")
        missing = []
        
        if intent == 'document_convert':
            if 'file_path' not in params and 'content' not in params:
                missing.append('file_path')
                logger.info("缺少参数: file_path")
            if 'doc_type' not in params:
                missing.append('doc_type')
                logger.info("缺少参数: doc_type")
        
        elif intent == 'sensitive_word_check':
            if 'file_path' not in params and 'content' not in params:
                missing.append('file_path')
                logger.info("缺少参数: file_path")
        
        elif intent == 'data_merge':
            if 'file_paths' not in params and 'file_path' not in params:
                missing.append('file_paths')
                logger.info("缺少参数: file_paths")
        
        elif intent == 'permission_manage':
            if 'action' in params:
                if params['action'] in ['create', 'delete', 'update'] and 'username' not in params:
                    missing.append('username')
                    logger.info("缺少参数: username")
                if params['action'] == 'update' and 'role' not in params:
                    missing.append('role')
                    logger.info("缺少参数: role")
        
        elif intent == 'task_manage':
            if 'action' in params:
                if params['action'] in ['complete', 'update'] and 'task_id' not in params:
                    missing.append('task_id')
                    logger.info("缺少参数: task_id")
            elif 'action' not in params and 'period' not in params:
                # 默认为周报告
                params['period'] = 'week'
        
        elif intent == 'scheduler_manage':
            if 'action' in params:
                if params['action'] in ['create', 'update']:
                    if 'task_name' not in params:
                        missing.append('task_name')
                        logger.info("缺少参数: task_name")
                    if 'hour' not in params or 'minute' not in params:
                        missing.append('time')
                        logger.info("缺少参数: time")
                elif params['action'] in ['delete', 'view'] and 'task_name' not in params:
                    missing.append('task_name')
                    logger.info("缺少参数: task_name")
        
        logger.info(f"缺失参数检查完成: {missing}")
        return missing
    
    def _generate_suggestions(self, intent: str, missing_params: List[str]) -> List[str]:
        """生成参数补充建议"""
        logger.info(f"开始生成补充建议，意图: {intent}, 缺失参数: {missing_params}")
        suggestions = []
        
        param_prompts = {
            'file_path': '请提供需要处理的文件路径或上传文件',
            'file_paths': '请提供需要合并/比对的多个文件路径',
            'doc_type': '请指定公文类型（如：通知、报告、请示等）',
            'content': '请提供需要处理的文本内容',
            'output_path': '请指定输出文件路径（可选）',
            'username': '请提供用户名',
            'role': '请提供角色名称（如：admin、user、guest）',
            'task_id': '请提供任务ID',
            'time': '请提供定时时间（如：每天 8:30）',
            'task_name': '请提供任务名称',
            'period': '请指定时间段（如：周、月、季度）',
        }
        
        for param in missing_params:
            if param in param_prompts:
                suggestion = param_prompts[param]
                suggestions.append(suggestion)
                logger.info(f"为参数 {param} 生成建议: {suggestion}")
        
        logger.info(f"补充建议生成完成: {suggestions}")
        return suggestions
    
    def process_message(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """
        处理用户消息
        
        Args:
            message: 用户输入消息
            user_id: 用户 ID
            
        Returns:
            处理结果
        """
        logger.info(f"开始处理用户消息：{message}, 用户：{user_id}")
        
        # 从配置中心加载用户偏好配置
        from backend.services.config_service import config_service
        logger.info("加载用户偏好配置")
        user_preference = config_service.get_config('user_preference', 'default', user_id)
        logger.info(f"用户偏好配置加载完成：{user_preference}")
        
        # 分析意图
        logger.info("开始分析用户意图")
        intent_result = self.analyze_intent(message)
        logger.info(f"意图分析完成：{intent_result}")
        
        # 如果有缺失参数，返回询问
        if intent_result['missing_params']:
            logger.info(f"存在缺失参数：{intent_result['missing_params']}，返回补充信息请求")
            response = {
                'success': True,
                'need_more_info': True,
                'intent': intent_result['intent'],
                'message': f"我需要更多信息才能完成任务。{'; '.join(intent_result['suggestions'])}",
                'suggestions': intent_result['suggestions']
            }
            logger.info(f"返回补充信息请求：{response}")
            return response
        
        # 系统功能处理
        if intent_result['skill_id'] == 'system_skill':
            logger.info("处理系统功能请求")
            try:
                # 权限检查
                from backend.services.permission_service import permission_service
                from backend.services.permission_service import PermissionType
                
                # 检查用户权限
                if not user_id:
                    user_id = 'default_user'
                
                # 映射数据库用户ID到权限服务用户ID
                # 因为API路由使用数据库用户ID，而权限服务使用文件存储的用户ID
                user_id_map = {
                    1: 'admin',
                    2: 'test'
                }
                if isinstance(user_id, int):
                    user_id = user_id_map.get(user_id, 'admin')
                
                # 权限映射
                permission_map = {
                    'permission_manage': PermissionType.USER_MANAGE,
                    'task_manage': PermissionType.TASK_VIEW,
                    'config_manage': PermissionType.CONFIG_VIEW,
                    'file_retrieval': PermissionType.FILE_RETRIEVAL,
                    'integration_manage': PermissionType.INTEGRATION_VIEW
                }
                
                # 获取当前意图需要的权限
                required_permission = permission_map.get(intent_result['intent'])
                if required_permission:
                    # 检查用户是否有相应权限
                    logger.info(f"检查用户 {user_id} 是否有 {required_permission} 权限")
                    # 打印用户列表
                    users = permission_service.list_users()
                    logger.info(f"用户列表: {users}")
                    # 打印角色列表
                    roles = permission_service.list_roles()
                    logger.info(f"角色列表: {roles}")
                    # 检查用户权限
                    has_permission = permission_service.check_permission(user_id, required_permission)
                    logger.info(f"权限检查结果: {has_permission}")
                    if not has_permission:
                        logger.warning(f"用户 {user_id} 没有权限执行 {intent_result['intent']} 操作")
                        response = {
                            'success': False,
                            'need_more_info': False,
                            'message': f"您没有权限执行此操作，请联系管理员"
                        }
                        return response
                # 权限管理功能
                if intent_result['intent'] == 'permission_manage':
                    params = intent_result['params']
                    
                    if '创建' in message:
                        # 创建用户
                        if 'username' in params:
                            username = params['username']
                            password = '123456'  # 默认密码
                            from backend.services.permission_service import RoleType
                            role = RoleType.USER  # 默认角色
                            if 'role' in params:
                                role_str = params['role'].lower()
                                if role_str == 'admin':
                                    role = RoleType.ADMIN
                                elif role_str == 'guest':
                                    role = RoleType.GUEST
                            
                            user = permission_service.create_user(username, password, role)
                            response = {
                                'success': True,
                                'need_more_info': False,
                                'intent': intent_result['intent'],
                                'message': f"用户 {username} 创建成功，默认密码：123456",
                                'data': user.to_dict()
                            }
                        else:
                            response = {
                                'success': False,
                                'need_more_info': True,
                                'message': '请提供用户名'
                            }
                    
                    elif '删除' in message:
                        # 删除用户
                        if 'username' in params:
                            username = params['username']
                            # 查找用户ID
                            users = permission_service.list_users()
                            user_id_to_delete = None
                            for user in users:
                                if user['username'] == username:
                                    user_id_to_delete = user['user_id']
                                    break
                            
                            if user_id_to_delete:
                                success = permission_service.delete_user(user_id_to_delete)
                                if success:
                                    response = {
                                        'success': True,
                                        'need_more_info': False,
                                        'intent': intent_result['intent'],
                                        'message': f"用户 {username} 删除成功"
                                    }
                                else:
                                    response = {
                                        'success': False,
                                        'need_more_info': False,
                                        'message': f"用户 {username} 删除失败"
                                    }
                            else:
                                response = {
                                    'success': False,
                                    'need_more_info': False,
                                    'message': f"用户 {username} 不存在"
                                }
                        else:
                            response = {
                                'success': False,
                                'need_more_info': True,
                                'message': '请提供用户名'
                            }
                    
                    elif '修改' in message or '更新' in message:
                        # 更新用户角色
                        if 'username' in params and 'role' in params:
                            username = params['username']
                            role_str = params['role'].lower()
                            from backend.services.permission_service import RoleType
                            role = RoleType.USER
                            if role_str == 'admin':
                                role = RoleType.ADMIN
                            elif role_str == 'guest':
                                role = RoleType.GUEST
                            
                            # 查找用户ID
                            users = permission_service.list_users()
                            user_id_to_update = None
                            for user in users:
                                if user['username'] == username:
                                    user_id_to_update = user['user_id']
                                    break
                            
                            if user_id_to_update:
                                success = permission_service.update_user_role(user_id_to_update, role)
                                if success:
                                    response = {
                                        'success': True,
                                        'need_more_info': False,
                                        'intent': intent_result['intent'],
                                        'message': f"用户 {username} 角色更新为 {role.value} 成功"
                                    }
                                else:
                                    response = {
                                        'success': False,
                                        'need_more_info': False,
                                        'message': f"用户 {username} 角色更新失败"
                                    }
                            else:
                                response = {
                                    'success': False,
                                    'need_more_info': False,
                                    'message': f"用户 {username} 不存在"
                                }
                        else:
                            response = {
                                'success': False,
                                'need_more_info': True,
                                'message': '请提供用户名和角色'
                            }
                    
                    else:
                        # 查看用户列表
                        users = permission_service.list_users()
                        roles = permission_service.list_roles()
                        response = {
                            'success': True,
                            'need_more_info': False,
                            'intent': intent_result['intent'],
                            'message': f"当前系统有 {len(users)} 个用户，{len(roles)} 个角色",
                            'data': {
                                'users': users,
                                'roles': roles
                            }
                        }
                
                # 任务管理功能
                elif intent_result['intent'] == 'task_manage':
                    import requests
                    params = intent_result['params']
                    
                    if '工作总结' in message or '工作汇报' in message:
                        # 生成工作总结
                        period = params.get('period', 'week')
                        url = f"http://localhost:5000/api/tasks/work-summary?period={period}"
                        try:
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
                                
                                response = {
                                    'success': True,
                                    'need_more_info': False,
                                    'intent': intent_result['intent'],
                                    'message': message,
                                    'data': summary
                                }
                            else:
                                response = {
                                    'success': False,
                                    'need_more_info': False,
                                    'message': '生成工作总结失败'
                                }
                        except Exception as e:
                            logger.error(f"调用任务API失败：{str(e)}")
                            response = {
                                'success': False,
                                'need_more_info': False,
                                'message': '生成工作总结失败，请检查系统连接'
                            }
                    
                    elif '任务列表' in message or '查看任务' in message:
                        # 获取任务列表
                        url = "http://localhost:5000/api/tasks"
                        try:
                            response_data = requests.get(url).json()
                            if response_data.get('success'):
                                tasks = response_data['data']
                                message = f"当前系统共有 {len(tasks)} 个任务：\n"
                                for task in tasks[:5]:  # 只显示前5个
                                    message += f"- {task['title']}（状态：{task['status']}，优先级：{task['priority']}）\n"
                                if len(tasks) > 5:
                                    message += f"... 还有 {len(tasks) - 5} 个任务"
                                
                                response = {
                                    'success': True,
                                    'need_more_info': False,
                                    'intent': intent_result['intent'],
                                    'message': message,
                                    'data': tasks
                                }
                            else:
                                response = {
                                    'success': False,
                                    'need_more_info': False,
                                    'message': '获取任务列表失败'
                                }
                        except Exception as e:
                            logger.error(f"调用任务API失败：{str(e)}")
                            response = {
                                'success': False,
                                'need_more_info': False,
                                'message': '获取任务列表失败，请检查系统连接'
                            }
                    
                    else:
                        # 任务汇总
                        url = "http://localhost:5000/api/tasks/summary"
                        try:
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
                                
                                response = {
                                    'success': True,
                                    'need_more_info': False,
                                    'intent': intent_result['intent'],
                                    'message': message,
                                    'data': summary
                                }
                            else:
                                response = {
                                    'success': False,
                                    'need_more_info': False,
                                    'message': '获取任务汇总失败'
                                }
                        except Exception as e:
                            logger.error(f"调用任务API失败：{str(e)}")
                            response = {
                                'success': False,
                                'need_more_info': False,
                                'message': '获取任务汇总失败，请检查系统连接'
                            }
                
                # 配置管理功能
                elif intent_result['intent'] == 'config_manage':
                    params = intent_result['params']
                    
                    if '设置' in message or '修改' in message:
                        # 设置配置
                        if 'key' in params and 'value' in params:
                            key = params['key']
                            value = params['value']
                            config_service.set_config(key, value, user_id)
                            response = {
                                'success': True,
                                'need_more_info': False,
                                'intent': intent_result['intent'],
                                'message': f"配置 {key} 设置成功"
                            }
                        else:
                            response = {
                                'success': False,
                                'need_more_info': True,
                                'message': '请提供配置键和值'
                            }
                    
                    else:
                        # 查看配置
                        configs = config_service.get_all_configs(user_id)
                        response = {
                            'success': True,
                            'need_more_info': False,
                            'intent': intent_result['intent'],
                            'message': f"当前系统配置：\n{configs}"
                        }
                
                # 文件检索功能
                elif intent_result['intent'] == 'file_retrieval':
                    params = intent_result['params']
                    
                    if '搜索' in message:
                        # 搜索文件
                        if 'keyword' in params:
                            keyword = params['keyword']
                            # 这里应该调用文件检索服务
                            response = {
                                'success': True,
                                'need_more_info': False,
                                'intent': intent_result['intent'],
                                'message': f"搜索关键词 '{keyword}' 的结果：\n（文件检索功能待实现）"
                            }
                        else:
                            response = {
                                'success': False,
                                'need_more_info': True,
                                'message': '请提供搜索关键词'
                            }
                    
                    else:
                        # 查看文件列表
                        # 这里应该调用文件服务
                        response = {
                            'success': True,
                            'need_more_info': False,
                            'intent': intent_result['intent'],
                            'message': "文件列表：\n（文件列表功能待实现）"
                        }
                
                # 集成管理功能
                elif intent_result['intent'] == 'integration_manage':
                    params = intent_result['params']
                    
                    if '添加' in message:
                        # 添加集成
                        if 'name' in params and 'url' in params:
                            name = params['name']
                            url = params['url']
                            # 这里应该调用集成服务
                            response = {
                                'success': True,
                                'need_more_info': False,
                                'intent': intent_result['intent'],
                                'message': f"集成 {name} 添加成功"
                            }
                        else:
                            response = {
                                'success': False,
                                'need_more_info': True,
                                'message': '请提供集成名称和URL'
                            }
                    
                    else:
                        # 查看集成列表
                        # 这里应该调用集成服务
                        response = {
                            'success': True,
                            'need_more_info': False,
                            'intent': intent_result['intent'],
                            'message': "集成列表：\n（集成列表功能待实现）"
                        }
                
                # 默认响应
                else:
                    response = {
                        'success': True,
                        'need_more_info': False,
                        'intent': intent_result['intent'],
                        'message': f"执行 {intent_result['intent']} 操作成功"
                    }
                
                logger.info(f"系统功能处理完成：{response}")
                return response
                
            except Exception as e:
                logger.error(f"系统功能处理失败：{str(e)}")
                response = {
                    'success': False,
                    'need_more_info': False,
                    'message': f"系统功能处理失败：{str(e)}"
                }
                return response
        # 尝试使用 LLM 服务生成真实响应
        # 注意：系统功能优先处理，不使用 LLM 服务
        if intent_result['skill_id'] != 'system_skill':
            logger.info("尝试使用 LLM 服务生成响应")
            try:
                from backend.services.llm_service import get_llm_service
                llm_service = get_llm_service()
                
                if llm_service and llm_service.enabled:
                    logger.info("LLM 服务已启用，准备调用模型")
                    # 构建消息列表
                    system_prompt = "你是一系统 AI 助手，一个专业的办公自动化助手，擅长处理文档、数据和任务管理。请根据用户的需求，提供专业、准确的回答。"
                    
                    # 应用用户偏好配置
                    if user_preference and 'preferences' in user_preference:
                        preferences = user_preference['preferences']
                        if 'response_language' in preferences:
                            system_prompt += f"\n请使用{preferences['response_language']}回答。"
                            logger.info(f"应用语言偏好：{preferences['response_language']}")
                        if 'response_style' in preferences:
                            system_prompt += f"\n回答风格：{preferences['response_style']}。"
                            logger.info(f"应用风格偏好：{preferences['response_style']}")
                    
                    messages = [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": message
                        }
                    ]
                    
                    # 调用 LLM 服务
                    logger.info("调用 LLM 服务生成回复")
                    llm_result = llm_service.chat_completion(messages, temperature=0.7, max_tokens=1000)
                    logger.info(f"LLM 服务返回结果：{llm_result}")
                    
                    if llm_result.get('success'):
                        logger.info("LLM 服务生成回复成功")
                        response = {
                            'success': True,
                            'need_more_info': False,
                            'intent': intent_result['intent'],
                            'message': llm_result['response'],
                            'suggestions': []
                        }
                        logger.info(f"返回 LLM 生成的回复：{response}")
                        return response
            except Exception as e:
                logger.error(f"使用 LLM 服务失败：{str(e)}")
        
        # 如果没有匹配的 Skill，返回通用回复
        if not intent_result['skill_id']:
            logger.info("没有匹配的 Skill，返回通用回复")
            # 应用用户偏好配置
            default_message = '抱歉，我暂时无法理解您的需求。您可以尝试：\n- 帮我转换公文\n- 检查敏感词\n- 合并 Excel 表格\n- 查看任务列表\n- 生成工作总结\n- 管理用户权限'
            default_suggestions = [
                '把这个文件转成标准公文',
                '检查这篇材料的敏感词',
                '合并这两个表',
                '查看任务列表',
                '生成本周工作总结',
                '创建新用户'
            ]
            
            if user_preference and 'preferences' in user_preference:
                preferences = user_preference['preferences']
                if 'default_suggestions' in preferences:
                    default_suggestions = preferences['default_suggestions']
                    logger.info(f"应用自定义建议：{default_suggestions}")
            
            response = {
                'success': True,
                'need_more_info': False,
                'message': default_message,
                'suggestions': default_suggestions
            }
            logger.info(f"返回通用回复：{response}")
            return response
        
        # 执行 Skill
        logger.info("准备执行 Skill")
        if self.skill_engine:
            logger.info(f"执行 Skill：{intent_result['skill_id']}，参数：{intent_result['params']}")
            result = self.skill_engine.execute_skill(
                intent_result['skill_id'],
                intent_result['params'],
                user_id
            )
            logger.info(f"Skill 执行结果：{result}")
            
            response = {
                'success': result.get('success', False),
                'need_more_info': False,
                'intent': intent_result['intent'],
                'skill_id': intent_result['skill_id'],
                'message': result.get('message', ''),
                'data': result.get('data'),
                'file_path': result.get('file_path')
            }
            logger.info(f"返回 Skill 执行结果：{response}")
            return response
        else:
            logger.error("Skill 引擎未初始化")
            response = {
                'success': False,
                'need_more_info': False,
                'message': 'Skill 引擎未初始化'
            }
            logger.info(f"返回错误响应：{response}")
            return response
    
    def get_help_text(self) -> str:
        """获取帮助文本"""
        return """
我可以帮您完成以下任务：

📄 文档处理
  - 把文件转换成标准公文格式
  - 生成通知、报告、请示等公文
  - 调整文档格式

🔍 敏感词检查
  - 检查文档中的敏感词
  - 替换敏感词
  - 标记敏感词

📊 数据合并
  - 合并多个 Excel/CSV 文件
  - 比对两个数据表
  - 数据统计分析

� 任务管理
  - 查看任务列表
  - 获取任务汇总
  - 生成工作总结（周报、月报、季度报告）

👥 权限管理
  - 创建新用户
  - 删除用户
  - 修改用户角色
  - 查看用户和角色列表

⚙️ 配置管理
  - 查看用户偏好设置
  - 获取系统配置

⏰ 定时任务管理
  - 创建定时任务
  - 修改定时任务
  - 删除定时任务
  - 查看定时任务列表

�� 使用示例：
  - "把这个文件转成通知公文"
  - "检查这篇材料的敏感词"
  - "合并这两个 Excel 表格"
  - "查看任务列表"
  - "生成本周工作总结"
  - "创建新用户张三"
  - "修改用户李四的角色为管理员"

请告诉我您需要什么帮助？
"""


# 全局 AI 助手服务实例
ai_assistant_service = None


def init_ai_service(skill_engine=None):
    """初始化 AI 助手服务"""
    global ai_assistant_service
    ai_assistant_service = AIAssistantService(skill_engine)
    return ai_assistant_service
