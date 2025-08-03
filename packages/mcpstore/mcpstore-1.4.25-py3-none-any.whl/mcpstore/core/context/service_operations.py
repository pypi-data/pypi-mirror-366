"""
MCPStore Service Operations Module
Implementation of service-related operations
"""

import logging
from typing import Dict, List, Optional, Any, Union

from mcpstore.core.models.service import ServiceInfo, ServiceConfigUnion
from .types import ContextType

logger = logging.getLogger(__name__)

class ServiceOperationsMixin:
    """Service operations mixin class"""

    # === Core service interface ===
    def list_services(self) -> List[ServiceInfo]:
        """
        List services (synchronous version)
        - store context: aggregate services from all client_ids under global_agent_store
        - agent context: aggregate services from all client_ids under agent_id
        """
        return self._sync_helper.run_async(self.list_services_async())

    async def list_services_async(self) -> List[ServiceInfo]:
        """
        List services (asynchronous version)
        - store context: aggregate services from all client_ids under global_agent_store
        - agent context: aggregate services from all client_ids under agent_id (show original names)
        """
        if self._context_type == ContextType.STORE:
            return await self._store.list_services()
        else:
            # Agent mode: get global service list, then convert to local names
            global_services = await self._store.list_services(self._agent_id, agent_mode=True)

            # Use mapper to convert to local names
            if self._service_mapper:
                local_services = self._service_mapper.convert_service_list_to_local(global_services)
                return local_services
            else:
                return global_services

    def add_service(self, config: Union[ServiceConfigUnion, List[str], None] = None, json_file: str = None) -> 'MCPStoreContext':
        """
        Enhanced service addition method (synchronous version), supports multiple configuration formats

        Args:
            config: Service configuration, supports multiple formats
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
