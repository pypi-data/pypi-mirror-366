from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AgentStatus(BaseModel):
    id: str
    name: str
    status: str  # "running", "idle", "error", "stopped"
    last_seen: str
    resources: Dict[str, Any] = {}


class LogEntry(BaseModel):
    timestamp: str
    level: str  # "INFO", "WARNING", "ERROR", "DEBUG"
    message: str
    source: str
    metadata: Dict[str, Any] = {}


class DashboardStats(BaseModel):
    ray_cluster: Dict[str, Any] = {}
    backend: Dict[str, Any] = {}
    connected_users: int = 0
    active_jobs: int = 0
    total_plugins: int = 0


class PluginInfo(BaseModel):
    name: str
    version: str
    category: str
    status: str
    last_run: Optional[str] = None


class JobInfo(BaseModel):
    id: str
    plugin_name: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    progress: float = 0.0
    logs: List[LogEntry] = []


class ConfigResponse(BaseModel):
    config: Dict[str, Any]
    file_path: str
    last_modified: Optional[str] = None


class ConfigUpdateRequest(BaseModel):
    config: Dict[str, Any]
