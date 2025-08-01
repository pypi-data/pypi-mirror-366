"""
MCPStore Context Module
提供 MCPStore 的上下文管理功能
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, TYPE_CHECKING

from mcpstore.core.models.agent import (
    AgentsSummary, AgentStatistics, AgentServiceSummary
)
from mcpstore.core.models.service import (
    ServiceInfo, ServiceConfigUnion, ServiceConnectionState
)
from mcpstore.core.models.tool import ToolExecutionRequest, ToolInfo

from .async_sync_helper import get_global_helper
from .auth_security import get_auth_manager
from .cache_performance import get_performance_optimizer
from .component_control import get_component_manager
from .exceptions import ServiceNotFoundError, InvalidConfigError, DeleteServiceError
from .monitoring import MonitoringManager, NetworkEndpoint, SystemResourceInfo
from .monitoring_analytics import get_monitoring_manager
from .openapi_integration import get_openapi_manager
# 导入新功能模块
from .tool_transformation import get_transformation_manager
from .agent_service_mapper import AgentServiceMapper

# 创建logger实例
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..adapters.langchain_adapter import LangChainAdapter
    from .unified_config import UnifiedConfigManager

class ContextType(Enum):
    """上下文类型"""
    STORE = "store"
    AGENT = "agent"

class MCPStoreContext:
    """
    MCPStore上下文类
    负责处理具体的业务操作，维护操作的上下文环境
    """
    def __init__(self, store: 'MCPStore', agent_id: Optional[str] = None):
        self._store = store
        self._agent_id = agent_id
        self._context_type = ContextType.STORE if agent_id is None else ContextType.AGENT

        # 异步/同步兼容助手
        self._sync_helper = get_global_helper()

        # 新功能管理器
        self._transformation_manager = get_transformation_manager()
        self._component_manager = get_component_manager()
        self._openapi_manager = get_openapi_manager()
        self._auth_manager = get_auth_manager()
        self._performance_optimizer = get_performance_optimizer()
        self._monitoring_manager = get_monitoring_manager()

        # 监控管理器 - 使用数据空间管理器或默认路径
        if hasattr(self._store, '_data_space_manager') and self._store._data_space_manager:
            # 使用数据空间管理器的路径
            data_dir = self._store._data_space_manager.get_file_path("monitoring").parent
        else:
            # 使用默认路径（向后兼容）
            config_dir = Path(self._store.config.json_path).parent
            data_dir = config_dir / "monitoring"

        self._monitoring = MonitoringManager(
            data_dir,
            self._store.tool_record_max_file_size,
            self._store.tool_record_retention_days
        )

        # Agent服务名称映射器
        self._service_mapper = AgentServiceMapper(agent_id) if agent_id else None

        # 扩展预留
        self._metadata: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
        self._cache: Dict[str, Any] = {}

    def for_langchain(self) -> 'LangChainAdapter':
        """返回一个 LangChain 适配器实例，用于后续的 LangChain 相关操作。"""
        from ..adapters.langchain_adapter import LangChainAdapter
        return LangChainAdapter(self)

    # === 核心服务接口 ===
    def list_services(self) -> List[ServiceInfo]:
        """
        列出服务列表（同步版本）
        - store上下文：聚合 global_agent_store 下所有 client_id 的服务
        - agent上下文：聚合 agent_id 下所有 client_id 的服务
        """
        return self._sync_helper.run_async(self.list_services_async())

    async def list_services_async(self) -> List[ServiceInfo]:
        """
        列出服务列表（异步版本）
        - store上下文：聚合 global_agent_store 下所有 client_id 的服务
        - agent上下文：聚合 agent_id 下所有 client_id 的服务（显示原始名称）
        """
        if self._context_type == ContextType.STORE:
            return await self._store.list_services()
        else:
            # Agent模式：获取全局服务列表，然后转换为本地名称
            global_services = await self._store.list_services(self._agent_id, agent_mode=True)

            # 使用映射器转换为本地名称
            if self._service_mapper:
                local_services = self._service_mapper.convert_service_list_to_local(global_services)
                return local_services
            else:
                return global_services

    def add_service(self, config: Union[ServiceConfigUnion, List[str], None] = None, json_file: str = None) -> 'MCPStoreContext':
        """
        增强版的服务添加方法（同步版本），支持多种配置格式

        Args:
            config: 服务配置，支持多种格式
            json_file: JSON文件路径，如果指定则读取该文件作为配置
        """
        return self._sync_helper.run_async(self.add_service_async(config, json_file), timeout=120.0)

    def add_service_with_details(self, config: Union[Dict[str, Any], List[Dict[str, Any]], str] = None) -> Dict[str, Any]:
        """
        添加服务并返回详细信息（同步版本）

        Args:
            config: 服务配置

        Returns:
            Dict: 包含添加结果的详细信息
        """
        return self._sync_helper.run_async(self.add_service_with_details_async(config), timeout=120.0)

    async def add_service_with_details_async(self, config: Union[Dict[str, Any], List[Dict[str, Any]], str] = None) -> Dict[str, Any]:
        """
        添加服务并返回详细信息（异步版本）

        Args:
            config: 服务配置

        Returns:
            Dict: 包含添加结果的详细信息
        """
        logger.info(f"[add_service_with_details_async] 开始添加服务，配置: {config}")

        # 预处理配置
        try:
            processed_config = self._preprocess_service_config(config)
            logger.info(f"[add_service_with_details_async] 预处理后的配置: {processed_config}")
        except ValueError as e:
            logger.error(f"[add_service_with_details_async] 预处理配置失败: {e}")
            return {
                "success": False,
                "added_services": [],
                "failed_services": self._extract_service_names(config),
                "service_details": {},
                "total_services": 0,
                "total_tools": 0,
                "message": str(e)
            }

        # 添加服务
        try:
            logger.info(f"[add_service_with_details_async] 调用 add_service_async")
            result = await self.add_service_async(processed_config)
            logger.info(f"[add_service_with_details_async] add_service_async 结果: {result}")
        except Exception as e:
            logger.error(f"[add_service_with_details_async] add_service_async 失败: {e}")
            return {
                "success": False,
                "added_services": [],
                "failed_services": self._extract_service_names(config),
                "service_details": {},
                "total_services": 0,
                "total_tools": 0,
                "message": f"Service addition failed: {str(e)}"
            }

        if result is None:
            logger.error(f"[add_service_with_details_async] add_service_async 返回 None")
            return {
                "success": False,
                "added_services": [],
                "failed_services": self._extract_service_names(config),
                "service_details": {},
                "total_services": 0,
                "total_tools": 0,
                "message": "Service addition failed"
            }

        # 获取添加后的详情
        logger.info(f"[add_service_with_details_async] 获取添加后的服务和工具列表")
        services = await self.list_services_async()
        tools = await self.list_tools_async()
        logger.info(f"[add_service_with_details_async] 当前服务数量: {len(services)}, 工具数量: {len(tools)}")
        logger.info(f"[add_service_with_details_async] 当前服务列表: {[getattr(s, 'name', 'unknown') for s in services]}")

        # 分析添加结果
        expected_service_names = self._extract_service_names(config)
        logger.info(f"[add_service_with_details_async] 期望的服务名称: {expected_service_names}")
        added_services = []
        service_details = {}

        for service_name in expected_service_names:
            service_info = next((s for s in services if getattr(s, "name", None) == service_name), None)
            logger.info(f"[add_service_with_details_async] 检查服务 {service_name}: {'找到' if service_info else '未找到'}")
            if service_info:
                added_services.append(service_name)
                service_tools = [t for t in tools if getattr(t, "service_name", None) == service_name]
                service_details[service_name] = {
                    "tools_count": len(service_tools),
                    "status": getattr(service_info, "status", "unknown")
                }
                logger.info(f"[add_service_with_details_async] 服务 {service_name} 有 {len(service_tools)} 个工具")

        failed_services = [name for name in expected_service_names if name not in added_services]
        success = len(added_services) > 0
        total_tools = sum(details["tools_count"] for details in service_details.values())

        logger.info(f"[add_service_with_details_async] 添加成功的服务: {added_services}")
        logger.info(f"[add_service_with_details_async] 添加失败的服务: {failed_services}")

        message = (
            f"Successfully added {len(added_services)} service(s) with {total_tools} tools"
            if success else
            f"Failed to add services. Available services: {[getattr(s, 'name', 'unknown') for s in services]}"
        )

        return {
            "success": success,
            "added_services": added_services,
            "failed_services": failed_services,
            "service_details": service_details,
            "total_services": len(added_services),
            "total_tools": total_tools,
            "message": message
        }

    def _preprocess_service_config(self, config: Union[Dict[str, Any], List[Dict[str, Any]], str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]], str]:
        """预处理服务配置"""
        if not config:
            return config

        if isinstance(config, dict):
            # 处理单个服务配置
            if "mcpServers" in config:
                # mcpServers格式，直接返回
                return config
            else:
                # 单个服务格式，进行验证和转换
                processed = config.copy()

                # 验证必需字段
                if "name" not in processed:
                    raise ValueError("Service name is required")

                # 验证互斥字段
                if "url" in processed and "command" in processed:
                    raise ValueError("Cannot specify both url and command")

                # 自动推断transport类型
                if "url" in processed and "transport" not in processed:
                    url = processed["url"]
                    if "/sse" in url.lower():
                        processed["transport"] = "sse"
                    else:
                        processed["transport"] = "streamable-http"

                # 验证args格式
                if "command" in processed and not isinstance(processed.get("args", []), list):
                    raise ValueError("Args must be a list")

                return processed

        return config

    def _extract_service_names(self, config: Union[Dict[str, Any], List[Dict[str, Any]], str] = None) -> List[str]:
        """从配置中提取服务名称"""
        if not config:
            return []

        if isinstance(config, dict):
            if "name" in config:
                return [config["name"]]
            elif "mcpServers" in config:
                return list(config["mcpServers"].keys())
        elif isinstance(config, list):
            return config

        return []

    async def add_service_async(self, config: Union[ServiceConfigUnion, List[str], None] = None, json_file: str = None) -> 'MCPStoreContext':
        """
        增强版的服务添加方法，支持多种配置格式：
        1. URL方式：
           await add_service({
               "name": "weather",
               "url": "https://weather-api.example.com/mcp",
               "transport": "streamable-http"
           })

        2. 本地命令方式：
           await add_service({
               "name": "assistant",
               "command": "python",
               "args": ["./assistant_server.py"],
               "env": {"DEBUG": "true"}
           })

        3. MCPConfig字典方式：
           await add_service({
               "mcpServers": {
                   "weather": {
                       "url": "https://weather-api.example.com/mcp"
                   }
               }
           })

        4. 服务名称列表方式（从现有配置中选择）：
           await add_service(['weather', 'assistant'])

        5. 无参数方式（仅限Store上下文）：
           await add_service()  # 注册所有服务

        6. JSON文件方式：
           await add_service(json_file="path/to/config.json")  # 读取JSON文件作为配置

        所有新添加的服务都会同步到 mcp.json 配置文件中。

        Args:
            config: 服务配置，支持多种格式
            json_file: JSON文件路径，如果指定则读取该文件作为配置

        Returns:
            MCPStoreContext: 返回自身实例以支持链式调用
        """
        try:
            # 处理json_file参数
            if json_file is not None:
                logger.info(f"从JSON文件读取配置: {json_file}")
                try:
                    import json
                    import os

                    if not os.path.exists(json_file):
                        raise Exception(f"JSON文件不存在: {json_file}")

                    with open(json_file, 'r', encoding='utf-8') as f:
                        file_config = json.load(f)

                    logger.info(f"成功读取JSON文件，配置: {file_config}")

                    # 如果同时指定了config和json_file，优先使用json_file
                    if config is not None:
                        logger.warning("同时指定了config和json_file参数，将使用json_file")

                    config = file_config

                except Exception as e:
                    raise Exception(f"读取JSON文件失败: {e}")

            # 如果既没有config也没有json_file，且不是Store模式的全量注册，则报错
            if config is None and json_file is None and self._context_type != ContextType.STORE:
                raise Exception("必须指定config参数或json_file参数")

        except Exception as e:
            logger.error(f"参数处理失败: {e}")
            raise

        try:
            # 获取正确的 agent_id（Store级别使用global_agent_store作为agent_id）
            agent_id = self._agent_id if self._context_type == ContextType.AGENT else self._store.orchestrator.client_manager.global_agent_store_id
            logger.info(f"当前模式: {self._context_type.name}, agent_id: {agent_id}")
            
            # 处理不同的输入格式
            if config is None:
                # Store模式下的全量注册
                if self._context_type == ContextType.STORE:
                    logger.info("STORE模式-使用统一同步机制注册所有服务")
                    # 🔧 修改：使用统一同步机制，不再手动注册
                    if hasattr(self._store.orchestrator, 'sync_manager') and self._store.orchestrator.sync_manager:
                        results = await self._store.orchestrator.sync_manager.sync_global_agent_store_from_mcp_json()
                        logger.info(f"同步结果: {results}")
                        if not (results.get("added") or results.get("updated")):
                            logger.warning("没有服务被同步，可能mcp.json为空或所有服务已是最新")
                    else:
                        logger.warning("统一同步管理器不可用，跳过同步")
                    return self
                else:
                    logger.warning("AGENT模式-未指定服务配置")
                    raise Exception("AGENT模式必须指定服务配置")
                    
            # 处理列表格式
            elif isinstance(config, list):
                if not config:
                    raise Exception("列表为空")

                # 判断是服务名称列表还是服务配置列表
                if all(isinstance(item, str) for item in config):
                    # 服务名称列表
                    logger.info(f"注册指定服务: {config}")
                    if self._context_type == ContextType.STORE:
                        resp = await self._store.register_selected_services_for_store(config)
                    else:
                        resp = await self._store.register_services_for_agent(agent_id, config)
                    logger.info(f"注册结果: {resp}")
                    if not (resp and resp.service_names):
                        raise Exception("服务注册失败")
                    # 服务名称列表注册完成，直接返回
                    return self

                elif all(isinstance(item, dict) for item in config):
                    # 批量服务配置列表
                    logger.info(f"批量服务配置注册，数量: {len(config)}")

                    # 转换为MCPConfig格式
                    mcp_config = {"mcpServers": {}}
                    for service_config in config:
                        service_name = service_config.get("name")
                        if not service_name:
                            raise Exception("批量配置中的服务缺少name字段")
                        mcp_config["mcpServers"][service_name] = {
                            k: v for k, v in service_config.items() if k != "name"
                        }

                    # 将config设置为转换后的mcp_config，然后继续处理
                    config = mcp_config

                else:
                    raise Exception("列表中的元素类型不一致，必须全部是字符串（服务名称）或全部是字典（服务配置）")

            # 处理字典格式的配置（包括从批量配置转换来的）
            if isinstance(config, dict):
                # 转换为标准格式
                if "mcpServers" in config:
                    # 已经是MCPConfig格式
                    mcp_config = config
                else:
                    # 单个服务配置，需要转换为MCPConfig格式
                    service_name = config.get("name")
                    if not service_name:
                        raise Exception("服务配置缺少name字段")
                        
                    mcp_config = {
                        "mcpServers": {
                            service_name: {k: v for k, v in config.items() if k != "name"}
                        }
                    }
                
                # 更新配置文件和处理同名服务
                try:
                    # 1. 加载现有配置
                    current_config = self._store.config.load_config()

                    # 🔧 新增：Agent模式下为服务名添加后缀
                    if self._context_type == ContextType.AGENT:
                        # 为Agent添加的服务名添加后缀：{原服务名}by{agent_id}
                        suffixed_services = {}
                        for original_name, service_config in mcp_config["mcpServers"].items():
                            suffixed_name = f"{original_name}by{self._agent_id}"
                            suffixed_services[suffixed_name] = service_config
                            logger.info(f"Agent服务名转换: {original_name} -> {suffixed_name}")

                        # 检查转换后是否还有冲突（极少数情况）
                        existing_services = set(current_config.get("mcpServers", {}).keys())
                        new_suffixed_services = set(suffixed_services.keys())
                        conflicts = new_suffixed_services & existing_services

                        if conflicts:
                            conflict_list = list(conflicts)
                            logger.error(f"Agent {self._agent_id} 添加的服务在后缀转换后仍有冲突: {conflict_list}")
                            raise Exception(f"服务名冲突（即使添加Agent后缀）: {conflict_list}。请使用不同的服务名。")

                        # 使用转换后的服务名
                        services_to_add = suffixed_services
                    else:
                        # Store模式：保持原服务名
                        services_to_add = mcp_config["mcpServers"]

                    # 2. 合并新配置到mcp.json
                    for name, service_config in services_to_add.items():
                        current_config["mcpServers"][name] = service_config

                    # 3. 保存更新后的配置
                    self._store.config.save_config(current_config)

                    # 4. 重新加载配置以确保同步
                    self._store.config.load_config()

                    # 🔧 修改：Store模式使用统一同步机制，Agent模式保持原有逻辑
                    if self._context_type == ContextType.STORE:
                        # Store模式：主动触发同步，确保服务立即生效
                        logger.info("Store模式：mcp.json已更新，主动触发同步机制处理global_agent_store")

                        # 🔧 修复：主动触发同步而不是等待文件监听器
                        if hasattr(self._store.orchestrator, 'sync_manager') and self._store.orchestrator.sync_manager:
                            try:
                                sync_result = await self._store.orchestrator.sync_manager.sync_global_agent_store_from_mcp_json()
                                logger.info(f"Store模式同步完成: {sync_result}")
                            except Exception as e:
                                logger.error(f"Store模式同步失败: {e}")
                                # 如果同步失败，仍然继续执行，让文件监听器作为备用机制
                    else:
                        # Agent模式：保持原有的手动注册逻辑，但使用转换后的服务名
                        created_client_ids = []
                        for suffixed_name, service_config in services_to_add.items():
                            # 使用转换后的服务名进行注册
                            success = self._store.client_manager.replace_service_in_agent(
                                agent_id=agent_id,
                                service_name=suffixed_name,
                                new_service_config=service_config
                            )
                            if not success:
                                raise Exception(f"替换服务 {suffixed_name} 失败")
                            logger.info(f"成功处理Agent服务: {suffixed_name}")

                            # 获取刚创建的client_id用于Registry注册
                            client_ids = self._store.client_manager.get_agent_clients(agent_id)
                            for client_id in client_ids:
                                client_config = self._store.client_manager.get_client_config(client_id)
                                if client_config and suffixed_name in client_config.get("mcpServers", {}):
                                    if client_id not in created_client_ids:
                                        created_client_ids.append(client_id)
                                    break

                        # 注册服务到Registry（使用已创建的client配置）
                        logger.info(f"注册服务到Registry，使用client_ids: {created_client_ids}")
                        for client_id in created_client_ids:
                            client_config = self._store.client_manager.get_client_config(client_id)
                            if client_config:
                                try:
                                    await self._store.orchestrator.register_json_services(client_config, client_id=client_id)
                                    logger.info(f"成功注册client {client_id} 到Registry")
                                except Exception as e:
                                    logger.warning(f"注册client {client_id} 到Registry失败: {e}")

                    logger.info(f"服务配置更新和Registry注册完成")

                except Exception as e:
                    raise Exception(f"更新配置文件失败: {e}")
            
            else:
                raise Exception(f"不支持的配置格式: {type(config)}")
            
            return self
            
        except Exception as e:
            logger.error(f"服务添加失败: {e}")
            raise

    def list_tools(self) -> List[ToolInfo]:
        """
        列出工具列表（同步版本）
        - store上下文：聚合 global_agent_store 下所有 client_id 的工具
        - agent上下文：聚合 agent_id 下所有 client_id 的工具
        """
        return self._sync_helper.run_async(self.list_tools_async())

    async def list_tools_async(self) -> List[ToolInfo]:
        """
        列出工具列表（异步版本）
        - store上下文：聚合 global_agent_store 下所有 client_id 的工具
        - agent上下文：聚合 agent_id 下所有 client_id 的工具（显示本地名称）
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
        tools = await self.list_tools_async()

        # 计算统计信息
        services_count = len(set(getattr(tool, "service_name", None) for tool in tools))

        return {
            "tools": tools,
            "metadata": {
                "total_tools": len(tools),
                "services_count": services_count,
                "context_type": self._context_type.name.lower(),
                "agent_id": self._agent_id if self._context_type == ContextType.AGENT else None,
                "last_updated": None  # 可以后续添加时间戳功能
            }
        }

    def get_system_stats(self) -> Dict[str, Any]:
        """
        获取系统统计信息（同步版本）

        Returns:
            Dict: 包含系统统计信息
        """
        return self._sync_helper.run_async(self.get_system_stats_async())

    async def get_system_stats_async(self) -> Dict[str, Any]:
        """
        获取系统统计信息（异步版本）

        Returns:
            Dict: 包含系统统计信息
        """
        # 获取基础数据
        services = await self.list_services_async()
        health_check = await self.check_services_async()
        tools = await self.list_tools_async()

        # 统计服务信息
        total_services = len(services) if services else 0
        healthy_services = 0
        unhealthy_services = 0

        if isinstance(health_check, dict) and "services" in health_check:
            for service in health_check["services"]:
                if service.get("status") == "healthy":
                    healthy_services += 1
                else:
                    unhealthy_services += 1

        total_tools = len(tools) if tools else 0

        # 按传输类型分组服务
        transport_stats = {}
        if services:
            for service in services:
                transport = getattr(service, 'transport_type', 'unknown')
                transport_name = transport.value if hasattr(transport, 'value') else str(transport)
                transport_stats[transport_name] = transport_stats.get(transport_name, 0) + 1

        return {
            "services": {
                "total": total_services,
                "healthy": healthy_services,
                "unhealthy": unhealthy_services,
                "by_transport": transport_stats
            },
            "tools": {
                "total": total_tools
            },
            "system": {
                "orchestrator_status": health_check.get("orchestrator_status", "unknown") if isinstance(health_check, dict) else "unknown",
                "context": self._context_type.name.lower(),
                "agent_id": self._agent_id if self._context_type == ContextType.AGENT else None
            }
        }

    def batch_add_services(self, services: List[Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """
        批量添加服务（同步版本）

        Args:
            services: 服务列表，可以是服务名或配置字典

        Returns:
            Dict: 批量操作结果
        """
        return self._sync_helper.run_async(self.batch_add_services_async(services), timeout=180.0)

    async def batch_add_services_async(self, services: List[Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """
        批量添加服务（异步版本）

        Args:
            services: 服务列表，可以是服务名或配置字典

        Returns:
            Dict: 批量操作结果
        """
        results = []

        for i, service in enumerate(services):
            try:
                if isinstance(service, str):
                    # 服务名方式
                    result = await self.add_service_async([service])
                elif isinstance(service, dict):
                    # 配置方式
                    result = await self.add_service_async(service)
                else:
                    results.append({
                        "index": i,
                        "success": False,
                        "message": "Invalid service format"
                    })
                    continue

                # add_service返回MCPStoreContext对象，表示成功
                success = result is not None
                results.append({
                    "index": i,
                    "service": service,
                    "success": success,
                    "message": f"Add operation {'succeeded' if success else 'failed'}"
                })

            except Exception as e:
                results.append({
                    "index": i,
                    "service": service,
                    "success": False,
                    "message": str(e)
                })

        success_count = sum(1 for r in results if r.get("success", False))
        total_count = len(results)

        return {
            "results": results,
            "summary": {
                "total": total_count,
                "succeeded": success_count,
                "failed": total_count - success_count
            },
            "success": success_count > 0,
            "message": f"Batch add completed: {success_count}/{total_count} succeeded"
        }

    def check_services(self) -> dict:
        """
        健康检查（同步版本），store/agent上下文自动判断
        - store上下文：聚合 global_agent_store 下所有 client_id 的服务健康状态
        - agent上下文：聚合 agent_id 下所有 client_id 的服务健康状态
        """
        return self._sync_helper.run_async(self.check_services_async())

    async def check_services_async(self) -> dict:
        """
        异步健康检查，store/agent上下文自动判断
        - store上下文：聚合 global_agent_store 下所有 client_id 的服务健康状态
        - agent上下文：聚合 agent_id 下所有 client_id 的服务健康状态
        """
        if self._context_type.name == 'STORE':
            return await self._store.get_health_status()
        elif self._context_type.name == 'AGENT':
            return await self._store.get_health_status(self._agent_id, agent_mode=True)
        else:
            print(f"[ERROR][check_services] 未知上下文类型: {self._context_type}")
            return {}

    def get_service_info(self, name: str) -> Any:
        """
        获取服务详情（同步版本），支持 store/agent 上下文
        - store上下文：在 global_agent_store 下的所有 client 中查找服务
        - agent上下文：在指定 agent_id 下的所有 client 中查找服务
        """
        return self._sync_helper.run_async(self.get_service_info_async(name))

    async def get_service_info_async(self, name: str) -> Any:
        """
        获取服务详情（异步版本），支持 store/agent 上下文
        - store上下文：在 global_agent_store 下的所有 client 中查找服务
        - agent上下文：在指定 agent_id 下的所有 client 中查找服务（支持本地名称）
        """
        if not name:
            return {}

        if self._context_type == ContextType.STORE:
            print(f"[INFO][get_service_info] STORE模式-在global_agent_store中查找服务: {name}")
            return await self._store.get_service_info(name)
        elif self._context_type == ContextType.AGENT:
            # Agent模式：将本地名称转换为全局名称进行查找
            global_name = name
            if self._service_mapper:
                global_name = self._service_mapper.to_global_name(name)

            print(f"[INFO][get_service_info] AGENT模式-在agent({self._agent_id})中查找服务: {name} (global: {global_name})")
            return await self._store.get_service_info(global_name, self._agent_id)
        else:
            print(f"[ERROR][get_service_info] 未知上下文类型: {self._context_type}")
            return {}

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
        from mcpstore.core.tool_resolver import ToolNameResolver

        resolver = ToolNameResolver(available_services=self._get_available_services())

        try:
            resolution = resolver.resolve_tool_name(tool_name, available_tools)
            logger.debug(f"Tool resolved: {tool_name} -> {resolution.service_name}::{resolution.original_tool_name} ({resolution.resolution_method})")
        except ValueError as e:
            raise ValueError(f"Tool resolution failed: {e}")

        # 构造标准化的工具执行请求
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

    def _get_available_services(self) -> List[str]:
        """获取可用服务列表"""
        try:
            if self._context_type == ContextType.STORE:
                services = self._store.for_store().list_services()
            else:
                services = self._store.for_agent(self._agent_id).list_services()
            return [service.name for service in services]
        except Exception:
            return []

    def _extract_original_tool_name(self, display_name: str, service_name: str) -> str:
        """
        从显示名称中提取原始工具名称

        Args:
            display_name: 显示名称（如：mcpstore-demo-weather_get_current_weather）
            service_name: 服务名称（如：mcpstore-demo-weather）

        Returns:
            原始工具名称（如：get_current_weather）
        """
        # 尝试移除服务名前缀
        if display_name.startswith(f"{service_name}_"):
            return display_name[len(service_name) + 1:]

        # 如果没有前缀，可能就是原始名称
        return display_name

    # === 上下文信息 ===
    @property
    def context_type(self) -> ContextType:
        """获取上下文类型"""
        return self._context_type

    @property
    def agent_id(self) -> Optional[str]:
        """获取当前agent_id"""
        return self._agent_id 

    def show_mcpconfig(self) -> Dict[str, Any]:
        """
        根据当前上下文（store/agent）获取对应的配置信息

        Returns:
            Dict[str, Any]: Store上下文返回MCP JSON格式，Agent上下文返回client配置字典
        """
        if self._context_type == ContextType.STORE:
            # Store上下文：返回MCP JSON格式的配置
            try:
                config = self._store.config.load_config()
                # 确保返回格式正确
                if isinstance(config, dict) and 'mcpServers' in config:
                    return config
                else:
                    logging.warning("Invalid MCP config format")
                    return {"mcpServers": {}}
            except Exception as e:
                logging.error(f"Failed to show MCP config: {e}")
                return {"mcpServers": {}}
        else:
            # Agent上下文：返回所有相关client配置的字典
            agent_id = self._agent_id
            client_ids = self._store.orchestrator.client_manager.get_agent_clients(agent_id)

            # 获取每个client的配置
            result = {}
            for client_id in client_ids:
                client_config = self._store.orchestrator.client_manager.get_client_config(client_id)
                if client_config:
                    result[client_id] = client_config

            return result

    # === 两步操作方法（推荐使用） ===

    async def update_config_two_step(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        两步操作：更新MCP JSON文件 + 重新注册服务

        Args:
            config: 新的配置内容

        Returns:
            Dict包含两步操作的结果：
            {
                "step1_json_update": bool,  # JSON文件更新是否成功
                "step2_service_registration": bool,  # 服务注册是否成功
                "step1_error": str,  # JSON更新错误信息（如果有）
                "step2_error": str,  # 服务注册错误信息（如果有）
                "overall_success": bool  # 整体是否成功
            }
        """
        result = {
            "step1_json_update": False,
            "step2_service_registration": False,
            "step1_error": None,
            "step2_error": None,
            "overall_success": False
        }

        # 第一步：更新JSON文件（必须成功）
        try:
            if self._context_type == ContextType.STORE:
                result["step1_json_update"] = self._store.config.save_config(config)
            else:
                # Agent级别暂时不支持直接更新JSON文件
                result["step1_error"] = "Agent level JSON update not supported"
                return result

            if not result["step1_json_update"]:
                result["step1_error"] = "Failed to update MCP JSON file"
                return result
        except Exception as e:
            result["step1_error"] = f"JSON update failed: {str(e)}"
            logging.error(f"Step 1 (JSON update) failed: {e}")
            return result

        # 第二步：重新注册服务（失败不影响第一步）
        try:
            if self._context_type == ContextType.STORE:
                # Store级别：使用统一同步机制重新注册所有服务
                if hasattr(self._store.orchestrator, 'sync_manager') and self._store.orchestrator.sync_manager:
                    sync_results = await self._store.orchestrator.sync_manager.sync_global_agent_store_from_mcp_json()
                    result["step2_service_registration"] = bool(sync_results.get("added") or sync_results.get("updated"))
                    if not result["step2_service_registration"]:
                        result["step2_error"] = f"同步失败: {sync_results.get('failed', [])}"
                else:
                    result["step2_service_registration"] = False
                    result["step2_error"] = "统一同步管理器不可用"
            else:
                # Agent级别：重新注册该Agent的服务
                service_names = list(config.get("mcpServers", {}).keys())
                registration_result = await self._store.register_services_for_agent(self._agent_id, service_names)
                result["step2_service_registration"] = registration_result.success
                if not result["step2_service_registration"]:
                    result["step2_error"] = registration_result.message

        except Exception as e:
            result["step2_error"] = f"Service registration failed: {str(e)}"
            logging.warning(f"Step 2 (service registration) failed: {e}, but JSON file was updated successfully")

        result["overall_success"] = result["step1_json_update"] and result["step2_service_registration"]
        return result

    def update_service(self, name: str, config: Dict[str, Any]) -> bool:
        """
        更新服务配置（同步版本）- 完全替换配置

        Args:
            name: 服务名称（不可更改）
            config: 新的完整服务配置（必须包含url或command字段）

        Returns:
            bool: 更新是否成功

        Note:
            此方法会完全替换服务配置。如需增量更新，请使用 patch_service() 方法。
        """
        return self._sync_helper.run_async(self.update_service_async(name, config))

    def patch_service(self, name: str, updates: Dict[str, Any]) -> bool:
        """
        增量更新服务配置（同步版本）- 推荐使用

        Args:
            name: 服务名称（不可更改）
            updates: 要更新的字段（会与现有配置合并）

        Returns:
            bool: 更新是否成功
        """
        return self._sync_helper.run_async(self.patch_service_async(name, updates))

    async def update_service_async(self, name: str, config: Dict[str, Any]) -> bool:
        """
        更新服务配置
        
        Args:
            name: 服务名称（不可更改）
            config: 新的服务配置
            
        Returns:
            bool: 更新是否成功
            
        Raises:
            ServiceNotFoundError: 服务不存在
            InvalidConfigError: 配置无效
        """
        try:
            # 1. 验证服务是否存在
            if not self._store.config.get_service_config(name):
                raise ServiceNotFoundError(f"Service {name} not found")
            
            # 2. 更新 mcp.json 中的配置（无论是 store 还是 agent 级别都要更新）
            if not self._store.config.update_service(name, config):
                raise InvalidConfigError(f"Failed to update service {name}")
            
            # 3. 获取需要更新的 client_ids
            if self._context_type == ContextType.STORE:
                # store 级别：更新所有 client
                client_ids = self._store.orchestrator.client_manager.get_global_agent_store_ids()
            else:
                # agent 级别：同样更新所有配置
                client_ids = self._store.orchestrator.client_manager.get_global_agent_store_ids()
            
            # 4. 更新每个 client 的配置
            for client_id in client_ids:
                client_config = self._store.orchestrator.client_manager.get_client_config(client_id)
                if client_config and name in client_config.get("mcpServers", {}):
                    client_config["mcpServers"][name] = config
                    self._store.orchestrator.client_manager.save_client_config(client_id, client_config)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to update service {name}: {str(e)}")
            raise

    async def patch_service_async(self, name: str, updates: Dict[str, Any]) -> bool:
        """
        增量更新服务配置（异步版本）

        Args:
            name: 服务名称（不可更改）
            updates: 要更新的字段（会与现有配置合并）

        Returns:
            bool: 更新是否成功

        Raises:
            ServiceNotFoundError: 服务不存在
            InvalidConfigError: 配置无效
        """
        try:
            # 1. 获取当前服务配置
            current_config = self._store.config.get_service_config(name)
            if not current_config:
                raise ServiceNotFoundError(f"Service {name} not found")

            # 2. 合并配置（updates 覆盖 current_config）
            merged_config = {**current_config, **updates}

            # 3. 调用完整更新方法
            return await self.update_service_async(name, merged_config)

        except Exception as e:
            logging.error(f"Failed to patch service {name}: {str(e)}")
            raise

    def delete_service(self, name: str) -> bool:
        """
        删除服务（同步版本）

        Args:
            name: 要删除的服务名称

        Returns:
            bool: 删除是否成功
        """
        return self._sync_helper.run_async(self.delete_service_async(name))

    async def delete_service_async(self, name: str) -> bool:
        """
        删除服务
        
        Args:
            name: 要删除的服务名称
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            ServiceNotFoundError: 服务不存在
            DeleteServiceError: 删除失败
        """
        try:
            # 1. 验证服务是否存在
            if not self._store.config.get_service_config(name):
                raise ServiceNotFoundError(f"Service {name} not found")
            
            # 2. 根据上下文确定删除范围
            if self._context_type == ContextType.STORE:
                # store 级别：删除所有 client 中的服务并更新 mcp.json
                client_ids = self._store.orchestrator.client_manager.get_global_agent_store_ids()
                
                # 从 mcp.json 中删除
                if not self._store.config.remove_service(name):
                    raise DeleteServiceError(f"Failed to remove service {name} from mcp.json")
                
                # 从所有 client 配置中删除
                for client_id in client_ids:
                    client_config = self._store.orchestrator.client_manager.get_client_config(client_id)
                    if client_config and name in client_config.get("mcpServers", {}):
                        del client_config["mcpServers"][name]
                        self._store.orchestrator.client_manager.save_client_config(client_id, client_config)
                
            else:
                # agent 级别：只删除该 agent 的 client 列表中的服务
                client_ids = self._store.orchestrator.client_manager.get_agent_clients(self._agent_id)
                
                # 从指定 agent 的 client 配置中删除
                for client_id in client_ids:
                    client_config = self._store.orchestrator.client_manager.get_client_config(client_id)
                    if client_config and name in client_config.get("mcpServers", {}):
                        del client_config["mcpServers"][name]
                        self._store.orchestrator.client_manager.save_client_config(client_id, client_config)
            
            return True

        except Exception as e:
            logging.error(f"Failed to delete service {name}: {str(e)}")
            raise

    async def delete_service_two_step(self, service_name: str) -> Dict[str, Any]:
        """
        两步操作：从MCP JSON文件删除服务 + 注销服务

        Args:
            service_name: 要删除的服务名称

        Returns:
            Dict包含两步操作的结果：
            {
                "step1_json_delete": bool,  # JSON文件删除是否成功
                "step2_service_unregistration": bool,  # 服务注销是否成功
                "step1_error": str,  # JSON删除错误信息（如果有）
                "step2_error": str,  # 服务注销错误信息（如果有）
                "overall_success": bool  # 整体是否成功
            }
        """
        result = {
            "step1_json_delete": False,
            "step2_service_unregistration": False,
            "step1_error": None,
            "step2_error": None,
            "overall_success": False
        }

        # 第一步：从JSON文件删除服务（必须成功）
        try:
            if self._context_type == ContextType.STORE:
                # 验证服务是否存在
                if not self._store.config.get_service_config(service_name):
                    result["step1_error"] = f"Service {service_name} not found in JSON file"
                    return result

                result["step1_json_delete"] = self._store.config.remove_service(service_name)
            else:
                # Agent级别暂时不支持直接删除JSON文件
                result["step1_error"] = "Agent level JSON delete not supported"
                return result

            if not result["step1_json_delete"]:
                result["step1_error"] = f"Failed to delete service {service_name} from MCP JSON file"
                return result
        except Exception as e:
            result["step1_error"] = f"JSON delete failed: {str(e)}"
            logging.error(f"Step 1 (JSON delete) failed: {e}")
            return result

        # 第二步：注销服务（失败不影响第一步）
        try:
            if self._context_type == ContextType.STORE:
                # Store级别：从所有client中注销服务
                client_ids = self._store.orchestrator.client_manager.get_global_agent_store_ids()

                unregistration_success = True
                for client_id in client_ids:
                    try:
                        client_config = self._store.orchestrator.client_manager.get_client_config(client_id)
                        if client_config and service_name in client_config.get("mcpServers", {}):
                            del client_config["mcpServers"][service_name]
                            self._store.orchestrator.client_manager.save_client_config(client_id, client_config)
                    except Exception as e:
                        unregistration_success = False
                        logging.warning(f"Failed to unregister service {service_name} from client {client_id}: {e}")

                result["step2_service_unregistration"] = unregistration_success
                if not unregistration_success:
                    result["step2_error"] = f"Failed to unregister service {service_name} from some clients"
            else:
                # Agent级别：从该Agent的client中注销服务
                client_ids = self._store.orchestrator.client_manager.get_agent_clients(self._agent_id)

                unregistration_success = True
                for client_id in client_ids:
                    try:
                        client_config = self._store.orchestrator.client_manager.get_client_config(client_id)
                        if client_config and service_name in client_config.get("mcpServers", {}):
                            del client_config["mcpServers"][service_name]
                            self._store.orchestrator.client_manager.save_client_config(client_id, client_config)
                    except Exception as e:
                        unregistration_success = False
                        logging.warning(f"Failed to unregister service {service_name} from agent client {client_id}: {e}")

                result["step2_service_unregistration"] = unregistration_success
                if not unregistration_success:
                    result["step2_error"] = f"Failed to unregister service {service_name} from agent clients"

        except Exception as e:
            result["step2_error"] = f"Service unregistration failed: {str(e)}"
            logging.warning(f"Step 2 (service unregistration) failed: {e}, but JSON file was updated successfully")

        result["overall_success"] = result["step1_json_delete"] and result["step2_service_unregistration"]
        return result



    def reset_config(self) -> bool:
        """重置配置（同步版本）"""
        return self._sync_helper.run_async(self.reset_config_async(), timeout=60.0)

    async def reset_config_async(self) -> bool:
        """
        重置配置（链式操作）
        - Store级别：重置global_agent_store的配置，并从文件中删除相关配置
        - Agent级别：重置指定Agent的配置，并从文件中删除相关配置

        Returns:
            是否成功重置
        """
        try:
            if self._agent_id is None:
                # Store级别重置
                global_agent_store_id = self._store.orchestrator.client_manager.global_agent_store_id

                # 1. 清理registry中的store级别数据
                if global_agent_store_id in self._store.orchestrator.registry.sessions:
                    del self._store.orchestrator.registry.sessions[global_agent_store_id]
                if global_agent_store_id in self._store.orchestrator.registry.service_health:
                    del self._store.orchestrator.registry.service_health[global_agent_store_id]
                if global_agent_store_id in self._store.orchestrator.registry.tool_cache:
                    del self._store.orchestrator.registry.tool_cache[global_agent_store_id]
                if global_agent_store_id in self._store.orchestrator.registry.tool_to_session_map:
                    del self._store.orchestrator.registry.tool_to_session_map[global_agent_store_id]

                # 2. 清理重连队列
                self._cleanup_reconnection_queue_for_client(global_agent_store_id)

                # 3. 从文件中删除Store相关配置
                file_success = self._store.orchestrator.client_manager.remove_store_from_files(global_agent_store_id)

                if file_success:
                    logging.info("Successfully reset store config, registry and files")
                else:
                    logging.warning("Reset store config and registry, but failed to clean files")

                return file_success
            else:
                # Agent级别重置

                # 1. 清理registry中的agent级别数据
                if self._agent_id in self._store.orchestrator.registry.sessions:
                    del self._store.orchestrator.registry.sessions[self._agent_id]
                if self._agent_id in self._store.orchestrator.registry.service_health:
                    del self._store.orchestrator.registry.service_health[self._agent_id]
                if self._agent_id in self._store.orchestrator.registry.tool_cache:
                    del self._store.orchestrator.registry.tool_cache[self._agent_id]
                if self._agent_id in self._store.orchestrator.registry.tool_to_session_map:
                    del self._store.orchestrator.registry.tool_to_session_map[self._agent_id]

                # 2. 清理重连队列
                agent_clients = self._store.orchestrator.client_manager.get_agent_clients(self._agent_id)
                for client_id in agent_clients:
                    self._cleanup_reconnection_queue_for_client(client_id)

                # 3. 从文件中删除Agent相关配置
                file_success = self._store.orchestrator.client_manager.remove_agent_from_files(self._agent_id)

                if file_success:
                    logging.info(f"Successfully reset agent {self._agent_id} config, registry and files")
                else:
                    logging.warning(f"Reset agent {self._agent_id} config and registry, but failed to clean files")

                return file_success

        except Exception as e:
            logging.error(f"Failed to reset config: {str(e)}")
            return False

    def _cleanup_reconnection_queue_for_client(self, client_id: str):
        """清理重连队列中与指定client相关的条目"""
        try:
            # 查找所有与该client相关的重连条目
            entries_to_remove = []
            for service_key in self._store.orchestrator.smart_reconnection.entries:
                if service_key.startswith(f"{client_id}:"):
                    entries_to_remove.append(service_key)

            # 移除这些条目
            for entry in entries_to_remove:
                self._store.orchestrator.smart_reconnection.remove_service(entry)

            if entries_to_remove:
                logging.info(f"Cleaned up {len(entries_to_remove)} reconnection queue entries for client {client_id}")

        except Exception as e:
            logging.warning(f"Failed to cleanup reconnection queue for client {client_id}: {e}")



    def get_service_status(self, name: str) -> dict:
        """获取单个服务的状态信息（同步版本）"""
        return self._sync_helper.run_async(self.get_service_status_async(name))

    async def get_service_status_async(self, name: str) -> dict:
        """获取单个服务的状态信息"""
        try:
            service_info = await self.get_service_info_async(name)
            if hasattr(service_info, 'service') and service_info.service:
                return {
                    "name": service_info.service.name,
                    "status": service_info.service.status,
                    "connected": service_info.connected,
                    "tool_count": service_info.service.tool_count,
                    "last_heartbeat": service_info.service.last_heartbeat,
                    "transport_type": service_info.service.transport_type
                }
            else:
                return {
                    "name": name,
                    "status": "not_found",
                    "connected": False,
                    "tool_count": 0,
                    "last_heartbeat": None,
                    "transport_type": None
                }
        except Exception as e:
            logging.error(f"Failed to get service status for {name}: {e}")
            return {
                "name": name,
                "status": "error",
                "connected": False,
                "error": str(e)
            }

    def restart_service(self, name: str) -> bool:
        """重启指定服务（同步版本）"""
        return self._sync_helper.run_async(self.restart_service_async(name))

    async def restart_service_async(self, name: str) -> bool:
        """重启指定服务"""
        try:
            # 首先验证服务是否存在
            service_info = await self.get_service_info_async(name)
            if not service_info or not (hasattr(service_info, 'service') and service_info.service):
                logging.error(f"Service {name} not found in registry")
                return False

            # 获取服务配置
            service_config = self._store.config.get_service_config(name)
            if not service_config:
                logging.error(f"Service config not found for {name} in mcp.json")
                # 尝试从当前运行的服务中获取配置信息
                logging.info(f"Attempting to restart service {name} without config reload")
                # 简单的重连尝试
                try:
                    # 获取当前上下文的client_id
                    agent_id = self._agent_id if self._context_type == ContextType.AGENT else self._store.orchestrator.client_manager.global_agent_store_id
                    client_ids = self._store.orchestrator.client_manager.get_agent_clients(agent_id)

                    for client_id in client_ids:
                        if self._store.orchestrator.registry.has_service(client_id, name):
                            # 尝试重新连接服务
                            success, message = await self._store.orchestrator.connect_service(name)
                            if success:
                                logging.info(f"Service {name} reconnected successfully")
                                return True

                    logging.error(f"Failed to reconnect service {name}")
                    return False
                except Exception as e:
                    logging.error(f"Failed to reconnect service {name}: {e}")
                    return False

            # 先删除服务
            delete_success = await self.delete_service_async(name)
            if not delete_success:
                logging.warning(f"Failed to delete service {name} during restart, attempting to continue")

            # 等待一小段时间确保服务完全停止
            import asyncio
            await asyncio.sleep(1)

            # 构造添加服务的配置
            add_config = {
                "name": name,
                **service_config
            }

            # 重新添加服务
            await self.add_service_async(add_config)
            logging.info(f"Service {name} restarted successfully")
            return True

        except Exception as e:
            logging.error(f"Failed to restart service {name}: {e}")
            return False



    # === 文件直接重置功能 ===
    def reset_mcp_json_file(self) -> bool:
        """直接重置MCP JSON配置文件（同步版本）"""
        return self._sync_helper.run_async(self.reset_mcp_json_file_async(), timeout=60.0)

    async def reset_mcp_json_file_async(self) -> bool:
        """
        直接重置MCP JSON配置文件（仅Store级别可用）
        备份后重置为空字典 {"mcpServers": {}}

        Returns:
            是否成功重置
        """
        if self._agent_id is not None:
            logging.warning("reset_mcp_json_file is only available for store level")
            return False

        try:
            success = self._store.config.reset_mcp_json_file()
            if success:
                # 重置后需要重新加载配置
                await self._store.orchestrator.setup()
                logging.info("Successfully reset MCP JSON file and reloaded")
            return success

        except Exception as e:
            logging.error(f"Failed to reset MCP JSON file: {str(e)}")
            return False

    def reset_client_services_file(self) -> bool:
        """直接重置client_services.json文件（同步版本）"""
        return self._sync_helper.run_async(self.reset_client_services_file_async(), timeout=60.0)

    async def reset_client_services_file_async(self) -> bool:
        """
        直接重置client_services.json文件（仅Store级别可用）
        备份后重置为空字典 {}

        Returns:
            是否成功重置
        """
        if self._agent_id is not None:
            logging.warning("reset_client_services_file is only available for store level")
            return False

        try:
            success = self._store.orchestrator.client_manager.reset_client_services_file()
            if success:
                # 重置后需要重新加载配置
                await self._store.orchestrator.setup()
                logging.info("Successfully reset client_services.json file and reloaded")
            return success

        except Exception as e:
            logging.error(f"Failed to reset client_services.json file: {str(e)}")
            return False

    def reset_agent_clients_file(self) -> bool:
        """直接重置agent_clients.json文件（同步版本）"""
        return self._sync_helper.run_async(self.reset_agent_clients_file_async(), timeout=60.0)

    async def reset_agent_clients_file_async(self) -> bool:
        """
        直接重置agent_clients.json文件（仅Store级别可用）
        备份后重置为空字典 {}

        Returns:
            是否成功重置
        """
        if self._agent_id is not None:
            logging.warning("reset_agent_clients_file is only available for store level")
            return False

        try:
            success = self._store.orchestrator.client_manager.reset_agent_clients_file()
            if success:
                # 重置后需要重新加载配置
                await self._store.orchestrator.setup()
                logging.info("Successfully reset agent_clients.json file and reloaded")
            return success

        except Exception as e:
            logging.error(f"Failed to reset agent_clients.json file: {str(e)}")
            return False



    def get_unified_config(self) -> 'UnifiedConfigManager':
        """获取统一配置管理器

        Returns:
            UnifiedConfigManager: 统一配置管理器实例
        """
        return self._store.get_unified_config()

    # === 新功能：工具转换 ===

    def create_simple_tool(self, original_tool: str, friendly_name: str = None) -> 'MCPStoreContext':
        """
        创建简化版工具

        Args:
            original_tool: 原始工具名
            friendly_name: 友好名称（可选）

        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            result = self._transformation_manager.create_simple_weather_tool(original_tool)
            logging.info(f"[{self._context_type.value}] Created simple tool for: {original_tool}")
            return self
        except Exception as e:
            logging.error(f"[{self._context_type.value}] Failed to create simple tool: {e}")
            return self

    def create_safe_tool(self, original_tool: str, validation_rules: Dict[str, Any]) -> 'MCPStoreContext':
        """
        创建安全版工具（带验证）

        Args:
            original_tool: 原始工具名
            validation_rules: 验证规则字典

        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            # 转换验证规则为函数
            validation_functions = {}
            for param, rule in validation_rules.items():
                if isinstance(rule, dict):
                    validation_functions[param] = self._create_validation_function(rule)

            result = self._transformation_manager.transformer.create_validated_tool(
                original_tool, validation_functions
            )
            logging.info(f"[{self._context_type.value}] Created safe tool for: {original_tool}")
            return self
        except Exception as e:
            logging.error(f"[{self._context_type.value}] Failed to create safe tool: {e}")
            return self

    # === 新功能：环境管理 ===

    def switch_environment(self, environment: str) -> 'MCPStoreContext':
        """
        切换运行环境

        Args:
            environment: 环境名称 (development, testing, production)

        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            success = self._component_manager.switch_environment(environment)
            if success:
                logging.info(f"[{self._context_type.value}] Switched to environment: {environment}")
            else:
                logging.warning(f"[{self._context_type.value}] Failed to switch to environment: {environment}")
            return self
        except Exception as e:
            logging.error(f"[{self._context_type.value}] Error switching environment: {e}")
            return self

    def create_custom_environment(self, name: str, allowed_categories: List[str]) -> 'MCPStoreContext':
        """
        创建自定义环境

        Args:
            name: 环境名称
            allowed_categories: 允许的工具分类

        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            self._component_manager.create_custom_environment(name, allowed_categories)
            logging.info(f"[{self._context_type.value}] Created custom environment: {name}")
            return self
        except Exception as e:
            logging.error(f"[{self._context_type.value}] Failed to create environment {name}: {e}")
            return self

    # === 新功能：OpenAPI 集成 ===

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
            logging.info(f"[{self._context_type.value}] Imported API {api_name}: {result.get('total_endpoints', 0)} endpoints")
            return self
        except Exception as e:
            logging.error(f"[{self._context_type.value}] Failed to import API {api_url}: {e}")
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

    # === 新功能：性能优化 ===

    def enable_caching(self, patterns: Dict[str, int] = None) -> 'MCPStoreContext':
        """
        启用智能缓存

        Args:
            patterns: 缓存模式配置 {工具模式: TTL秒数}

        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            self._performance_optimizer.setup_tool_caching(patterns)
            logging.info(f"[{self._context_type.value}] Enabled intelligent caching")
            return self
        except Exception as e:
            logging.error(f"[{self._context_type.value}] Failed to enable caching: {e}")
            return self

    def get_performance_report(self) -> Dict[str, Any]:
        """
        获取性能报告

        Returns:
            Dict: 性能报告数据
        """
        try:
            return self._performance_optimizer.get_performance_summary()
        except Exception as e:
            logging.error(f"[{self._context_type.value}] Failed to get performance report: {e}")
            return {}

    # === 新功能：认证安全 ===

    def setup_auth(self, auth_type: str = "bearer", enabled: bool = True) -> 'MCPStoreContext':
        """
        设置认证

        Args:
            auth_type: 认证类型 ("bearer", "api_key")
            enabled: 是否启用

        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            if auth_type == "bearer":
                self._auth_manager.setup_bearer_auth(enabled)
            elif auth_type == "api_key":
                self._auth_manager.setup_api_key_auth(enabled)
            else:
                logging.warning(f"[{self._context_type.value}] Unknown auth type: {auth_type}")
                return self

            logging.info(f"[{self._context_type.value}] Setup {auth_type} authentication: {'enabled' if enabled else 'disabled'}")
            return self
        except Exception as e:
            logging.error(f"[{self._context_type.value}] Failed to setup authentication: {e}")
            return self

    # === 新功能：监控分析 ===

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        获取使用统计

        Returns:
            Dict: 使用统计数据
        """
        try:
            return self._monitoring_manager.get_dashboard_data()
        except Exception as e:
            logging.error(f"[{self._context_type.value}] Failed to get usage stats: {e}")
            return {}

    def record_tool_execution(self, tool_name: str, duration: float, success: bool, error: Exception = None) -> 'MCPStoreContext':
        """
        记录工具执行情况

        Args:
            tool_name: 工具名称
            duration: 执行时间
            success: 是否成功
            error: 错误信息（可选）

        Returns:
            MCPStoreContext: 支持链式调用
        """
        try:
            service_name = self._extract_service_name(tool_name)
            self._monitoring_manager.record_tool_execution(
                tool_name=tool_name,
                service_name=service_name,
                duration=duration,
                success=success,
                user_id=self._agent_id,
                error=error
            )
            return self
        except Exception as e:
            logging.error(f"[{self._context_type.value}] Failed to record tool execution: {e}")
            return self

    # === 辅助方法 ===

    def _create_validation_function(self, rule: Dict[str, Any]) -> callable:
        """创建验证函数"""
        def validate(value):
            if "min_length" in rule and len(str(value)) < rule["min_length"]:
                raise ValueError(f"Value too short, minimum length: {rule['min_length']}")
            if "max_length" in rule and len(str(value)) > rule["max_length"]:
                raise ValueError(f"Value too long, maximum length: {rule['max_length']}")
            if "pattern" in rule:
                import re
                if not re.match(rule["pattern"], str(value)):
                    raise ValueError(f"Value doesn't match pattern: {rule['pattern']}")
            return value
        return validate

    def _extract_service_name(self, tool_name: str) -> str:
        """从工具名提取服务名"""
        if "_" in tool_name:
            return tool_name.split("_")[0]
        return "unknown"

    # === 监控和统计接口 ===

    # 旧的get_tool_usage_stats方法已移除，使用get_tool_records代替



    async def check_network_endpoints(self, endpoints: List[Dict[str, str]]) -> List[NetworkEndpoint]:
        """检查网络端点状态"""
        return await self._monitoring.check_network_endpoints(endpoints)

    def get_system_resource_info(self) -> SystemResourceInfo:
        """获取系统资源信息"""
        return self._monitoring.get_system_resource_info()

    async def get_system_resource_info_async(self) -> SystemResourceInfo:
        """异步获取系统资源信息"""
        return self.get_system_resource_info()

    def record_api_call(self, response_time: float):
        """记录API调用"""
        self._monitoring.record_api_call(response_time)

    # 旧的record_tool_execution方法已移除，使用新的详细记录系统

    def increment_active_connections(self):
        """增加活跃连接数"""
        self._monitoring.increment_active_connections()

    def decrement_active_connections(self):
        """减少活跃连接数"""
        self._monitoring.decrement_active_connections()

    def get_tool_records(self, limit: int = 50) -> Dict[str, Any]:
        """获取工具执行记录"""
        return self._monitoring.get_tool_records(limit)

    async def get_tool_records_async(self, limit: int = 50) -> Dict[str, Any]:
        """异步获取工具执行记录"""
        return self.get_tool_records(limit)

    # === Agent统计功能 ===
    def get_agents_summary(self) -> AgentsSummary:
        """
        获取所有Agent的统计摘要信息（同步版本）

        Returns:
            AgentsSummary: 包含所有Agent统计信息的汇总对象
        """
        return self._sync_helper.run_async(self.get_agents_summary_async())

    async def get_agents_summary_async(self) -> AgentsSummary:
        """
        获取所有Agent的统计摘要信息（异步版本）

        Returns:
            AgentsSummary: 包含所有Agent统计信息的汇总对象
        """
        try:
            # 1. 获取所有Agent ID
            all_agent_data = self._store.client_manager.load_all_agent_clients()
            agent_ids = list(all_agent_data.keys())

            # 2. 获取Store级别的统计信息
            store_services = await self._store.for_store().list_services_async()
            store_tools = await self._store.for_store().list_tools_async()

            # 3. 统计每个Agent的信息
            agent_statistics = []
            total_services = len(store_services)
            total_tools = len(store_tools)
            active_agents = 0

            for agent_id in agent_ids:
                try:
                    agent_stats = await self._get_agent_statistics(agent_id)
                    if agent_stats.service_count > 0:
                        active_agents += 1
                    agent_statistics.append(agent_stats)
                    total_services += agent_stats.service_count
                    total_tools += agent_stats.tool_count
                except Exception as e:
                    logger.warning(f"Failed to get statistics for agent {agent_id}: {e}")
                    # 创建空的统计信息
                    agent_statistics.append(AgentStatistics(
                        agent_id=agent_id,
                        service_count=0,
                        tool_count=0,
                        healthy_services=0,
                        unhealthy_services=0,
                        total_tool_executions=0,
                        services=[]
                    ))

            # 4. 构建汇总信息
            summary = AgentsSummary(
                total_agents=len(agent_ids),
                active_agents=active_agents,
                total_services=total_services,
                total_tools=total_tools,
                store_services=len(store_services),
                store_tools=len(store_tools),
                agents=agent_statistics
            )

            logger.info(f"Generated agents summary: {len(agent_ids)} agents, {active_agents} active")
            return summary

        except Exception as e:
            logger.error(f"Failed to get agents summary: {e}")
            # 返回空的汇总信息
            return AgentsSummary(
                total_agents=0,
                active_agents=0,
                total_services=0,
                total_tools=0,
                store_services=0,
                store_tools=0,
                agents=[]
            )

    async def _get_agent_statistics(self, agent_id: str) -> AgentStatistics:
        """
        获取单个Agent的统计信息

        Args:
            agent_id: Agent ID

        Returns:
            AgentStatistics: Agent统计信息
        """
        try:
            # 🔧 修复：global_agent_store 使用Store模式，其他Agent使用Agent模式
            if agent_id == self._store.client_manager.global_agent_store_id:
                # global_agent_store 使用Store模式的服务、工具列表和健康检查
                services = await self._store.list_services()
                tools = await self._store.list_tools()
                health_status = await self.check_services_async()
            else:
                # 普通Agent使用Agent模式
                agent_context = self._store.for_agent(agent_id)
                services = await agent_context.list_services_async()
                tools = await agent_context.list_tools_async()
                health_status = await agent_context.check_services_async()
            healthy_count = 0
            unhealthy_count = 0

            # 构建服务摘要
            service_summaries = []
            for service in services:
                # 获取服务配置以确定类型和状态
                service_config = self._store.config.get_service_config(service.name) or {}

                # 确定服务类型
                service_type = "unknown"
                if service_config.get('url'):
                    service_type = "remote"
                elif service_config.get('command'):
                    service_type = "local"
                elif hasattr(service, 'transport') and service.transport:
                    service_type = service.transport
                elif hasattr(service, 'config') and service.config:
                    if 'url' in service.config:
                        service_type = "remote"
                    elif 'command' in service.config:
                        service_type = "local"

                # 确定服务状态 - 修复数据结构访问
                service_status = "unknown"
                if isinstance(health_status, dict) and 'services' in health_status:
                    # health_status 是字典格式: {"orchestrator_status": "running", "services": [...]}
                    for health_item in health_status['services']:
                        if isinstance(health_item, dict) and health_item.get('name') == service.name:
                            service_status = health_item.get('status', 'unknown')
                            break
                elif isinstance(health_status, list):
                    # health_status 是列表格式
                    for health_item in health_status:
                        if isinstance(health_item, dict) and health_item.get('name') == service.name:
                            service_status = health_item.get('status', 'unknown')
                            break

                # 如果还是unknown，直接调用健康检查
                if service_status == "unknown":
                    try:
                        is_healthy = await self._store.orchestrator.is_service_healthy(service.name, agent_id)
                        service_status = "healthy" if is_healthy else "unhealthy"
                    except Exception as e:
                        logger.debug(f"Health check failed for service {service.name}: {e}")
                        service_status = "unhealthy"

                if service_status == "healthy":
                    healthy_count += 1
                elif service_status == "unhealthy":
                    unhealthy_count += 1

                # 统计该服务的工具数量
                service_tool_count = len([t for t in tools if t.service_name == service.name])

                # 获取client_id - 从多个来源尝试获取
                client_id = None
                if hasattr(service, 'client_id'):
                    client_id = service.client_id
                else:
                    # 尝试从client_manager获取
                    try:
                        client_ids = self._store.client_manager.get_agent_clients(agent_id)
                        if client_ids:
                            client_id = client_ids[0]  # 使用第一个client_id
                    except Exception:
                        pass

                # 获取生命周期状态和元数据
                service_state = self._store.orchestrator.lifecycle_manager.get_service_state(agent_id, service.name)
                state_metadata = self._store.orchestrator.lifecycle_manager.get_service_metadata(agent_id, service.name)

                # 🔧 修复：确保service_state不为None，提供默认值
                if service_state is None:
                    # 如果没有状态记录，根据服务健康状况设置默认状态
                    if service_status == "healthy":
                        service_state = ServiceConnectionState.HEALTHY
                    elif service_status == "unhealthy":
                        service_state = ServiceConnectionState.UNREACHABLE
                    else:
                        service_state = ServiceConnectionState.INITIALIZING

                service_summaries.append(AgentServiceSummary(
                    service_name=service.name,
                    service_type=service_type,
                    status=service_state,  # 使用新的7状态枚举
                    tool_count=service_tool_count,
                    client_id=client_id,
                    response_time=state_metadata.response_time if state_metadata else None,
                    health_details=state_metadata
                ))

            # 统计健康和不健康的服务（基于新的7状态）
            healthy_count = 0
            unhealthy_count = 0
            for service_summary in service_summaries:
                if service_summary.status == ServiceConnectionState.HEALTHY:
                    healthy_count += 1
                elif service_summary.status in [ServiceConnectionState.WARNING, ServiceConnectionState.RECONNECTING]:
                    # WARNING和RECONNECTING状态算作部分健康，不计入unhealthy
                    pass
                elif service_summary.status in [ServiceConnectionState.UNREACHABLE, ServiceConnectionState.DISCONNECTED]:
                    unhealthy_count += 1
                # INITIALIZING和DISCONNECTING状态不计入统计

            # 获取工具执行统计（如果有监控数据）
            total_executions = 0
            last_activity = None
            try:
                tool_records = agent_context.get_tool_records(limit=1000)
                if isinstance(tool_records, dict) and 'records' in tool_records:
                    total_executions = len(tool_records['records'])
                    if tool_records['records']:
                        # 获取最近的活动时间
                        latest_record = max(tool_records['records'],
                                          key=lambda x: x.get('timestamp', ''))
                        if latest_record.get('timestamp'):
                            from datetime import datetime
                            last_activity = datetime.fromisoformat(latest_record['timestamp'].replace('Z', '+00:00'))
            except Exception as e:
                logger.debug(f"Could not get tool execution stats for agent {agent_id}: {e}")

            return AgentStatistics(
                agent_id=agent_id,
                service_count=len(services),
                tool_count=len(tools),
                healthy_services=healthy_count,
                unhealthy_services=unhealthy_count,
                total_tool_executions=total_executions,
                last_activity=last_activity,
                services=service_summaries
            )

        except Exception as e:
            logger.error(f"Failed to get statistics for agent {agent_id}: {e}")
            return AgentStatistics(
                agent_id=agent_id,
                service_count=0,
                tool_count=0,
                healthy_services=0,
                unhealthy_services=0,
                total_tool_executions=0,
                services=[]
            )


