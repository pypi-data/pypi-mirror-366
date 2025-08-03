"""
Registry Types
注册模块相关的类型定义

包含注册模块中使用的所有类型定义，便于统一管理和导入。
"""

from typing import Dict, Any, Optional, List, Set, TypeVar, Protocol
from datetime import datetime

# 重新导出模型类型，便于统一导入
try:
    from ..models.service import ServiceConnectionState, ServiceStateMetadata
except ImportError:
    # 如果模型导入失败，提供占位符
    ServiceConnectionState = None
    ServiceStateMetadata = None

# 定义一个协议，表示任何具有call_tool方法的会话类型
class SessionProtocol(Protocol):
    """会话协议 - 定义会话必须实现的接口"""
    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """调用工具方法"""
        ...

# 会话类型变量
SessionType = TypeVar('SessionType')

# 注册相关类型别名
AgentId = str
ServiceName = str
ToolName = str
ClientId = str

# 注册数据结构类型
SessionsDict = Dict[AgentId, Dict[ServiceName, Any]]
ToolCacheDict = Dict[AgentId, Dict[ToolName, Any]]
ToolToSessionDict = Dict[AgentId, Dict[ToolName, Any]]
ServiceHealthDict = Dict[AgentId, Dict[ServiceName, datetime]]

class RegistryTypes:
    """注册类型集合 - 便于统一管理所有类型"""
    
    # 基础类型
    AgentId = AgentId
    ServiceName = ServiceName
    ToolName = ToolName
    ClientId = ClientId
    
    # 协议类型
    SessionProtocol = SessionProtocol
    SessionType = SessionType
    
    # 数据结构类型
    SessionsDict = SessionsDict
    ToolCacheDict = ToolCacheDict
    ToolToSessionDict = ToolToSessionDict
    ServiceHealthDict = ServiceHealthDict
    
    # 模型类型
    ServiceConnectionState = ServiceConnectionState
    ServiceStateMetadata = ServiceStateMetadata

__all__ = [
    'SessionProtocol',
    'SessionType',
    'AgentId',
    'ServiceName', 
    'ToolName',
    'ClientId',
    'SessionsDict',
    'ToolCacheDict',
    'ToolToSessionDict',
    'ServiceHealthDict',
    'RegistryTypes',
    'ServiceConnectionState',
    'ServiceStateMetadata'
]
