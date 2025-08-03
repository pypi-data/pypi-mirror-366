#!/usr/bin/env python3
"""
MCPStore 独立配置系统
完全不依赖环境变量，通过默认参数和初始化配置工作
"""

import logging
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union

from .registry.schema_manager import get_schema_manager

logger = logging.getLogger(__name__)

@dataclass
class StandaloneConfig:
    """独立配置类 - 不依赖任何环境变量"""
    
    # === 核心配置 ===
    heartbeat_interval_seconds: int = 60
    http_timeout_seconds: int = 30
    reconnection_interval_seconds: int = 300
    cleanup_interval_seconds: int = 3600
    
    # === 网络配置 ===
    streamable_http_endpoint: str = "/mcp"
    default_transport: str = "http"
    
    # === 文件路径配置 ===
    config_dir: Optional[str] = None  # 如果为None，使用内存配置
    mcp_config_file: Optional[str] = None
    client_services_file: Optional[str] = None
    agent_clients_file: Optional[str] = None
    
    # === 服务配置 ===
    known_services: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {})
    
    # === 环境隔离配置 ===
    isolated_environment: bool = True  # 是否使用隔离环境
    base_environment: Dict[str, str] = field(default_factory=lambda: {
        "PYTHONPATH": ".",
        "PATH": "/usr/local/bin:/usr/bin:/bin"  # 基础PATH，不依赖系统
    })
    
    # === 日志配置 ===
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_debug: bool = False

class StandaloneConfigManager:
    """独立配置管理器 - 完全不依赖环境变量"""
    
    def __init__(self, config: Optional[StandaloneConfig] = None):
        """
        初始化独立配置管理器
        
        Args:
            config: 自定义配置，如果为None则使用默认配置
        """
        self.config = config or StandaloneConfig()
        self._runtime_config: Dict[str, Any] = {}
        self._service_configs: Dict[str, Dict[str, Any]] = {}
        
        # 初始化默认配置
        self._initialize_default_configs()
        
        logger.info("StandaloneConfigManager initialized without environment dependencies")
    
    def _initialize_default_configs(self):
        """初始化默认配置"""
        # 设置运行时配置
        self._runtime_config = {
            "timing": {
                "heartbeat_interval_seconds": self.config.heartbeat_interval_seconds,
                "http_timeout_seconds": self.config.http_timeout_seconds,
                "reconnection_interval_seconds": self.config.reconnection_interval_seconds,
                "cleanup_interval_seconds": self.config.cleanup_interval_seconds
            },
            "network": {
                "streamable_http_endpoint": self.config.streamable_http_endpoint,
                "default_transport": self.config.default_transport
            },
            "environment": {
                "isolated": self.config.isolated_environment,
                "base_env": self.config.base_environment.copy()
            }
        }

        # 使用Schema管理器初始化已知服务配置
        schema_manager = get_schema_manager()
        self._service_configs = {
            "mcpstore-wiki": schema_manager.get_known_service_config("mcpstore-wiki"),
            "howtocook": schema_manager.get_known_service_config("howtocook")
        }
        # 合并用户自定义的服务配置
        self._service_configs.update(deepcopy(self.config.known_services))
    
    def get_timing_config(self) -> Dict[str, int]:
        """获取时间配置"""
        return self._runtime_config["timing"]
    
    def get_network_config(self) -> Dict[str, str]:
        """获取网络配置"""
        return self._runtime_config["network"]
    
    def get_environment_config(self) -> Dict[str, Any]:
        """获取环境配置"""
        return self._runtime_config["environment"]
    
    def get_service_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """获取服务配置"""
        return self._service_configs.get(service_name)
    
    def add_service_config(self, service_name: str, config: Dict[str, Any]):
        """添加服务配置"""
        self._service_configs[service_name] = deepcopy(config)
        logger.info(f"Added service config for: {service_name}")
    
    def get_all_service_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取所有服务配置"""
        return deepcopy(self._service_configs)
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """获取MCP格式的配置"""
        return {
            "mcpServers": deepcopy(self._service_configs),
            "version": "1.0.0",
            "description": "MCPStore standalone configuration"
        }
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Updated config: {key} = {value}")
        
        # 重新初始化配置
        self._initialize_default_configs()
    
    def get_isolated_environment(self, custom_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        获取隔离的环境变量
        
        Args:
            custom_env: 自定义环境变量
            
        Returns:
            隔离的环境变量字典
        """
        if not self.config.isolated_environment:
            # 如果不使用隔离环境，返回空字典（让FastMCP处理）
            return custom_env or {}
        
        # 使用基础环境
        env = self.config.base_environment.copy()
        
        # 添加自定义环境变量
        if custom_env:
            env.update(custom_env)
        
        return env
    
    def get_config_paths(self) -> Dict[str, Optional[str]]:
        """获取配置文件路径"""
        return {
            "config_dir": self.config.config_dir,
            "mcp_config_file": self.config.mcp_config_file,
            "client_services_file": self.config.client_services_file,
            "agent_clients_file": self.config.agent_clients_file
        }
    
    def is_file_based(self) -> bool:
        """检查是否使用文件配置"""
        return self.config.config_dir is not None or self.config.mcp_config_file is not None

class StandaloneConfigBuilder:
    """独立配置构建器 - 提供流畅的配置构建接口"""
    
    def __init__(self):
        self._config = StandaloneConfig()
    
    def with_timing(self, heartbeat: int = None, timeout: int = None, reconnection: int = None) -> 'StandaloneConfigBuilder':
        """设置时间配置"""
        if heartbeat is not None:
            self._config.heartbeat_interval_seconds = heartbeat
        if timeout is not None:
            self._config.http_timeout_seconds = timeout
        if reconnection is not None:
            self._config.reconnection_interval_seconds = reconnection
        return self
    
    def with_network(self, endpoint: str = None, transport: str = None) -> 'StandaloneConfigBuilder':
        """设置网络配置"""
        if endpoint is not None:
            self._config.streamable_http_endpoint = endpoint
        if transport is not None:
            self._config.default_transport = transport
        return self
    
    def with_files(self, config_dir: str = None, mcp_file: str = None) -> 'StandaloneConfigBuilder':
        """设置文件配置"""
        if config_dir is not None:
            self._config.config_dir = config_dir
        if mcp_file is not None:
            self._config.mcp_config_file = mcp_file
        return self
    
    def with_service(self, name: str, config: Dict[str, Any]) -> 'StandaloneConfigBuilder':
        """添加服务配置"""
        self._config.known_services[name] = config
        return self
    
    def with_environment(self, isolated: bool = None, base_env: Dict[str, str] = None) -> 'StandaloneConfigBuilder':
        """设置环境配置"""
        if isolated is not None:
            self._config.isolated_environment = isolated
        if base_env is not None:
            self._config.base_environment = base_env
        return self
    
    def with_logging(self, level: str = None, debug: bool = None) -> 'StandaloneConfigBuilder':
        """设置日志配置"""
        if level is not None:
            self._config.log_level = level
        if debug is not None:
            self._config.enable_debug = debug
        return self
    
    def build(self) -> StandaloneConfig:
        """构建配置"""
        return deepcopy(self._config)

# === 预定义配置模板 ===

def create_minimal_config() -> StandaloneConfig:
    """创建最小配置 - 只包含基本功能"""
    return StandaloneConfigBuilder().build()

def create_development_config() -> StandaloneConfig:
    """创建开发配置 - 包含调试功能"""
    return (StandaloneConfigBuilder()
            .with_timing(heartbeat=30, timeout=10, reconnection=60)
            .with_logging(level="DEBUG", debug=True)
            .build())

def create_production_config() -> StandaloneConfig:
    """创建生产配置 - 优化性能和稳定性"""
    return (StandaloneConfigBuilder()
            .with_timing(heartbeat=120, timeout=60, reconnection=600)
            .with_environment(isolated=True)
            .with_logging(level="WARNING", debug=False)
            .build())

def create_studio_config() -> StandaloneConfig:
    """创建Studio配置 - 针对长连接优化"""
    return (StandaloneConfigBuilder()
            .with_timing(heartbeat=300, timeout=120, reconnection=1800)
            .with_network(transport="streamable-http")
            .with_environment(isolated=False)  # Studio可能需要访问系统环境
            .build())

# === 全局配置实例 ===
_global_config_manager: Optional[StandaloneConfigManager] = None

def get_global_config() -> StandaloneConfigManager:
    """获取全局配置管理器"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = StandaloneConfigManager()
    return _global_config_manager

def set_global_config(config: Union[StandaloneConfig, StandaloneConfigManager]):
    """设置全局配置"""
    global _global_config_manager
    if isinstance(config, StandaloneConfig):
        _global_config_manager = StandaloneConfigManager(config)
    else:
        _global_config_manager = config
    logger.info("Global standalone config updated")

def reset_global_config():
    """重置全局配置"""
    global _global_config_manager
    _global_config_manager = None
    logger.info("Global standalone config reset")
