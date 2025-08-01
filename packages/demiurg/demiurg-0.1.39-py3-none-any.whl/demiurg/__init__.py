"""
Demiurg - AI Agent Framework

A flexible framework for building AI agents with support for multiple LLM providers
and seamless integration with the Demiurg platform.
"""

__version__ = "0.1.28"

# Public API imports
from .agent import Agent
from .scheduled_agent import ScheduledAgent
from .models import Config, Message, Response, ScheduleConfig, ScheduledTask
from .messaging import (
    send_text_message as send_text,
    send_file_message as send_file, 
    get_conversation_history,
    register_agent,
    get_messaging_client,
    MessagingClient,
)
from .providers import get_provider, Provider, OpenAIProvider
from .tools import Composio

__all__ = [
    "Agent",
    "ScheduledAgent",
    "Config", 
    "Message",
    "Response",
    "ScheduleConfig",
    "ScheduledTask",
    "send_text",
    "send_file",
    "get_conversation_history",
    "register_agent",
    "get_messaging_client",
    "MessagingClient",
    "get_provider",
    "Provider",
    "OpenAIProvider",
    "Composio",
]