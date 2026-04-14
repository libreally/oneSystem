"""
敏感词检查 Skill
支持文档敏感词检测、替换、标记等功能
"""
from .base_skill import BaseSkill
from typing import Dict, Any, List
import os
import re
import logging

logger = logging.getLogger(__name__)


class SensitiveWordSkill(BaseSkill):
    """敏感词检查 Skill"""
    
    def __init__(self):
        super().__init__(
            skill_id='sensitive_word_checker',
            name='敏感词检查',
            description='支持文档敏感词检测、替换、标记等功能'
        )
        self.sensitive_words = self._load_sensitive_words()
    
    def _load_sensitive_words(self) -> Dict[str, List[str]]:
        """加载敏感词库"""
        # 从配置中心加载
        from backend.services.config_service import config_service
        
        # 默认敏感词示例
        words = {
            'high': ['敏感词 1', '敏感词 2'],
            'medium': ['注意词 1', '注意词 2'],
            'low': ['提示词 1']
        }
        
        # 从配置中心加载敏感词库
        config = config_service.get_config('sensitive_word', 'default')
        if config and 'words' in config:
            try:
                # 处理配置中的敏感词
                if isinstance(config['words'], list):
                    # 兼容旧格式
                    words['high'] = config['words']
                elif isinstance(config['words'], dict):
                    # 新格式，按级别分类
                    words = config['words']
            except Exception as e:
                logger.error(f"加载配置中心敏感词库失败：{e}")
        
        # 从文件加载（作为备用）
        word_file = 'data/sensitive_words/words.txt'
        if os.path.exists(word_file):
            try:
                with open(word_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split(',')
                            if len(parts) >= 2:
                                level = parts[0].strip()
                                word = parts[1].strip()
                                if level not in words:
                                    words[level] = []
                                words[level].append(word)
            except Exception as e:
                logger.error(f"加载敏感词库失败：{e}")
        
        return words
    
    def validate_params(self, params: Dict[str, Any]) -> tuple:
        """验证参数"""
        errors = []
        
        if 'content' not in params and 'file_path' not in params:
            errors.append('需要提供 content 或 file_path')
        
        return len(errors) == 0, errors
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行敏感词检查"""
        try:
            content = params.get('content', '')
            file_path = params.get('file_path')
            action = params.get('action', 'check')  # check, replace, mark
            level = params.get('level', 'all')  # all, high, medium, low
            
            # 如果提供了文件路径，读取文件内容
            if file_path and os.path.exists(file_path):
                content = self._read_file(file_path)
            
            if not content:
                return {
                    'success': False,
                    'message': '未提供有效内容'
                }
            
            # 获取指定级别的敏感词
            words_to_check = []
            if level == 'all':
                for level_words in self.sensitive_words.values():
                    words_to_check.extend(level_words)
            elif level in self.sensitive_words:
                words_to_check = self.sensitive_words[level]
            
            # 执行检查
            if action == 'check':
                result = self._check_sensitive_words(content, words_to_check)
            elif action == 'replace':
                result = self._replace_sensitive_words(content, words_to_check)
            elif action == 'mark':
                result = self._mark_sensitive_words(content, words_to_check)
            else:
                return {
                    'success': False,
                    'message': f'未知的操作类型：{action}'
                }
            
            return {
                'success': True,
                'message': '检查完成',
                'data': result
            }
            
        except Exception as e:
            logger.error(f"敏感词检查失败：{str(e)}")
            return {
                'success': False,
                'message': f'检查失败：{str(e)}'
            }
    
    def _read_file(self, file_path: str) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
    
    def _check_sensitive_words(self, content: str, words: List[str]) -> Dict[str, Any]:
        """检查敏感词"""
        found_words = []
        
        for word in words:
            if word in content:
                # 计算出现次数和位置
                positions = []
                start = 0
                while True:
                    pos = content.find(word, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + len(word)
                
                found_words.append({
                    'word': word,
                    'count': len(positions),
                    'positions': positions
                })
        
        return {
            'total_found': len(found_words),
            'sensitive_words': found_words,
            'has_sensitive': len(found_words) > 0
        }
    
    def _replace_sensitive_words(self, content: str, words: List[str]) -> Dict[str, Any]:
        """替换敏感词"""
        replaced_content = content
        replaced_count = 0
        
        for word in words:
            if word in replaced_content:
                count = replaced_content.count(word)
                replaced_content = replaced_content.replace(word, '*' * len(word))
                replaced_count += count
        
        return {
            'original_content': content,
            'replaced_content': replaced_content,
            'replaced_count': replaced_count
        }
    
    def _mark_sensitive_words(self, content: str, words: List[str]) -> Dict[str, Any]:
        """标记敏感词"""
        marked_content = content
        
        for word in words:
            if word in marked_content:
                # 使用【】标记敏感词
                marked_content = marked_content.replace(word, f'【{word}】')
        
        return {
            'original_content': content,
            'marked_content': marked_content
        }
