"""
Data models for Demiurg agents.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ScheduledTask(BaseModel):
    """Definition of a scheduled task."""
    name: str
    schedule: Union[str, Dict[str, Any]]  # Cron expression or schedule config
    task_type: str  # 'tool', 'llm_query', 'workflow', 'openai_tool', 'custom_tool'
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = None


class ScheduleConfig(BaseModel):
    """Configuration for agent scheduling."""
    enabled: bool = False
    timezone: str = "UTC"
    tasks: List[ScheduledTask] = Field(default_factory=list)
    start_on_init: bool = True  # Auto-start scheduler on agent initialization
    persist_state: bool = False  # Save/restore schedule state across restarts


class Config(BaseModel):
    """Configuration for an agent."""
    name: str = "Demiurg Agent"
    version: str = "1.0.0"
    description: str = "An AI-powered conversational agent"
    model: str = "gpt-4o-mini"
    provider: str = "openai"  # LLM provider
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: Optional[str] = None
    use_tools: bool = False  # Whether to use OpenAI function calling tools
    billing_mode: str = "builder"  # "builder" or "user" - who pays for API calls
    show_progress_indicators: bool = True  # Show progress messages for long operations
    schedule: Optional[ScheduleConfig] = None  # Optional scheduling configuration


class Message(BaseModel):
    """Structure of messages."""
    content: str = Field(..., min_length=1, max_length=10000)
    user_id: str
    conversation_id: str
    message_type: str = "user_message"
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class Response(BaseModel):
    """Structure for agent responses."""
    content: str
    agent_id: str
    conversation_id: str
    response_type: str = "agent_response"
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def dict(self, **kwargs) -> Dict[str, Any]:
        """Ensure JSON serializable output."""
        data = super().model_dump(**kwargs)
        if isinstance(data.get('timestamp'), datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        return data