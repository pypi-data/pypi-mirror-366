"""
MCPStore 健康状态管理器
实现分级健康状态、智能超时调整等高级健康检查功能
"""

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """服务健康状态枚举"""
    HEALTHY = "healthy"         # 响应正常，时间快
    WARNING = "warning"         # 响应正常，但较慢
    SLOW = "slow"              # 响应很慢但成功
    UNHEALTHY = "unhealthy"    # 响应失败或超时
    DISCONNECTED = "disconnected"  # 已断开连接
    RECONNECTING = "reconnecting"  # 重连中
    FAILED = "failed"          # 重连失败，已放弃
    UNKNOWN = "unknown"        # 状态未知

@dataclass
class HealthCheckResult:
    """健康检查结果"""
    status: HealthStatus
    response_time: float
    timestamp: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ServiceHealthConfig:
    """服务健康配置"""
    # 超时配置
    ping_timeout: float = 3.0
    startup_wait_time: float = 2.0
    
    # 健康状态阈值
    healthy_threshold: float = 1.0      # 1秒内为健康
    warning_threshold: float = 3.0      # 3秒内为警告
    slow_threshold: float = 10.0        # 10秒内为慢响应
    
    # 智能超时配置
    enable_adaptive_timeout: bool = False
    adaptive_multiplier: float = 2.0
    history_size: int = 10

class ServiceHealthTracker:
    """服务健康状态跟踪器"""
    
    def __init__(self, service_name: str, config: ServiceHealthConfig):
        self.service_name = service_name
        self.config = config
        self.response_history: deque = deque(maxlen=config.history_size)
        self.last_check_time: float = 0
        self.last_status: HealthStatus = HealthStatus.UNKNOWN
        self.consecutive_failures: int = 0
        
    def record_response(self, response_time: float, success: bool, error: Optional[str] = None):
        """记录响应时间和结果"""
        timestamp = time.time()
        
        if success:
            # 成功响应，记录时间
            self.response_history.append(response_time)
            self.consecutive_failures = 0
            
            # 根据响应时间确定状态
            if response_time <= self.config.healthy_threshold:
                status = HealthStatus.HEALTHY
            elif response_time <= self.config.warning_threshold:
                status = HealthStatus.WARNING
            elif response_time <= self.config.slow_threshold:
                status = HealthStatus.SLOW
            else:
                status = HealthStatus.SLOW  # 超过慢响应阈值但仍成功
        else:
            # 失败响应
            self.consecutive_failures += 1
            status = HealthStatus.UNHEALTHY
            
        self.last_status = status
        self.last_check_time = timestamp
        
        logger.debug(f"Service {self.service_name}: {status.value}, response_time={response_time:.2f}s, consecutive_failures={self.consecutive_failures}")
        
        return HealthCheckResult(
            status=status,
            response_time=response_time,
            timestamp=timestamp,
            error_message=error,
            details={
                "consecutive_failures": self.consecutive_failures,
                "avg_response_time": self.get_average_response_time()
            }
        )
    
    def get_average_response_time(self) -> float:
        """获取平均响应时间"""
        if not self.response_history:
            return 0.0
        return sum(self.response_history) / len(self.response_history)
    
    def get_adaptive_timeout(self) -> float:
        """获取智能调整的超时时间"""
        if not self.config.enable_adaptive_timeout or not self.response_history:
            return self.config.ping_timeout
            
        avg_time = self.get_average_response_time()
        adaptive_timeout = avg_time * self.config.adaptive_multiplier
        
        # 限制在合理范围内
        min_timeout = self.config.ping_timeout
        max_timeout = self.config.ping_timeout * 3
        
        return max(min_timeout, min(adaptive_timeout, max_timeout))
    
    def should_retry(self) -> bool:
        """判断是否应该重试"""
        # 如果连续失败次数较少，可以重试
        return self.consecutive_failures < 3
    
    def get_health_summary(self) -> Dict[str, Any]:
        """获取健康状态摘要"""
        return {
            "service_name": self.service_name,
            "current_status": self.last_status.value,
            "last_check_time": self.last_check_time,
            "consecutive_failures": self.consecutive_failures,
            "average_response_time": self.get_average_response_time(),
            "adaptive_timeout": self.get_adaptive_timeout(),
            "response_history_size": len(self.response_history)
        }

class HealthManager:
    """健康管理器 - 管理所有服务的健康状态"""
    
    def __init__(self):
        self.service_trackers: Dict[str, ServiceHealthTracker] = {}
        self.default_config = ServiceHealthConfig()
        
    def get_or_create_tracker(self, service_name: str, config: Optional[ServiceHealthConfig] = None) -> ServiceHealthTracker:
        """获取或创建服务跟踪器"""
        if service_name not in self.service_trackers:
            service_config = config or self.default_config
            self.service_trackers[service_name] = ServiceHealthTracker(service_name, service_config)
        return self.service_trackers[service_name]
    
    def update_config(self, monitoring_config: Dict[str, Any]):
        """根据监控配置更新默认配置"""
        # 更新默认配置
        if "local_service_ping_timeout" in monitoring_config:
            self.default_config.ping_timeout = monitoring_config["local_service_ping_timeout"]
        if "startup_wait_time" in monitoring_config:
            self.default_config.startup_wait_time = monitoring_config["startup_wait_time"]
        if "healthy_response_threshold" in monitoring_config:
            self.default_config.healthy_threshold = monitoring_config["healthy_response_threshold"]
        if "warning_response_threshold" in monitoring_config:
            self.default_config.warning_threshold = monitoring_config["warning_response_threshold"]
        if "slow_response_threshold" in monitoring_config:
            self.default_config.slow_threshold = monitoring_config["slow_response_threshold"]
        if "enable_adaptive_timeout" in monitoring_config:
            self.default_config.enable_adaptive_timeout = monitoring_config["enable_adaptive_timeout"]
        if "adaptive_timeout_multiplier" in monitoring_config:
            self.default_config.adaptive_multiplier = monitoring_config["adaptive_timeout_multiplier"]
        if "response_time_history_size" in monitoring_config:
            self.default_config.history_size = monitoring_config["response_time_history_size"]
            
        logger.info(f"Health manager config updated: {self.default_config}")
    
    def get_service_config(self, service_name: str, service_config: Dict[str, Any]) -> ServiceHealthConfig:
        """根据服务类型获取配置"""
        config = ServiceHealthConfig()
        
        # 根据服务类型调整配置
        if service_config.get("url"):
            # 远程服务
            config.ping_timeout = getattr(self.default_config, 'remote_service_ping_timeout', 5.0)
        else:
            # 本地服务
            config.ping_timeout = getattr(self.default_config, 'local_service_ping_timeout', 3.0)
            
        # 应用其他配置
        config.startup_wait_time = self.default_config.startup_wait_time
        config.healthy_threshold = self.default_config.healthy_threshold
        config.warning_threshold = self.default_config.warning_threshold
        config.slow_threshold = self.default_config.slow_threshold
        config.enable_adaptive_timeout = self.default_config.enable_adaptive_timeout
        config.adaptive_multiplier = self.default_config.adaptive_multiplier
        config.history_size = self.default_config.history_size
        
        return config
    
    def record_health_check(self, service_name: str, response_time: float, success: bool, 
                          error: Optional[str] = None, service_config: Optional[Dict[str, Any]] = None) -> HealthCheckResult:
        """记录健康检查结果"""
        # 获取或创建跟踪器
        if service_name not in self.service_trackers and service_config:
            config = self.get_service_config(service_name, service_config)
            self.service_trackers[service_name] = ServiceHealthTracker(service_name, config)
            
        tracker = self.get_or_create_tracker(service_name)
        return tracker.record_response(response_time, success, error)
    
    def get_service_timeout(self, service_name: str, service_config: Optional[Dict[str, Any]] = None) -> float:
        """获取服务的超时时间（可能是智能调整的）"""
        if service_name in self.service_trackers:
            return self.service_trackers[service_name].get_adaptive_timeout()
        
        # 新服务，使用默认配置
        if service_config and service_config.get("url"):
            return getattr(self.default_config, 'remote_service_ping_timeout', 5.0)
        else:
            return getattr(self.default_config, 'local_service_ping_timeout', 3.0)
    
    def get_all_health_summary(self) -> Dict[str, Any]:
        """获取所有服务的健康状态摘要"""
        summary = {
            "total_services": len(self.service_trackers),
            "healthy_count": 0,
            "warning_count": 0,
            "slow_count": 0,
            "unhealthy_count": 0,
            "services": {}
        }
        
        for service_name, tracker in self.service_trackers.items():
            service_summary = tracker.get_health_summary()
            summary["services"][service_name] = service_summary
            
            # 统计各状态数量
            status = tracker.last_status
            if status == HealthStatus.HEALTHY:
                summary["healthy_count"] += 1
            elif status == HealthStatus.WARNING:
                summary["warning_count"] += 1
            elif status == HealthStatus.SLOW:
                summary["slow_count"] += 1
            elif status == HealthStatus.UNHEALTHY:
                summary["unhealthy_count"] += 1
                
        return summary
    
    def cleanup_old_trackers(self, active_services: List[str]):
        """清理不再活跃的服务跟踪器"""
        inactive_services = set(self.service_trackers.keys()) - set(active_services)
        for service_name in inactive_services:
            del self.service_trackers[service_name]
            logger.debug(f"Cleaned up tracker for inactive service: {service_name}")

# 全局健康管理器实例
_global_health_manager = None

def get_health_manager() -> HealthManager:
    """获取全局健康管理器实例"""
    global _global_health_manager
    if _global_health_manager is None:
        _global_health_manager = HealthManager()
    return _global_health_manager
