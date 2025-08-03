"""
MCPStore Monitoring Module
监控模块

负责工具监控、性能分析、指标收集和监控配置
"""

# 主要导出 - 保持向后兼容性
from .tools_monitor import ToolsUpdateMonitor
from .message_handler import MCPStoreMessageHandler
try:
    from .analytics import MonitoringAnalytics, EventCollector, ToolUsageMetrics, ServiceHealthMetrics
except ImportError:
    # 如果analytics模块导入失败，提供占位符
    MonitoringAnalytics = None
    EventCollector = None
    ToolUsageMetrics = None
    ServiceHealthMetrics = None

try:
    from .base_monitor import MonitoringManager, NetworkEndpoint, SystemResourceInfo
    BaseMonitor = MonitoringManager  # 为了向后兼容
except ImportError as e:
    print(f"Warning: Failed to import from base_monitor: {e}")
    BaseMonitor = None
    MonitoringManager = None
    NetworkEndpoint = None
    SystemResourceInfo = None

try:
    from .config import MonitoringConfig
except ImportError:
    MonitoringConfig = None

__all__ = [
    'ToolsUpdateMonitor',
    'MCPStoreMessageHandler',
    'MonitoringAnalytics',
    'EventCollector',
    'ToolUsageMetrics',
    'ServiceHealthMetrics',
    'BaseMonitor',
    'MonitoringManager',
    'NetworkEndpoint',
    'SystemResourceInfo',
    'MonitoringConfig'
]
