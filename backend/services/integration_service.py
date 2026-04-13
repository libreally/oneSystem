"""
业务系统适配器框架
支持对接 OA、ERP、CRM 等第三方业务系统
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SystemType(Enum):
    """系统类型"""
    OA = 'oa'  # 办公自动化
    ERP = 'erp'  # 企业资源计划
    CRM = 'crm'  # 客户关系管理
    HR = 'hr'  # 人力资源
    FINANCE = 'finance'  # 财务系统
    PROJECT = 'project'  # 项目管理
    CUSTOM = 'custom'  # 自定义


@dataclass
class SystemConfig:
    """系统配置"""
    system_id: str
    system_name: str
    system_type: SystemType
    base_url: str
    api_key: str = ''
    username: str = ''
    password: str = ''
    auth_type: str = 'api_key'  # api_key, basic, oauth2
    timeout: int = 30
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'system_id': self.system_id,
            'system_name': self.system_name,
            'system_type': self.system_type.value,
            'base_url': self.base_url,
            'auth_type': self.auth_type,
            'timeout': self.timeout,
            'enabled': self.enabled
        }


@dataclass
class TaskItem:
    """任务项"""
    task_id: str
    title: str
    description: str = ''
    status: str = 'pending'  # pending, in_progress, completed, cancelled
    priority: str = 'medium'  # low, medium, high, urgent
    source_system: str = ''
    assignee: str = ''
    due_date: datetime = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'source_system': self.source_system,
            'assignee': self.assignee,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }


class BaseSystemAdapter(ABC):
    """业务系统适配器基类"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.connected = False
        self._client = None
    
    @abstractmethod
    def connect(self) -> bool:
        """连接到系统"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开连接"""
        pass
    
    @abstractmethod
    def get_tasks(self, filters: Dict[str, Any] = None) -> List[TaskItem]:
        """获取任务列表"""
        pass
    
    @abstractmethod
    def create_task(self, task_data: Dict[str, Any]) -> TaskItem:
        """创建任务"""
        pass
    
    @abstractmethod
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> TaskItem:
        """更新任务"""
        pass
    
    @abstractmethod
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        pass
    
    @abstractmethod
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """获取用户信息"""
        pass
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            return self.connect()
        except Exception as e:
            logger.error(f"连接测试失败：{str(e)}")
            return False
    
    def sync_tasks(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """同步任务（默认实现）"""
        tasks = self.get_tasks(filters)
        return [task.to_dict() for task in tasks]


class MockSystemAdapter(BaseSystemAdapter):
    """模拟系统适配器（用于开发和测试）"""
    
    def __init__(self, config: SystemConfig):
        super().__init__(config)
        self.mock_tasks = self._generate_mock_tasks()
    
    def _generate_mock_tasks(self) -> List[TaskItem]:
        """生成模拟任务"""
        return [
            TaskItem(
                task_id=f"{self.config.system_id}_task_001",
                title="审批流程 - 采购申请",
                description="需要审批的采购申请单",
                status='pending',
                priority='high',
                source_system=self.config.system_id,
                assignee='admin',
                due_date=datetime.now().replace(hour=18, minute=0),
                metadata={'type': 'approval', 'amount': 5000}
            ),
            TaskItem(
                task_id=f"{self.config.system_id}_task_002",
                title="项目进度报告",
                description="提交本周项目进度报告",
                status='in_progress',
                priority='medium',
                source_system=self.config.system_id,
                assignee='admin',
                due_date=datetime.now().replace(day=25),
                metadata={'type': 'report', 'project_id': 'P001'}
            ),
            TaskItem(
                task_id=f"{self.config.system_id}_task_003",
                title="客户回访",
                description="对重点客户进行季度回访",
                status='pending',
                priority='low',
                source_system=self.config.system_id,
                assignee='admin',
                due_date=datetime.now().replace(month=12, day=31),
                metadata={'type': 'follow_up', 'customer_count': 10}
            )
        ]
    
    def connect(self) -> bool:
        """连接系统"""
        logger.info(f"连接到模拟系统：{self.config.system_name}")
        self.connected = True
        return True
    
    def disconnect(self):
        """断开连接"""
        logger.info(f"断开模拟系统连接：{self.config.system_name}")
        self.connected = False
    
    def get_tasks(self, filters: Dict[str, Any] = None) -> List[TaskItem]:
        """获取任务"""
        if not self.connected:
            raise Exception("未连接到系统")
        
        tasks = self.mock_tasks.copy()
        
        # 应用过滤器
        if filters:
            if 'status' in filters:
                tasks = [t for t in tasks if t.status == filters['status']]
            if 'priority' in filters:
                tasks = [t for t in tasks if t.priority == filters['priority']]
            if 'assignee' in filters:
                tasks = [t for t in tasks if t.assignee == filters['assignee']]
        
        return tasks
    
    def create_task(self, task_data: Dict[str, Any]) -> TaskItem:
        """创建任务"""
        task = TaskItem(
            task_id=f"{self.config.system_id}_task_{len(self.mock_tasks) + 1:03d}",
            title=task_data.get('title', '新任务'),
            description=task_data.get('description', ''),
            status=task_data.get('status', 'pending'),
            priority=task_data.get('priority', 'medium'),
            source_system=self.config.system_id,
            assignee=task_data.get('assignee', ''),
            metadata=task_data.get('metadata', {})
        )
        self.mock_tasks.append(task)
        logger.info(f"创建任务：{task.task_id}")
        return task
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> TaskItem:
        """更新任务"""
        for task in self.mock_tasks:
            if task.task_id == task_id:
                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                task.updated_at = datetime.now()
                logger.info(f"更新任务：{task_id}")
                return task
        
        raise ValueError(f"任务不存在：{task_id}")
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        for i, task in enumerate(self.mock_tasks):
            if task.task_id == task_id:
                self.mock_tasks.pop(i)
                logger.info(f"删除任务：{task_id}")
                return True
        
        return False
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """获取用户信息"""
        return {
            'user_id': user_id,
            'username': user_id,
            'display_name': f'用户 {user_id}',
            'email': f'{user_id}@example.com',
            'department': '测试部门',
            'role': 'user'
        }


class AdapterFactory:
    """适配器工厂"""
    
    _adapters: Dict[str, BaseSystemAdapter] = {}
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register_adapter(cls, system_type: SystemType, adapter_class: type):
        """注册适配器类型"""
        cls._registry[system_type.value] = adapter_class
        logger.info(f"注册适配器：{system_type.value} -> {adapter_class.__name__}")
    
    @classmethod
    def create_adapter(cls, config: SystemConfig) -> BaseSystemAdapter:
        """创建适配器实例"""
        # 如果已存在，返回缓存的实例
        if config.system_id in cls._adapters:
            return cls._adapters[config.system_id]
        
        # 查找适配器类型
        adapter_class = cls._registry.get(
            config.system_type.value, 
            MockSystemAdapter  # 默认使用模拟适配器
        )
        
        # 创建实例
        adapter = adapter_class(config)
        cls._adapters[config.system_id] = adapter
        
        logger.info(f"创建适配器：{config.system_id} ({config.system_type.value})")
        return adapter
    
    @classmethod
    def get_adapter(cls, system_id: str) -> Optional[BaseSystemAdapter]:
        """获取适配器实例"""
        return cls._adapters.get(system_id)
    
    @classmethod
    def remove_adapter(cls, system_id: str) -> bool:
        """移除适配器"""
        if system_id in cls._adapters:
            adapter = cls._adapters[system_id]
            adapter.disconnect()
            del cls._adapters[system_id]
            logger.info(f"移除适配器：{system_id}")
            return True
        return False
    
    @classmethod
    def list_adapters(cls) -> List[Dict[str, Any]]:
        """列出所有适配器"""
        return [
            {
                'system_id': adapter.config.system_id,
                'system_name': adapter.config.system_name,
                'system_type': adapter.config.system_type.value,
                'connected': adapter.connected,
                'enabled': adapter.config.enabled
            }
            for adapter in cls._adapters.values()
        ]


# 注册默认适配器
AdapterFactory.register_adapter(SystemType.CUSTOM, MockSystemAdapter)


class OASystemAdapter(BaseSystemAdapter):
    """OA 系统适配器"""
    
    def connect(self) -> bool:
        """连接到 OA 系统"""
        logger.info(f"连接到 OA 系统：{self.config.system_name}")
        # 实际实现需要根据具体 OA 系统的 API 进行连接
        self.connected = True
        return True
    
    def disconnect(self):
        """断开连接"""
        logger.info(f"断开 OA 系统连接：{self.config.system_name}")
        self.connected = False
    
    def get_tasks(self, filters: Dict[str, Any] = None) -> List[TaskItem]:
        """获取任务列表"""
        if not self.connected:
            raise Exception("未连接到系统")
        
        # 实际实现需要调用 OA 系统的 API
        # 这里返回模拟数据
        tasks = [
            TaskItem(
                task_id=f"{self.config.system_id}_approval_001",
                title="审批：采购申请单",
                description="采购部门提交的办公用品采购申请",
                status='pending',
                priority='high',
                source_system=self.config.system_id,
                assignee='admin',
                due_date=datetime.now().replace(hour=17, minute=0),
                metadata={'form_id': 'PR001', 'amount': 3500}
            ),
            TaskItem(
                task_id=f"{self.config.system_id}_leave_001",
                title="审批：请假申请",
                description="张三的年假申请，共计3天",
                status='in_progress',
                priority='medium',
                source_system=self.config.system_id,
                assignee='admin',
                due_date=datetime.now().replace(hour=12, minute=0),
                metadata={'employee_id': 'E001', 'days': 3}
            )
        ]
        
        # 应用过滤器
        if filters:
            if 'status' in filters:
                tasks = [t for t in tasks if t.status == filters['status']]
            if 'priority' in filters:
                tasks = [t for t in tasks if t.priority == filters['priority']]
        
        return tasks
    
    def create_task(self, task_data: Dict[str, Any]) -> TaskItem:
        """创建任务"""
        task = TaskItem(
            task_id=f"{self.config.system_id}_task_{int(datetime.now().timestamp())}",
            title=task_data.get('title', '新任务'),
            description=task_data.get('description', ''),
            status=task_data.get('status', 'pending'),
            priority=task_data.get('priority', 'medium'),
            source_system=self.config.system_id,
            assignee=task_data.get('assignee', ''),
            metadata=task_data.get('metadata', {})
        )
        logger.info(f"在 OA 系统创建任务：{task.task_id}")
        return task
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> TaskItem:
        """更新任务"""
        # 实际实现需要调用 OA 系统的 API
        # 这里返回模拟数据
        task = TaskItem(
            task_id=task_id,
            title=updates.get('title', '任务标题'),
            description=updates.get('description', ''),
            status=updates.get('status', 'pending'),
            priority=updates.get('priority', 'medium'),
            source_system=self.config.system_id,
            assignee=updates.get('assignee', ''),
            metadata=updates.get('metadata', {})
        )
        logger.info(f"在 OA 系统更新任务：{task_id}")
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        logger.info(f"在 OA 系统删除任务：{task_id}")
        return True
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """获取用户信息"""
        return {
            'user_id': user_id,
            'username': user_id,
            'display_name': f'OA 用户 {user_id}',
            'email': f'{user_id}@oa.example.com',
            'department': '行政部',
            'role': 'employee'
        }


class ERPSystemAdapter(BaseSystemAdapter):
    """ERP 系统适配器"""
    
    def connect(self) -> bool:
        """连接到 ERP 系统"""
        logger.info(f"连接到 ERP 系统：{self.config.system_name}")
        # 实际实现需要根据具体 ERP 系统的 API 进行连接
        self.connected = True
        return True
    
    def disconnect(self):
        """断开连接"""
        logger.info(f"断开 ERP 系统连接：{self.config.system_name}")
        self.connected = False
    
    def get_tasks(self, filters: Dict[str, Any] = None) -> List[TaskItem]:
        """获取任务列表"""
        if not self.connected:
            raise Exception("未连接到系统")
        
        # 实际实现需要调用 ERP 系统的 API
        # 这里返回模拟数据
        tasks = [
            TaskItem(
                task_id=f"{self.config.system_id}_po_001",
                title="处理：采购订单",
                description="供应商提交的采购订单需要确认",
                status='pending',
                priority='high',
                source_system=self.config.system_id,
                assignee='admin',
                due_date=datetime.now().replace(hour=15, minute=0),
                metadata={'po_id': 'PO001', 'supplier': '供应商A'}
            ),
            TaskItem(
                task_id=f"{self.config.system_id}_inv_001",
                title="处理：库存盘点",
                description="月底库存盘点任务",
                status='in_progress',
                priority='medium',
                source_system=self.config.system_id,
                assignee='admin',
                due_date=datetime.now().replace(day=30, hour=23, minute=59),
                metadata={'warehouse': '主仓库'}
            )
        ]
        
        # 应用过滤器
        if filters:
            if 'status' in filters:
                tasks = [t for t in tasks if t.status == filters['status']]
            if 'priority' in filters:
                tasks = [t for t in tasks if t.priority == filters['priority']]
        
        return tasks
    
    def create_task(self, task_data: Dict[str, Any]) -> TaskItem:
        """创建任务"""
        task = TaskItem(
            task_id=f"{self.config.system_id}_task_{int(datetime.now().timestamp())}",
            title=task_data.get('title', '新任务'),
            description=task_data.get('description', ''),
            status=task_data.get('status', 'pending'),
            priority=task_data.get('priority', 'medium'),
            source_system=self.config.system_id,
            assignee=task_data.get('assignee', ''),
            metadata=task_data.get('metadata', {})
        )
        logger.info(f"在 ERP 系统创建任务：{task.task_id}")
        return task
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> TaskItem:
        """更新任务"""
        # 实际实现需要调用 ERP 系统的 API
        # 这里返回模拟数据
        task = TaskItem(
            task_id=task_id,
            title=updates.get('title', '任务标题'),
            description=updates.get('description', ''),
            status=updates.get('status', 'pending'),
            priority=updates.get('priority', 'medium'),
            source_system=self.config.system_id,
            assignee=updates.get('assignee', ''),
            metadata=updates.get('metadata', {})
        )
        logger.info(f"在 ERP 系统更新任务：{task_id}")
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        logger.info(f"在 ERP 系统删除任务：{task_id}")
        return True
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """获取用户信息"""
        return {
            'user_id': user_id,
            'username': user_id,
            'display_name': f'ERP 用户 {user_id}',
            'email': f'{user_id}@erp.example.com',
            'department': '财务部',
            'role': 'employee'
        }


class CRMSystemAdapter(BaseSystemAdapter):
    """CRM 系统适配器"""
    
    def connect(self) -> bool:
        """连接到 CRM 系统"""
        logger.info(f"连接到 CRM 系统：{self.config.system_name}")
        # 实际实现需要根据具体 CRM 系统的 API 进行连接
        self.connected = True
        return True
    
    def disconnect(self):
        """断开连接"""
        logger.info(f"断开 CRM 系统连接：{self.config.system_name}")
        self.connected = False
    
    def get_tasks(self, filters: Dict[str, Any] = None) -> List[TaskItem]:
        """获取任务列表"""
        if not self.connected:
            raise Exception("未连接到系统")
        
        # 实际实现需要调用 CRM 系统的 API
        # 这里返回模拟数据
        tasks = [
            TaskItem(
                task_id=f"{self.config.system_id}_call_001",
                title="跟进：客户电话",
                description="需要给重要客户回电话",
                status='pending',
                priority='high',
                source_system=self.config.system_id,
                assignee='admin',
                due_date=datetime.now().replace(hour=14, minute=0),
                metadata={'customer_id': 'C001', 'contact': '王经理'}
            ),
            TaskItem(
                task_id=f"{self.config.system_id}_visit_001",
                title="安排：客户拜访",
                description="下周客户拜访计划",
                status='in_progress',
                priority='medium',
                source_system=self.config.system_id,
                assignee='admin',
                due_date=datetime.now().replace(day=15, hour=9, minute=0),
                metadata={'customer_id': 'C002', 'product': '产品A'}
            )
        ]
        
        # 应用过滤器
        if filters:
            if 'status' in filters:
                tasks = [t for t in tasks if t.status == filters['status']]
            if 'priority' in filters:
                tasks = [t for t in tasks if t.priority == filters['priority']]
        
        return tasks
    
    def create_task(self, task_data: Dict[str, Any]) -> TaskItem:
        """创建任务"""
        task = TaskItem(
            task_id=f"{self.config.system_id}_task_{int(datetime.now().timestamp())}",
            title=task_data.get('title', '新任务'),
            description=task_data.get('description', ''),
            status=task_data.get('status', 'pending'),
            priority=task_data.get('priority', 'medium'),
            source_system=self.config.system_id,
            assignee=task_data.get('assignee', ''),
            metadata=task_data.get('metadata', {})
        )
        logger.info(f"在 CRM 系统创建任务：{task.task_id}")
        return task
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> TaskItem:
        """更新任务"""
        # 实际实现需要调用 CRM 系统的 API
        # 这里返回模拟数据
        task = TaskItem(
            task_id=task_id,
            title=updates.get('title', '任务标题'),
            description=updates.get('description', ''),
            status=updates.get('status', 'pending'),
            priority=updates.get('priority', 'medium'),
            source_system=self.config.system_id,
            assignee=updates.get('assignee', ''),
            metadata=updates.get('metadata', {})
        )
        logger.info(f"在 CRM 系统更新任务：{task_id}")
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        logger.info(f"在 CRM 系统删除任务：{task_id}")
        return True
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """获取用户信息"""
        return {
            'user_id': user_id,
            'username': user_id,
            'display_name': f'CRM 用户 {user_id}',
            'email': f'{user_id}@crm.example.com',
            'department': '销售部',
            'role': 'sales'
        }


# 注册系统适配器
AdapterFactory.register_adapter(SystemType.OA, OASystemAdapter)
AdapterFactory.register_adapter(SystemType.ERP, ERPSystemAdapter)
AdapterFactory.register_adapter(SystemType.CRM, CRMSystemAdapter)


class SystemIntegrationService:
    """系统集成服务"""
    
    def __init__(self):
        self.factory = AdapterFactory()
        self.systems: Dict[str, SystemConfig] = {}
    
    def add_system(self, config: SystemConfig) -> bool:
        """添加业务系统"""
        if config.system_id in self.systems:
            logger.warning(f"系统已存在：{config.system_id}")
            return False
        
        self.systems[config.system_id] = config
        
        # 创建并连接适配器
        adapter = self.factory.create_adapter(config)
        if config.enabled:
            adapter.connect()
        
        logger.info(f"添加业务系统：{config.system_name}")
        return True
    
    def remove_system(self, system_id: str) -> bool:
        """移除业务系统"""
        if system_id not in self.systems:
            return False
        
        self.factory.remove_adapter(system_id)
        del self.systems[system_id]
        
        logger.info(f"移除业务系统：{system_id}")
        return True
    
    def enable_system(self, system_id: str) -> bool:
        """启用系统"""
        if system_id not in self.systems:
            return False
        
        self.systems[system_id].enabled = True
        adapter = self.factory.get_adapter(system_id)
        if adapter:
            adapter.connect()
        
        return True
    
    def disable_system(self, system_id: str) -> bool:
        """禁用系统"""
        if system_id not in self.systems:
            return False
        
        self.systems[system_id].enabled = False
        adapter = self.factory.get_adapter(system_id)
        if adapter:
            adapter.disconnect()
        
        return True
    
    def get_all_tasks(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取所有系统的任务"""
        all_tasks = []
        
        for system_id, config in self.systems.items():
            if not config.enabled:
                continue
            
            try:
                adapter = self.factory.get_adapter(system_id)
                if adapter and adapter.connected:
                    tasks = adapter.sync_tasks(filters)
                    all_tasks.extend(tasks)
            except Exception as e:
                logger.error(f"从系统 {system_id} 获取任务失败：{str(e)}")
        
        # 按优先级和截止时间排序
        priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_tasks.sort(key=lambda x: (
            priority_order.get(x.get('priority', 'medium'), 2),
            x.get('due_date') or '9999'
        ))
        
        return all_tasks
    
    def get_system_summary(self) -> Dict[str, Any]:
        """获取系统集成摘要"""
        summary = {
            'total_systems': len(self.systems),
            'enabled_systems': sum(1 for s in self.systems.values() if s.enabled),
            'connected_systems': sum(1 for a in self.factory.list_adapters() if a['connected']),
            'systems': []
        }
        
        for system_id, config in self.systems.items():
            adapter = self.factory.get_adapter(system_id)
            system_info = config.to_dict()
            system_info['connected'] = adapter.connected if adapter else False
            
            # 统计任务数
            try:
                if adapter and adapter.connected:
                    tasks = adapter.get_tasks()
                    system_info['task_count'] = len(tasks)
                    system_info['pending_tasks'] = sum(1 for t in tasks if t.status == 'pending')
            except:
                system_info['task_count'] = 0
                system_info['pending_tasks'] = 0
            
            summary['systems'].append(system_info)
        
        return summary


# 全局系统集成服务实例
integration_service = SystemIntegrationService()


def init_integration_service() -> SystemIntegrationService:
    """初始化系统集成服务"""
    global integration_service
    
    # 添加示例系统
    demo_configs = [
        SystemConfig(
            system_id='oa_demo',
            system_name='OA 办公系统（演示）',
            system_type=SystemType.OA,
            base_url='http://oa.example.com/api',
            auth_type='api_key',
            api_key='demo_key'
        ),
        SystemConfig(
            system_id='erp_demo',
            system_name='ERP 系统（演示）',
            system_type=SystemType.ERP,
            base_url='http://erp.example.com/api',
            auth_type='basic',
            username='demo',
            password='demo'
        ),
        SystemConfig(
            system_id='crm_demo',
            system_name='CRM 客户系统（演示）',
            system_type=SystemType.CRM,
            base_url='http://crm.example.com/api',
            auth_type='oauth2',
            config={'client_id': 'demo_client'}
        )
    ]
    
    for config in demo_configs:
        integration_service.add_system(config)
    
    logger.info("系统集成服务已初始化")
    return integration_service
