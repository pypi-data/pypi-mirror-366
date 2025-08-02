"""
Tool integration utilities for Demiurg agents.

Supports multiple tool providers (Composio, MCP, etc.)
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..exceptions import ToolError

logger = logging.getLogger(__name__)


class ToolProvider(ABC):
    """Abstract base class for tool providers."""
    
    @abstractmethod
    def init_tools(
        self, 
        user_id: Optional[str] = None,
        enabled_tools: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Initialize and return available tools."""
        pass
    
    @abstractmethod
    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a single tool and return results."""
        pass


class ComposioProvider(ToolProvider):
    """Composio tool provider implementation with authentication support."""
    
    def __init__(self):
        """Initialize Composio provider."""
        try:
            from composio import Composio
            # Import the OpenAI provider if available
            try:
                from composio_openai import OpenAIProvider as ComposioOpenAIProvider
                self.provider = ComposioOpenAIProvider()
                self.client = Composio(provider=self.provider)
                logger.debug("Initialized Composio with OpenAI provider")
            except ImportError:
                # Fall back to default provider
                self.client = Composio()
                self.provider = None
                logger.debug("Initialized Composio with default provider")
            
            self.available = True
            self._connected_accounts = {}  # Cache for connected accounts
        except ImportError:
            logger.warning("Composio not available")
            self.client = None
            self.provider = None
            self.available = False
            self._connected_accounts = {}
    
    def init_tools(
        self, 
        user_id: Optional[str] = None,
        enabled_tools: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Initialize Composio tools, checking for existing connections."""
        if not self.available:
            return []
        
        try:
            # Get user ID
            if user_id is None:
                user_id = os.getenv("COMPOSIO_USER_ID", "default")
            
            # Get enabled tools list
            if enabled_tools is None:
                tools_env = os.getenv("COMPOSIO_TOOLS", "")
                enabled_tools = [t.strip() for t in tools_env.split(",") if t.strip()]
            
            if not enabled_tools:
                logger.debug("No Composio tools configured")
                return []
            
            # Check which toolkits have active connections
            connected_toolkits = []
            for toolkit in enabled_tools:
                if self.check_connection(user_id, toolkit):
                    connected_toolkits.append(toolkit)
                    logger.debug(f"Found existing connection for {toolkit}")
                else:
                    logger.warning(f"No active connection found for {toolkit}")
            
            if not connected_toolkits:
                logger.warning(f"No connected toolkits found for user {user_id}")
                return []
            
            # Get tools only for connected toolkits
            tools = self.client.tools.get(
                user_id=user_id,
                toolkits=connected_toolkits,
                limit=1000  # Ensure we get all available tools (default is 20)
            )
            
            logger.debug(f"Loaded {len(tools)} Composio tools from {len(connected_toolkits)} connected toolkits")
            return tools
            
        except Exception as e:
            logger.error(f"Failed to initialize Composio tools: {e}")
            raise ToolError(f"Composio initialization failed: {str(e)}")
    
    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a Composio tool."""
        if not self.available:
            raise ToolError("Composio not available")
        
        if user_id is None:
            user_id = os.getenv("COMPOSIO_USER_ID", "default")
        
        try:
            result = self.client.tools.execute(
                slug=tool_name,
                arguments=arguments,
                user_id=user_id
            )
            return result
        except Exception as e:
            logger.error(f"Error executing Composio tool {tool_name}: {e}")
            raise ToolError(f"Tool execution failed: {str(e)}")
    
    def handle_tool_calls(self, response: Any, user_id: str) -> Any:
        """Handle tool calls from OpenAI response using Composio's built-in method."""
        if not self.available:
            raise ToolError("Composio not available")
        
        if not self.provider:
            raise ToolError("Composio OpenAI provider not available")
        
        try:
            # Use Composio's built-in handle_tool_calls method
            result = self.provider.handle_tool_calls(response=response, user_id=user_id)
            return result
        except Exception as e:
            logger.error(f"Error handling tool calls: {e}")
            raise ToolError(f"Tool execution failed: {str(e)}")
    
    def check_connection(
        self,
        user_id: str,
        toolkit: str
    ) -> bool:
        """Check if user has an active connection for a toolkit."""
        if not self.available:
            return False
        
        try:
            # Check cache first
            cache_key = f"{user_id}:{toolkit}"
            if cache_key in self._connected_accounts:
                return True
            
            # Check with Composio
            connections = self.client.connected_accounts.list(
                user_ids=[user_id]
            )
            
            for conn in connections.items:
                if hasattr(conn, 'toolkit') and hasattr(conn.toolkit, 'slug') and conn.toolkit.slug.upper() == toolkit.upper():
                    self._connected_accounts[cache_key] = conn
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking connection: {e}")
            return False
    
    def initiate_connection(
        self,
        user_id: str,
        auth_config_id: str
    ) -> Dict[str, Any]:
        """Initiate Composio connection for user authorization."""
        if not self.available:
            raise ToolError("Composio not available")
        
        try:
            connection_request = self.client.connected_accounts.initiate(
                user_id=user_id,
                auth_config_id=auth_config_id
            )
            
            return {
                "id": getattr(connection_request, 'id', None),
                "redirect_url": connection_request.redirect_url,
                "connection_request": connection_request,
                "status": "pending"
            }
        except Exception as e:
            logger.error(f"Failed to initiate connection: {e}")
            raise ToolError(f"Connection initiation failed: {str(e)}")
    
    def wait_for_connection(
        self,
        connection_request,
        timeout: int = 300
    ) -> bool:
        """Wait for user to complete authorization."""
        try:
            # This is a blocking call that waits for the user to authorize
            connected_account = connection_request.wait_for_connection(timeout=timeout)
            
            if connected_account:
                # Cache the connection
                user_id = getattr(connected_account, 'user_id', None)
                app_id = getattr(connected_account, 'appUniqueId', None)
                if user_id and app_id:
                    cache_key = f"{user_id}:{app_id}"
                    self._connected_accounts[cache_key] = connected_account
                
                return True
            return False
        except Exception as e:
            logger.error(f"Connection authorization failed: {e}")
            return False
    
    def get_connection_status(
        self,
        user_id: str,
        toolkit: str
    ) -> Dict[str, Any]:
        """Get detailed connection status for a user and toolkit."""
        status = {
            "connected": False,
            "toolkit": toolkit,
            "user_id": user_id,
            "connection_id": None,
            "needs_reauth": False
        }
        
        if not self.available:
            status["error"] = "Composio not available"
            return status
        
        try:
            cache_key = f"{user_id}:{toolkit}"
            
            # Check cache
            if cache_key in self._connected_accounts:
                conn = self._connected_accounts[cache_key]
                status["connected"] = True
                status["connection_id"] = getattr(conn, 'id', None)
                return status
            
            # Check with Composio
            connections = self.client.connected_accounts.list(
                user_ids=[user_id]
            )
            
            for conn in connections.items:
                if hasattr(conn, 'toolkit') and hasattr(conn.toolkit, 'slug') and conn.toolkit.slug.upper() == toolkit.upper():
                    status["connected"] = True
                    status["connection_id"] = getattr(conn, 'id', None)
                    self._connected_accounts[cache_key] = conn
                    return status
            
            return status
        except Exception as e:
            status["error"] = str(e)
            return status


# Registry of tool providers
_PROVIDERS: Dict[str, type] = {
    "composio": ComposioProvider,
}

# Cached provider instances
_provider_instances: Dict[str, ToolProvider] = {}


def get_tool_provider(name: str = "composio") -> ToolProvider:
    """
    Get a tool provider instance by name.
    
    Args:
        name: Provider name (e.g., "composio", "mcp")
        
    Returns:
        ToolProvider instance
        
    Raises:
        ToolError: If provider not found
    """
    if name not in _PROVIDERS:
        available = ", ".join(_PROVIDERS.keys())
        raise ToolError(
            f"Tool provider '{name}' not found. Available providers: {available}"
        )
    
    # Return cached instance if available
    if name not in _provider_instances:
        provider_class = _PROVIDERS[name]
        _provider_instances[name] = provider_class()
    
    return _provider_instances[name]


def register_tool_provider(name: str, provider_class: type):
    """
    Register a new tool provider.
    
    Args:
        name: Provider name
        provider_class: Provider class (must inherit from ToolProvider)
    """
    if not issubclass(provider_class, ToolProvider):
        raise ValueError("Provider class must inherit from ToolProvider")
    
    _PROVIDERS[name] = provider_class
    logger.debug(f"Registered tool provider: {name}")


# High-level convenience functions

def init_tools(
    provider: str = "composio",
    user_id: Optional[str] = None,
    enabled_tools: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Initialize tools using the specified provider.
    
    Args:
        provider: Tool provider name
        user_id: User ID for provider
        enabled_tools: List of tools to enable
        
    Returns:
        List of tool definitions for LLM
    """
    tool_provider = get_tool_provider(provider)
    return tool_provider.init_tools(user_id, enabled_tools)


async def execute_tools(
    tool_calls: List[Any],
    provider: str = "composio",
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Execute tool calls using the specified provider.
    
    Args:
        tool_calls: List of tool calls from LLM
        provider: Tool provider name
        user_id: User ID for provider
        
    Returns:
        List of tool results with 'tool_call_id' and 'output'
    """
    tool_provider = get_tool_provider(provider)
    results = []
    
    for tool_call in tool_calls:
        try:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            logger.debug(f"Executing tool: {function_name} via {provider}")
            
            # Execute via provider
            result = await tool_provider.execute_tool(
                tool_name=function_name,
                arguments=arguments,
                user_id=user_id
            )
            
            results.append({
                "tool_call_id": tool_call.id,
                "output": result
            })
            
        except Exception as e:
            logger.error(f"Error executing tool {function_name}: {e}")
            results.append({
                "tool_call_id": tool_call.id,
                "output": {"error": str(e)}
            })
    
    return results


def format_tool_results(
    tool_results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Format tool results for inclusion in LLM messages.
    
    Args:
        tool_results: List of tool execution results
        
    Returns:
        List of formatted messages for LLM
    """
    messages = []
    
    for result in tool_results:
        messages.append({
            "role": "tool",
            "tool_call_id": result["tool_call_id"],
            "content": json.dumps(result["output"])
        })
    
    return messages