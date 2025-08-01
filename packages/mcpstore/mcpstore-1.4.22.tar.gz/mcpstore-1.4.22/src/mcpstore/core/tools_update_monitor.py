"""
工具更新监控器
负责定期检查和更新服务的工具列表
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ToolsUpdateMonitor:
    """工具列表更新监控器"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.registry = orchestrator.registry
        
        # 配置参数（从orchestrator配置中获取）
        timing_config = orchestrator.config.get("timing", {})
        self.tools_update_interval = timing_config.get("tools_update_interval_seconds", 7200)  # 默认2小时
        self.enable_tools_update = timing_config.get("enable_tools_update", True)
        self.update_tools_on_reconnection = timing_config.get("update_tools_on_reconnection", True)
        self.detect_tools_changes = timing_config.get("detect_tools_changes", False)
        
        # 状态跟踪
        self.last_update_times: Dict[str, float] = {}  # service_name -> timestamp
        self.update_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        logger.info(f"ToolsUpdateMonitor initialized: interval={self.tools_update_interval}s, "
                   f"enabled={self.enable_tools_update}, reconnection_update={self.update_tools_on_reconnection}")
    
    async def start(self):
        """启动工具更新监控"""
        if not self.enable_tools_update:
            logger.info("Tools update monitoring is disabled")
            return
        
        if self.is_running:
            logger.warning("ToolsUpdateMonitor is already running")
            return
        
        self.is_running = True
        self.update_task = asyncio.create_task(self._update_loop())
        logger.info("ToolsUpdateMonitor started")
    
    async def stop(self):
        """停止工具更新监控"""
        self.is_running = False
        if self.update_task and not self.update_task.done():
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        logger.info("ToolsUpdateMonitor stopped")
    
    async def _update_loop(self):
        """工具更新循环"""
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        while self.is_running:
            try:
                await asyncio.sleep(self.tools_update_interval)
                await self._check_and_update_tools()
                consecutive_failures = 0
                
            except asyncio.CancelledError:
                logger.info("Tools update loop cancelled")
                break
            except Exception as e:
                consecutive_failures += 1
                logger.error(f"Tools update loop error (failure {consecutive_failures}/{max_consecutive_failures}): {e}")
                
                if consecutive_failures >= max_consecutive_failures:
                    logger.critical("Too many consecutive tools update failures, stopping update loop")
                    break
                
                # 指数退避延迟
                backoff_delay = min(300 * (2 ** consecutive_failures), 1800)  # 最大30分钟
                await asyncio.sleep(backoff_delay)
    
    async def _check_and_update_tools(self):
        """检查并更新所有服务的工具列表"""
        logger.debug("Starting periodic tools update check...")
        
        # 收集所有需要检查的服务
        services_to_check = set()
        for client_id, services in self.registry.sessions.items():
            for service_name in services:
                services_to_check.add((client_id, service_name))
        
        if not services_to_check:
            logger.debug("No services to check for tools update")
            return
        
        # 并发检查服务
        update_tasks = []
        for client_id, service_name in services_to_check:
            task = asyncio.create_task(
                self._check_single_service_tools(service_name, client_id),
                name=f"tools_update_{service_name}_{client_id}"
            )
            update_tasks.append(task)
        
        # 等待所有检查完成
        results = await asyncio.gather(*update_tasks, return_exceptions=True)
        
        # 统计结果
        updated_count = 0
        error_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_count += 1
                logger.warning(f"Tools update check failed for task {update_tasks[i].get_name()}: {result}")
            elif result:
                updated_count += 1
        
        logger.info(f"Tools update check completed: {updated_count} updated, {error_count} errors, {len(services_to_check)} total")
    
    async def _check_single_service_tools(self, service_name: str, client_id: str) -> bool:
        """检查单个服务的工具列表是否需要更新"""
        try:
            service_key = f"{client_id}:{service_name}"
            current_time = time.time()
            last_update = self.last_update_times.get(service_key, 0)
            
            # 检查是否需要更新
            if current_time - last_update < self.tools_update_interval:
                logger.debug(f"Service {service_name} tools recently updated, skipping")
                return False
            
            # 检查服务是否健康
            if not await self.orchestrator.is_service_healthy(service_name, client_id):
                logger.debug(f"Service {service_name} is not healthy, skipping tools update")
                return False
            
            # 智能变化检测（如果启用）
            if self.detect_tools_changes:
                if not await self._detect_tools_changes(service_name, client_id):
                    logger.debug(f"No tools changes detected for {service_name}, skipping update")
                    self.last_update_times[service_key] = current_time
                    return False
            
            # 执行工具列表更新
            success = await self._update_service_tools(service_name, client_id)
            if success:
                self.last_update_times[service_key] = current_time
                logger.info(f"Tools updated successfully for service: {service_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error checking tools for service {service_name}: {e}")
            return False
    
    async def _detect_tools_changes(self, service_name: str, client_id: str) -> bool:
        """智能检测工具列表变化"""
        try:
            # 获取当前缓存的工具数量
            cached_tools = self.registry.get_tools(client_id)
            cached_service_tools = {name: tool for name, tool in cached_tools.items() 
                                  if self.registry.tool_to_session_map.get(client_id, {}).get(name) == service_name}
            cached_count = len(cached_service_tools)
            
            # 快速检查：创建临时连接获取当前工具数量
            service_config = self.orchestrator.mcp_config.get_service_config(service_name)
            if not service_config:
                return False
            
            from fastmcp import Client
            from mcpstore.core.config_processor import ConfigProcessor
            
            # 处理配置
            user_config = {"mcpServers": {service_name: service_config}}
            fastmcp_config = ConfigProcessor.process_user_config_for_fastmcp(user_config)
            
            if service_name not in fastmcp_config.get("mcpServers", {}):
                return False
            
            # 创建临时客户端检查工具数量
            client = Client(fastmcp_config)
            async with client:
                current_tools = await client.list_tools()
                current_count = len(current_tools)
            
            # 如果数量不同，说明有变化
            has_changes = cached_count != current_count
            if has_changes:
                logger.info(f"Tools count changed for {service_name}: {cached_count} -> {current_count}")
            
            return has_changes
            
        except Exception as e:
            logger.debug(f"Error detecting tools changes for {service_name}: {e}")
            # 检测失败时，假设有变化，触发更新
            return True
    
    async def _update_service_tools(self, service_name: str, client_id: str) -> bool:
        """更新服务的工具列表"""
        try:
            logger.info(f"Updating tools list for service: {service_name}")
            
            # 重新连接服务以获取最新工具列表
            success, message = await self.orchestrator.connect_service(service_name, agent_id=client_id)
            
            if success:
                logger.info(f"Tools list updated successfully for {service_name}")
                return True
            else:
                logger.warning(f"Failed to update tools for {service_name}: {message}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating tools for {service_name}: {e}")
            return False
    
    async def on_service_reconnected(self, service_name: str, client_id: str):
        """服务重连时的回调"""
        if not self.update_tools_on_reconnection:
            return
        
        try:
            logger.info(f"Service {service_name} reconnected, updating tools...")
            success = await self._update_service_tools(service_name, client_id)
            
            if success:
                # 更新时间戳
                service_key = f"{client_id}:{service_name}"
                self.last_update_times[service_key] = time.time()
                logger.info(f"Tools updated after reconnection for {service_name}")
            
        except Exception as e:
            logger.error(f"Error updating tools after reconnection for {service_name}: {e}")
    
    async def manual_update_service(self, service_name: str, client_id: str = None) -> bool:
        """手动更新特定服务的工具列表"""
        if client_id is None:
            client_id = self.orchestrator.client_manager.global_agent_store_id
        
        logger.info(f"Manual tools update requested for service: {service_name}")
        success = await self._update_service_tools(service_name, client_id)
        
        if success:
            service_key = f"{client_id}:{service_name}"
            self.last_update_times[service_key] = time.time()
        
        return success
    
    async def manual_update_all(self) -> Dict[str, bool]:
        """手动更新所有服务的工具列表"""
        logger.info("Manual tools update requested for all services")
        
        # 收集所有服务
        services_to_update = []
        for client_id, services in self.registry.sessions.items():
            for service_name in services:
                services_to_update.append((client_id, service_name))
        
        # 并发更新
        results = {}
        update_tasks = []
        for client_id, service_name in services_to_update:
            task = asyncio.create_task(
                self.manual_update_service(service_name, client_id),
                name=f"manual_update_{service_name}_{client_id}"
            )
            update_tasks.append((service_name, task))
        
        # 等待所有更新完成
        for service_name, task in update_tasks:
            try:
                results[service_name] = await task
            except Exception as e:
                logger.error(f"Manual update failed for {service_name}: {e}")
                results[service_name] = False
        
        success_count = sum(1 for success in results.values() if success)
        logger.info(f"Manual tools update completed: {success_count}/{len(results)} successful")
        
        return results
    
    def get_update_status(self) -> Dict[str, Any]:
        """获取更新状态"""
        return {
            "enabled": self.enable_tools_update,
            "running": self.is_running,
            "interval_seconds": self.tools_update_interval,
            "update_on_reconnection": self.update_tools_on_reconnection,
            "detect_changes": self.detect_tools_changes,
            "last_update_times": self.last_update_times.copy(),
            "tracked_services": len(self.last_update_times)
        }
