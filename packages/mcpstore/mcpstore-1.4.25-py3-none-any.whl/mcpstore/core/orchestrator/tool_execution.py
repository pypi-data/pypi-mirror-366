"""
MCPOrchestrator Tool Execution Module
工具执行模块 - 包含工具执行和处理
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple

from fastmcp import Client

logger = logging.getLogger(__name__)

class ToolExecutionMixin:
    """工具执行混入类"""

    async def execute_tool_fastmcp(
        self,
        service_name: str,
        tool_name: str,
        arguments: Dict[str, Any] = None,
        agent_id: Optional[str] = None,
        timeout: Optional[float] = None,
        progress_handler = None,
        raise_on_error: bool = True
    ) -> Any:
        """
        执行工具（FastMCP 标准）
        严格按照 FastMCP 官网标准执行工具调用

        Args:
            service_name: 服务名称
            tool_name: 工具名称（FastMCP 原始名称）
            arguments: 工具参数
            agent_id: Agent ID（可选）
            timeout: 超时时间（秒）
            progress_handler: 进度处理器
            raise_on_error: 是否在错误时抛出异常

        Returns:
            FastMCP CallToolResult 或提取的数据
        """
        from mcpstore.core.registry.tool_resolver import FastMCPToolExecutor

        arguments = arguments or {}
        executor = FastMCPToolExecutor(default_timeout=timeout or 30.0)

        try:
            if agent_id:
                # Agent 模式：在指定 Agent 的客户端中查找服务
                client_ids = self.client_manager.get_agent_clients(agent_id)
                if not client_ids:
                    raise Exception(f"No clients found for agent {agent_id}")
            else:
                # Store 模式：在 global_agent_store 的客户端中查找服务
                client_ids = self.client_manager.get_agent_clients(self.client_manager.global_agent_store_id)
                if not client_ids:
                    raise Exception("No clients found in global_agent_store")

            # 遍历客户端查找服务
            for client_id in client_ids:
                if self.registry.has_service(client_id, service_name):
                    try:
                        # 获取服务配置并创建客户端
                        service_config = self.mcp_config.get_service_config(service_name)
                        if not service_config:
                            logger.warning(f"Service configuration not found for {service_name}")
                            continue

                        # 标准化配置并创建 FastMCP 客户端
                        normalized_config = self._normalize_service_config(service_config)
                        client = Client({"mcpServers": {service_name: normalized_config}})

                        async with client:
                            # 验证工具存在
                            tools = await client.list_tools()
                            if not any(t.name == tool_name for t in tools):
                                logger.warning(f"Tool {tool_name} not found in service {service_name}")
                                continue

                            # 使用 FastMCP 标准执行器执行工具
                            result = await executor.execute_tool(
                                client=client,
                                tool_name=tool_name,
                                arguments=arguments,
                                timeout=timeout,
                                progress_handler=progress_handler,
                                raise_on_error=raise_on_error
                            )

                            # 提取结果数据（按照 FastMCP 标准）
                            extracted_data = executor.extract_result_data(result)

                            logger.info(f"Tool {tool_name} executed successfully in service {service_name}")
                            return extracted_data

                    except Exception as e:
                        logger.error(f"Failed to execute tool in client {client_id}: {e}")
                        if raise_on_error:
                            raise
                        continue

            raise Exception(f"Tool {tool_name} not found in service {service_name}")

        except Exception as e:
            logger.error(f"FastMCP tool execution failed: {e}")
            raise Exception(f"Tool execution failed: {str(e)}")

    async def execute_tool(
        self,
        service_name: str,
        tool_name: str,
        parameters: Dict[str, Any],
        agent_id: Optional[str] = None
    ) -> Any:
        """
        执行工具（旧版本，已废弃）

        ⚠️ 此方法已废弃，请使用 execute_tool_fastmcp() 方法
        该方法保留仅为向后兼容，将在未来版本中移除
        """
        logger.warning("execute_tool() is deprecated, use execute_tool_fastmcp() instead")
        try:
            if agent_id:
                # agent模式：在agent的所有client中查找服务
                client_ids = self.client_manager.get_agent_clients(agent_id)
                if not client_ids:
                    raise Exception(f"No clients found for agent {agent_id}")
                    
                # 在所有client中查找服务
                for client_id in client_ids:
                    if self.registry.has_service(client_id, service_name):
                        # 获取服务配置
                        service_config = self.mcp_config.get_service_config(service_name)
                        if not service_config:
                            logger.warning(f"Service configuration not found for {service_name}")
                            continue
                            
                        logger.debug(f"Creating new client for service {service_name} with config: {service_config}")
                        # 确保配置包含transport字段（自动推断）
                        normalized_config = self._normalize_service_config(service_config)
                        # 创建新的客户端实例
                        client = Client({"mcpServers": {service_name: normalized_config}})
                        try:
                            async with client:
                                logger.debug(f"Client connected: {client.is_connected()}")
                                
                                # 获取工具列表并打印
                                tools = await client.list_tools()
                                logger.debug(f"Available tools for service {service_name}: {[t.name for t in tools]}")
                                
                                # 检查工具名称格式
                                base_tool_name = tool_name
                                if tool_name.startswith(f"{service_name}_"):
                                    base_tool_name = tool_name[len(service_name)+1:]
                                logger.debug(f"Using base tool name: {base_tool_name}")
                                
                                # 检查工具是否存在
                                if not any(t.name == base_tool_name for t in tools):
                                    logger.warning(f"Tool {base_tool_name} not found in available tools")
                                    continue
                                
                                # 执行工具
                                logger.debug(f"Calling tool {base_tool_name} with parameters: {parameters}")
                                result = await client.call_tool(base_tool_name, parameters)
                                logger.info(f"Tool {base_tool_name} executed successfully with client {client_id}")
                                return result
                        except Exception as e:
                            logger.error(f"Failed to execute tool with client {client_id}: {e}")
                            continue
                                
                raise Exception(f"Service {service_name} not found in any client for agent {agent_id}")
            else:
                # store模式：在global_agent_store的所有client中查找服务
                client_ids = self.client_manager.get_agent_clients(self.client_manager.global_agent_store_id)
                if not client_ids:
                    raise Exception("No clients found in global_agent_store")
                    
                # 在所有client中查找服务
                for client_id in client_ids:
                    if self.registry.has_service(client_id, service_name):
                        # 获取服务配置
                        service_config = self.mcp_config.get_service_config(service_name)
                        if not service_config:
                            logger.warning(f"Service configuration not found for {service_name}")
                            continue
                            
                        logger.debug(f"Creating new client for service {service_name} with config: {service_config}")
                        # 确保配置包含transport字段（自动推断）
                        normalized_config = self._normalize_service_config(service_config)
                        # 创建新的客户端实例
                        client = Client({"mcpServers": {service_name: normalized_config}})
                        try:
                            async with client:
                                logger.debug(f"Client connected: {client.is_connected()}")
                                
                                # 获取工具列表并打印
                                tools = await client.list_tools()
                                logger.debug(f"Available tools for service {service_name}: {[t.name for t in tools]}")
                                
                                # 检查工具名称格式
                                base_tool_name = tool_name
                                if tool_name.startswith(f"{service_name}_"):
                                    base_tool_name = tool_name[len(service_name)+1:]
                                logger.debug(f"Using base tool name: {base_tool_name}")
                                
                                # 检查工具是否存在
                                if not any(t.name == base_tool_name for t in tools):
                                    logger.warning(f"Tool {base_tool_name} not found in available tools")
                                    continue
                                
                                # 执行工具
                                logger.debug(f"Calling tool {base_tool_name} with parameters: {parameters}")
                                result = await client.call_tool(base_tool_name, parameters)
                                logger.info(f"Tool {base_tool_name} executed successfully with client {client_id}")
                                return result
                        except Exception as e:
                            logger.error(f"Failed to execute tool with client {client_id}: {e}")
                            continue
                                
                raise Exception(f"Tool not found: {tool_name}")
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            raise Exception(f"Tool execution failed: {str(e)}")

    async def cleanup(self):
        """清理资源"""
        logger.info("Cleaning up MCP Orchestrator resources...")

        # 清理会话
        self.session_manager.cleanup_expired_sessions()

        # 旧的监控任务已被废弃，无需停止
        logger.info("Legacy monitoring tasks were already disabled")

        # 关闭所有客户端连接
        for name, client in self.clients.items():
            try:
                await client.close()
            except Exception as e:
                logger.error(f"Error closing client {name}: {e}")

        # 清理所有状态
        self.clients.clear()
        # 智能重连管理器已被废弃，无需清理

        logger.info("MCP Orchestrator cleanup completed")

    async def _restart_monitoring_tasks(self):
        """重启监控任务以应用新配置"""
        logger.info("Restarting monitoring tasks with new configuration...")

        # 旧的监控任务已被废弃，无需停止
        logger.info("Legacy monitoring tasks were already disabled")

        # 重新启动监控（现在由ServiceLifecycleManager处理）
        await self.start_monitoring()
        logger.info("Monitoring tasks restarted successfully")
