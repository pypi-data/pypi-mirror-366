"""
MCPOrchestrator Package
编排器包 - 模块化重构后的MCP服务编排器

这个包将原来的2056行orchestrator.py重构为8个专门模块：
- base_orchestrator.py: 核心基础设施和生命周期管理 (12个方法)
- monitoring_tasks.py: 监控任务和循环管理 (12个方法)
- service_connection.py: 服务连接和状态管理 (15个方法)
- tool_execution.py: 工具执行和处理 (4个方法)
- service_management.py: 服务管理和信息获取 (15个方法)
- resources_prompts.py: Resources/Prompts功能 (12个方法)
- network_utils.py: 网络工具和错误处理 (2个方法)
- standalone_config.py: 独立配置适配器 (6个方法)

总计78个方法，完全保持向后兼容性。
"""

from .base_orchestrator import MCPOrchestrator

# 导出主要类
__all__ = ['MCPOrchestrator']

# 版本信息
__version__ = "0.8.1"
__description__ = "Modular MCP Service Orchestrator"
