"""
数据合并 Skill
支持 Excel/CSV 文件合并、数据比对等功能
"""
from .base_skill import BaseSkill
from typing import Dict, Any, List
import os
import logging

logger = logging.getLogger(__name__)


class DataMergeSkill(BaseSkill):
    """数据合并 Skill"""
    
    def __init__(self):
        super().__init__(
            skill_id='data_merger',
            name='数据合并',
            description='支持 Excel/CSV 文件合并、数据比对、统计等功能'
        )
    
    def validate_params(self, params: Dict[str, Any]) -> tuple:
        """验证参数"""
        errors = []
        
        if 'action' not in params:
            errors.append('缺少 action 参数')
        
        if params.get('action') in ['merge_files', 'compare_files']:
            if 'file_paths' not in params or not params['file_paths']:
                errors.append('需要提供 file_paths 参数')
        
        return len(errors) == 0, errors
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行数据合并"""
        try:
            action = params.get('action')
            
            if action == 'merge_files':
                return self._merge_files(params)
            elif action == 'compare_files':
                return self._compare_files(params)
            elif action == 'statistics':
                return self._statistics(params)
            else:
                return {
                    'success': False,
                    'message': f'未知的操作类型：{action}'
                }
                
        except Exception as e:
            logger.error(f"数据合并失败：{str(e)}")
            return {
                'success': False,
                'message': f'处理失败：{str(e)}'
            }
    
    def _merge_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """合并多个文件"""
        import pandas as pd
        
        file_paths = params.get('file_paths', [])
        merge_key = params.get('merge_key')  # 合并键
        output_path = params.get('output_path', 'merged_output.xlsx')
        sheet_name = params.get('sheet_name', 'Sheet1')
        
        if not file_paths:
            return {
                'success': False,
                'message': '未提供文件路径'
            }
        
        # 读取所有文件
        dataframes = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"文件不存在：{file_path}")
                continue
            
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                dataframes.append(df)
            except Exception as e:
                logger.error(f"读取文件失败 {file_path}: {e}")
        
        if not dataframes:
            return {
                'success': False,
                'message': '未能读取任何有效文件'
            }
        
        # 合并数据
        if merge_key:
            # 按指定键合并（类似 SQL JOIN）
            merged_df = dataframes[0]
            for df in dataframes[1:]:
                merged_df = pd.merge(merged_df, df, on=merge_key, how='outer')
        else:
            # 直接拼接
            merged_df = pd.concat(dataframes, ignore_index=True)
        
        # 保存结果
        merged_df.to_excel(output_path, index=False)
        
        self.log_execution('merge_files', f'已合并 {len(file_paths)} 个文件，输出：{output_path}')
        
        return {
            'success': True,
            'message': f'成功合并 {len(dataframes)} 个文件',
            'file_path': os.path.abspath(output_path),
            'data': {
                'total_rows': len(merged_df),
                'total_columns': len(merged_df.columns),
                'columns': list(merged_df.columns)
            }
        }
    
    def _compare_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """比对两个文件"""
        import pandas as pd
        
        file_paths = params.get('file_paths', [])
        compare_key = params.get('compare_key')  # 比对键
        
        if len(file_paths) < 2:
            return {
                'success': False,
                'message': '至少需要提供两个文件路径'
            }
        
        # 读取文件
        df1 = pd.read_excel(file_paths[0]) if file_paths[0].endswith('.xlsx') else pd.read_csv(file_paths[0])
        df2 = pd.read_excel(file_paths[1]) if file_paths[1].endswith('.xlsx') else pd.read_csv(file_paths[1])
        
        # 比对
        if compare_key:
            # 找出差异
            keys1 = set(df1[compare_key].unique())
            keys2 = set(df2[compare_key].unique())
            
            only_in_file1 = keys1 - keys2
            only_in_file2 = keys2 - keys1
            common = keys1 & keys2
            
            result = {
                'only_in_file1': list(only_in_file1),
                'only_in_file2': list(only_in_file2),
                'common': list(common),
                'count_only_in_file1': len(only_in_file1),
                'count_only_in_file2': len(only_in_file2),
                'count_common': len(common)
            }
        else:
            # 简单比对
            result = {
                'file1_shape': list(df1.shape),
                'file2_shape': list(df2.shape),
                'file1_columns': list(df1.columns),
                'file2_columns': list(df2.columns)
            }
        
        return {
            'success': True,
            'message': '比对完成',
            'data': result
        }
    
    def _statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """数据统计"""
        import pandas as pd
        
        file_path = params.get('file_path')
        group_by = params.get('group_by')  # 分组字段
        aggregate = params.get('aggregate')  # 聚合字段
        
        if not file_path or not os.path.exists(file_path):
            return {
                'success': False,
                'message': '文件路径无效'
            }
        
        # 读取文件
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # 统计
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        if group_by and group_by in df.columns:
            grouped = df.groupby(group_by)
            stats['group_stats'] = {}
            for name, group in grouped:
                stats['group_stats'][str(name)] = len(group)
        
        return {
            'success': True,
            'message': '统计完成',
            'data': stats
        }
