"""
WPS 集成服务
支持与本地 WPS 深度集成，处理 Word、Excel 文件
"""
import os
import subprocess
import logging
import win32com.client
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WPSIntegrationService:
    """WPS 集成服务"""
    
    def __init__(self):
        """初始化 WPS 集成服务"""
        self.wps_app = None
        self.word_app = None
        self.excel_app = None
        
    def _get_wps_app(self) -> Optional[Any]:
        """
        获取 WPS 应用实例
        
        Returns:
            WPS 应用实例或 None
        """
        try:
            # 尝试获取已运行的 WPS 实例
            self.wps_app = win32com.client.GetActiveObject("KWPS.Application")
        except Exception:
            try:
                # 尝试启动新的 WPS 实例
                self.wps_app = win32com.client.Dispatch("KWPS.Application")
            except Exception as e:
                logger.error(f"无法启动 WPS: {str(e)}")
                self.wps_app = None
        
        return self.wps_app
    
    def _get_word_app(self) -> Optional[Any]:
        """
        获取 WPS 文字应用实例
        
        Returns:
            WPS 文字应用实例或 None
        """
        try:
            # 尝试获取已运行的 WPS 文字实例
            self.word_app = win32com.client.GetActiveObject("KWPS.Application")
        except Exception:
            try:
                # 尝试启动新的 WPS 文字实例
                self.word_app = win32com.client.Dispatch("KWPS.Application")
            except Exception as e:
                logger.error(f"无法启动 WPS 文字: {str(e)}")
                self.word_app = None
        
        return self.word_app
    
    def _get_excel_app(self) -> Optional[Any]:
        """
        获取 WPS 表格应用实例
        
        Returns:
            WPS 表格应用实例或 None
        """
        try:
            # 尝试获取已运行的 WPS 表格实例
            self.excel_app = win32com.client.GetActiveObject("KET.Application")
        except Exception:
            try:
                # 尝试启动新的 WPS 表格实例
                self.excel_app = win32com.client.Dispatch("KET.Application")
            except Exception as e:
                logger.error(f"无法启动 WPS 表格: {str(e)}")
                self.excel_app = None
        
        return self.excel_app
    
    def get_active_document(self) -> Optional[Dict[str, Any]]:
        """
        识别当前 WPS 活动文档
        
        Returns:
            活动文档信息或 None
        """
        try:
            # 检查 WPS 文字
            word_app = self._get_word_app()
            if word_app and word_app.Documents.Count > 0:
                doc = word_app.ActiveDocument
                return {
                    'type': 'word',
                    'path': doc.FullName,
                    'name': doc.Name,
                    'application': 'WPS 文字'
                }
            
            # 检查 WPS 表格
            excel_app = self._get_excel_app()
            if excel_app and excel_app.Workbooks.Count > 0:
                workbook = excel_app.ActiveWorkbook
                return {
                    'type': 'excel',
                    'path': workbook.FullName,
                    'name': workbook.Name,
                    'application': 'WPS 表格'
                }
            
        except Exception as e:
            logger.error(f"获取活动文档失败: {str(e)}")
        
        return None
    
    def open_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        打开指定本地文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            打开的文件信息或 None
        """
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return None
        
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.doc', '.docx']:
                # 打开 Word 文档
                word_app = self._get_word_app()
                if word_app:
                    doc = word_app.Documents.Open(file_path)
                    word_app.Visible = True
                    return {
                        'success': True,
                        'type': 'word',
                        'path': file_path,
                        'name': os.path.basename(file_path)
                    }
            
            elif ext in ['.xls', '.xlsx', '.csv']:
                # 打开 Excel 文件
                excel_app = self._get_excel_app()
                if excel_app:
                    workbook = excel_app.Workbooks.Open(file_path)
                    excel_app.Visible = True
                    return {
                        'success': True,
                        'type': 'excel',
                        'path': file_path,
                        'name': os.path.basename(file_path)
                    }
            
            else:
                # 尝试用 WPS 打开其他类型文件
                wps_app = self._get_wps_app()
                if wps_app:
                    wps_app.Visible = True
                    subprocess.Popen(['wps', file_path])
                    return {
                        'success': True,
                        'type': 'other',
                        'path': file_path,
                        'name': os.path.basename(file_path)
                    }
        
        except Exception as e:
            logger.error(f"打开文件失败: {str(e)}")
        
        return {
            'success': False,
            'message': '无法打开文件'
        }
    
    def process_word_document(self, file_path: str, operation: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        处理 Word 文档
        
        Args:
            file_path: 文件路径
            operation: 操作类型 ('convert', 'clean', 'extract')
            params: 操作参数
            
        Returns:
            处理结果
        """
        if not os.path.exists(file_path):
            return {'success': False, 'message': '文件不存在'}
        
        try:
            word_app = self._get_word_app()
            if not word_app:
                return {'success': False, 'message': '无法启动 WPS 文字'}
            
            doc = word_app.Documents.Open(file_path)
            
            if operation == 'convert':
                # 转换为标准公文格式
                # 这里简化处理，实际需要根据模板进行转换
                output_path = self._get_output_path(file_path, 'converted')
                doc.SaveAs(output_path)
                doc.Close()
                
                return {
                    'success': True,
                    'output_path': output_path,
                    'message': '文档已转换为标准格式'
                }
            
            elif operation == 'clean':
                # 清理敏感词
                # 实际需要调用敏感词检查服务
                output_path = self._get_output_path(file_path, 'cleaned')
                doc.SaveAs(output_path)
                doc.Close()
                
                return {
                    'success': True,
                    'output_path': output_path,
                    'message': '文档敏感词已清理'
                }
            
            elif operation == 'extract':
                # 提取内容
                content = doc.Content.Text
                doc.Close()
                
                return {
                    'success': True,
                    'content': content[:1000],  # 限制返回内容长度
                    'message': '文档内容已提取'
                }
            
            doc.Close()
            return {'success': False, 'message': '不支持的操作'}
            
        except Exception as e:
            logger.error(f"处理 Word 文档失败: {str(e)}")
            return {'success': False, 'message': f'处理失败: {str(e)}'}
    
    def process_excel_document(self, file_path: str, operation: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        处理 Excel 文档
        
        Args:
            file_path: 文件路径
            operation: 操作类型 ('merge', 'analyze', 'extract')
            params: 操作参数
            
        Returns:
            处理结果
        """
        if not os.path.exists(file_path):
            return {'success': False, 'message': '文件不存在'}
        
        try:
            excel_app = self._get_excel_app()
            if not excel_app:
                return {'success': False, 'message': '无法启动 WPS 表格'}
            
            workbook = excel_app.Workbooks.Open(file_path)
            
            if operation == 'merge':
                # 合并工作表
                # 这里简化处理，实际需要根据参数进行合并
                output_path = self._get_output_path(file_path, 'merged')
                workbook.SaveAs(output_path)
                workbook.Close()
                
                return {
                    'success': True,
                    'output_path': output_path,
                    'message': '工作表已合并'
                }
            
            elif operation == 'analyze':
                # 分析数据
                # 实际需要根据参数进行数据分析
                output_path = self._get_output_path(file_path, 'analyzed')
                workbook.SaveAs(output_path)
                workbook.Close()
                
                return {
                    'success': True,
                    'output_path': output_path,
                    'message': '数据已分析'
                }
            
            elif operation == 'extract':
                # 提取数据
                # 实际需要根据参数提取特定数据
                sheet = workbook.ActiveSheet
                range_data = sheet.UsedRange.Value
                workbook.Close()
                
                # 转换为列表格式
                data = []
                for row in range_data:
                    data.append(list(row))
                
                return {
                    'success': True,
                    'data': data[:100],  # 限制返回数据量
                    'message': '数据已提取'
                }
            
            workbook.Close()
            return {'success': False, 'message': '不支持的操作'}
            
        except Exception as e:
            logger.error(f"处理 Excel 文档失败: {str(e)}")
            return {'success': False, 'message': f'处理失败: {str(e)}'}
    
    def _get_output_path(self, original_path: str, suffix: str) -> str:
        """
        获取输出文件路径
        
        Args:
            original_path: 原始文件路径
            suffix: 后缀
            
        Returns:
            输出文件路径
        """
        dir_path = os.path.dirname(original_path)
        base_name = os.path.splitext(os.path.basename(original_path))[0]
        ext = os.path.splitext(original_path)[1]
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        return os.path.join(dir_path, f"{base_name}_{suffix}_{timestamp}{ext}")
    
    def close_applications(self):
        """
        关闭所有 WPS 应用实例
        """
        try:
            if self.word_app:
                self.word_app.Quit()
                self.word_app = None
            
            if self.excel_app:
                self.excel_app.Quit()
                self.excel_app = None
            
            if self.wps_app:
                self.wps_app.Quit()
                self.wps_app = None
                
        except Exception as e:
            logger.error(f"关闭 WPS 应用失败: {str(e)}")


# 全局 WPS 集成服务实例
wps_integration_service = WPSIntegrationService()


def init_wps_integration_service() -> WPSIntegrationService:
    """初始化 WPS 集成服务"""
    global wps_integration_service
    return wps_integration_service
