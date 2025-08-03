"""
MCPStore Lifecycle Management Module
生命周期管理模块

负责服务生命周期、健康监控、内容管理和智能重连
"""

# 主要导出 - 保持向后兼容性
from .manager import ServiceLifecycleManager
from .content_manager import ServiceContentManager
from .health_manager import get_health_manager, HealthStatus, HealthCheckResult
from .smart_reconnection import SmartReconnectionManager
from .config import ServiceLifecycleConfig

__all__ = [
    'ServiceLifecycleManager',
    'ServiceContentManager',
    'get_health_manager',
    'HealthStatus',
    'HealthCheckResult',
    'SmartReconnectionManager',
    'ServiceLifecycleConfig'
]

# 为了向后兼容，也导出一些常用的类型
try:
    from mcpstore.core.models.service import ServiceConnectionState, ServiceStateMetadata
    __all__.extend(['ServiceConnectionState', 'ServiceStateMetadata'])
except ImportError:
    pass
