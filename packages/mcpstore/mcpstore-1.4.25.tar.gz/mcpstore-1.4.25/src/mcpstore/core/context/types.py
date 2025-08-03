"""
MCPStore Context Types
上下文相关的类型定义
"""

from enum import Enum

class ContextType(Enum):
    """上下文类型"""
    STORE = "store"
    AGENT = "agent"
