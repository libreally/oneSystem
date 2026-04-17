"""
意图分析模型

实现基于机器学习的意图分析，支持自主学习和自我修改能力
"""
import os
import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class IntentModel:
    """意图分析模型类"""
    
    def __init__(self, model_path="models/intent_model"):
        """
        初始化意图模型
        
        Args:
            model_path: 模型保存路径
        """
        self.model_path = model_path
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression(max_iter=1000)
        self.intent_mapping = {}
        self.reverse_intent_mapping = {}
        self.training_data = []
        self.is_trained = False
        
        # 创建模型目录
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # 尝试加载已训练的模型
        self.load_model()
    
    def load_model(self):
        """加载已训练的模型"""
        try:
            if os.path.exists(f"{self.model_path}_vectorizer.pkl") and os.path.exists(f"{self.model_path}_model.pkl") and os.path.exists(f"{self.model_path}_mapping.json"):
                with open(f"{self.model_path}_vectorizer.pkl", "rb") as f:
                    self.vectorizer = pickle.load(f)
                with open(f"{self.model_path}_model.pkl", "rb") as f:
                    self.model = pickle.load(f)
                with open(f"{self.model_path}_mapping.json", "r", encoding="utf-8") as f:
                    self.intent_mapping = json.load(f)
                # 创建反向映射
                self.reverse_intent_mapping = {v: k for k, v in self.intent_mapping.items()}
                self.is_trained = True
                logger.info("加载意图模型成功")
            else:
                logger.info("没有找到已训练的模型，将使用新模型")
        except Exception as e:
            logger.error(f"加载模型失败：{str(e)}")
    
    def save_model(self):
        """保存模型"""
        try:
            with open(f"{self.model_path}_vectorizer.pkl", "wb") as f:
                pickle.dump(self.vectorizer, f)
            with open(f"{self.model_path}_model.pkl", "wb") as f:
                pickle.dump(self.model, f)
            with open(f"{self.model_path}_mapping.json", "w", encoding="utf-8") as f:
                json.dump(self.intent_mapping, f, ensure_ascii=False, indent=2)
            logger.info("保存意图模型成功")
        except Exception as e:
            logger.error(f"保存模型失败：{str(e)}")
    
    def add_training_data(self, intent, examples):
        """
        添加训练数据
        
        Args:
            intent: 意图名称
            examples: 示例句子列表
        """
        for example in examples:
            self.training_data.append((example, intent))
    
    def train(self):
        """训练模型"""
        if not self.training_data:
            logger.warning("没有训练数据，无法训练模型")
            return
        
        # 准备训练数据
        X = [item[0] for item in self.training_data]
        y = [item[1] for item in self.training_data]
        
        # 创建意图映射
        unique_intents = list(set(y))
        self.intent_mapping = {intent: i for i, intent in enumerate(unique_intents)}
        self.reverse_intent_mapping = {v: k for k, v in self.intent_mapping.items()}
        
        # 将意图转换为数字
        y_encoded = [self.intent_mapping[intent] for intent in y]
        
        # 分割训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
        
        # 特征提取
        self.vectorizer.fit(X_train)
        X_train_vectors = self.vectorizer.transform(X_train)
        X_test_vectors = self.vectorizer.transform(X_test)
        
        # 训练模型
        self.model.fit(X_train_vectors, y_train)
        
        # 评估模型
        y_pred = self.model.predict(X_test_vectors)
        y_test_labels = [self.reverse_intent_mapping[yi] for yi in y_test]
        y_pred_labels = [self.reverse_intent_mapping[yi] for yi in y_pred]
        
        logger.info("模型评估结果：")
        logger.info(classification_report(y_test_labels, y_pred_labels))
        
        # 保存模型
        self.save_model()
        self.is_trained = True
        
        logger.info("模型训练完成")
    
    def predict(self, text):
        """
        预测意图
        
        Args:
            text: 输入文本
            
        Returns:
            意图名称和置信度
        """
        if not self.is_trained:
            logger.warning("模型未训练，返回默认意图")
            return "unknown", 0.0
        
        try:
            # 特征提取
            text_vector = self.vectorizer.transform([text])
            
            # 预测意图
            intent_code = self.model.predict(text_vector)[0]
            intent = self.reverse_intent_mapping[intent_code]
            
            # 计算置信度
            proba = self.model.predict_proba(text_vector)[0]
            confidence = max(proba)
            
            logger.info(f"预测意图：{intent}，置信度：{confidence}")
            return intent, confidence
        except Exception as e:
            logger.error(f"预测意图失败：{str(e)}")
            return "unknown", 0.0
    
    def learn_from_feedback(self, text, correct_intent):
        """
        从反馈中学习
        
        Args:
            text: 输入文本
            correct_intent: 正确的意图
        """
        # 添加到训练数据
        self.add_training_data(correct_intent, [text])
        
        # 重新训练模型
        self.train()
        
        logger.info(f"从反馈中学习：文本='{text}'，正确意图='{correct_intent}'")
    
    def get_intents(self):
        """
        获取所有意图
        
        Returns:
            意图列表
        """
        return list(self.intent_mapping.keys())

# 初始化意图模型实例
intent_model = None

def get_intent_model():
    """
    获取意图模型实例
    
    Returns:
        意图模型实例
    """
    global intent_model
    if intent_model is None:
        intent_model = IntentModel()
    return intent_model

# 初始化默认训练数据
def init_default_training_data():
    """初始化默认训练数据"""
    model = get_intent_model()
    
    # 添加默认训练数据
    model.add_training_data('permission_manage', [
        '查看用户', '用户管理', '角色管理', '权限管理', '创建用户', '删除用户', '修改用户', '查看权限',
        '用户列表', '查看用户列表', '管理用户', '管理角色', '管理权限'
    ])
    
    model.add_training_data('task_manage', [
        '查看任务', '任务管理', '任务列表', '查看任务列表', '任务汇总', '工作总结', '工作汇报',
        '完成任务', '更新任务', '管理任务', '查看任务状态'
    ])
    
    model.add_training_data('config_manage', [
        '配置管理', '获取配置', '保存配置', '删除配置', '导入配置', '导出配置', '用户偏好',
        '系统配置', '管理配置', '查看配置'
    ])
    
    model.add_training_data('file_retrieval', [
        '搜索文件', '文件检索', '查找文件', '文件列表', '查看文件', '管理文件', '检索文件'
    ])
    
    model.add_training_data('integration_manage', [
        '集成管理', '添加集成', '删除集成', '修改集成', '查看集成', '管理集成', '系统集成'
    ])
    
    # 训练模型
    model.train()

# 初始化
if __name__ == "__main__":
    init_default_training_data()
