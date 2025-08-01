"""
本地 MCP 服务管理器
解决 FastAPI 环境下无法启动本地命令服务的问题
"""

import asyncio
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

try:
    import psutil
except ImportError:
    psutil = None
import tempfile

logger = logging.getLogger(__name__)

@dataclass
class LocalServiceProcess:
    """本地服务进程信息"""
    name: str
    process: subprocess.Popen
    config: Dict[str, Any]
    start_time: float
    pid: int
    status: str = "running"
    restart_count: int = 0
    last_health_check: float = 0

class LocalServiceManager:
    """本地 MCP 服务管理器"""
    
    def __init__(self, base_work_dir: str = None):
        self.processes: Dict[str, LocalServiceProcess] = {}
        self.base_work_dir = Path(base_work_dir or os.getcwd())
        self.temp_dir = Path(tempfile.gettempdir()) / "mcpstore_local_services"
        self.temp_dir.mkdir(exist_ok=True)
        
        # 健康检查配置
        self.health_check_interval = 30  # 30秒
        self.max_restart_attempts = 3
        self.restart_delay = 5  # 5秒
        
        # 启动健康检查任务
        self._health_check_task = None
        # 延迟启动健康监控，避免在没有事件循环时创建任务
        self._monitor_started = False
    
    def _start_health_monitor(self):
        """启动健康监控任务"""
        try:
            # 检查是否有运行的事件循环
            loop = asyncio.get_running_loop()
            if self._health_check_task is None or self._health_check_task.done():
                self._health_check_task = asyncio.create_task(self._health_monitor_loop())
                self._monitor_started = True
        except RuntimeError:
            # 没有运行的事件循环，延迟启动
            self._monitor_started = False
    
    def _ensure_health_monitor_started(self):
        """确保健康监控已启动"""
        if not self._monitor_started:
            self._start_health_monitor()

    async def _health_monitor_loop(self):
        """健康监控循环"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._check_all_services_health()
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    async def _check_all_services_health(self):
        """检查所有服务健康状态"""
        for service_name, service_proc in list(self.processes.items()):
            try:
                if not self._is_process_alive(service_proc):
                    logger.warning(f"Service {service_name} is not running, attempting restart...")
                    await self._restart_service(service_name)
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
    
    def _is_process_alive(self, service_proc: LocalServiceProcess) -> bool:
        """检查进程是否存活"""
        try:
            # 检查进程是否存在
            if service_proc.process.poll() is not None:
                return False
            
            # 使用 psutil 进行更详细的检查（如果可用）
            if psutil:
                try:
                    proc = psutil.Process(service_proc.pid)
                    return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
                except psutil.NoSuchProcess:
                    return False
            else:
                # 如果没有 psutil，使用基本检查
                return True
                
        except Exception as e:
            logger.debug(f"Process check error: {e}")
            return False
    
    async def start_local_service(self, name: str, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        启动本地 MCP 服务

        Args:
            name: 服务名称
            config: 服务配置，包含 command, args, env, working_dir 等

        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 确保健康监控已启动
            self._ensure_health_monitor_started()
            # 检查是否已经运行
            if name in self.processes and self._is_process_alive(self.processes[name]):
                return True, f"Service {name} is already running"
            
            # 验证配置
            if "command" not in config:
                return False, "Missing required 'command' field"
            
            # 准备启动参数
            command = config["command"]
            args = config.get("args", [])
            env = self._prepare_environment(config.get("env", {}))
            working_dir = self._resolve_working_dir(config.get("working_dir"))
            
            # 构建完整命令
            full_command = [command] + args
            
            logger.info(f"Starting local service {name}: {' '.join(full_command)}")
            logger.debug(f"Working directory: {working_dir}")
            logger.debug(f"Environment: {env}")
            
            # 启动进程
            process = subprocess.Popen(
                full_command,
                cwd=working_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 等待一小段时间确保进程启动
            await asyncio.sleep(1)
            
            # 检查进程是否成功启动
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                error_msg = f"Process failed to start. Exit code: {process.returncode}"
                if stderr:
                    error_msg += f"\nStderr: {stderr}"
                return False, error_msg
            
            # 记录进程信息
            service_proc = LocalServiceProcess(
                name=name,
                process=process,
                config=config,
                start_time=time.time(),
                pid=process.pid
            )
            
            self.processes[name] = service_proc
            
            logger.info(f"Local service {name} started successfully (PID: {process.pid})")
            return True, f"Service started successfully (PID: {process.pid})"
            
        except Exception as e:
            logger.error(f"Failed to start local service {name}: {e}")
            return False, str(e)
    
    def _prepare_environment(self, custom_env: Dict[str, str]) -> Dict[str, str]:
        """准备环境变量"""
        # 🔧 修改：支持独立环境配置
        try:
            # 尝试获取独立配置管理器
            from mcpstore.core.standalone_config import get_global_config
            config_manager = get_global_config()

            if config_manager and config_manager.config.isolated_environment:
                # 使用独立环境配置
                env = config_manager.get_isolated_environment(custom_env)
                logger.info("Using isolated environment from standalone config")
            else:
                # 使用传统环境继承
                env = os.environ.copy()
                env.update(custom_env)
                logger.debug("Using inherited environment variables")
        except Exception as e:
            # 回退到传统方式
            logger.warning(f"Failed to use standalone config, falling back to inherited env: {e}")
            env = os.environ.copy()
            env.update(custom_env)

        # 确保 Python 路径正确
        if "PYTHONPATH" not in env:
            env["PYTHONPATH"] = str(self.base_work_dir)
        else:
            env["PYTHONPATH"] = f"{self.base_work_dir}:{env['PYTHONPATH']}"

        return env
    
    def _resolve_working_dir(self, working_dir: Optional[str]) -> str:
        """解析工作目录"""
        if working_dir:
            # 如果是相对路径，相对于 base_work_dir
            work_path = Path(working_dir)
            if not work_path.is_absolute():
                work_path = self.base_work_dir / work_path
            return str(work_path.resolve())
        else:
            return str(self.base_work_dir)
    
    async def stop_local_service(self, name: str) -> Tuple[bool, str]:
        """停止本地服务"""
        try:
            if name not in self.processes:
                return False, f"Service {name} not found"
            
            service_proc = self.processes[name]
            
            # 尝试优雅关闭
            try:
                service_proc.process.terminate()
                
                # 等待进程结束
                try:
                    service_proc.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # 强制杀死
                    service_proc.process.kill()
                    service_proc.process.wait()
                
                logger.info(f"Local service {name} stopped successfully")
                
            except Exception as e:
                logger.warning(f"Error stopping service {name}: {e}")
            
            # 清理记录
            del self.processes[name]
            return True, "Service stopped successfully"
            
        except Exception as e:
            logger.error(f"Failed to stop local service {name}: {e}")
            return False, str(e)
    
    async def _restart_service(self, name: str) -> bool:
        """重启服务"""
        try:
            if name not in self.processes:
                return False
            
            service_proc = self.processes[name]
            
            # 检查重启次数
            if service_proc.restart_count >= self.max_restart_attempts:
                logger.error(f"Service {name} exceeded max restart attempts")
                service_proc.status = "failed"
                return False
            
            # 停止服务
            await self.stop_local_service(name)
            
            # 等待一段时间
            await asyncio.sleep(self.restart_delay)
            
            # 重新启动
            success, message = await self.start_local_service(name, service_proc.config)
            
            if success:
                self.processes[name].restart_count = service_proc.restart_count + 1
                logger.info(f"Service {name} restarted successfully (attempt {service_proc.restart_count + 1})")
                return True
            else:
                logger.error(f"Failed to restart service {name}: {message}")
                return False
                
        except Exception as e:
            logger.error(f"Error restarting service {name}: {e}")
            return False
    
    def get_service_status(self, name: str) -> Dict[str, Any]:
        """获取服务状态"""
        if name not in self.processes:
            return {"status": "not_found"}
        
        service_proc = self.processes[name]
        is_alive = self._is_process_alive(service_proc)
        
        return {
            "status": "running" if is_alive else "stopped",
            "pid": service_proc.pid,
            "start_time": service_proc.start_time,
            "restart_count": service_proc.restart_count,
            "uptime": time.time() - service_proc.start_time if is_alive else 0
        }
    
    def list_services(self) -> Dict[str, Dict[str, Any]]:
        """列出所有服务状态"""
        return {name: self.get_service_status(name) for name in self.processes}
    
    async def cleanup(self):
        """清理所有服务"""
        logger.info("Cleaning up local services...")
        
        # 停止健康监控
        if self._health_check_task:
            self._health_check_task.cancel()
        
        # 停止所有服务
        for name in list(self.processes.keys()):
            await self.stop_local_service(name)
        
        logger.info("Local service cleanup completed")

# 全局实例
_local_service_manager: Optional[LocalServiceManager] = None

def get_local_service_manager() -> LocalServiceManager:
    """获取全局本地服务管理器实例"""
    global _local_service_manager
    if _local_service_manager is None:
        _local_service_manager = LocalServiceManager()
    return _local_service_manager
