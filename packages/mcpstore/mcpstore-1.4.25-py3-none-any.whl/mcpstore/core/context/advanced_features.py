"""
MCPStore Advanced Features Module
高级功能相关操作的实现
"""

import logging
from typing import Dict, List, Optional, Any, Union

from .types import ContextType

logger = logging.getLogger(__name__)

class AdvancedFeaturesMixin:
    """高级功能混入类"""
    
    def create_simple_tool(self, original_tool: str, friendly_name: Optional[str] = None) -> 'MCPStoreContext':
        """
        创建简化版工具
        
        Args:
            original_tool: 原始工具名称
            friendly_name: 友好名称（可选）
            
        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            friendly_name = friendly_name or f"simple_{original_tool}"
            result = self._transformation_manager.create_simple_tool(
                original_tool=original_tool,
                friendly_name=friendly_name
            )
            logger.info(f"[{self._context_type.value}] Created simple tool: {friendly_name} -> {original_tool}")
            return self
        except Exception as e:
            logger.error(f"[{self._context_type.value}] Failed to create simple tool {original_tool}: {e}")
            return self

    def create_safe_tool(self, original_tool: str, validation_rules: Dict[str, Any]) -> 'MCPStoreContext':
        """
        创建安全版工具（带验证）
        
        Args:
            original_tool: 原始工具名称
            validation_rules: 验证规则
            
        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            # 创建验证函数
            validation_func = self._create_validation_function(validation_rules)
            
            result = self._transformation_manager.create_safe_tool(
                original_tool=original_tool,
                validation_func=validation_func,
                rules=validation_rules
            )
            logger.info(f"[{self._context_type.value}] Created safe tool for: {original_tool}")
            return self
        except Exception as e:
            logger.error(f"[{self._context_type.value}] Failed to create safe tool {original_tool}: {e}")
            return self

    def switch_environment(self, environment: str) -> 'MCPStoreContext':
        """
        切换运行环境
        
        Args:
            environment: 环境名称（如 "development", "production"）
            
        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            result = self._component_manager.switch_environment(environment)
            logger.info(f"[{self._context_type.value}] Switched to environment: {environment}")
            return self
        except Exception as e:
            logger.error(f"[{self._context_type.value}] Failed to switch environment to {environment}: {e}")
            return self

    def create_custom_environment(self, name: str, allowed_categories: List[str]) -> 'MCPStoreContext':
        """
        创建自定义环境
        
        Args:
            name: 环境名称
            allowed_categories: 允许的工具类别
            
        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            result = self._component_manager.create_custom_environment(
                name=name,
                allowed_categories=allowed_categories
            )
            logger.info(f"[{self._context_type.value}] Created custom environment: {name}")
            return self
        except Exception as e:
            logger.error(f"[{self._context_type.value}] Failed to create custom environment {name}: {e}")
            return self

    def import_api(self, api_url: str, api_name: str = None) -> 'MCPStoreContext':
        """
        导入 OpenAPI 服务（同步）
        
        Args:
            api_url: API 规范 URL
            api_name: API 名称（可选）
            
        Returns:
            MCPStoreContext: 支持链式调用
        """
        return self._sync_helper.run_async(self.import_api_async(api_url, api_name))

    async def import_api_async(self, api_url: str, api_name: str = None) -> 'MCPStoreContext':
        """
        导入 OpenAPI 服务（异步）

        Args:
            api_url: API 规范 URL
            api_name: API 名称（可选）

        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            import time
            api_name = api_name or f"api_{int(time.time())}"
            result = await self._openapi_manager.import_openapi_service(
                name=api_name,
                spec_url=api_url
            )
            logger.info(f"[{self._context_type.value}] Imported API {api_name}: {result.get('total_endpoints', 0)} endpoints")
            return self
        except Exception as e:
            logger.error(f"[{self._context_type.value}] Failed to import API {api_url}: {e}")
            return self

    def enable_caching(self, patterns: Dict[str, int] = None) -> 'MCPStoreContext':
        """
        启用智能缓存
        
        Args:
            patterns: 缓存模式配置
            
        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            patterns = patterns or {
                "tool_results": 300,  # 5分钟
                "service_status": 60,  # 1分钟
                "tool_list": 120      # 2分钟
            }
            result = self._performance_optimizer.enable_caching(patterns)
            logger.info(f"[{self._context_type.value}] Enabled caching with patterns: {patterns}")
            return self
        except Exception as e:
            logger.error(f"[{self._context_type.value}] Failed to enable caching: {e}")
            return self

    def get_performance_report(self) -> Dict[str, Any]:
        """
        获取性能报告
        
        Returns:
            Dict: 性能统计信息
        """
        try:
            return self._performance_optimizer.get_performance_report()
        except Exception as e:
            logger.error(f"[{self._context_type.value}] Failed to get performance report: {e}")
            return {"error": str(e)}

    def setup_auth(self, auth_type: str = "bearer", enabled: bool = True) -> 'MCPStoreContext':
        """
        设置认证
        
        Args:
            auth_type: 认证类型
            enabled: 是否启用
            
        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            result = self._auth_manager.setup_auth(
                auth_type=auth_type,
                enabled=enabled
            )
            logger.info(f"[{self._context_type.value}] Setup auth: {auth_type}, enabled: {enabled}")
            return self
        except Exception as e:
            logger.error(f"[{self._context_type.value}] Failed to setup auth: {e}")
            return self

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        获取使用统计
        
        Returns:
            Dict: 使用统计信息
        """
        try:
            return self._monitoring_manager.get_usage_stats()
        except Exception as e:
            logger.error(f"[{self._context_type.value}] Failed to get usage stats: {e}")
            return {"error": str(e)}

    def record_tool_execution(self, tool_name: str, duration: float, success: bool, error: Exception = None) -> 'MCPStoreContext':
        """
        记录工具执行情况
        
        Args:
            tool_name: 工具名称
            duration: 执行时长
            success: 是否成功
            error: 错误信息（如果有）
            
        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            self._monitoring_manager.record_tool_execution(
                tool_name=tool_name,
                duration=duration,
                success=success,
                error=error
            )
            return self
        except Exception as e:
            logger.error(f"[{self._context_type.value}] Failed to record tool execution: {e}")
            return self

    def reset_mcp_json_file(self) -> bool:
        """直接重置MCP JSON配置文件（同步版本）"""
        return self._sync_helper.run_async(self.reset_mcp_json_file_async(), timeout=60.0)

    async def reset_mcp_json_file_async(self) -> bool:
        """
        直接重置MCP JSON配置文件（异步版本）
        
        这是一个文件级别的操作，直接重置mcp.json文件内容
        """
        try:
            # 使用数据空间管理器获取正确的文件路径
            if hasattr(self._store, '_data_space_manager') and self._store._data_space_manager:
                mcp_json_path = self._store._data_space_manager.get_file_path("mcp.json")
            else:
                mcp_json_path = self._store.config.json_path
            
            # 重置为默认配置
            default_config = {"mcpServers": {}}
            
            import json
            with open(mcp_json_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully reset MCP JSON file: {mcp_json_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset MCP JSON file: {e}")
            return False

    def reset_client_services_file(self) -> bool:
        """直接重置client_services.json文件（同步版本）"""
        return self._sync_helper.run_async(self.reset_client_services_file_async(), timeout=60.0)

    async def reset_client_services_file_async(self) -> bool:
        """
        直接重置client_services.json文件（异步版本）
        
        这是一个文件级别的操作，直接重置client_services.json文件内容
        """
        try:
            # 使用数据空间管理器获取正确的文件路径
            if hasattr(self._store, '_data_space_manager') and self._store._data_space_manager:
                client_services_path = self._store._data_space_manager.get_file_path("client_services.json")
            else:
                # 默认路径
                from pathlib import Path
                config_dir = Path(self._store.config.json_path).parent
                client_services_path = config_dir / "client_services.json"
            
            # 重置为空配置
            default_config = {}
            
            import json
            with open(client_services_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully reset client_services file: {client_services_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset client_services file: {e}")
            return False

    def reset_agent_clients_file(self) -> bool:
        """直接重置agent_clients.json文件（同步版本）"""
        return self._sync_helper.run_async(self.reset_agent_clients_file_async(), timeout=60.0)

    async def reset_agent_clients_file_async(self) -> bool:
        """
        直接重置agent_clients.json文件（异步版本）
        
        这是一个文件级别的操作，直接重置agent_clients.json文件内容
        """
        try:
            # 使用数据空间管理器获取正确的文件路径
            if hasattr(self._store, '_data_space_manager') and self._store._data_space_manager:
                agent_clients_path = self._store._data_space_manager.get_file_path("agent_clients.json")
            else:
                # 默认路径
                from pathlib import Path
                config_dir = Path(self._store.config.json_path).parent
                agent_clients_path = config_dir / "agent_clients.json"
            
            # 重置为空配置
            default_config = {}
            
            import json
            with open(agent_clients_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully reset agent_clients file: {agent_clients_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset agent_clients file: {e}")
            return False
