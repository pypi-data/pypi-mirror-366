"""
Service Lifecycle Manager
Implements 7-state lifecycle state machine, manages complete lifecycle from service initialization to termination
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Tuple, Set

from mcpstore.core.models.service import ServiceConnectionState, ServiceStateMetadata
from .config import ServiceLifecycleConfig
from .state_machine import ServiceStateMachine

logger = logging.getLogger(__name__)


class ServiceLifecycleManager:
    """Service lifecycle state machine manager"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.registry = orchestrator.registry
        self.config = ServiceLifecycleConfig()

        # State storage: agent_id -> service_name -> state
        self.service_states: Dict[str, Dict[str, ServiceConnectionState]] = {}
        # State metadata: agent_id -> service_name -> metadata
        self.state_metadata: Dict[str, Dict[str, ServiceStateMetadata]] = {}

        # Scheduled tasks
        self.lifecycle_task: Optional[asyncio.Task] = None
        self.is_running = False

        # Performance optimization: batch processing queue
        self.state_change_queue: Set[Tuple[str, str]] = set()  # (agent_id, service_name)

        # State machine
        self.state_machine = ServiceStateMachine(self.config)
        
        logger.info("ServiceLifecycleManager initialized")
    
    async def start(self):
        """Start lifecycle management"""
        if self.is_running:
            logger.warning("ServiceLifecycleManager is already running")
            return

        self.is_running = True
        # 确保任务在当前事件循环中创建，并添加错误处理
        try:
            loop = asyncio.get_running_loop()
            self.lifecycle_task = loop.create_task(self._lifecycle_management_loop())
            # 添加任务完成回调，用于错误处理
            self.lifecycle_task.add_done_callback(self._task_done_callback)
            logger.info("ServiceLifecycleManager started")
        except Exception as e:
            self.is_running = False
            logger.error(f"Failed to start ServiceLifecycleManager: {e}")
            raise
    
    async def stop(self):
        """停止生命周期管理"""
        self.is_running = False
        
        if self.lifecycle_task and not self.lifecycle_task.done():
            logger.debug("Cancelling lifecycle management task...")
            self.lifecycle_task.cancel()
            try:
                await self.lifecycle_task
            except asyncio.CancelledError:
                logger.debug("Lifecycle management task was cancelled")
            except Exception as e:
                logger.error(f"Error during lifecycle task cancellation: {e}")
        
        # 清理状态
        self.state_change_queue.clear()
        logger.info("ServiceLifecycleManager stopped")
    
    def _task_done_callback(self, task):
        """生命周期任务完成回调"""
        if task.cancelled():
            logger.info("Lifecycle management task was cancelled")
        elif task.exception():
            logger.error(f"Lifecycle management task failed: {task.exception()}")
            # 可以在这里添加重启逻辑
        else:
            logger.info("Lifecycle management task completed normally")
        
        # 标记为未运行
        self.is_running = False
    
    def initialize_service(self, agent_id: str, service_name: str, config: Dict[str, Any]) -> bool:
        """
        服务初始化入口，设置状态为INITIALIZING
        
        Args:
            agent_id: Agent ID
            service_name: 服务名称
            config: 服务配置
            
        Returns:
            bool: 是否成功初始化
        """
        try:
            logger.debug(f"🔧 [INITIALIZE_SERVICE] Starting initialization for {service_name} in agent {agent_id}")
            
            # 确保agent存在
            if agent_id not in self.service_states:
                self.service_states[agent_id] = {}
                logger.debug(f"🔧 [INITIALIZE_SERVICE] Created agent_id {agent_id} in service_states")
            
            if agent_id not in self.state_metadata:
                self.state_metadata[agent_id] = {}
                logger.debug(f"🔧 [INITIALIZE_SERVICE] Created agent_id {agent_id} in state_metadata")
            
            # 设置初始状态
            self.service_states[agent_id][service_name] = ServiceConnectionState.INITIALIZING
            
            # 创建状态元数据
            self.state_metadata[agent_id][service_name] = ServiceStateMetadata(
                service_name=service_name,
                agent_id=agent_id,
                state_entered_time=datetime.now(),
                consecutive_failures=0,
                reconnect_attempts=0,
                next_retry_time=None,
                error_message=None,
                service_config=config
            )
            
            # 添加到处理队列
            self.state_change_queue.add((agent_id, service_name))
            
            logger.info(f"✅ [INITIALIZE_SERVICE] Service {service_name} (agent {agent_id}) initialized in INITIALIZING state")
            return True
            
        except Exception as e:
            logger.error(f"❌ [INITIALIZE_SERVICE] Failed to initialize service {service_name}: {e}")
            return False
    
    def get_service_state(self, agent_id: str, service_name: str) -> Optional[ServiceConnectionState]:
        """获取服务状态，如果服务不存在则返回None"""
        state = self.service_states.get(agent_id, {}).get(service_name, None)
        if state is None:
            logger.debug(f"🔍 [GET_SERVICE_STATE] No state found for {service_name} in agent {agent_id}")
        else:
            logger.debug(f"🔍 [GET_SERVICE_STATE] Service {service_name} (agent {agent_id}) state: {state}")
        return state
    
    def get_service_metadata(self, agent_id: str, service_name: str) -> Optional[ServiceStateMetadata]:
        """获取服务状态元数据"""
        return self.state_metadata.get(agent_id, {}).get(service_name)
    
    async def handle_health_check_result(self, agent_id: str, service_name: str,
                                       success: bool, response_time: float = 0.0,
                                       error_message: Optional[str] = None):
        """
        处理健康检查结果，触发状态转换
        
        Args:
            agent_id: Agent ID
            service_name: 服务名称
            success: 健康检查是否成功
            response_time: 响应时间
            error_message: 错误信息（如果失败）
        """
        logger.debug(f"🔍 [HEALTH_CHECK_RESULT] Processing for {service_name} (agent {agent_id}): success={success}, response_time={response_time}")
        
        # 获取当前状态
        current_state = self.get_service_state(agent_id, service_name)
        if current_state is None:
            logger.warning(f"⚠️ [HEALTH_CHECK_RESULT] No state found for {service_name} (agent {agent_id}), skipping")
            return
        
        # 获取元数据
        metadata = self.get_service_metadata(agent_id, service_name)
        if not metadata:
            logger.error(f"❌ [HEALTH_CHECK_RESULT] No metadata found for {service_name} (agent {agent_id})")
            return
        
        # 更新元数据
        metadata.last_health_check = datetime.now()
        metadata.last_response_time = response_time
        
        if success:
            logger.debug(f"✅ [HEALTH_CHECK_RESULT] Success for {service_name}")
            metadata.consecutive_failures = 0
            metadata.error_message = None
            await self.state_machine.handle_success_transition(
                agent_id, service_name, current_state,
                self.get_service_metadata, self._transition_to_state
            )
        else:
            logger.debug(f"❌ [HEALTH_CHECK_RESULT] Failure for {service_name}: {error_message}")
            metadata.consecutive_failures += 1
            metadata.error_message = error_message
            await self.state_machine.handle_failure_transition(
                agent_id, service_name, current_state,
                self.get_service_metadata, self._transition_to_state
            )
        
        # 添加到处理队列
        self.state_change_queue.add((agent_id, service_name))
        
        logger.debug(f"🔍 [HEALTH_CHECK_RESULT] Completed for {service_name}")
    
    async def _transition_to_state(self, agent_id: str, service_name: str,
                                 new_state: ServiceConnectionState):
        """执行状态转换"""
        await self.state_machine.transition_to_state(
            agent_id, service_name, new_state,
            self.get_service_state, self.get_service_metadata,
            self._set_service_state, self._on_state_entered
        )
    
    def _set_service_state(self, agent_id: str, service_name: str, state: ServiceConnectionState):
        """设置服务状态"""
        # 确保agent存在
        if agent_id not in self.service_states:
            self.service_states[agent_id] = {}
        self.service_states[agent_id][service_name] = state
    
    async def _on_state_entered(self, agent_id: str, service_name: str,
                              new_state: ServiceConnectionState, old_state: ServiceConnectionState):
        """状态进入时的处理逻辑"""
        await self.state_machine.on_state_entered(
            agent_id, service_name, new_state, old_state,
            self._enter_reconnecting_state, self._enter_unreachable_state,
            self._enter_disconnecting_state, self._enter_healthy_state
        )

    async def _enter_reconnecting_state(self, agent_id: str, service_name: str):
        """进入重连状态的处理"""
        metadata = self.get_service_metadata(agent_id, service_name)
        if metadata:
            metadata.reconnect_attempts = 0
            # 计算下次重连时间（指数退避）
            delay = self.state_machine.calculate_reconnect_delay(metadata.reconnect_attempts)
            metadata.next_retry_time = datetime.now() + timedelta(seconds=delay)

        # 暂停服务操作（在工具调用时检查状态）
        logger.info(f"Service {service_name} (agent {agent_id}) entered RECONNECTING state")

    async def _enter_unreachable_state(self, agent_id: str, service_name: str):
        """进入无法访问状态的处理"""
        metadata = self.get_service_metadata(agent_id, service_name)
        if metadata:
            # 设置长周期重试
            metadata.next_retry_time = datetime.now() + timedelta(seconds=self.config.long_retry_interval)

        # TODO: 触发告警通知（后期完善）
        await self._trigger_alert_notification(agent_id, service_name, "Service unreachable")

        logger.warning(f"Service {service_name} (agent {agent_id}) entered UNREACHABLE state")

    async def _enter_disconnecting_state(self, agent_id: str, service_name: str):
        """进入断连状态的处理"""
        # TODO: 发送注销请求（如果服务支持）
        await self._send_deregistration_request(agent_id, service_name)

        # 设置断连超时
        metadata = self.get_service_metadata(agent_id, service_name)
        if metadata:
            metadata.next_retry_time = datetime.now() + timedelta(seconds=self.config.disconnection_timeout)

        logger.info(f"Service {service_name} (agent {agent_id}) entered DISCONNECTING state")

    async def _enter_healthy_state(self, agent_id: str, service_name: str):
        """进入健康状态的处理"""
        metadata = self.get_service_metadata(agent_id, service_name)
        if metadata:
            # 重置计数器
            metadata.consecutive_failures = 0
            metadata.reconnect_attempts = 0
            metadata.error_message = None

        logger.info(f"Service {service_name} (agent {agent_id}) entered HEALTHY state")

    async def _trigger_alert_notification(self, agent_id: str, service_name: str, message: str):
        """触发告警通知（占位符实现）"""
        # TODO: 实现告警通知逻辑
        logger.warning(f"ALERT: {message} for service {service_name} (agent {agent_id})")

    async def _send_deregistration_request(self, agent_id: str, service_name: str):
        """发送注销请求（占位符实现）"""
        # TODO: 实现注销请求逻辑
        logger.debug(f"Sending deregistration request for service {service_name} (agent {agent_id})")

    async def request_reconnection(self, agent_id: str, service_name: str):
        """
        请求重连服务

        Args:
            agent_id: Agent ID
            service_name: 服务名称
        """
        logger.debug(f"🔄 [REQUEST_RECONNECTION] Starting for {service_name} (agent {agent_id})")

        current_state = self.get_service_state(agent_id, service_name)
        if current_state is None:
            logger.warning(f"⚠️ [REQUEST_RECONNECTION] No state found for {service_name} (agent {agent_id})")
            return

        metadata = self.get_service_metadata(agent_id, service_name)
        if not metadata:
            logger.error(f"❌ [REQUEST_RECONNECTION] No metadata found for {service_name} (agent {agent_id})")
            return

        # 检查是否可以重连
        if current_state in [ServiceConnectionState.RECONNECTING, ServiceConnectionState.UNREACHABLE]:
            if not self.state_machine.should_retry_now(metadata):
                logger.debug(f"⏸️ [REQUEST_RECONNECTION] Not time to retry yet for {service_name}")
                return

            # 增加重连尝试次数
            metadata.reconnect_attempts += 1
            logger.debug(f"🔄 [REQUEST_RECONNECTION] Attempt #{metadata.reconnect_attempts} for {service_name}")

            # 尝试重连
            try:
                # 调用orchestrator的重连逻辑
                success = await self.orchestrator.connect_service(service_name, metadata.service_config, agent_id)

                if success:
                    logger.info(f"✅ [REQUEST_RECONNECTION] Reconnection successful for {service_name}")
                    await self._transition_to_state(agent_id, service_name, ServiceConnectionState.HEALTHY)
                else:
                    logger.warning(f"❌ [REQUEST_RECONNECTION] Reconnection failed for {service_name}")
                    # 状态转换将由健康检查结果处理

            except Exception as e:
                logger.error(f"❌ [REQUEST_RECONNECTION] Reconnection error for {service_name}: {e}")
                metadata.error_message = str(e)
        else:
            logger.debug(f"⏸️ [REQUEST_RECONNECTION] Service {service_name} is not in a reconnectable state: {current_state}")

    async def request_disconnection(self, agent_id: str, service_name: str):
        """
        请求断开服务连接

        Args:
            agent_id: Agent ID
            service_name: 服务名称
        """
        logger.debug(f"🔌 [REQUEST_DISCONNECTION] Starting for {service_name} (agent {agent_id})")

        current_state = self.get_service_state(agent_id, service_name)
        if current_state is None:
            logger.warning(f"⚠️ [REQUEST_DISCONNECTION] No state found for {service_name} (agent {agent_id})")
            return

        # 只有在非断开状态下才能请求断开
        if current_state not in [ServiceConnectionState.DISCONNECTING, ServiceConnectionState.DISCONNECTED]:
            await self._transition_to_state(agent_id, service_name, ServiceConnectionState.DISCONNECTING)

            # 执行实际的断开操作
            try:
                await self.orchestrator.disconnect_service(service_name, agent_id)
                await self._transition_to_state(agent_id, service_name, ServiceConnectionState.DISCONNECTED)
                logger.info(f"✅ [REQUEST_DISCONNECTION] Service {service_name} (agent {agent_id}) disconnected")
            except Exception as e:
                logger.error(f"❌ [REQUEST_DISCONNECTION] Failed to disconnect {service_name}: {e}")
        else:
            logger.debug(f"⏸️ [REQUEST_DISCONNECTION] Service {service_name} is already disconnecting/disconnected")

    def remove_service(self, agent_id: str, service_name: str):
        """
        移除服务的生命周期管理

        Args:
            agent_id: Agent ID
            service_name: 服务名称
        """
        logger.debug(f"🗑️ [REMOVE_SERVICE] Removing {service_name} (agent {agent_id})")

        # 从状态存储中移除
        if agent_id in self.service_states and service_name in self.service_states[agent_id]:
            del self.service_states[agent_id][service_name]
            logger.debug(f"🗑️ [REMOVE_SERVICE] Removed state for {service_name}")

        # 从元数据存储中移除
        if agent_id in self.state_metadata and service_name in self.state_metadata[agent_id]:
            del self.state_metadata[agent_id][service_name]
            logger.debug(f"🗑️ [REMOVE_SERVICE] Removed metadata for {service_name}")

        # 从处理队列中移除
        self.state_change_queue.discard((agent_id, service_name))

        logger.info(f"✅ [REMOVE_SERVICE] Service {service_name} (agent {agent_id}) removed from lifecycle management")

    async def _lifecycle_management_loop(self):
        """生命周期管理主循环"""
        logger.info("Starting lifecycle management loop")

        while self.is_running:
            try:
                # 批量处理状态变更队列
                if self.state_change_queue:
                    # 复制队列并清空，避免在处理过程中被修改
                    services_to_process = list(self.state_change_queue)
                    self.state_change_queue.clear()

                    logger.debug(f"🔄 [LIFECYCLE_LOOP] Processing {len(services_to_process)} services")

                    # 并发处理多个服务
                    tasks = []
                    for agent_id, service_name in services_to_process:
                        task = asyncio.create_task(self._process_service(agent_id, service_name))
                        tasks.append(task)

                    if tasks:
                        # 等待所有任务完成，但不抛出异常
                        results = await asyncio.gather(*tasks, return_exceptions=True)

                        # 记录异常
                        for i, result in enumerate(results):
                            if isinstance(result, Exception):
                                agent_id, service_name = services_to_process[i]
                                logger.error(f"❌ [LIFECYCLE_LOOP] Error processing {service_name} (agent {agent_id}): {result}")

                # 等待下一次循环
                await asyncio.sleep(5.0)  # 5秒检查一次

            except asyncio.CancelledError:
                logger.info("Lifecycle management loop was cancelled")
                break
            except Exception as e:
                logger.error(f"❌ [LIFECYCLE_LOOP] Unexpected error in lifecycle management loop: {e}")
                # 继续运行，不要因为单次错误而停止整个循环
                await asyncio.sleep(1.0)

        logger.info("Lifecycle management loop ended")

    async def _process_service(self, agent_id: str, service_name: str):
        """处理单个服务的生命周期"""
        logger.debug(f"🔍 [PROCESS_SERVICE] Processing {service_name} (agent {agent_id})")

        current_state = self.get_service_state(agent_id, service_name)
        metadata = self.get_service_metadata(agent_id, service_name)

        logger.debug(f"🔍 [PROCESS_SERVICE] Current state: {current_state}, metadata exists: {metadata is not None}")

        if not metadata:
            logger.warning(f"⚠️ [PROCESS_SERVICE] No metadata found for {service_name}, removing from queue")
            # 从队列中移除，避免重复处理
            self.state_change_queue.discard((agent_id, service_name))
            return

        now = datetime.now()
        logger.debug(f"🔍 [PROCESS_SERVICE] Current time: {now}")

        # 处理需要连接/重试的状态
        if current_state == ServiceConnectionState.INITIALIZING:
            logger.debug(f"🔧 [PROCESS_SERVICE] INITIALIZING state - attempting initial connection for {service_name}")
            # 新服务初始化，尝试首次连接
            await self._attempt_initial_connection(agent_id, service_name)

        elif current_state == ServiceConnectionState.RECONNECTING:
            logger.debug(f"🔧 [PROCESS_SERVICE] RECONNECTING state - checking retry time for {service_name}")
            logger.debug(f"🔧 [PROCESS_SERVICE] Next retry time: {metadata.next_retry_time}, current time: {now}")
            if metadata.next_retry_time and now >= metadata.next_retry_time:
                logger.debug(f"🔧 [PROCESS_SERVICE] Time to retry reconnection for {service_name}")
                await self._attempt_reconnection(agent_id, service_name)
            else:
                logger.debug(f"⏸️ [PROCESS_SERVICE] Not time to retry yet for {service_name}")

        elif current_state == ServiceConnectionState.UNREACHABLE:
            logger.debug(f"🔧 [PROCESS_SERVICE] UNREACHABLE state - checking long period retry for {service_name}")
            if metadata.next_retry_time and now >= metadata.next_retry_time:
                logger.debug(f"🔧 [PROCESS_SERVICE] Time for long period retry for {service_name}")
                await self._attempt_long_period_retry(agent_id, service_name)
            else:
                logger.debug(f"⏸️ [PROCESS_SERVICE] Not time for long period retry yet for {service_name}")

        elif current_state == ServiceConnectionState.DISCONNECTING:
            logger.debug(f"🔧 [PROCESS_SERVICE] DISCONNECTING state - checking timeout for {service_name}")
            if metadata.next_retry_time and now >= metadata.next_retry_time:
                logger.debug(f"🔧 [PROCESS_SERVICE] Disconnect timeout reached for {service_name}, forcing DISCONNECTED")
                # 断连超时，强制转换为DISCONNECTED
                await self._transition_to_state(agent_id, service_name, ServiceConnectionState.DISCONNECTED)
            else:
                logger.debug(f"⏸️ [PROCESS_SERVICE] Disconnect timeout not reached yet for {service_name}")

        else:
            logger.debug(f"⏸️ [PROCESS_SERVICE] No processing needed for {service_name} in state {current_state}")

        logger.debug(f"🔍 [PROCESS_SERVICE] Completed processing {service_name}")

    async def _attempt_initial_connection(self, agent_id: str, service_name: str):
        """尝试初始连接"""
        metadata = self.get_service_metadata(agent_id, service_name)
        if not metadata:
            return

        try:
            # 检查服务是否已经连接成功（通过检查工具数量）
            session = self.registry.sessions.get(agent_id, {}).get(service_name)
            if session:
                # 检查是否有工具
                service_tools = [name for name, sess in self.registry.tool_to_session_map.get(agent_id, {}).items()
                               if sess == session]

                if service_tools:
                    # 有工具，说明连接成功
                    await self.handle_health_check_result(
                        agent_id=agent_id,
                        service_name=service_name,
                        success=True,
                        response_time=0.0
                    )
                    logger.info(f"Service {service_name} initial connection successful with {len(service_tools)} tools")
                    return
                else:
                    # 有会话但没有工具，可能是连接失败了
                    # 等待一段时间后再检查，给连接过程一些时间
                    await asyncio.sleep(3)

                    # 再次检查工具
                    service_tools = [name for name, sess in self.registry.tool_to_session_map.get(agent_id, {}).items()
                                   if sess == session]

                    if service_tools:
                        # 现在有工具了，连接成功
                        await self.handle_health_check_result(
                            agent_id=agent_id,
                            service_name=service_name,
                            success=True,
                            response_time=0.0
                        )
                        logger.info(f"Service {service_name} initial connection successful with {len(service_tools)} tools")
                        return
                    else:
                        # 仍然没有工具，认为连接失败
                        await self.handle_health_check_result(
                            agent_id=agent_id,
                            service_name=service_name,
                            success=False,
                            response_time=0.0,
                            error_message="No tools available after connection attempt"
                        )
                        logger.warning(f"Service {service_name} initial connection failed: no tools available after connection attempt")
                        return

            # 如果没有会话，尝试重新连接
            success = await self.orchestrator.connect_service(service_name, metadata.service_config, agent_id)

            if success:
                # 连接成功，处理成功转换
                await self.handle_health_check_result(
                    agent_id=agent_id,
                    service_name=service_name,
                    success=True,
                    response_time=0.0
                )
                logger.info(f"Service {service_name} initial connection successful")
            else:
                # 连接失败，处理失败转换
                await self.handle_health_check_result(
                    agent_id=agent_id,
                    service_name=service_name,
                    success=False,
                    response_time=0.0,
                    error_message="Initial connection failed"
                )
                logger.warning(f"Service {service_name} initial connection failed")

        except Exception as e:
            logger.error(f"❌ [ATTEMPT_INITIAL_CONNECTION] Error during initial connection for {service_name}: {e}")
            await self.handle_health_check_result(
                agent_id=agent_id,
                service_name=service_name,
                success=False,
                response_time=0.0,
                error_message=str(e)
            )

    async def _attempt_reconnection(self, agent_id: str, service_name: str):
        """尝试重连"""
        metadata = self.get_service_metadata(agent_id, service_name)
        if not metadata:
            return

        try:
            logger.debug(f"🔄 [ATTEMPT_RECONNECTION] Starting reconnection attempt #{metadata.reconnect_attempts + 1} for {service_name}")

            # 增加重连尝试次数
            metadata.reconnect_attempts += 1

            # 尝试重连
            success = await self.orchestrator.connect_service(service_name, metadata.service_config, agent_id)

            if success:
                # 重连成功
                await self.handle_health_check_result(
                    agent_id=agent_id,
                    service_name=service_name,
                    success=True,
                    response_time=0.0
                )
                logger.info(f"✅ [ATTEMPT_RECONNECTION] Reconnection successful for {service_name} after {metadata.reconnect_attempts} attempts")
            else:
                # 重连失败，计算下次重试时间
                delay = self.state_machine.calculate_reconnect_delay(metadata.reconnect_attempts)
                metadata.next_retry_time = datetime.now() + timedelta(seconds=delay)

                await self.handle_health_check_result(
                    agent_id=agent_id,
                    service_name=service_name,
                    success=False,
                    response_time=0.0,
                    error_message=f"Reconnection attempt #{metadata.reconnect_attempts} failed"
                )
                logger.warning(f"❌ [ATTEMPT_RECONNECTION] Reconnection attempt #{metadata.reconnect_attempts} failed for {service_name}, next retry in {delay}s")

        except Exception as e:
            logger.error(f"❌ [ATTEMPT_RECONNECTION] Error during reconnection for {service_name}: {e}")

            # 计算下次重试时间
            delay = self.state_machine.calculate_reconnect_delay(metadata.reconnect_attempts)
            metadata.next_retry_time = datetime.now() + timedelta(seconds=delay)

            await self.handle_health_check_result(
                agent_id=agent_id,
                service_name=service_name,
                success=False,
                response_time=0.0,
                error_message=str(e)
            )

    async def _attempt_long_period_retry(self, agent_id: str, service_name: str):
        """尝试长周期重试"""
        metadata = self.get_service_metadata(agent_id, service_name)
        if not metadata:
            return

        try:
            logger.debug(f"🔄 [ATTEMPT_LONG_PERIOD_RETRY] Starting long period retry for {service_name}")

            # 重置重连尝试次数，开始新一轮重连
            metadata.reconnect_attempts = 0

            # 尝试连接
            success = await self.orchestrator.connect_service(service_name, metadata.service_config, agent_id)

            if success:
                # 连接成功，转换到HEALTHY状态
                await self.handle_health_check_result(
                    agent_id=agent_id,
                    service_name=service_name,
                    success=True,
                    response_time=0.0
                )
                logger.info(f"✅ [ATTEMPT_LONG_PERIOD_RETRY] Long period retry successful for {service_name}")
            else:
                # 连接失败，转换到RECONNECTING状态开始新一轮重连
                await self._transition_to_state(agent_id, service_name, ServiceConnectionState.RECONNECTING)
                logger.warning(f"❌ [ATTEMPT_LONG_PERIOD_RETRY] Long period retry failed for {service_name}, starting new reconnection cycle")

        except Exception as e:
            logger.error(f"❌ [ATTEMPT_LONG_PERIOD_RETRY] Error during long period retry for {service_name}: {e}")

            # 连接失败，转换到RECONNECTING状态
            await self._transition_to_state(agent_id, service_name, ServiceConnectionState.RECONNECTING)

    def get_service_status_summary(self, agent_id: str = None) -> Dict[str, Any]:
        """
        获取服务状态摘要

        Args:
            agent_id: Agent ID，如果为None则返回所有agent的状态

        Returns:
            Dict: 状态摘要
        """
        summary = {
            "timestamp": datetime.now().isoformat(),
            "agents": {}
        }

        if agent_id:
            # 返回特定agent的状态
            if agent_id in self.service_states:
                summary["agents"][agent_id] = self._get_agent_status_summary(agent_id)
        else:
            # 返回所有agent的状态
            for aid in self.service_states:
                summary["agents"][aid] = self._get_agent_status_summary(aid)

        return summary

    def _get_agent_status_summary(self, agent_id: str) -> Dict[str, Any]:
        """获取单个agent的状态摘要"""
        agent_summary = {
            "services": {},
            "total_services": 0,
            "healthy_services": 0,
            "warning_services": 0,
            "reconnecting_services": 0,
            "unreachable_services": 0,
            "disconnected_services": 0
        }

        if agent_id not in self.service_states:
            return agent_summary

        for service_name, state in self.service_states[agent_id].items():
            metadata = self.get_service_metadata(agent_id, service_name)

            service_info = {
                "state": state.value,
                "state_entered_time": metadata.state_entered_time.isoformat() if metadata and metadata.state_entered_time else None,
                "consecutive_failures": metadata.consecutive_failures if metadata else 0,
                "reconnect_attempts": metadata.reconnect_attempts if metadata else 0,
                "error_message": metadata.error_message if metadata else None,
                "next_retry_time": metadata.next_retry_time.isoformat() if metadata and metadata.next_retry_time else None
            }

            agent_summary["services"][service_name] = service_info
            agent_summary["total_services"] += 1

            # 统计各状态数量
            if state == ServiceConnectionState.HEALTHY:
                agent_summary["healthy_services"] += 1
            elif state == ServiceConnectionState.WARNING:
                agent_summary["warning_services"] += 1
            elif state == ServiceConnectionState.RECONNECTING:
                agent_summary["reconnecting_services"] += 1
            elif state == ServiceConnectionState.UNREACHABLE:
                agent_summary["unreachable_services"] += 1
            elif state in [ServiceConnectionState.DISCONNECTING, ServiceConnectionState.DISCONNECTED]:
                agent_summary["disconnected_services"] += 1

        return agent_summary

    def update_config(self, new_config: Dict[str, Any]):
        """更新生命周期配置"""
        for key, value in new_config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.debug(f"Updated lifecycle config: {key} = {value}")

        # 更新状态机配置
        self.state_machine.config = self.config
        logger.info(f"Lifecycle configuration updated: {self.config}")

    def cleanup(self):
        """清理资源"""
        logger.debug("Cleaning up ServiceLifecycleManager")

        # 清理状态数据
        self.service_states.clear()
        self.state_metadata.clear()
        self.state_change_queue.clear()

        logger.info("ServiceLifecycleManager cleanup completed")
