from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Literal, Union

from pydantic import BaseModel, Field


class TransportType(str, Enum):
    STREAMABLE_HTTP = "streamable_http"
    STDIO = "stdio"
    STDIO_PYTHON = "stdio_python"
    STDIO_NODE = "stdio_node"
    STDIO_SHELL = "stdio_shell"


class ServiceConnectionState(str, Enum):
    """Service connection lifecycle state enumeration"""
    INITIALIZING = "initializing"     # Initializing: configuration validated, performing first connection
    HEALTHY = "healthy"               # Healthy: connection normal, heartbeat successful
    WARNING = "warning"               # Warning: occasional heartbeat failures, but not reaching reconnection threshold
    RECONNECTING = "reconnecting"     # Reconnecting: consecutive failures reached threshold, reconnecting
    UNREACHABLE = "unreachable"       # Unreachable: reconnection failed, entering long-cycle retry
    DISCONNECTING = "disconnecting"   # Disconnecting: performing graceful shutdown
    DISCONNECTED = "disconnected"     # Disconnected: service terminated, waiting for manual deletion

class ServiceStateMetadata(BaseModel):
    """Service state metadata"""
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_ping_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    reconnect_attempts: int = 0
    next_retry_time: Optional[datetime] = None
    state_entered_time: Optional[datetime] = None
    disconnect_reason: Optional[str] = None


class ServiceInfo(BaseModel):
    url: str = ""
    name: str
    transport_type: TransportType
    status: ServiceConnectionState  # Use new 7-state enumeration
    tool_count: int
    keep_alive: bool
    working_dir: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    last_heartbeat: Optional[datetime] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    package_name: Optional[str] = None
    # New lifecycle-related fields
    state_metadata: Optional[ServiceStateMetadata] = None
    last_state_change: Optional[datetime] = None
    client_id: Optional[str] = None  # Add client_id field

class ServiceInfoResponse(BaseModel):
    """Detailed information response model for a single service"""
    service: Optional[ServiceInfo] = Field(None, description="服务信息")
    tools: List[Dict[str, Any]] = Field(..., description="服务提供的工具列表")
    connected: bool = Field(..., description="服务连接状态")
    success: bool = Field(True, description="操作是否成功")
    message: Optional[str] = Field(None, description="响应消息")

class ServicesResponse(BaseModel):
    """Service list response model"""
    services: List[ServiceInfo] = Field(..., description="服务列表")
    total_services: int = Field(..., description="服务总数")
    total_tools: int = Field(..., description="工具总数")
    success: bool = Field(True, description="操作是否成功")
    message: Optional[str] = Field(None, description="响应消息")

class RegisterRequestUnion(BaseModel):
    url: Optional[str] = None
    name: Optional[str] = None
    transport: Optional[str] = None
    keep_alive: Optional[bool] = None
    working_dir: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    package_name: Optional[str] = None

class JsonUpdateRequest(BaseModel):
    client_id: Optional[str] = None
    service_names: Optional[List[str]] = None
    config: Dict[str, Any]

# 这些响应模型已移动到 common.py 中，请直接从 common.py 导入

class ServiceConfig(BaseModel):
    """服务配置基类"""
    name: str = Field(..., description="服务名称")

class URLServiceConfig(ServiceConfig):
    """URL方式的服务配置"""
    url: str = Field(..., description="服务URL")
    transport: Optional[str] = Field("streamable-http", description="传输类型: streamable-http 或 sse")
    headers: Optional[Dict[str, str]] = Field(default=None, description="请求头")

class CommandServiceConfig(ServiceConfig):
    """本地命令方式的服务配置"""
    command: str = Field(..., description="执行命令")
    args: Optional[List[str]] = Field(default=None, description="命令参数")
    env: Optional[Dict[str, str]] = Field(default=None, description="环境变量")
    working_dir: Optional[str] = Field(default=None, description="工作目录")

class MCPServerConfig(BaseModel):
    """完整的MCP服务配置"""
    mcpServers: Dict[str, Dict[str, Any]] = Field(..., description="MCP服务配置字典")

# 支持多种配置格式
ServiceConfigUnion = Union[URLServiceConfig, CommandServiceConfig, MCPServerConfig, Dict[str, Any]]

class AddServiceRequest(BaseModel):
    """添加服务请求"""
    config: ServiceConfigUnion = Field(..., description="服务配置，支持多种格式")
    update_config: bool = Field(default=True, description="是否更新配置文件") 
