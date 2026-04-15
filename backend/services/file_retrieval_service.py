"""
本地文件检索服务
支持根据用户提问内容自动在本地检索相关文件
构建本次对话的临时知识库
"""
import os
import re
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class FileRetrievalService:
    """本地文件检索服务"""
    
    def __init__(self, search_paths: List[str] = None):
        """
        初始化文件检索服务
        
        Args:
            search_paths: 搜索路径列表，默认包含常用目录
        """
        self.search_paths = search_paths or self._get_default_search_paths()
        self.supported_extensions = {
            '.doc', '.docx',  # Word
            '.xls', '.xlsx', '.csv',  # Excel
            '.ppt', '.pptx',  # PowerPoint
            '.pdf',  # PDF
            '.txt', '.md',  # 文本
            '.json', '.xml', '.yaml', '.yml',  # 配置文件
        }
        self.session_knowledge_base: Dict[str, Dict[str, Any]] = {}
        
    def _get_default_search_paths(self) -> List[str]:
        """获取默认搜索路径"""
        home = str(Path.home())
        return [
            os.path.join(home, 'Documents'),
            os.path.join(home, 'Desktop'),
            os.path.join(home, 'Downloads'),
            os.path.join(home, 'Work'),
            os.getcwd(),  # 当前工作目录
        ]
    
    def extract_keywords(self, query: str) -> List[str]:
        """
        从查询中提取关键词
        
        Args:
            query: 用户查询
            
        Returns:
            关键词列表
        """
        keywords = []
        
        # 提取文件名模式（带扩展名）
        file_patterns = re.findall(r'[\w\u4e00-\u9fa5\-_]+\.(?:docx?|xlsx?|csv|pdf|pptx?|txt|md)', query, re.IGNORECASE)
        keywords.extend(file_patterns)
        
        # 提取可能的文件名（不含扩展名）
        name_patterns = re.findall(r'(?:文件 | 文档 | 表 | 报告 | 总结 | 计划)[:：\s]*([\w\u4e00-\u9fa5\-_]+)', query)
        keywords.extend(name_patterns)
        
        # 提取专业术语（连续的中文字符或英文单词）
        terms = re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z][a-zA-Z0-9_-]{2,}', query)
        keywords.extend(terms)
        
        # 去重并过滤太短的词
        keywords = list(set([k for k in keywords if len(k) >= 2]))
        
        return keywords[:10]  # 限制最多 10 个关键词
    
    def search_files(self, 
                     query: str = None,
                     keywords: List[str] = None,
                     file_types: List[str] = None,
                     max_results: int = 20,
                     search_paths: List[str] = None) -> List[Dict[str, Any]]:
        """
        搜索文件
        
        Args:
            query: 用户查询语句
            keywords: 直接指定的关键词
            file_types: 文件类型过滤 ['.docx', '.xlsx']
            max_results: 最大返回结果数
            search_paths: 搜索路径
            
        Returns:
            匹配的文件信息列表
        """
        results = []
        
        # 确定搜索路径
        paths = search_paths or self.search_paths
        paths = [p for p in paths if os.path.exists(p)]
        
        # 确定文件类型过滤
        if file_types:
            extensions = set(file_types)
        else:
            extensions = self.supported_extensions
        
        # 提取关键词
        if keywords is None and query:
            keywords = self.extract_keywords(query)
        
        logger.info(f"开始搜索文件，查询：{query}, 关键词：{keywords}, 文件类型：{file_types}, 最大结果数：{max_results}, 路径数量：{len(paths)}")
        
        # 遍历搜索路径
        for search_path in paths:
            if not os.path.exists(search_path):
                continue
                
            try:
                matched_files = self._search_in_directory(
                    search_path, 
                    keywords, 
                    extensions,
                    max_results
                )
                results.extend(matched_files)
                logger.info(f"在路径 {search_path} 中找到 {len(matched_files)} 个匹配文件")
            except Exception as e:
                logger.warning(f"搜索路径 {search_path} 时出错：{str(e)}")
            
            # 如果已经找到足够的结果，提前退出
            if len(results) >= max_results:
                logger.info(f"已找到足够的结果 ({len(results)} 个)，提前退出")
                break
        
        # 按相关度排序
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        logger.info(f"搜索完成，共找到 {len(results)} 个匹配文件")
        return results[:max_results]
    
    def _search_in_directory(self, 
                             directory: str, 
                             keywords: List[str],
                             extensions: Set[str],
                             max_results: int) -> List[Dict[str, Any]]:
        """
        在目录中搜索文件
        
        Args:
            directory: 搜索目录
            keywords: 关键词列表
            extensions: 文件扩展名集合
            max_results: 最大结果数
            
        Returns:
            匹配的文件信息
        """
        matched_files = []
        
        try:
            logger.info(f"开始搜索目录：{directory}, 关键词：{keywords}, 扩展名：{extensions}, 最大结果数：{max_results}")
            
            for root, dirs, files in os.walk(directory):
                # 跳过隐藏目录和系统目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
                
                logger.debug(f"遍历目录：{root}, 子目录数：{len(dirs)}, 文件数：{len(files)}")
                
                for filename in files:
                    # 检查扩展名
                    _, ext = os.path.splitext(filename)
                    if ext.lower() not in extensions:
                        continue
                    
                    file_path = os.path.join(root, filename)
                    
                    # 计算相关度分数
                    score = self._calculate_relevance(filename, keywords)
                    
                    if score > 0:
                        file_stat = os.stat(file_path)
                        matched_files.append({
                            'file_path': file_path,
                            'filename': filename,
                            'directory': root,
                            'extension': ext.lower(),
                            'size': file_stat.st_size,
                            'modified_time': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                            'relevance_score': score,
                            'match_keywords': self._get_matched_keywords(filename, keywords)
                        })
                        
                        logger.debug(f"找到匹配文件：{filename}, 相关度：{score}")
                        
                        if len(matched_files) >= max_results:
                            logger.info(f"已达到最大结果数 {max_results}，停止搜索目录 {directory}")
                            return matched_files
                            
        except PermissionError:
            logger.warning(f"无权限访问目录：{directory}")
        except Exception as e:
            logger.warning(f"搜索目录 {directory} 时异常：{str(e)}")
        
        logger.info(f"目录搜索完成，在 {directory} 中找到 {len(matched_files)} 个匹配文件")
        return matched_files
    
    def _calculate_relevance(self, filename: str, keywords: List[str]) -> float:
        """
        计算文件与关键词的相关度
        
        Args:
            filename: 文件名
            keywords: 关键词列表
            
        Returns:
            相关度分数 (0-100)
        """
        if not keywords:
            return 0
        
        filename_lower = filename.lower()
        score = 0
        
        logger.debug(f"开始计算文件相关度，文件名：{filename}，关键词：{keywords}")
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # 完全匹配文件名（不含扩展名）
            name_without_ext = os.path.splitext(filename)[0].lower()
            if keyword_lower == name_without_ext:
                score += 50
                logger.debug(f"关键词 '{keyword}' 完全匹配文件名，加 50 分")
            
            # 包含关键词
            elif keyword_lower in filename_lower:
                # 在文件名开头匹配得分更高
                if filename_lower.startswith(keyword_lower):
                    score += 30
                    logger.debug(f"关键词 '{keyword}' 在文件名开头，加 30 分")
                else:
                    score += 20
                    logger.debug(f"关键词 '{keyword}' 在文件名中，加 20 分")
            
            # 部分匹配（关键词包含文件名的一部分）
            elif name_without_ext in keyword_lower:
                score += 10
                logger.debug(f"文件名包含在关键词 '{keyword}' 中，加 10 分")
        
        final_score = min(score, 100)  # 最高 100 分
        logger.debug(f"文件 {filename} 的最终相关度分数：{final_score}")
        return final_score
    
    def _get_matched_keywords(self, filename: str, keywords: List[str]) -> List[str]:
        """获取匹配的关键词"""
        matched = []
        filename_lower = filename.lower()
        
        for keyword in keywords:
            if keyword.lower() in filename_lower:
                matched.append(keyword)
        
        return matched
    
    def add_to_session_knowledge_base(self, 
                                       session_id: str, 
                                       file_paths: List[str]) -> bool:
        """
        添加文件到会话知识库
        
        Args:
            session_id: 会话 ID
            file_paths: 文件路径列表
            
        Returns:
            是否成功
        """
        logger.info(f"开始添加文件到会话知识库，会话 ID：{session_id}，文件数量：{len(file_paths)}")
        
        if session_id not in self.session_knowledge_base:
            self.session_knowledge_base[session_id] = {
                'files': {},
                'created_at': datetime.now().isoformat()
            }
            logger.info(f"为会话 {session_id} 创建新的知识库")
        
        added_count = 0
        skipped_count = 0
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                file_stat = os.stat(file_path)
                _, filename = os.path.split(file_path)
                _, ext = os.path.splitext(filename)
                
                self.session_knowledge_base[session_id]['files'][file_path] = {
                    'filename': filename,
                    'extension': ext.lower(),
                    'size': file_stat.st_size,
                    'added_at': datetime.now().isoformat()
                }
                logger.info(f"成功添加文件到知识库：{filename} (大小：{file_stat.st_size} 字节)")
                added_count += 1
            else:
                logger.warning(f"跳过不存在的文件：{file_path}")
                skipped_count += 1
        
        logger.info(f"文件添加完成，会话 {session_id}：成功添加 {added_count} 个文件，跳过 {skipped_count} 个文件")
        return True
    
    def get_session_knowledge_base(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话知识库
        
        Args:
            session_id: 会话 ID
            
        Returns:
            知识库信息
        """
        return self.session_knowledge_base.get(session_id, {
            'files': {},
            'created_at': None
        })
    
    def clear_session_knowledge_base(self, session_id: str) -> bool:
        """
        清空会话知识库
        
        Args:
            session_id: 会话 ID
            
        Returns:
            是否成功
        """
        logger.info(f"开始清空会话知识库，会话 ID：{session_id}")
        
        if session_id in self.session_knowledge_base:
            file_count = len(self.session_knowledge_base[session_id].get('files', {}))
            del self.session_knowledge_base[session_id]
            logger.info(f"成功清空会话 {session_id} 的知识库，共删除 {file_count} 个文件")
            return True
        else:
            logger.warning(f"会话 {session_id} 的知识库不存在，无需清空")
            return False
    
    def search_in_session_knowledge_base(self, 
                                          session_id: str, 
                                          query: str = None,
                                          keywords: List[str] = None) -> List[Dict[str, Any]]:
        """
        在会话知识库中搜索
        
        Args:
            session_id: 会话 ID
            query: 查询语句
            keywords: 关键词
            
        Returns:
            匹配的文件信息
        """
        kb = self.get_session_knowledge_base(session_id)
        if not kb['files']:
            return []
        
        # 提取关键词
        if keywords is None and query:
            keywords = self.extract_keywords(query)
        
        results = []
        for file_path, file_info in kb['files'].items():
            if os.path.exists(file_path):
                score = self._calculate_relevance(file_info['filename'], keywords or [])
                if score > 0:
                    results.append({
                        'file_path': file_path,
                        'filename': file_info['filename'],
                        'extension': file_info['extension'],
                        'size': file_info['size'],
                        'relevance_score': score,
                        'from_knowledge_base': True
                    })
        
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results
    
    def read_file_content(self, file_path: str, max_length: int = 10000) -> Optional[str]:
        """
        读取文件内容（仅支持文本类文件）
        
        Args:
            file_path: 文件路径
            max_length: 最大读取长度
            
        Returns:
            文件内容或 None
        """
        logger.info(f"开始读取文件内容，文件路径：{file_path}，最大长度：{max_length}")
        
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在：{file_path}")
            return None
        
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # 只读取文本类文件
        text_extensions = {'.txt', '.md', '.json', '.xml', '.yaml', '.yml', '.csv'}
        if ext not in text_extensions:
            logger.warning(f"不支持读取 {ext} 类型文件的内容，文件：{file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(max_length)
            logger.info(f"成功读取文件内容，文件：{file_path}，读取长度：{len(content)} 字符")
            return content
        except Exception as e:
            logger.error(f"读取文件 {file_path} 失败：{str(e)}")
            return None
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        获取文件详细信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        logger.info(f"开始获取文件信息，文件路径：{file_path}")
        
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在：{file_path}")
            return None
        
        try:
            file_stat = os.stat(file_path)
            _, filename = os.path.split(file_path)
            _, ext = os.path.splitext(filename)
            
            file_info = {
                'file_path': file_path,
                'filename': filename,
                'extension': ext.lower(),
                'size': file_stat.st_size,
                'created_time': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                'is_readable': ext.lower() in {'.txt', '.md', '.json', '.xml', '.yaml', '.yml', '.csv'}
            }
            
            logger.info(f"成功获取文件信息，文件：{filename}，大小：{file_stat.st_size} 字节")
            return file_info
        except Exception as e:
            logger.error(f"获取文件信息失败，文件：{file_path}，错误：{str(e)}")
            return None


# 全局文件检索服务实例
file_retrieval_service = FileRetrievalService()


def init_file_retrieval_service(search_paths: List[str] = None) -> FileRetrievalService:
    """初始化文件检索服务"""
    global file_retrieval_service
    file_retrieval_service = FileRetrievalService(search_paths)
    return file_retrieval_service
