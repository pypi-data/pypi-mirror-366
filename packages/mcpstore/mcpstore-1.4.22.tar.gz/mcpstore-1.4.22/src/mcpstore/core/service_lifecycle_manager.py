"""
服务生命周期管理器
实现7状态生命周期状态机，管理服务从初始化到终止的完整生命周期
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Tuple, Set
from dataclasses import dataclass, field

from .models.service import ServiceConnectionState, ServiceStateMetadata

logger = logging.getLogger(__name__)


@dataclass
class ServiceLifecycleConfig:
    """服务生命周期配置"""
    # 状态转换阈值
    warning_failure_threshold: int = 2          # 进入WARNING状态的失败次数阈值
    reconnecting_failure_threshold: int = 1     # 🔧 修复：降低阈值，首次失败即转到RECONNECTING
    max_reconnect_attempts: int = 10            # 最大重连尝试次数
    
    # 重试间隔配置
    base_reconnect_delay: float = 1.0           # 基础重连延迟（秒）
    max_reconnect_delay: float = 60.0           # 最大重连延迟（秒）
    long_retry_interval: float = 300.0          # 长周期重试间隔（5分钟）
    
    # 心跳配置
    normal_heartbeat_interval: float = 30.0     # 正常心跳间隔（秒）
    warning_heartbeat_interval: float = 10.0    # 警告状态心跳间隔（秒）
    
    # 超时配置
    initialization_timeout: float = 30.0        # 初始化超时（秒）
    disconnection_timeout: float = 10.0         # 断连超时（秒）


class ServiceLifecycleManager:
    """服务生命周期状态机管理器"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.registry = orchestrator.registry
        self.config = ServiceLifecycleConfig()
        
        # 状态存储：agent_id -> service_name -> state
        self.service_states: Dict[str, Dict[str, ServiceConnectionState]] = {}
        # 状态元数据：agent_id -> service_name -> metadata
        self.state_metadata: Dict[str, Dict[str, ServiceStateMetadata]] = {}
        
        # 定时任务
        self.lifecycle_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # 性能优化：批量处理队列
        self.state_change_queue: Set[Tuple[str, str]] = set()  # (agent_id, service_name)
        
        logger.info("ServiceLifecycleManager initialized")
    
    async def start(self):
        """启动生命周期管理"""
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
            self.lifecycle_task.cancel()
            try:
                # 🔧 修复：增加超时时间，给任务更多时间来正常取消
                await asyncio.wait_for(self.lifecycle_task, timeout=5.0)
            except asyncio.CancelledError:
                logger.debug("Lifecycle task cancelled successfully")
            except asyncio.TimeoutError:
                logger.warning("Lifecycle task cancellation timed out")
            except Exception as e:
                logger.warning(f"Unexpected error during lifecycle task cancellation: {e}")

        # 🔧 修复：清理任务引用和队列
        self.lifecycle_task = None
        self.state_change_queue.clear()
        logger.info("ServiceLifecycleManager stopped")

    def _task_done_callback(self, task):
        """生命周期任务完成回调"""
        if task.cancelled():
            logger.info("Lifecycle management task was cancelled")
        elif task.exception():
            logger.error(f"Lifecycle management task failed with exception: {task.exception()}")
            import traceback
            logger.error(f"Traceback: {''.join(traceback.format_exception(type(task.exception()), task.exception(), task.exception().__traceback__))}")
            # 如果任务异常结束，标记为不再运行
            self.is_running = False
        else:
            logger.info("Lifecycle management task completed normally")
            self.is_running = False

    def initialize_service(self, agent_id: str, service_name: str, config: Dict[str, Any]) -> bool:
        """
        服务初始化入口，设置状态为INITIALIZING
        只要配置语法正确，就算添加成功
        """
        logger.debug(f"🔧 [INITIALIZE] Starting initialization for {service_name} in agent {agent_id}")
        logger.debug(f"🔧 [INITIALIZE] Service config: {config}")

        # 添加当前状态快照
        logger.info(f"🔧 [INITIALIZE] Current service_states keys: {list(self.service_states.keys())}")
        for aid, services in self.service_states.items():
            logger.info(f"🔧 [INITIALIZE]   Agent {aid}: {list(services.keys())}")

        try:
            # 确保agent存在
            if agent_id not in self.service_states:
                logger.debug(f"🔧 [INITIALIZE] Creating service_states for agent {agent_id}")
                self.service_states[agent_id] = {}
                self.state_metadata[agent_id] = {}

            # 设置初始状态
            logger.debug(f"🔧 [INITIALIZE] Setting initial state INITIALIZING for {service_name}")
            self.service_states[agent_id][service_name] = ServiceConnectionState.INITIALIZING
            self.state_metadata[agent_id][service_name] = ServiceStateMetadata(
                state_entered_time=datetime.now()
            )

            # 添加到处理队列
            logger.debug(f"🔧 [INITIALIZE] Adding {service_name} to processing queue")
            self.state_change_queue.add((agent_id, service_name))
            logger.debug(f"🔧 [INITIALIZE] Queue size after adding: {len(self.state_change_queue)}")

            logger.info(f"✅ [INITIALIZE] Service {service_name} initialized for agent {agent_id}")
            return True

        except Exception as e:
            logger.error(f"❌ [INITIALIZE] Failed to initialize service {service_name} for agent {agent_id}: {e}")
            return False
    
    def get_service_state(self, agent_id: str, service_name: str) -> Optional[ServiceConnectionState]:
        """获取服务状态，如果服务不存在则返回None"""
        state = self.service_states.get(agent_id, {}).get(service_name, None)
        logger.debug(f"🔍 [GET_STATE] agent_id={agent_id}, service_name={service_name}, state={state.value if state else 'None'}")

        # 如果没找到，打印当前所有状态用于调试
        if agent_id not in self.service_states or service_name not in self.service_states.get(agent_id, {}):
            logger.debug(f"🔍 [GET_STATE] Service not found. Current states:")
            for aid, services in self.service_states.items():
                logger.debug(f"🔍 [GET_STATE]   Agent {aid}: {list(services.keys())}")

        return state
    
    def get_service_metadata(self, agent_id: str, service_name: str) -> Optional[ServiceStateMetadata]:
        """获取服务状态元数据"""
        return self.state_metadata.get(agent_id, {}).get(service_name)
    
    async def handle_health_check_result(self, agent_id: str, service_name: str,
                                       success: bool, response_time: float = 0.0,
                                       error_message: Optional[str] = None):
        """处理健康检查结果，触发状态转换"""
        logger.debug(f"🔍 [LIFECYCLE] handle_health_check_result called: agent_id={agent_id}, service_name={service_name}, success={success}, error_message={error_message}")

        current_state = self.get_service_state(agent_id, service_name)
        metadata = self.get_service_metadata(agent_id, service_name)

        logger.debug(f"🔍 [LIFECYCLE] Current state: {current_state}, metadata exists: {metadata is not None}")

        # 🔧 修复：如果没有元数据，先初始化服务
        if not metadata:
            logger.warning(f"🔧 [LIFECYCLE] No metadata found for service {service_name} in agent {agent_id}, initializing...")
            # 使用空配置初始化服务
            self.initialize_service(agent_id, service_name, {})
            metadata = self.get_service_metadata(agent_id, service_name)
            current_state = self.get_service_state(agent_id, service_name)
            logger.debug(f"🔧 [LIFECYCLE] After initialization: state={current_state}, metadata exists={metadata is not None}")

            if not metadata:
                logger.error(f"❌ [LIFECYCLE] Failed to initialize metadata for service {service_name} in agent {agent_id}")
                return
        
        # 更新元数据
        logger.debug(f"🔍 [LIFECYCLE] Updating metadata for {service_name}")
        metadata.last_ping_time = datetime.now()
        metadata.response_time = response_time

        if success:
            logger.debug(f"✅ [LIFECYCLE] Success case for {service_name}")
            metadata.consecutive_failures = 0
            metadata.consecutive_successes += 1
            metadata.last_success_time = datetime.now()
            metadata.error_message = None

            logger.debug(f"✅ [LIFECYCLE] Calling _handle_success_transition for {service_name}, current_state={current_state}")
            # 成功时的状态转换
            await self._handle_success_transition(agent_id, service_name, current_state)
        else:
            logger.debug(f"❌ [LIFECYCLE] Failure case for {service_name}")
            metadata.consecutive_successes = 0
            metadata.consecutive_failures += 1
            metadata.last_failure_time = datetime.now()
            metadata.error_message = error_message

            logger.debug(f"❌ [LIFECYCLE] Updated metadata: consecutive_failures={metadata.consecutive_failures}, error_message={error_message}")
            logger.debug(f"❌ [LIFECYCLE] Calling _handle_failure_transition for {service_name}, current_state={current_state}")
            # 失败时的状态转换
            await self._handle_failure_transition(agent_id, service_name, current_state)

        logger.debug(f"🔍 [LIFECYCLE] handle_health_check_result completed for {service_name}")
    
    async def _handle_success_transition(self, agent_id: str, service_name: str,
                                       current_state: ServiceConnectionState):
        """处理成功时的状态转换"""
        logger.debug(f"✅ [SUCCESS_TRANSITION] Processing for {service_name}, current_state={current_state}")

        if current_state in [ServiceConnectionState.INITIALIZING,
                           ServiceConnectionState.WARNING,
                           ServiceConnectionState.RECONNECTING,
                           ServiceConnectionState.UNREACHABLE]:  # 🔧 添加：UNREACHABLE也可以恢复到HEALTHY
            # 🔧 修复：成功转换时重置所有失败相关的计数器
            metadata = self.get_service_metadata(agent_id, service_name)
            if metadata:
                metadata.consecutive_failures = 0
                metadata.reconnect_attempts = 0
                metadata.next_retry_time = None
                metadata.error_message = None
                logger.debug(f"✅ [SUCCESS_TRANSITION] Reset failure counters for {service_name}")
            await self._transition_to_state(agent_id, service_name, ServiceConnectionState.HEALTHY)
        elif current_state == ServiceConnectionState.HEALTHY:
            logger.debug(f"✅ [SUCCESS_TRANSITION] {service_name} already HEALTHY")
        elif current_state in [ServiceConnectionState.DISCONNECTING, ServiceConnectionState.DISCONNECTED]:
            logger.debug(f"⏸️ [SUCCESS_TRANSITION] {service_name} is disconnecting/disconnected, no transition")
        else:
            logger.debug(f"⏸️ [SUCCESS_TRANSITION] No transition rules for state {current_state}")

        logger.debug(f"✅ [SUCCESS_TRANSITION] Completed for {service_name}")
    
    async def _handle_failure_transition(self, agent_id: str, service_name: str,
                                       current_state: ServiceConnectionState):
        """处理失败时的状态转换"""
        logger.debug(f"🔍 [FAILURE_TRANSITION] Starting for {service_name}, current_state={current_state}")

        metadata = self.get_service_metadata(agent_id, service_name)
        if not metadata:
            logger.error(f"❌ [FAILURE_TRANSITION] No metadata found for {service_name}")
            return

        logger.debug(f"🔍 [FAILURE_TRANSITION] Metadata: consecutive_failures={metadata.consecutive_failures}, reconnect_attempts={metadata.reconnect_attempts}")
        logger.debug(f"🔍 [FAILURE_TRANSITION] Config thresholds: warning={self.config.warning_failure_threshold}, reconnecting={self.config.reconnecting_failure_threshold}, max_reconnect={self.config.max_reconnect_attempts}")

        if current_state == ServiceConnectionState.HEALTHY:
            logger.debug(f"🔍 [FAILURE_TRANSITION] HEALTHY state processing")
            if metadata.consecutive_failures >= self.config.warning_failure_threshold:
                logger.debug(f"🔄 [FAILURE_TRANSITION] HEALTHY -> WARNING (failures: {metadata.consecutive_failures} >= {self.config.warning_failure_threshold})")
                await self._transition_to_state(agent_id, service_name, ServiceConnectionState.WARNING)
            else:
                logger.debug(f"⏸️ [FAILURE_TRANSITION] HEALTHY: Not enough failures yet ({metadata.consecutive_failures} < {self.config.warning_failure_threshold})")

        elif current_state == ServiceConnectionState.WARNING:
            logger.debug(f"🔍 [FAILURE_TRANSITION] WARNING state processing")
            if metadata.consecutive_failures >= self.config.reconnecting_failure_threshold:
                logger.debug(f"🔄 [FAILURE_TRANSITION] WARNING -> RECONNECTING (failures: {metadata.consecutive_failures} >= {self.config.reconnecting_failure_threshold})")
                await self._transition_to_state(agent_id, service_name, ServiceConnectionState.RECONNECTING)
            else:
                logger.debug(f"⏸️ [FAILURE_TRANSITION] WARNING: Not enough failures yet ({metadata.consecutive_failures} < {self.config.reconnecting_failure_threshold})")

        elif current_state == ServiceConnectionState.INITIALIZING:
            logger.debug(f"🔍 [FAILURE_TRANSITION] INITIALIZING state processing")
            # 🔧 修复：INITIALIZING失败应该转到RECONNECTING，而不是直接跳到UNREACHABLE
            if metadata.consecutive_failures >= self.config.reconnecting_failure_threshold:
                logger.debug(f"🔄 [FAILURE_TRANSITION] INITIALIZING -> RECONNECTING (failures: {metadata.consecutive_failures} >= {self.config.reconnecting_failure_threshold})")
                await self._transition_to_state(agent_id, service_name, ServiceConnectionState.RECONNECTING)
            else:
                logger.debug(f"⏸️ [FAILURE_TRANSITION] INITIALIZING: Not enough failures yet ({metadata.consecutive_failures} < {self.config.reconnecting_failure_threshold})")

        elif current_state == ServiceConnectionState.RECONNECTING:
            logger.debug(f"🔍 [FAILURE_TRANSITION] RECONNECTING state processing")
            if metadata.reconnect_attempts >= self.config.max_reconnect_attempts:
                logger.debug(f"🔄 [FAILURE_TRANSITION] RECONNECTING -> UNREACHABLE (attempts: {metadata.reconnect_attempts} >= {self.config.max_reconnect_attempts})")
                await self._transition_to_state(agent_id, service_name, ServiceConnectionState.UNREACHABLE)
            else:
                logger.debug(f"⏸️ [FAILURE_TRANSITION] RECONNECTING: Not enough attempts yet ({metadata.reconnect_attempts} < {self.config.max_reconnect_attempts})")

        elif current_state == ServiceConnectionState.UNREACHABLE:
            logger.debug(f"⏸️ [FAILURE_TRANSITION] UNREACHABLE: Already in final failure state")

        elif current_state == ServiceConnectionState.DISCONNECTING:
            logger.debug(f"⏸️ [FAILURE_TRANSITION] DISCONNECTING: Service is being disconnected")

        elif current_state == ServiceConnectionState.DISCONNECTED:
            logger.debug(f"⏸️ [FAILURE_TRANSITION] DISCONNECTED: Service is already disconnected")

        else:
            logger.debug(f"⏸️ [FAILURE_TRANSITION] No transition rules for state {current_state}")

        logger.debug(f"🔍 [FAILURE_TRANSITION] Completed for {service_name}")
    
    async def _transition_to_state(self, agent_id: str, service_name: str,
                                 new_state: ServiceConnectionState):
        """执行状态转换"""
        old_state = self.get_service_state(agent_id, service_name)
        logger.debug(f"🔄 [STATE_TRANSITION] Attempting transition for {service_name}: {old_state} -> {new_state}")

        if old_state == new_state:
            logger.debug(f"⏸️ [STATE_TRANSITION] No change needed for {service_name}: already in {new_state}")
            return

        # 确保agent存在
        if agent_id not in self.service_states:
            logger.debug(f"🔧 [STATE_TRANSITION] Creating agent_id {agent_id} in service_states")
            self.service_states[agent_id] = {}

        # 更新状态
        logger.debug(f"🔄 [STATE_TRANSITION] Updating state for {service_name}: {old_state} -> {new_state}")
        self.service_states[agent_id][service_name] = new_state
        metadata = self.get_service_metadata(agent_id, service_name)
        if metadata:
            metadata.state_entered_time = datetime.now()
            logger.debug(f"🔄 [STATE_TRANSITION] Updated state_entered_time for {service_name}")
        else:
            logger.warning(f"⚠️ [STATE_TRANSITION] No metadata found for {service_name} during state transition")

        # 执行状态进入处理
        logger.debug(f"🔄 [STATE_TRANSITION] Calling _on_state_entered for {service_name}")
        await self._on_state_entered(agent_id, service_name, new_state, old_state)

        logger.info(f"✅ [STATE_TRANSITION] Service {service_name} (agent {agent_id}) transitioned from {old_state} to {new_state}")
    
    async def _on_state_entered(self, agent_id: str, service_name: str, 
                              new_state: ServiceConnectionState, old_state: ServiceConnectionState):
        """状态进入时的处理逻辑"""
        if new_state == ServiceConnectionState.RECONNECTING:
            await self._enter_reconnecting_state(agent_id, service_name)
        elif new_state == ServiceConnectionState.UNREACHABLE:
            await self._enter_unreachable_state(agent_id, service_name)
        elif new_state == ServiceConnectionState.DISCONNECTING:
            await self._enter_disconnecting_state(agent_id, service_name)
        elif new_state == ServiceConnectionState.HEALTHY:
            await self._enter_healthy_state(agent_id, service_name)
    
    async def _enter_reconnecting_state(self, agent_id: str, service_name: str):
        """进入重连状态的处理"""
        metadata = self.get_service_metadata(agent_id, service_name)
        if metadata:
            metadata.reconnect_attempts = 0
            # 计算下次重连时间（指数退避）
            delay = min(self.config.base_reconnect_delay * (2 ** metadata.reconnect_attempts), 
                       self.config.max_reconnect_delay)
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
    
    async def graceful_disconnect(self, agent_id: str, service_name: str, reason: str = "user_requested"):
        """优雅断连服务"""
        metadata = self.get_service_metadata(agent_id, service_name)
        if metadata:
            metadata.disconnect_reason = reason
        
        await self._transition_to_state(agent_id, service_name, ServiceConnectionState.DISCONNECTING)
    
    def remove_service(self, agent_id: str, service_name: str):
        """完全移除服务记录"""
        if agent_id in self.service_states:
            self.service_states[agent_id].pop(service_name, None)
        if agent_id in self.state_metadata:
            self.state_metadata[agent_id].pop(service_name, None)
        
        # 从处理队列中移除
        self.state_change_queue.discard((agent_id, service_name))
        
        logger.info(f"Service {service_name} removed from agent {agent_id}")
    
    # TODO: 告警相关方法（后期完善）
    async def _trigger_alert_notification(self, agent_id: str, service_name: str, message: str):
        """触发告警通知 - 待实现"""
        # 预留接口，后期集成告警系统
        logger.warning(f"ALERT: {message} for service {service_name} in agent {agent_id}")
        pass
    
    async def _send_deregistration_request(self, agent_id: str, service_name: str):
        """发送注销请求 - 待实现"""
        # 预留接口，后期实现向服务发送注销请求
        logger.debug(f"Deregistration request for service {service_name} in agent {agent_id}")
        pass
    
    async def _lifecycle_management_loop(self):
        """生命周期管理主循环"""
        consecutive_failures = 0
        max_consecutive_failures = 5

        logger.info("Lifecycle management loop started")

        while self.is_running:
            try:
                logger.debug(f"🔄 [LIFECYCLE_LOOP] Iteration starting, queue size: {len(self.state_change_queue)}")
                await asyncio.sleep(5.0)  # 每5秒检查一次
                logger.debug(f"🔄 [LIFECYCLE_LOOP] About to process state changes, queue: {self.state_change_queue}")
                await self._process_state_changes()
                logger.debug(f"🔄 [LIFECYCLE_LOOP] State changes processed successfully, remaining queue size: {len(self.state_change_queue)}")
                consecutive_failures = 0

            except asyncio.CancelledError:
                logger.info("Lifecycle management loop cancelled")
                break
            except Exception as e:
                consecutive_failures += 1
                logger.error(f"Lifecycle management loop error (failure {consecutive_failures}/{max_consecutive_failures}): {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")

                if consecutive_failures >= max_consecutive_failures:
                    logger.critical("Too many consecutive lifecycle management failures, stopping loop")
                    break

                # 指数退避延迟
                backoff_delay = min(30 * (2 ** consecutive_failures), 300)  # 最大5分钟
                await asyncio.sleep(backoff_delay)

        logger.info("Lifecycle management loop ended")
    
    async def _process_state_changes(self):
        """处理状态变化队列"""
        if not self.state_change_queue:
            logger.debug("🔄 [PROCESS_QUEUE] Queue is empty, nothing to process")
            return

        logger.debug(f"🔄 [PROCESS_QUEUE] Processing {len(self.state_change_queue)} services in state change queue")
        logger.debug(f"🔄 [PROCESS_QUEUE] Queue contents: {self.state_change_queue}")

        # 批量处理状态变化
        current_queue = self.state_change_queue.copy()
        self.state_change_queue.clear()
        logger.debug(f"🔄 [PROCESS_QUEUE] Cleared queue, processing {len(current_queue)} items")

        for agent_id, service_name in current_queue:
            try:
                logger.debug(f"🔄 [PROCESS_QUEUE] Processing service {service_name} in agent {agent_id}")
                await self._process_single_service(agent_id, service_name)
                logger.debug(f"✅ [PROCESS_QUEUE] Successfully processed service {service_name} in agent {agent_id}")
            except Exception as e:
                logger.error(f"❌ [PROCESS_QUEUE] Failed to process service {service_name} in agent {agent_id}: {e}")
                import traceback
                logger.error(f"❌ [PROCESS_QUEUE] Traceback: {traceback.format_exc()}")
                # 重新添加到队列以便下次重试
                self.state_change_queue.add((agent_id, service_name))
                logger.debug(f"🔄 [PROCESS_QUEUE] Re-added {service_name} to queue for retry")
    
    async def _process_single_service(self, agent_id: str, service_name: str):
        """处理单个服务的状态逻辑"""
        logger.debug(f"🔍 [PROCESS_SERVICE] Processing {service_name} in agent {agent_id}")

        current_state = self.get_service_state(agent_id, service_name)
        metadata = self.get_service_metadata(agent_id, service_name)

        logger.debug(f"🔍 [PROCESS_SERVICE] Current state: {current_state}, metadata exists: {metadata is not None}")

        if not metadata:
            logger.warning(f"⚠️ [PROCESS_SERVICE] No metadata found for {service_name}, skipping")
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
                    await self._handle_success_transition(agent_id, service_name, ServiceConnectionState.INITIALIZING)
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
                        await self._handle_success_transition(agent_id, service_name, ServiceConnectionState.INITIALIZING)
                        logger.info(f"Service {service_name} initial connection successful with {len(service_tools)} tools")
                        return
                    else:
                        # 仍然没有工具，认为连接失败
                        # 🔧 修复：通过健康检查结果处理失败，避免重复计数
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
            success, message = await self.orchestrator.connect_service(service_name, agent_id=agent_id)

            if success:
                # 连接成功，处理成功转换
                await self._handle_success_transition(agent_id, service_name, ServiceConnectionState.INITIALIZING)
                logger.info(f"Service {service_name} initial connection successful")
            else:
                # 🔧 修复：连接失败，通过健康检查结果处理，避免重复计数
                await self.handle_health_check_result(
                    agent_id=agent_id,
                    service_name=service_name,
                    success=False,
                    response_time=0.0,
                    error_message=message
                )
                logger.warning(f"Service {service_name} initial connection failed: {message}")

        except Exception as e:
            # 🔧 修复：连接异常，通过健康检查结果处理，避免重复计数
            await self.handle_health_check_result(
                agent_id=agent_id,
                service_name=service_name,
                success=False,
                response_time=0.0,
                error_message=str(e)
            )
            logger.error(f"Service {service_name} initial connection error: {e}")

    async def _attempt_reconnection(self, agent_id: str, service_name: str):
        """尝试重连"""
        try:
            # 调用orchestrator的连接方法
            success, message = await self.orchestrator.connect_service(service_name, agent_id=agent_id)
            
            metadata = self.get_service_metadata(agent_id, service_name)
            if metadata:
                metadata.reconnect_attempts += 1
            
            if success:
                # 🔧 修复：重连成功后重置重连计数器
                if metadata:
                    metadata.reconnect_attempts = 0
                    metadata.next_retry_time = None
                    metadata.error_message = None
                await self._transition_to_state(agent_id, service_name, ServiceConnectionState.HEALTHY)
                logger.info(f"Reconnection successful for service {service_name} in agent {agent_id}")
            else:
                # 重连失败，计算下次重试时间
                if metadata:
                    delay = min(self.config.base_reconnect_delay * (2 ** metadata.reconnect_attempts), 
                               self.config.max_reconnect_delay)
                    metadata.next_retry_time = datetime.now() + timedelta(seconds=delay)
                    metadata.error_message = message
                
                # 检查是否达到最大重试次数
                if metadata and metadata.reconnect_attempts >= self.config.max_reconnect_attempts:
                    await self._transition_to_state(agent_id, service_name, ServiceConnectionState.UNREACHABLE)
                
                logger.debug(f"Reconnection failed for service {service_name} in agent {agent_id}: {message}")
                
        except Exception as e:
            logger.error(f"Reconnection attempt failed for service {service_name} in agent {agent_id}: {e}")
    
    async def _attempt_long_period_retry(self, agent_id: str, service_name: str):
        """尝试长周期重试"""
        try:
            # 尝试连接
            success, message = await self.orchestrator.connect_service(service_name, agent_id=agent_id)
            
            metadata = self.get_service_metadata(agent_id, service_name)
            
            if success:
                # 🔧 修复：长周期重试成功后重置相关计数器
                if metadata:
                    metadata.reconnect_attempts = 0
                    metadata.next_retry_time = None
                    metadata.error_message = None
                await self._transition_to_state(agent_id, service_name, ServiceConnectionState.HEALTHY)
                logger.info(f"Long period retry successful for service {service_name} in agent {agent_id}")
            else:
                # 设置下次长周期重试时间
                if metadata:
                    metadata.next_retry_time = datetime.now() + timedelta(seconds=self.config.long_retry_interval)
                    metadata.error_message = message
                
                logger.debug(f"Long period retry failed for service {service_name} in agent {agent_id}: {message}")
                
        except Exception as e:
            logger.error(f"Long period retry failed for service {service_name} in agent {agent_id}: {e}")
