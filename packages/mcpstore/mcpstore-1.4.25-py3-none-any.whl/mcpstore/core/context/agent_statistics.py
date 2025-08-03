"""
MCPStore Agent Statistics Module
Agent统计功能的实现
"""

import logging
from typing import Dict, List, Optional, Any, Union

from mcpstore.core.models.agent import AgentsSummary, AgentStatistics, AgentServiceSummary
from .types import ContextType

logger = logging.getLogger(__name__)

class AgentStatisticsMixin:
    """Agent统计混入类"""
    
    def get_agents_summary(self) -> AgentsSummary:
        """
        获取所有Agent的汇总信息（同步版本）
        
        Returns:
            AgentsSummary: Agent汇总信息
        """
        return self._sync_helper.run_async(self.get_agents_summary_async())

    async def get_agents_summary_async(self) -> AgentsSummary:
        """
        获取所有Agent的汇总信息（异步版本）
        
        Returns:
            AgentsSummary: Agent汇总信息
        """
        try:
            # 获取所有Agent ID
            all_agent_ids = self._store.orchestrator.client_manager.get_all_agent_ids()
            
            # 统计信息
            total_agents = len(all_agent_ids)
            active_agents = 0
            total_services = 0
            total_tools = 0
            
            agent_details = []
            
            for agent_id in all_agent_ids:
                try:
                    # 获取Agent统计信息
                    agent_stats = await self._get_agent_statistics(agent_id)
                    
                    if agent_stats.is_active:
                        active_agents += 1
                    
                    total_services += agent_stats.service_count
                    total_tools += agent_stats.tool_count
                    
                    agent_details.append(agent_stats)
                    
                except Exception as e:
                    logger.warning(f"Failed to get statistics for agent {agent_id}: {e}")
                    # 创建一个错误状态的统计信息
                    error_stats = AgentStatistics(
                        agent_id=agent_id,
                        service_count=0,
                        tool_count=0,
                        is_active=False,
                        last_activity=None,
                        services=[]
                    )
                    agent_details.append(error_stats)
            
            return AgentsSummary(
                total_agents=total_agents,
                active_agents=active_agents,
                total_services=total_services,
                total_tools=total_tools,
                agents=agent_details
            )
            
        except Exception as e:
            logger.error(f"Failed to get agents summary: {e}")
            return AgentsSummary(
                total_agents=0,
                active_agents=0,
                total_services=0,
                total_tools=0,
                agents=[]
            )

    async def _get_agent_statistics(self, agent_id: str) -> AgentStatistics:
        """
        获取单个Agent的详细统计信息
        
        Args:
            agent_id: Agent ID
            
        Returns:
            AgentStatistics: Agent统计信息
        """
        try:
            # 获取Agent的所有client
            client_ids = self._store.orchestrator.client_manager.get_agent_clients(agent_id)
            
            # 统计服务和工具
            services = []
            total_tools = 0
            is_active = False
            last_activity = None
            
            for client_id in client_ids:
                try:
                    # 获取client配置
                    client_config = self._store.orchestrator.client_manager.get_client_config(client_id)
                    if not client_config:
                        continue
                    
                    # 检查client是否活跃
                    client_status = await self._store.orchestrator.registry.get_client_status(client_id)
                    if client_status.get("is_active", False):
                        is_active = True
                        
                    # 更新最后活动时间
                    client_last_activity = client_status.get("last_activity")
                    if client_last_activity:
                        if not last_activity or client_last_activity > last_activity:
                            last_activity = client_last_activity
                    
                    # 统计服务
                    for service_name, service_config in client_config.get("mcpServers", {}).items():
                        try:
                            # 获取服务的工具数量
                            service_tools = await self._store.orchestrator.registry.get_service_tools(
                                service_name, client_id
                            )
                            tool_count = len(service_tools) if service_tools else 0
                            total_tools += tool_count
                            
                            # 获取服务状态
                            service_status = await self._store.orchestrator.registry.get_service_status(
                                service_name, client_id
                            )
                            
                            service_summary = AgentServiceSummary(
                                name=service_name,
                                tool_count=tool_count,
                                status=service_status.get("status", "unknown"),
                                client_id=client_id
                            )
                            services.append(service_summary)
                            
                        except Exception as e:
                            logger.warning(f"Failed to get service {service_name} stats for agent {agent_id}: {e}")
                            # 添加错误状态的服务
                            error_service = AgentServiceSummary(
                                name=service_name,
                                tool_count=0,
                                status="error",
                                client_id=client_id
                            )
                            services.append(error_service)
                            
                except Exception as e:
                    logger.warning(f"Failed to process client {client_id} for agent {agent_id}: {e}")
            
            return AgentStatistics(
                agent_id=agent_id,
                service_count=len(services),
                tool_count=total_tools,
                is_active=is_active,
                last_activity=last_activity,
                services=services
            )
            
        except Exception as e:
            logger.error(f"Failed to get statistics for agent {agent_id}: {e}")
            return AgentStatistics(
                agent_id=agent_id,
                service_count=0,
                tool_count=0,
                is_active=False,
                last_activity=None,
                services=[]
            )
