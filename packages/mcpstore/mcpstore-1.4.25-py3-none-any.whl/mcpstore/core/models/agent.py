"""
Agent相关的数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any

from .service import ServiceConnectionState, ServiceStateMetadata


@dataclass
class AgentInfo:
    """Agent信息"""
    agent_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AgentServiceSummary:
    """Agent服务摘要"""
    service_name: str
    service_type: str  # "local" | "remote" | "sse" | "stdio"
    status: ServiceConnectionState  # 使用新的7状态枚举
    tool_count: int
    last_used: Optional[datetime] = None
    client_id: Optional[str] = None
    # 新增生命周期相关字段
    response_time: Optional[float] = None
    health_details: Optional[ServiceStateMetadata] = None

@dataclass
class AgentStatistics:
    """Agent统计信息"""
    agent_id: str
    service_count: int
    tool_count: int
    healthy_services: int
    unhealthy_services: int
    total_tool_executions: int
    last_activity: Optional[datetime] = None
    services: List[AgentServiceSummary] = None
    
    def __post_init__(self):
        if self.services is None:
            self.services = []

@dataclass
class AgentsSummary:
    """所有Agent的汇总信息"""
    total_agents: int
    active_agents: int  # 有服务的Agent数量
    total_services: int
    total_tools: int
    store_services: int  # Store级别的服务数量
    store_tools: int    # Store级别的工具数量
    agents: List[AgentStatistics] = None
    
    def __post_init__(self):
        if self.agents is None:
            self.agents = []
