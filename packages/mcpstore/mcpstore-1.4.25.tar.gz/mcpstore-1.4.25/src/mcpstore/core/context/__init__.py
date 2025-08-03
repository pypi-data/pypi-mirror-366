"""
MCPStore Context Package
重构后的上下文管理模块

此包将原来的大型 context.py 文件拆分为多个专门的模块：
- base_context: 核心上下文类和基础功能
- service_operations: 服务相关操作
- tool_operations: 工具相关操作
- resources_prompts: Resources和Prompts功能
- advanced_features: 高级功能
"""

from .types import ContextType
from .base_context import MCPStoreContext

__all__ = ['ContextType', 'MCPStoreContext']
