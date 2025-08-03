import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List, Set, TypeVar, Protocol

from ..models.service import ServiceConnectionState, ServiceStateMetadata
from .types import SessionProtocol, SessionType

logger = logging.getLogger(__name__)

class ServiceRegistry:
    """
    Manages the state of connected services and their tools, with agent_id isolation.
    
    agent_id as primary key, implementing complete isolation between store/agent/agent:
    - self.sessions: Dict[agent_id, Dict[service_name, session]]
    - self.tool_cache: Dict[agent_id, Dict[tool_name, tool_def]]
    - self.tool_to_session_map: Dict[agent_id, Dict[tool_name, session]]
    - self.service_health: Dict[agent_id, Dict[service_name, last_heartbeat]]
    All operations must include agent_id, store level uses global_agent_store, agent level uses actual agent_id.
    """
    def __init__(self):
        # agent_id -> {service_name: session}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        # Service health status management has been moved to ServiceLifecycleManager
        # agent_id -> {tool_name: tool_definition}
        self.tool_cache: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # agent_id -> {tool_name: session}
        self.tool_to_session_map: Dict[str, Dict[str, Any]] = {}
        # 长连接服务标记 - agent_id:service_name
        self.long_lived_connections: Set[str] = set()

        # 新增：生命周期状态支持
        # agent_id -> {service_name: ServiceConnectionState}
        self.service_states: Dict[str, Dict[str, ServiceConnectionState]] = {}
        # agent_id -> {service_name: ServiceStateMetadata}
        self.service_metadata: Dict[str, Dict[str, ServiceStateMetadata]] = {}

        logger.info("ServiceRegistry initialized (multi-context isolation with lifecycle support).")

    def clear(self, agent_id: str):
        """
        清空指定 agent_id 的所有注册服务和工具。
        只影响该 agent_id 下的服务、工具、会话，不影响其它 agent。
        """
        self.sessions.pop(agent_id, None)
        # 健康状态由ServiceLifecycleManager管理
        self.tool_cache.pop(agent_id, None)
        self.tool_to_session_map.pop(agent_id, None)

    def add_service(self, agent_id: str, name: str, session: Any, tools: List[Tuple[str, Dict[str, Any]]]) -> List[str]:
        """
        为指定 agent_id 注册服务及其工具。
        - agent_id: store/agent 的唯一标识
        - name: 服务名
        - session: 服务会话对象
        - tools: [(tool_name, tool_def)]
        返回实际注册的工具名列表。
        """
        if agent_id not in self.sessions:
            self.sessions[agent_id] = {}
        # service_health已废弃，由ServiceLifecycleManager管理
        if agent_id not in self.tool_cache:
            self.tool_cache[agent_id] = {}
        if agent_id not in self.tool_to_session_map:
            self.tool_to_session_map[agent_id] = {}
            
        # 只在首次注册时打印日志
        if name not in self.sessions[agent_id]:
            logger.debug(f"首次注册服务 - agent_id={agent_id}, name={name}")
        
        if name in self.sessions[agent_id]:
            logger.warning(f"Attempting to add already registered service: {name} for agent {agent_id}. Removing old service before overwriting.")
            self.remove_service(agent_id, name)
            
        self.sessions[agent_id][name] = session
        # service_health已废弃，健康状态由ServiceLifecycleManager管理
        added_tool_names = []
        for tool_name, tool_definition in tools:
            # 🆕 使用新的工具归属判断逻辑
            # 检查工具定义中的服务归属
            tool_service_name = None
            if "function" in tool_definition:
                tool_service_name = tool_definition["function"].get("service_name")
            else:
                tool_service_name = tool_definition.get("service_name")

            # 验证工具是否属于当前服务
            if tool_service_name and tool_service_name != name:
                logger.warning(f"Tool '{tool_name}' belongs to service '{tool_service_name}', not '{name}'. Skipping this tool.")
                continue

            # 检查工具名冲突
            if tool_name in self.tool_cache[agent_id]:
                existing_session = self.tool_to_session_map[agent_id].get(tool_name)
                if existing_session is not session:
                    logger.warning(f"Tool name conflict: '{tool_name}' from {name} for agent {agent_id} conflicts with existing tool. Skipping this tool.")
                    continue

            # 存储工具
            self.tool_cache[agent_id][tool_name] = tool_definition
            self.tool_to_session_map[agent_id][tool_name] = session
            added_tool_names.append(tool_name)

        logger.info(f"Service '{name}' for agent '{agent_id}' added with tools: {added_tool_names}")
        return added_tool_names

    def remove_service(self, agent_id: str, name: str) -> Optional[Any]:
        """
        移除指定 agent_id 下的服务及其所有工具。
        只影响该 agent_id，不影响其它 agent。
        """
        session = self.sessions.get(agent_id, {}).pop(name, None)
        if not session:
            logger.warning(f"Attempted to remove non-existent service: {name} for agent {agent_id}")
            return None
        # service_health已废弃，健康状态由ServiceLifecycleManager管理
        # Remove associated tools efficiently
        tools_to_remove = [tool_name for tool_name, owner_session in self.tool_to_session_map.get(agent_id, {}).items() if owner_session is session]
        for tool_name in tools_to_remove:
            if tool_name in self.tool_cache.get(agent_id, {}): del self.tool_cache[agent_id][tool_name]
            if tool_name in self.tool_to_session_map.get(agent_id, {}): del self.tool_to_session_map[agent_id][tool_name]
        logger.info(f"Service '{name}' for agent '{agent_id}' removed from registry.")
        return session

    def get_session(self, agent_id: str, name: str) -> Optional[Any]:
        """
        获取指定 agent_id 下的服务会话。
        """
        return self.sessions.get(agent_id, {}).get(name)

    def get_session_for_tool(self, agent_id: str, tool_name: str) -> Optional[Any]:
        """
        获取指定 agent_id 下工具对应的服务会话。
        """
        return self.tool_to_session_map.get(agent_id, {}).get(tool_name)

    def get_all_tools(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        获取指定 agent_id 下所有工具的定义。
        """
        all_tools = []
        for tool_name, tool_def in self.tool_cache.get(agent_id, {}).items():
            session = self.tool_to_session_map.get(agent_id, {}).get(tool_name)
            service_name = None
            for name, sess in self.sessions.get(agent_id, {}).items():
                if sess is session:
                    service_name = name
                    break
            tool_with_service = tool_def.copy()
            if "function" not in tool_with_service and isinstance(tool_with_service, dict):
                tool_with_service = {
                    "type": "function",
                    "function": tool_with_service
                }
            if "function" in tool_with_service:
                function_data = tool_with_service["function"]
                if service_name:
                    original_description = function_data.get("description", "")
                    if not original_description.endswith(f" (来自服务: {service_name})"):
                        function_data["description"] = f"{original_description} (来自服务: {service_name})"
                function_data["service_info"] = {"service_name": service_name}
            all_tools.append(tool_with_service)
        logger.info(f"Returning {len(all_tools)} tools from {len(self.get_all_service_names(agent_id))} services for agent {agent_id}")
        return all_tools

    def get_all_tool_info(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        获取指定 agent_id 下所有工具的详细信息。
        """
        tools_info = []
        for tool_name in self.tool_cache.get(agent_id, {}).keys():
            session = self.tool_to_session_map.get(agent_id, {}).get(tool_name)
            service_name = None
            for name, sess in self.sessions.get(agent_id, {}).items():
                if sess is session:
                    service_name = name
                    break
            detailed_tool = self._get_detailed_tool_info(agent_id, tool_name)
            if detailed_tool:
                detailed_tool["service_name"] = service_name
                tools_info.append(detailed_tool)
        return tools_info

    def get_connected_services(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        获取指定 agent_id 下所有已连接服务的信息。
        """
        services = []
        for name in self.get_all_service_names(agent_id):
            tools = self.get_tools_for_service(agent_id, name)
            services.append({
                "name": name,
                "tool_count": len(tools)
            })
        return services

    def get_tools_for_service(self, agent_id: str, name: str) -> List[str]:
        """
        获取指定 agent_id 下某服务的所有工具名。
        """
        session = self.sessions.get(agent_id, {}).get(name)
        logger.info(f"Getting tools for service: {name} (agent_id={agent_id})")

        # 只在调试特定问题时打印详细日志
        if logger.getEffectiveLevel() <= logging.DEBUG:
            print(f"[DEBUG][get_tools_for_service] agent_id={agent_id}, name={name}, id(session)={id(session) if session else None}")

        if not session:
            return []

        # 🆕 使用新的工具过滤逻辑：根据 session 匹配
        tools = []
        for tool_name, tool_session in self.tool_to_session_map.get(agent_id, {}).items():
            if tool_session is session:
                tools.append(tool_name)

        logger.debug(f"Found {len(tools)} tools for service {name}: {tools}")
        return tools

    def _extract_description_from_schema(self, prop_info):
        """从 schema 中提取描述信息"""
        if isinstance(prop_info, dict):
            # 优先查找 description 字段
            if 'description' in prop_info:
                return prop_info['description']
            # 其次查找 title 字段
            elif 'title' in prop_info:
                return prop_info['title']
            # 检查是否有 anyOf 或 allOf 结构
            elif 'anyOf' in prop_info:
                for item in prop_info['anyOf']:
                    if isinstance(item, dict) and 'description' in item:
                        return item['description']
            elif 'allOf' in prop_info:
                for item in prop_info['allOf']:
                    if isinstance(item, dict) and 'description' in item:
                        return item['description']

        return "无描述"

    def _extract_type_from_schema(self, prop_info):
        """从 schema 中提取类型信息"""
        if isinstance(prop_info, dict):
            if 'type' in prop_info:
                return prop_info['type']
            elif 'anyOf' in prop_info:
                # 处理 Union 类型
                types = []
                for item in prop_info['anyOf']:
                    if isinstance(item, dict) and 'type' in item:
                        types.append(item['type'])
                return '|'.join(types) if types else '未知'
            elif 'allOf' in prop_info:
                # 处理 intersection 类型
                for item in prop_info['allOf']:
                    if isinstance(item, dict) and 'type' in item:
                        return item['type']

        return "未知"

    def _get_detailed_tool_info(self, agent_id: str, tool_name: str) -> Dict[str, Any]:
        """
        获取指定 agent_id 下某工具的详细信息。
        """
        tool_def = self.tool_cache.get(agent_id, {}).get(tool_name)
        if not tool_def:
            return {}
        session = self.tool_to_session_map.get(agent_id, {}).get(tool_name)
        service_name = None
        if session:
            for name, sess in self.sessions.get(agent_id, {}).items():
                if sess is session:
                    service_name = name
                    break

        if "function" in tool_def:
            function_data = tool_def["function"]
            tool_info = {
                "name": tool_name,  # 这是存储的键名（显示名称）
                "display_name": function_data.get("display_name", tool_name),  # 用户友好的显示名称
                "description": function_data.get("description", ""),
                "service_name": service_name,
                "inputSchema": function_data.get("parameters", {}),
                "original_name": function_data.get("name", tool_name)  # FastMCP 原始名称
            }
        else:
            tool_info = {
                "name": tool_name,
                "display_name": tool_def.get("display_name", tool_name),
                "description": tool_def.get("description", ""),
                "service_name": service_name,
                "inputSchema": tool_def.get("parameters", {}),
                "original_name": tool_def.get("name", tool_name)
            }
        return tool_info

    def get_service_details(self, agent_id: str, name: str) -> Dict[str, Any]:
        """
        获取指定 agent_id 下某服务的详细信息。
        """
        if name not in self.sessions.get(agent_id, {}):
            return {}
            
        logger.info(f"Getting service details for: {name} (agent_id={agent_id})")
        session = self.sessions.get(agent_id, {}).get(name)
        
        # 只在调试特定问题时打印详细日志
        if logger.getEffectiveLevel() <= logging.DEBUG:
            print(f"[DEBUG][get_service_details] agent_id={agent_id}, name={name}, id(session)={id(session) if session else None}")
            
        tools = self.get_tools_for_service(agent_id, name)
        # service_health已废弃，使用None作为默认值
        last_heartbeat = None
        detailed_tools = []
        for tool_name in tools:
            detailed_tool = self._get_detailed_tool_info(agent_id, tool_name)
            if detailed_tool:
                detailed_tools.append(detailed_tool)
        # TODO: 添加Resources和Prompts信息收集
        # 当前版本暂时返回空值，后续版本将实现完整的资源和提示词统计

        return {
            "name": name,
            "tools": detailed_tools,
            "tool_count": len(tools),
            "tool_names": [tool["name"] for tool in detailed_tools],

            # 新增：Resources相关字段
            "resource_count": 0,  # TODO: 实现资源数量统计
            "resource_names": [],  # TODO: 实现资源名称列表
            "resource_template_count": 0,  # TODO: 实现资源模板数量统计
            "resource_template_names": [],  # TODO: 实现资源模板名称列表

            # 新增：Prompts相关字段
            "prompt_count": 0,  # TODO: 实现提示词数量统计
            "prompt_names": [],  # TODO: 实现提示词名称列表

            # 新增：能力标识
            "capabilities": ["tools"],  # TODO: 根据实际支持的功能动态更新

            # 现有字段
            "last_heartbeat": str(last_heartbeat) if last_heartbeat else "N/A",
            "connected": name in self.sessions.get(agent_id, {})
        }

    def get_all_service_names(self, agent_id: str) -> List[str]:
        """
        获取指定 agent_id 下所有已注册服务名。
        """
        return list(self.sessions.get(agent_id, {}).keys())

    def update_service_health(self, agent_id: str, name: str):
        """
        更新指定 agent_id 下某服务的心跳时间。
        ⚠️ 已废弃：此方法已被ServiceLifecycleManager替代
        """
        logger.debug(f"update_service_health is deprecated for service: {name} (agent_id={agent_id})")
        pass

    def get_last_heartbeat(self, agent_id: str, name: str) -> Optional[datetime]:
        """
        获取指定 agent_id 下某服务的最后心跳时间。
        ⚠️ 已废弃：此方法已被ServiceLifecycleManager替代
        """
        logger.debug(f"get_last_heartbeat is deprecated for service: {name} (agent_id={agent_id})")
        return None

    def has_service(self, agent_id: str, name: str) -> bool:
        """
        判断指定 agent_id 下是否存在某服务。
        """
        return name in self.sessions.get(agent_id, {})

    def get_service_config(self, agent_id: str, name: str) -> Optional[Dict[str, Any]]:
        """获取服务配置"""
        if not self.has_service(agent_id, name):
            return None
            
        # 从 orchestrator 的 mcp_config 获取配置
        from api.deps import app_state
        orchestrator = app_state.get("orchestrator")
        if orchestrator and orchestrator.mcp_config:
            return orchestrator.mcp_config.get_service_config(name)
            
        return None

    def mark_as_long_lived(self, agent_id: str, service_name: str):
        """标记服务为长连接服务"""
        service_key = f"{agent_id}:{service_name}"
        self.long_lived_connections.add(service_key)
        logger.debug(f"Marked service '{service_name}' as long-lived for agent '{agent_id}'")

    def is_long_lived_service(self, agent_id: str, service_name: str) -> bool:
        """检查服务是否为长连接服务"""
        service_key = f"{agent_id}:{service_name}"
        return service_key in self.long_lived_connections

    def get_long_lived_services(self, agent_id: str) -> List[str]:
        """获取指定Agent的所有长连接服务"""
        prefix = f"{agent_id}:"
        return [
            key[len(prefix):] for key in self.long_lived_connections
            if key.startswith(prefix)
        ]

    # === 生命周期状态管理方法 ===

    def set_service_state(self, agent_id: str, service_name: str, state: ServiceConnectionState):
        """设置服务生命周期状态"""
        if agent_id not in self.service_states:
            self.service_states[agent_id] = {}
        self.service_states[agent_id][service_name] = state
        logger.debug(f"Service {service_name} (agent {agent_id}) state set to {state.value}")

    def get_service_state(self, agent_id: str, service_name: str) -> ServiceConnectionState:
        """获取服务生命周期状态"""
        return self.service_states.get(agent_id, {}).get(service_name, ServiceConnectionState.DISCONNECTED)

    def set_service_metadata(self, agent_id: str, service_name: str, metadata: ServiceStateMetadata):
        """设置服务状态元数据"""
        if agent_id not in self.service_metadata:
            self.service_metadata[agent_id] = {}
        self.service_metadata[agent_id][service_name] = metadata

    def get_service_metadata(self, agent_id: str, service_name: str) -> Optional[ServiceStateMetadata]:
        """获取服务状态元数据"""
        return self.service_metadata.get(agent_id, {}).get(service_name)

    def remove_service_lifecycle_data(self, agent_id: str, service_name: str):
        """移除服务的生命周期数据"""
        if agent_id in self.service_states:
            self.service_states[agent_id].pop(service_name, None)
        if agent_id in self.service_metadata:
            self.service_metadata[agent_id].pop(service_name, None)
        logger.debug(f"Removed lifecycle data for service {service_name} (agent {agent_id})")

    def get_all_service_states(self, agent_id: str) -> Dict[str, ServiceConnectionState]:
        """获取指定Agent的所有服务状态"""
        return self.service_states.get(agent_id, {}).copy()

    def clear_agent_lifecycle_data(self, agent_id: str):
        """清除指定Agent的所有生命周期数据"""
        self.service_states.pop(agent_id, None)
        self.service_metadata.pop(agent_id, None)
        logger.info(f"Cleared lifecycle data for agent {agent_id}")

    def should_cache_aggressively(self, agent_id: str, service_name: str) -> bool:
        """
        判断是否应该激进缓存
        长连接服务可以更激进地缓存，因为连接稳定
        """
        return self.is_long_lived_service(agent_id, service_name)
