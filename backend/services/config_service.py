"""
配置中心服务
支持公文模板、敏感词库、督办规则等配置管理
"""
import os
import json
import logging
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ConfigService:
    """配置中心服务"""
    
    def __init__(self):
        """初始化配置服务"""
        logger.info("开始初始化配置服务")
        self.config_base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'configs')
        logger.info(f"配置基础目录：{self.config_base_dir}")
        self._ensure_config_dirs()
        logger.info("配置服务初始化完成")
        
    def _ensure_config_dirs(self):
        """确保配置目录存在"""
        logger.info("开始确保配置目录存在")
        dirs = [
            os.path.join(self.config_base_dir, 'public'),
            os.path.join(self.config_base_dir, 'personal')
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"确保目录存在：{dir_path}")
        logger.info("配置目录检查完成")
    
    def get_config(self, config_type: str, config_name: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """
        获取配置
        
        Args:
            config_type: 配置类型
            config_name: 配置名称
            user_id: 用户 ID（用于个人配置）
            
        Returns:
            配置内容或 None
        """
        logger.info(f"开始获取配置，类型：{config_type}，名称：{config_name}，用户：{user_id}")
        
        # 优先查找个人配置
        if user_id:
            # 确保 user_id 是字符串类型
            user_id_str = str(user_id)
            personal_config_path = os.path.join(
                self.config_base_dir, 'personal', user_id_str, f'{config_type}', f'{config_name}.json'
            )
            logger.info(f"尝试读取个人配置：{personal_config_path}")
            if os.path.exists(personal_config_path):
                try:
                    with open(personal_config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        logger.info(f"成功读取个人配置")
                        return config
                except Exception as e:
                    logger.error(f"读取个人配置失败: {str(e)}")
        
        # 查找公共配置
        public_config_path = os.path.join(
            self.config_base_dir, 'public', f'{config_type}', f'{config_name}.json'
        )
        logger.info(f"尝试读取公共配置：{public_config_path}")
        if os.path.exists(public_config_path):
            try:
                with open(public_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"成功读取公共配置")
                    return config
            except Exception as e:
                logger.error(f"读取公共配置失败: {str(e)}")
        
        # 查找默认配置
        logger.info("尝试获取默认配置")
        default_config = self._get_default_config(config_type, config_name)
        if default_config:
            logger.info(f"成功获取默认配置")
            return default_config
        
        logger.warning(f"配置未找到：{config_type}/{config_name}")
        return None
    
    def save_config(self, config_type: str, config_name: str, config_data: Dict[str, Any], user_id: str = None) -> bool:
        """
        保存配置
        
        Args:
            config_type: 配置类型
            config_name: 配置名称
            config_data: 配置数据
            user_id: 用户 ID（用于个人配置）
            
        Returns:
            是否成功
        """
        logger.info(f"开始保存配置，类型：{config_type}，名称：{config_name}，用户：{user_id}")
        
        try:
            if user_id:
                # 确保 user_id 是字符串类型
                user_id_str = str(user_id)
                # 保存个人配置
                config_dir = os.path.join(self.config_base_dir, 'personal', user_id_str, f'{config_type}')
                logger.info(f"保存为个人配置到：{config_dir}")
            else:
                # 保存公共配置
                config_dir = os.path.join(self.config_base_dir, 'public', f'{config_type}')
                logger.info(f"保存为公共配置到：{config_dir}")
            
            os.makedirs(config_dir, exist_ok=True)
            logger.info(f"确保配置目录存在：{config_dir}")
            
            config_path = os.path.join(config_dir, f'{config_name}.json')
            logger.info(f"配置文件路径：{config_path}")
            
            # 添加元数据
            config_data['_metadata'] = {
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'config_type': config_type,
                'config_name': config_name,
                'user_id': user_id
            }
            logger.info("添加配置元数据")
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置已保存: {config_type}/{config_name}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
            return False
    
    def delete_config(self, config_type: str, config_name: str, user_id: str = None) -> bool:
        """
        删除配置
        
        Args:
            config_type: 配置类型
            config_name: 配置名称
            user_id: 用户 ID（用于个人配置）
            
        Returns:
            是否成功
        """
        try:
            if user_id:
                # 确保 user_id 是字符串类型
                user_id_str = str(user_id)
                # 删除个人配置
                config_path = os.path.join(
                    self.config_base_dir, 'personal', user_id_str, f'{config_type}', f'{config_name}.json'
                )
            else:
                # 删除公共配置
                config_path = os.path.join(
                    self.config_base_dir, 'public', f'{config_type}', f'{config_name}.json'
                )
            
            if os.path.exists(config_path):
                os.remove(config_path)
                logger.info(f"配置已删除: {config_type}/{config_name}")
                return True
            else:
                logger.warning(f"配置不存在: {config_type}/{config_name}")
                return False
                
        except Exception as e:
            logger.error(f"删除配置失败: {str(e)}")
            return False
    
    def list_configs(self, config_type: str = None, user_id: str = None) -> List[Dict[str, Any]]:
        """
        列出配置
        
        Args:
            config_type: 配置类型（可选）
            user_id: 用户 ID（用于个人配置）
            
        Returns:
            配置列表
        """
        configs = []
        
        # 列出公共配置
        public_dir = os.path.join(self.config_base_dir, 'public')
        if config_type:
            public_dir = os.path.join(public_dir, config_type)
        
        if os.path.exists(public_dir):
            for root, dirs, files in os.walk(public_dir):
                for file in files:
                    if file.endswith('.json'):
                        config_path = os.path.join(root, file)
                        try:
                            with open(config_path, 'r', encoding='utf-8') as f:
                                config_data = json.load(f)
                                configs.append({
                                    'type': 'public',
                                    'path': config_path.replace(self.config_base_dir, ''),
                                    'data': config_data
                                })
                        except Exception as e:
                            logger.error(f"读取公共配置失败: {str(e)}")
        
        # 列出个人配置
        if user_id:
            # 确保 user_id 是字符串类型
            user_id_str = str(user_id)
            personal_dir = os.path.join(self.config_base_dir, 'personal', user_id_str)
            if config_type:
                personal_dir = os.path.join(personal_dir, config_type)
            
            if os.path.exists(personal_dir):
                for root, dirs, files in os.walk(personal_dir):
                    for file in files:
                        if file.endswith('.json'):
                            config_path = os.path.join(root, file)
                            try:
                                with open(config_path, 'r', encoding='utf-8') as f:
                                    config_data = json.load(f)
                                    configs.append({
                                        'type': 'personal',
                                        'path': config_path.replace(self.config_base_dir, ''),
                                        'data': config_data
                                    })
                            except Exception as e:
                                logger.error(f"读取个人配置失败: {str(e)}")
        
        return configs
    
    def _get_default_config(self, config_type: str, config_name: str) -> Optional[Dict[str, Any]]:
        """
        获取默认配置
        
        Args:
            config_type: 配置类型
            config_name: 配置名称
            
        Returns:
            默认配置或 None
        """
        default_configs = {
            'document_template': {
                'standard': {
                    'title_format': '【{title}】',
                    'font': 'SimSun',
                    'font_size': 12,
                    'line_spacing': 1.5,
                    'margin': {
                        'top': 2.54,
                        'bottom': 2.54,
                        'left': 3.17,
                        'right': 3.17
                    },
                    'header': '',
                    'footer': '',
                    'signature': ''
                }
            },
            'sensitive_word': {
                'default': {
                    'words': [],
                    'categories': ['政治', '色情', '暴力'],
                    'action': 'mark',  # mark, replace, delete
                    'replace_with': '[敏感词]'
                }
            },
            'supervision_rule': {
                'default': {
                    'states': ['待处理', '处理中', '已完成', '已驳回'],
                    'transitions': {
                        '待处理': ['处理中'],
                        '处理中': ['已完成', '已驳回'],
                        '已驳回': ['处理中']
                    },
                    'deadline_days': 7,
                    'reminder_days': 3
                }
            },
            'recommendation_rule': {
                'default': {
                    'triggers': {
                        'time': [],
                        'keywords': [],
                        'actions': []
                    },
                    'priority': 'medium'
                }
            },
            'scheduler': {
                'default': {
                    'repeat_types': ['once', 'daily', 'weekly', 'monthly'],
                    'default_time': '09:00',
                    'max_retries': 3,
                    'retry_interval': 60
                }
            }
        }
        
        return default_configs.get(config_type, {}).get(config_name)
    
    def import_config(self, config_type: str, config_name: str, file_path: str, user_id: str = None) -> bool:
        """
        导入配置
        
        Args:
            config_type: 配置类型
            config_name: 配置名称
            file_path: 配置文件路径
            user_id: 用户 ID（用于个人配置）
            
        Returns:
            是否成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return self.save_config(config_type, config_name, config_data, user_id)
            
        except Exception as e:
            logger.error(f"导入配置失败: {str(e)}")
            return False
    
    def export_config(self, config_type: str, config_name: str, output_path: str, user_id: str = None) -> bool:
        """
        导出配置
        
        Args:
            config_type: 配置类型
            config_name: 配置名称
            output_path: 输出路径
            user_id: 用户 ID（用于个人配置）
            
        Returns:
            是否成功
        """
        try:
            config_data = self.get_config(config_type, config_name, user_id)
            if not config_data:
                return False
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置已导出: {config_type}/{config_name} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出配置失败: {str(e)}")
            return False


# 全局配置服务实例
config_service = ConfigService()


def init_config_service() -> ConfigService:
    """初始化配置服务"""
    global config_service
    return config_service
