"""
Skills 能力模块初始化
"""
from .base_skill import BaseSkill
from .document_skill import DocumentSkill
from .sensitive_word_skill import SensitiveWordSkill
from .data_merge_skill import DataMergeSkill

__all__ = [
    'BaseSkill',
    'DocumentSkill',
    'SensitiveWordSkill',
    'DataMergeSkill'
]
