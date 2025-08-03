"""
MCPStore Registry Module
注册模块 - 统一管理服务注册、工具解析、Schema管理等功能

重构说明：
- 将原来散装的注册相关文件统一到 registry/ 模块
- 保持100%向后兼容性，所有原有导入路径仍然有效
- 功能集中管理，便于维护和扩展

模块结构：
- core_registry.py: 核心服务注册表（原 registry.py）
- enhanced_registry.py: 增强服务注册表（原 registry_refactored.py）
- schema_manager.py: Schema管理器
- tool_resolver.py: 工具名称解析器
- types.py: 注册相关类型定义
"""

__all__ = [
    # 核心注册表
    'ServiceRegistry',
    'SessionProtocol', 
    'SessionType',
    
    # 增强注册表
    'EnhancedServiceRegistry',
    
    # Schema管理
    'SchemaManager',
    
    # 工具解析
    'ToolNameResolver',
    'ToolResolution',
    
    # 类型定义
    'RegistryTypes',
    
    # 兼容性导出
    'ServiceConnectionState',
    'ServiceStateMetadata'
]

# 主要导出 - 保持向后兼容性
from .core_registry import ServiceRegistry, SessionProtocol, SessionType
from .enhanced_registry import ServiceRegistry as EnhancedServiceRegistry
from .schema_manager import SchemaManager
from .tool_resolver import ToolNameResolver, ToolResolution
from .types import RegistryTypes

# 为了向后兼容，也导出一些常用的类型
try:
    from ..models.service import ServiceConnectionState, ServiceStateMetadata
    __all__.extend(['ServiceConnectionState', 'ServiceStateMetadata'])
except ImportError:
    pass

# 版本信息
__version__ = "1.0.0"
__author__ = "MCPStore Team"
__description__ = "Registry module for MCPStore - Service registration, tool resolution, and schema management"
