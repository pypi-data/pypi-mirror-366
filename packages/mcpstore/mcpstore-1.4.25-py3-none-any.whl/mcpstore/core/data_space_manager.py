"""
数据空间管理器
负责初始化和维护store的数据目录，确保每个store有独立的数据空间
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .registry.schema_manager import get_schema_manager

logger = logging.getLogger(__name__)

class DataSpaceManager:
    """数据空间管理器 - 负责初始化和维护store的数据目录"""

    # 必需文件定义 - 保持与默认配置一致的层级结构
    REQUIRED_FILES = {
        "defaults/agent_clients.json": {
            "schema_name": "agent_clients",
            "description": "Agent客户端映射文件"
        },
        "defaults/client_services.json": {
            "schema_name": "client_services",
            "description": "客户端服务映射文件"
        }
    }
    
    def __init__(self, mcp_json_path: str):
        """
        初始化数据空间管理器

        Args:
            mcp_json_path: MCP JSON配置文件路径
        """
        self.mcp_json_path = Path(mcp_json_path).resolve()
        self.workspace_dir = self.mcp_json_path.parent
        self.schema_manager = get_schema_manager()

        logger.info(f"DataSpaceManager initialized for workspace: {self.workspace_dir}")
    
    def initialize_workspace(self) -> bool:
        """
        初始化工作空间，确保所有必需文件存在且有效
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            logger.info(f"Initializing workspace: {self.workspace_dir}")
            
            # 1. 确保工作空间目录存在
            self.workspace_dir.mkdir(parents=True, exist_ok=True)
            
            # 2. 检查和处理MCP JSON文件
            if not self._validate_and_fix_mcp_json():
                logger.error("Failed to validate/fix MCP JSON file")
                return False
            
            # 3. 检查和创建必需文件
            if not self._ensure_required_files():
                logger.error("Failed to ensure required files")
                return False
            
            logger.info("Workspace initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Workspace initialization failed: {e}")
            return False
    
    def _validate_and_fix_mcp_json(self) -> bool:
        """
        验证和修复MCP JSON文件
        
        Returns:
            bool: 处理是否成功
        """
        try:
            if not self.mcp_json_path.exists():
                logger.info(f"MCP JSON file not found, creating: {self.mcp_json_path}")
                return self._create_mcp_json()
            
            # 尝试读取和验证现有文件
            try:
                with open(self.mcp_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 验证文件结构
                if self._validate_mcp_json_structure(data):
                    logger.info("MCP JSON file is valid")
                    return True
                else:
                    logger.warning("MCP JSON file structure is invalid, will backup and recreate")
                    return self._backup_and_recreate_mcp_json()
                    
            except json.JSONDecodeError as e:
                logger.warning(f"MCP JSON file has syntax errors: {e}, will backup and recreate")
                return self._backup_and_recreate_mcp_json()
            except Exception as e:
                logger.warning(f"Error reading MCP JSON file: {e}, will backup and recreate")
                return self._backup_and_recreate_mcp_json()
                
        except Exception as e:
            logger.error(f"Failed to validate/fix MCP JSON: {e}")
            return False
    
    def _validate_mcp_json_structure(self, data: Dict[str, Any]) -> bool:
        """
        验证MCP JSON文件结构
        
        Args:
            data: JSON数据
            
        Returns:
            bool: 结构是否有效
        """
        # 检查必需字段
        if not isinstance(data, dict):
            return False
        
        # 检查mcpServers字段
        if "mcpServers" not in data:
            return False
        
        if not isinstance(data["mcpServers"], dict):
            return False
        
        # 基本结构有效
        return True
    
    def _backup_and_recreate_mcp_json(self) -> bool:
        """
        备份现有文件并重新创建MCP JSON文件

        Returns:
            bool: 操作是否成功
        """
        try:
            # 创建备份 - 统一使用.bak后缀
            backup_path = Path(str(self.mcp_json_path) + '.bak')

            if self.mcp_json_path.exists():
                shutil.copy2(self.mcp_json_path, backup_path)
                logger.info(f"Backup created: {backup_path}")

            # 重新创建文件
            return self._create_mcp_json()

        except Exception as e:
            logger.error(f"Failed to backup and recreate MCP JSON: {e}")
            return False
    
    def _create_mcp_json(self) -> bool:
        """
        创建新的MCP JSON文件

        Returns:
            bool: 创建是否成功
        """
        try:
            # 使用Schema管理器获取模板
            template = self.schema_manager.get_mcp_config_template()

            with open(self.mcp_json_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)

            logger.info(f"Created new MCP JSON file: {self.mcp_json_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create MCP JSON file: {e}")
            return False
    
    def _ensure_required_files(self) -> bool:
        """
        确保所有必需文件存在且有效
        
        Returns:
            bool: 操作是否成功
        """
        try:
            for file_path, config in self.REQUIRED_FILES.items():
                full_path = self.workspace_dir / file_path
                
                # 确保目录存在
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                if not full_path.exists():
                    # 文件不存在，创建新文件
                    self._create_file_from_template(full_path, config)
                    logger.info(f"Created missing file: {full_path}")
                else:
                    # 文件存在，验证格式
                    if not self._validate_json_file(full_path):
                        # 文件格式错误，备份并重新创建
                        self._backup_and_recreate_file(full_path, config)
                        logger.warning(f"Recreated invalid file: {full_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure required files: {e}")
            return False
    
    def _create_file_from_template(self, file_path: Path, config: Dict[str, Any]) -> bool:
        """
        从模板创建文件

        Args:
            file_path: 文件路径
            config: 文件配置

        Returns:
            bool: 创建是否成功
        """
        try:
            # 使用Schema管理器获取模板
            schema_name = config.get("schema_name", "")
            template = self.schema_manager.get_template(schema_name)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to create file {file_path}: {e}")
            return False
    
    def _validate_json_file(self, file_path: Path) -> bool:
        """
        验证JSON文件格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 文件是否有效
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, Exception):
            return False
    
    def _backup_and_recreate_file(self, file_path: Path, config: Dict[str, Any]) -> bool:
        """
        备份并重新创建文件

        Args:
            file_path: 文件路径
            config: 文件配置

        Returns:
            bool: 操作是否成功
        """
        try:
            # 创建备份 - 统一使用.bak后缀
            backup_path = Path(str(file_path) + '.bak')

            if file_path.exists():
                shutil.copy2(file_path, backup_path)
                logger.info(f"Backup created: {backup_path}")

            # 重新创建文件
            return self._create_file_from_template(file_path, config)

        except Exception as e:
            logger.error(f"Failed to backup and recreate file {file_path}: {e}")
            return False
    
    def get_file_path(self, file_type: str) -> Path:
        """
        获取特定类型文件的路径
        
        Args:
            file_type: 文件类型 (如: 'agent_clients.json', 'monitoring/alerts.json')
            
        Returns:
            Path: 文件路径
        """
        if file_type == "mcp.json":
            return self.mcp_json_path
        
        if file_type in self.REQUIRED_FILES:
            return self.workspace_dir / file_type
        
        # 对于其他文件，直接返回相对于workspace的路径
        return self.workspace_dir / file_type
    
    def get_workspace_info(self) -> Dict[str, Any]:
        """
        获取工作空间信息
        
        Returns:
            Dict: 工作空间信息
        """
        info = {
            "workspace_dir": str(self.workspace_dir),
            "mcp_json_path": str(self.mcp_json_path),
            "files": {}
        }
        
        # 检查MCP JSON文件
        info["files"]["mcp.json"] = {
            "exists": self.mcp_json_path.exists(),
            "path": str(self.mcp_json_path)
        }
        
        # 检查必需文件
        for file_type in self.REQUIRED_FILES:
            file_path = self.get_file_path(file_type)
            info["files"][file_type] = {
                "exists": file_path.exists(),
                "path": str(file_path),
                "description": self.REQUIRED_FILES[file_type]["description"]
            }
        
        return info
