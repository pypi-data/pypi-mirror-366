"""
MCPStore Tool Operations Module
Implementation of tool-related operations
"""

import logging
from typing import Dict, List, Optional, Any, Union

from mcpstore.core.models.tool import ToolInfo
from .types import ContextType

logger = logging.getLogger(__name__)

class ToolOperationsMixin:
    """Tool operations mixin class"""

    def list_tools(self) -> List[ToolInfo]:
        """
        List tools (synchronous version)
        - store context: aggregate tools from all client_ids under global_agent_store
        - agent context: aggregate tools from all client_ids under agent_id
        """
        return self._sync_helper.run_async(self.list_tools_async())

    async def list_tools_async(self) -> List[ToolInfo]:
        """
        List tools (asynchronous version)
        - store context: aggregate tools from all client_ids under global_agent_store
        - agent context: aggregate tools from all client_ids under agent_id (show local names)
        """
        if self._context_type == ContextType.STORE:
            return await self._store.list_tools()
        else:
            # Agent模式：获取全局工具列表，然后转换为本地名称
            global_tools = await self._store.list_tools(self._agent_id, agent_mode=True)

            # 使用映射器转换工具名称为本地名称
            if self._service_mapper:
                local_tools = []
                for tool in global_tools:
                    # 检查工具是否属于当前Agent
                    if self._service_mapper.is_agent_service(tool.service_name):
                        # 转换服务名为本地名称
                        local_service_name = self._service_mapper.to_local_name(tool.service_name)

                        # 转换工具名为本地名称
                        if tool.name.startswith(f"{tool.service_name}_"):
                            tool_suffix = tool.name[len(tool.service_name) + 1:]
                            local_tool_name = f"{local_service_name}_{tool_suffix}"
                        else:
                            # 🔧 修复：如果工具名不符合预期格式，保持原名但记录警告
                            local_tool_name = tool.name
                            logger.debug(f"Tool name '{tool.name}' doesn't follow expected format for service '{tool.service_name}'")

                        # 创建新的ToolInfo对象，使用本地名称
                        local_tool = ToolInfo(
                            name=local_tool_name,
                            description=tool.description,
                            service_name=local_service_name,
                            inputSchema=tool.inputSchema
                        )
                        local_tools.append(local_tool)

                return local_tools
            else:
                return global_tools

    def get_tools_with_stats(self) -> Dict[str, Any]:
        """
        获取工具列表及统计信息（同步版本）

        Returns:
            Dict: 包含工具列表和统计信息
        """
        return self._sync_helper.run_async(self.get_tools_with_stats_async())

    async def get_tools_with_stats_async(self) -> Dict[str, Any]:
        """
        获取工具列表及统计信息（异步版本）

        Returns:
            Dict: 包含工具列表和统计信息
        """
        try:
            tools = await self.list_tools_async()
            
            # 统计信息
            stats = {
                "total_tools": len(tools),
                "tools_by_service": {},
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "service_name": tool.service_name,
                        "has_schema": tool.inputSchema is not None
                    }
                    for tool in tools
                ]
            }
            
            # 按服务分组统计
            for tool in tools:
                service_name = tool.service_name
                if service_name not in stats["tools_by_service"]:
                    stats["tools_by_service"][service_name] = 0
                stats["tools_by_service"][service_name] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get tools with stats: {e}")
            return {
                "total_tools": 0,
                "tools_by_service": {},
                "tools": [],
                "error": str(e)
            }

    def get_system_stats(self) -> Dict[str, Any]:
        """
        获取系统统计信息（同步版本）

        Returns:
            Dict: 系统统计信息
        """
        return self._sync_helper.run_async(self.get_system_stats_async())

    async def get_system_stats_async(self) -> Dict[str, Any]:
        """
        获取系统统计信息（异步版本）

        Returns:
            Dict: 系统统计信息
        """
        try:
            services = await self.list_services_async()
            tools = await self.list_tools_async()
            
            # 计算统计信息
            stats = {
                "total_services": len(services),
                "total_tools": len(tools),
                "healthy_services": len([s for s in services if getattr(s, "status", None) == "healthy"]),
                "context_type": self._context_type.value,
                "agent_id": self._agent_id,
                "services_by_status": {},
                "tools_by_service": {}
            }
            
            # 按状态分组服务
            for service in services:
                status = getattr(service, "status", "unknown")
                if status not in stats["services_by_status"]:
                    stats["services_by_status"][status] = 0
                stats["services_by_status"][status] += 1
            
            # 按服务分组工具
            for tool in tools:
                service_name = tool.service_name
                if service_name not in stats["tools_by_service"]:
                    stats["tools_by_service"][service_name] = 0
                stats["tools_by_service"][service_name] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {
                "total_services": 0,
                "total_tools": 0,
                "healthy_services": 0,
                "context_type": self._context_type.value,
                "agent_id": self._agent_id,
                "services_by_status": {},
                "tools_by_service": {},
                "error": str(e)
            }

    def batch_add_services(self, services: List[Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """
        批量添加服务（同步版本）

        Args:
            services: 服务列表

        Returns:
            Dict: 批量添加结果
        """
        return self._sync_helper.run_async(self.batch_add_services_async(services))

    async def batch_add_services_async(self, services: List[Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """
        批量添加服务（异步版本）

        Args:
            services: 服务列表

        Returns:
            Dict: 批量添加结果
        """
        try:
            if not services:
                return {
                    "success": False,
                    "message": "No services provided",
                    "added_services": [],
                    "failed_services": [],
                    "total_added": 0
                }
            
            # 使用现有的 add_service_async 方法
            result = await self.add_service_async(services)
            
            # 获取添加后的服务列表
            current_services = await self.list_services_async()
            service_names = [getattr(s, "name", "unknown") for s in current_services]
            
            return {
                "success": True,
                "message": f"Batch operation completed",
                "added_services": service_names,
                "failed_services": [],
                "total_added": len(service_names)
            }
            
        except Exception as e:
            logger.error(f"Batch add services failed: {e}")
            return {
                "success": False,
                "message": str(e),
                "added_services": [],
                "failed_services": services if isinstance(services, list) else [str(services)],
                "total_added": 0
            }

    def use_tool(self, tool_name: str, args: Union[Dict[str, Any], str] = None, **kwargs) -> Any:
        """
        使用工具（同步版本），支持 store/agent 上下文

        用户友好的工具调用接口，支持多种工具名称格式：
        - 直接工具名: "get_weather"
        - 服务前缀: "weather__get_weather"
        - 旧格式: "weather_get_weather"

        Args:
            tool_name: 工具名称（支持多种格式）
            args: 工具参数（字典或JSON字符串）
            **kwargs: 额外参数（timeout, progress_handler等）

        Returns:
            Any: 工具执行结果
            - 单个内容块：直接返回字符串/数据
            - 多个内容块：返回列表
        """
        return self._sync_helper.run_async(self.use_tool_async(tool_name, args, **kwargs))

    async def use_tool_async(self, tool_name: str, args: Dict[str, Any] = None, **kwargs) -> Any:
        """
        使用工具（异步版本），支持 store/agent 上下文

        Args:
            tool_name: 工具名称（支持多种格式）
            args: 工具参数
            **kwargs: 额外参数（timeout, progress_handler等）

        Returns:
            Any: 工具执行结果（FastMCP 标准格式）
        """
        args = args or {}

        # 获取可用工具列表用于智能解析
        available_tools = []
        try:
            if self._context_type == ContextType.STORE:
                tools = await self._store.list_tools()
            else:
                tools = await self._store.list_tools(self._agent_id, agent_mode=True)

            # 构建工具信息，包含显示名称和原始名称
            for tool in tools:
                # Agent模式：需要转换服务名称为本地名称
                if self._context_type == ContextType.AGENT and self._service_mapper:
                    # 转换服务名为本地名称
                    local_service_name = self._service_mapper.to_local_name(tool.service_name)
                    # 构建本地工具名称
                    if tool.name.startswith(f"{tool.service_name}_"):
                        tool_suffix = tool.name[len(tool.service_name) + 1:]
                        local_tool_name = f"{local_service_name}_{tool_suffix}"
                    else:
                        local_tool_name = tool.name

                    display_name = local_tool_name
                    service_name = local_service_name
                else:
                    display_name = tool.name
                    service_name = tool.service_name

                original_name = self._extract_original_tool_name(display_name, service_name)

                available_tools.append({
                    "name": display_name,           # 显示名称（Agent模式下使用本地名称）
                    "original_name": original_name, # 原始名称
                    "service_name": service_name,   # 服务名称（Agent模式下使用本地名称）
                    "global_tool_name": tool.name,  # 保存全局工具名称用于实际调用
                    "global_service_name": tool.service_name  # 保存全局服务名称
                })

            logger.debug(f"Available tools for resolution: {len(available_tools)}")
        except Exception as e:
            logger.warning(f"Failed to get available tools for resolution: {e}")

        # 使用统一解析器解析工具名称
        from mcpstore.core.registry.tool_resolver import ToolNameResolver

        resolver = ToolNameResolver(available_services=self._get_available_services())

        try:
            resolution = resolver.resolve_tool_name(tool_name, available_tools)
            logger.debug(f"Tool resolved: {tool_name} -> {resolution.service_name}::{resolution.original_tool_name} ({resolution.resolution_method})")
        except ValueError as e:
            raise ValueError(f"Tool resolution failed: {e}")

        # 构造标准化的工具执行请求
        from mcpstore.core.models.tool import ToolExecutionRequest

        if self._context_type == ContextType.STORE:
            logger.info(f"[STORE] Executing tool: {resolution.original_tool_name} from service: {resolution.service_name}")
            request = ToolExecutionRequest(
                tool_name=resolution.original_tool_name,
                service_name=resolution.service_name,
                args=args,
                **kwargs
            )
        else:
            # Agent模式：需要使用全局服务名称进行实际调用
            # 但在日志中显示本地名称以便用户理解
            global_service_name = resolution.service_name
            if self._service_mapper:
                # 检查resolution.service_name是否是本地名称，如果是则转换为全局名称
                # 通过检查是否以agent_id结尾来判断是否已经是全局名称
                if not resolution.service_name.endswith(f"by{self._agent_id}"):
                    # 是本地名称，需要转换为全局名称
                    global_service_name = self._service_mapper.to_global_name(resolution.service_name)
                else:
                    # 已经是全局名称，直接使用
                    global_service_name = resolution.service_name

            logger.info(f"[AGENT:{self._agent_id}] Executing tool: {resolution.original_tool_name} from service: {resolution.service_name} (global: {global_service_name})")
            request = ToolExecutionRequest(
                tool_name=resolution.original_tool_name,
                service_name=global_service_name,  # 使用全局服务名称
                args=args,
                agent_id=self._agent_id,
                **kwargs
            )

        return await self._store.process_tool_request(request)
