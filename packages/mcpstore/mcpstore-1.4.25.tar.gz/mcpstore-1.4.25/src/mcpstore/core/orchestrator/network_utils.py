"""
MCPOrchestrator Network Utils Module
网络工具模块 - 包含网络错误检测和工具方法
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class NetworkUtilsMixin:
    """网络工具混入类"""

    def _is_network_error(self, error: Exception) -> bool:
        """判断是否是网络相关错误"""
        error_str = str(error).lower()
        network_error_keywords = [
            'connection', 'network', 'timeout', 'unreachable',
            'refused', 'reset', 'dns', 'resolve', 'socket'
        ]
        return any(keyword in error_str for keyword in network_error_keywords)

    def _is_filesystem_error(self, error: Exception) -> bool:
        """判断是否是文件系统相关错误"""
        if isinstance(error, (FileNotFoundError, PermissionError, OSError, IOError)):
            return True

        error_str = str(error).lower()
        filesystem_error_keywords = [
            'no such file', 'file not found', 'permission denied',
            'access denied', 'directory not found', 'path not found'
        ]
        return any(keyword in error_str for keyword in filesystem_error_keywords)
