"""
MCP Store 异常类定义
"""

class MCPStoreError(Exception):
    """MCP Store 基础异常类"""
    pass

class ServiceNotFoundError(MCPStoreError):
    """服务不存在"""
    pass

class InvalidConfigError(MCPStoreError):
    """配置无效"""
    pass

class DeleteServiceError(MCPStoreError):
    """删除服务失败"""
    pass 
