"""
MCPStore Service Management Module
服务管理相关操作的实现
"""

import logging
from typing import Dict, List, Optional, Any, Union

from .types import ContextType

logger = logging.getLogger(__name__)

class ServiceManagementMixin:
    """服务管理混入类"""
    
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
            logger.error(f"[check_services] 未知上下文类型: {self._context_type}")
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
            logger.info(f"[get_service_info] STORE模式-在global_agent_store中查找服务: {name}")
            return await self._store.get_service_info(name)
        elif self._context_type == ContextType.AGENT:
            # Agent模式：将本地名称转换为全局名称进行查找
            global_name = name
            if self._service_mapper:
                global_name = self._service_mapper.to_global_name(name)

            logger.info(f"[get_service_info] AGENT模式-在agent({self._agent_id})中查找服务: {name} (global: {global_name})")
            return await self._store.get_service_info(global_name, self._agent_id)
        else:
            logger.error(f"[get_service_info] 未知上下文类型: {self._context_type}")
            return {}

    def update_service(self, name: str, config: Dict[str, Any]) -> bool:
        """
        更新服务配置（同步版本）- 完全替换配置
        
        Args:
            name: 服务名称
            config: 新的服务配置
            
        Returns:
            bool: 更新是否成功
        """
        return self._sync_helper.run_async(self.update_service_async(name, config), timeout=60.0)

    async def update_service_async(self, name: str, config: Dict[str, Any]) -> bool:
        """
        更新服务配置（异步版本）- 完全替换配置
        
        Args:
            name: 服务名称
            config: 新的服务配置
            
        Returns:
            bool: 更新是否成功
        """
        try:
            if self._context_type == ContextType.STORE:
                # Store级别：直接更新mcp.json中的服务配置
                current_config = self._store.config.load_config()
                if name not in current_config.get("mcpServers", {}):
                    logger.error(f"Service {name} not found in store configuration")
                    return False
                
                # 完全替换配置
                current_config["mcpServers"][name] = config
                success = self._store.config.save_config(current_config)
                
                if success:
                    # 触发重新注册
                    if hasattr(self._store.orchestrator, 'sync_manager') and self._store.orchestrator.sync_manager:
                        await self._store.orchestrator.sync_manager.sync_global_agent_store_from_mcp_json()
                
                return success
            else:
                # Agent级别：更新agent的服务配置
                global_name = name
                if self._service_mapper:
                    global_name = self._service_mapper.to_global_name(name)
                
                return self._store.client_manager.replace_service_in_agent(
                    agent_id=self._agent_id,
                    service_name=global_name,
                    new_service_config=config
                )
        except Exception as e:
            logger.error(f"Failed to update service {name}: {e}")
            return False

    def patch_service(self, name: str, updates: Dict[str, Any]) -> bool:
        """
        增量更新服务配置（同步版本）- 推荐使用
        
        Args:
            name: 服务名称
            updates: 要更新的配置项
            
        Returns:
            bool: 更新是否成功
        """
        return self._sync_helper.run_async(self.patch_service_async(name, updates), timeout=60.0)

    async def patch_service_async(self, name: str, updates: Dict[str, Any]) -> bool:
        """
        增量更新服务配置（异步版本）- 推荐使用
        
        Args:
            name: 服务名称
            updates: 要更新的配置项
            
        Returns:
            bool: 更新是否成功
        """
        try:
            if self._context_type == ContextType.STORE:
                # Store级别：增量更新mcp.json中的服务配置
                current_config = self._store.config.load_config()
                if name not in current_config.get("mcpServers", {}):
                    logger.error(f"Service {name} not found in store configuration")
                    return False
                
                # 增量更新配置
                service_config = current_config["mcpServers"][name]
                service_config.update(updates)
                
                success = self._store.config.save_config(current_config)
                
                if success:
                    # 触发重新注册
                    if hasattr(self._store.orchestrator, 'sync_manager') and self._store.orchestrator.sync_manager:
                        await self._store.orchestrator.sync_manager.sync_global_agent_store_from_mcp_json()
                
                return success
            else:
                # Agent级别：增量更新agent的服务配置
                global_name = name
                if self._service_mapper:
                    global_name = self._service_mapper.to_global_name(name)
                
                # 获取当前配置
                client_ids = self._store.client_manager.get_agent_clients(self._agent_id)
                for client_id in client_ids:
                    client_config = self._store.client_manager.get_client_config(client_id)
                    if client_config and global_name in client_config.get("mcpServers", {}):
                        # 增量更新
                        client_config["mcpServers"][global_name].update(updates)
                        return self._store.client_manager.save_client_config(client_id, client_config)
                
                logger.error(f"Service {global_name} not found in agent {self._agent_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to patch service {name}: {e}")
            return False

    def delete_service(self, name: str) -> bool:
        """
        删除服务（同步版本）
        
        Args:
            name: 服务名称
            
        Returns:
            bool: 删除是否成功
        """
        return self._sync_helper.run_async(self.delete_service_async(name), timeout=60.0)

    async def delete_service_async(self, name: str) -> bool:
        """
        删除服务（异步版本）
        
        Args:
            name: 服务名称
            
        Returns:
            bool: 删除是否成功
        """
        try:
            if self._context_type == ContextType.STORE:
                # Store级别：从mcp.json中删除服务
                current_config = self._store.config.load_config()
                if name not in current_config.get("mcpServers", {}):
                    logger.warning(f"Service {name} not found in store configuration")
                    return True  # 已经不存在，视为成功
                
                # 删除服务配置
                del current_config["mcpServers"][name]
                success = self._store.config.save_config(current_config)
                
                if success:
                    # 触发重新注册
                    if hasattr(self._store.orchestrator, 'sync_manager') and self._store.orchestrator.sync_manager:
                        await self._store.orchestrator.sync_manager.sync_global_agent_store_from_mcp_json()
                
                return success
            else:
                # Agent级别：从agent配置中删除服务
                global_name = name
                if self._service_mapper:
                    global_name = self._service_mapper.to_global_name(name)
                
                return self._store.client_manager.remove_service_from_agent(
                    agent_id=self._agent_id,
                    service_name=global_name
                )
        except Exception as e:
            logger.error(f"Failed to delete service {name}: {e}")
            return False

    async def delete_service_two_step(self, service_name: str) -> Dict[str, Any]:
        """
        两步删除服务：从配置文件删除 + 从Registry注销
        
        Args:
            service_name: 服务名称
            
        Returns:
            Dict: 包含两步操作结果的字典
        """
        result = {
            "step1_config_removal": False,
            "step2_registry_cleanup": False,
            "step1_error": None,
            "step2_error": None,
            "overall_success": False
        }
        
        # 第一步：从配置文件删除
        try:
            result["step1_config_removal"] = await self.delete_service_async(service_name)
            if not result["step1_config_removal"]:
                result["step1_error"] = "Failed to remove service from configuration"
        except Exception as e:
            result["step1_error"] = f"Configuration removal failed: {str(e)}"
            logger.error(f"Step 1 (config removal) failed: {e}")
        
        # 第二步：从Registry清理（即使第一步失败也尝试）
        try:
            if self._context_type == ContextType.STORE:
                # Store级别：清理global_agent_store的Registry
                cleanup_success = await self._store.orchestrator.registry.cleanup_service(service_name)
            else:
                # Agent级别：清理特定agent的Registry
                global_name = service_name
                if self._service_mapper:
                    global_name = self._service_mapper.to_global_name(service_name)
                cleanup_success = await self._store.orchestrator.registry.cleanup_service(global_name, self._agent_id)
            
            result["step2_registry_cleanup"] = cleanup_success
            if not cleanup_success:
                result["step2_error"] = "Failed to cleanup service from registry"
        except Exception as e:
            result["step2_error"] = f"Registry cleanup failed: {str(e)}"
            logger.warning(f"Step 2 (registry cleanup) failed: {e}")
        
        result["overall_success"] = result["step1_config_removal"] and result["step2_registry_cleanup"]
        return result

    def reset_config(self) -> bool:
        """重置配置（同步版本）"""
        return self._sync_helper.run_async(self.reset_config_async(), timeout=60.0)

    async def reset_config_async(self) -> bool:
        """
        重置配置（异步版本）

        根据上下文类型执行不同的重置操作：
        - Store上下文：重置整个mcp.json配置文件
        - Agent上下文：重置该Agent的所有client配置
        """
        try:
            if self._context_type == ContextType.STORE:
                # Store级别：重置mcp.json
                default_config = {"mcpServers": {}}
                success = self._store.config.save_config(default_config)

                if success:
                    # 触发重新注册（清空所有服务）
                    if hasattr(self._store.orchestrator, 'sync_manager') and self._store.orchestrator.sync_manager:
                        await self._store.orchestrator.sync_manager.sync_global_agent_store_from_mcp_json()

                return success
            else:
                # Agent级别：重置该Agent的所有配置
                return self._store.client_manager.reset_agent_configs(self._agent_id)
        except Exception as e:
            logger.error(f"Failed to reset config: {e}")
            return False

    def get_service_status(self, name: str) -> dict:
        """获取单个服务的状态信息（同步版本）"""
        return self._sync_helper.run_async(self.get_service_status_async(name))

    async def get_service_status_async(self, name: str) -> dict:
        """获取单个服务的状态信息"""
        try:
            if self._context_type == ContextType.STORE:
                return await self._store.orchestrator.get_service_status(name)
            else:
                # Agent模式：转换服务名称
                global_name = name
                if self._service_mapper:
                    global_name = self._service_mapper.to_global_name(name)
                return await self._store.orchestrator.get_service_status(global_name, self._agent_id)
        except Exception as e:
            logger.error(f"Failed to get service status for {name}: {e}")
            return {"status": "error", "error": str(e)}

    def restart_service(self, name: str) -> bool:
        """重启指定服务（同步版本）"""
        return self._sync_helper.run_async(self.restart_service_async(name))

    async def restart_service_async(self, name: str) -> bool:
        """重启指定服务"""
        try:
            if self._context_type == ContextType.STORE:
                return await self._store.orchestrator.restart_service(name)
            else:
                # Agent模式：转换服务名称
                global_name = name
                if self._service_mapper:
                    global_name = self._service_mapper.to_global_name(name)
                return await self._store.orchestrator.restart_service(global_name, self._agent_id)
        except Exception as e:
            logger.error(f"Failed to restart service {name}: {e}")
            return False

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
                    logger.warning("Invalid MCP config format")
                    return {"mcpServers": {}}
            except Exception as e:
                logger.error(f"Failed to show MCP config: {e}")
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
            logger.error(f"Step 1 (JSON update) failed: {e}")
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
            logger.warning(f"Step 2 (service registration) failed: {e}, but JSON file was updated successfully")

        result["overall_success"] = result["step1_json_update"] and result["step2_service_registration"]
        return result
