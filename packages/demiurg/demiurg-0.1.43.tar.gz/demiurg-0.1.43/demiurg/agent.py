"""
Base Agent class for Demiurg framework.
"""

import base64
import json
import logging
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

# FastAPI is optional - only needed if using with FastAPI server
try:
    from fastapi.responses import JSONResponse
except ImportError:
    JSONResponse = None

# Type hints
if TYPE_CHECKING:
    from .tools import Composio

from .providers.base import Provider

from .exceptions import DemiurgError
from .messaging import (
    MessagingClient,
    enqueue_message_for_processing,
    get_messaging_client,
    send_text_message,
    send_file_message,
)
from .models import Config, Message, Response
from .providers import get_provider
from .utils.files import (
    create_file_content,
    download_file,
    get_file_info,
    get_file_type,
    is_file_message,
)
from .utils.tools import init_tools, get_tool_provider
from .tool_registry import ToolRegistry, ToolCategory

logger = logging.getLogger(__name__)


class Agent:
    """
    Base agent class for building AI agents.
    
    This class provides the core functionality for:
    - Processing messages with LLM providers
    - Managing tool integrations
    - Handling file uploads and downloads
    - Managing conversations and message history
    """
    
    def __init__(
        self,
        provider: Optional[Union[str, 'Provider']] = None,
        composio: Optional['Composio'] = None,
        config: Optional[Config] = None,
        system_prompt: Optional[str] = None,
        agent_id: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        messaging_enabled: bool = True,
        billing: Optional[str] = None,
        use_tools: Optional[bool] = None,
        show_progress_indicators: Optional[bool] = None,
    ):
        """
        Initialize the agent.
        
        Args:
            provider: LLM provider name or instance
            composio: Composio configuration for tools
            config: Agent configuration
            system_prompt: System prompt for the agent
            agent_id: Unique agent identifier
            api_key: API key for the provider
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            messaging_enabled: Enable messaging features
            billing: Billing mode ('builder' or 'user')
            use_tools: Enable tool usage
            show_progress_indicators: Show progress indicators for long operations
        """
        # Store provider instance if provided
        self._provider_instance = provider if isinstance(provider, Provider) else None
        self._composio_config = composio
        
        # Create default config if not provided
        if config is None:
            config = Config()
        
        # Override config with provided parameters
        if provider and isinstance(provider, str):
            config.provider = provider
        if model is not None:
            config.model = model
        if temperature is not None:
            config.temperature = temperature
        if max_tokens is not None:
            config.max_tokens = max_tokens
        if billing is not None:
            config.billing_mode = billing
        if use_tools is not None:
            config.use_tools = use_tools
        if show_progress_indicators is not None:
            config.show_progress_indicators = show_progress_indicators
        
        # Store configuration
        self.config = config
        # Use system_prompt from parameters, then config, then default
        self.system_prompt = system_prompt or config.system_prompt or self._get_default_system_prompt()
        self.agent_id = agent_id or f"agent_{int(time.time())}"
        
        # Store API key if provided
        if api_key:
            os.environ[f"{config.provider.upper()}_API_KEY"] = api_key
        
        # Setup Composio if provided
        if self._composio_config is not None:
            from .tools import Composio
            if isinstance(self._composio_config, Composio):
                self._setup_composio(self._composio_config)
        
        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        
        # Store composio toolkits for OAuth tool
        self._composio_toolkits = []
        if self._composio_config is not None and hasattr(self._composio_config, 'toolkits'):
            self._composio_toolkits = self._composio_config.toolkits
        
        # Initialize tools
        self.tools = []
        self.tool_provider = None
        self._init_tools()
        
        # Custom tool handlers
        self.custom_tool_handlers = {}
        
        # Register OpenAI built-in tools if enabled
        if self.config.use_tools and self.config.provider == "openai":
            from .tools.openai_tools import OPENAI_TOOLS
            for tool in OPENAI_TOOLS:
                self.tool_registry.register_tool(
                    tool,
                    ToolCategory.MODEL_PROVIDER,
                    {"provider": "openai"}
                )
        
        # Register Composio OAuth connection tool if Composio is configured
        if self._composio_toolkits:
            self._register_oauth_connection_tool()
        
        # Initialize provider
        self._init_provider()
        
        # Setup messaging and file directory
        self.file_cache_dir = Path("/tmp/agent_files")
        self.file_cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize messaging client
        if messaging_enabled:
            self.messaging_client = get_messaging_client()
            self.messaging_enabled = True
        else:
            self.messaging_enabled = False
            self.messaging_client = None
        
        # Store current conversation ID for file sending
        self.current_conversation_id: Optional[str] = None
        
        logger.info(f"Initialized {self.config.name} v{self.config.version}")
        logger.info(f"Provider: {self.config.provider}")
        logger.info(f"Tools: {len(self.tools)} available")
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the agent."""
        base_prompt = f"""You are {self.config.name}, a helpful AI assistant.
{self.config.description}
You should:
- Be helpful, polite, and professional
- Provide accurate and relevant information
- Ask for clarification when needed
- Use available tools when appropriate"""
        
        # Add version info if available
        if self.config.version and self.config.version != "1.0.0":
            base_prompt += f"\n\nVersion: {self.config.version}"
        
        return base_prompt
    
    def _register_oauth_connection_tool(self):
        """Register the OAuth connection tool for Composio services."""
        tool_def = {
            "type": "function",
            "function": {
                "name": "connect_service", 
                "description": "Connect to an external service when authorization is needed. Use this when a user wants to use a service (like Twitter, GitHub, etc.) but hasn't connected it yet.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service": {
                            "type": "string",
                            "enum": self._composio_toolkits,
                            "description": f"The service to connect. Available: {', '.join(self._composio_toolkits)}"
                        }
                    },
                    "required": ["service"]
                }
            }
        }
        
        # Register the tool
        self.register_custom_tool(tool_def, self._handle_connect_service)
        logger.info(f"Registered OAuth connection tool for services: {', '.join(self._composio_toolkits)}")
    
    async def _handle_connect_service(self, service: str) -> str:
        """Handle the connect_service tool call."""
        # Validate service
        if service not in self._composio_toolkits:
            return f"Service '{service}' is not configured for this agent. Available services: {', '.join(self._composio_toolkits)}"
        
        # Check if we have the current message context
        if not hasattr(self, '_current_message') or not self._current_message:
            return "Unable to initiate connection without message context. Please try again."
        
        # Use the existing OAuth flow handler
        try:
            await self.handle_composio_auth_in_conversation(
                self._current_message,
                service
            )
            return f"I've sent you a link to connect your {service} account. Please authorize access and then send me another message to continue!"
        except Exception as e:
            logger.error(f"Error initiating OAuth flow for {service}: {e}")
            return f"Failed to initiate connection for {service}. Please try again later."
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt."""
        self.system_prompt = prompt
        logger.info("Updated system prompt")
    
    def get_system_prompt(self) -> str:
        """Get the current system prompt."""
        return self.system_prompt
    
    def use_composio(self, composio: 'Composio'):
        """Configure Composio for tool usage."""
        self._setup_composio(composio)
        # Reinitialize tools with new configuration
        self._init_tools()
        
        # Re-register managed provider tools
        if self.tools:
            for tool in self.tools:
                self.tool_registry.register_tool(
                    tool,
                    ToolCategory.MANAGED_PROVIDER,
                    {"provider": self.tool_provider}
                )
    
    def set_provider(self, provider: Union[str, 'Provider'], api_key: Optional[str] = None):
        """Change the LLM provider."""
        if api_key:
            os.environ[f"{provider.upper()}_API_KEY"] = api_key
        
        if isinstance(provider, str):
            self.config.provider = provider
            self._provider_instance = None
        else:
            self._provider_instance = provider
            self.config.provider = provider.__class__.__name__.lower().replace('provider', '')
        
        # Reinitialize provider
        self._init_provider()
    
    def _setup_composio(self, composio: 'Composio'):
        """Setup Composio configuration from Composio instance."""
        # Set environment variables
        os.environ["TOOL_PROVIDER"] = "composio"
        os.environ["COMPOSIO_TOOLS"] = ",".join(composio.toolkits)
        
        # Load auth configs from file
        self.composio_auth_configs = self._load_composio_auth_file(composio.auth_file)
        
        logger.info(f"Configured Composio with toolkits: {', '.join(composio.toolkits)}")
    
    def _load_composio_auth_file(self, auth_file: str) -> Dict[str, str]:
        """Load Composio auth configs from file."""
        configs = {}
        try:
            with open(auth_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        toolkit, auth_id = line.split('=', 1)
                        configs[toolkit.strip()] = auth_id.strip()
                        # Also set as environment variable for SDK compatibility
                        os.environ[f"COMPOSIO_AUTH_CONFIG_{toolkit.strip()}"] = auth_id.strip()
            logger.info(f"Loaded {len(configs)} Composio auth configs from {auth_file}")
        except FileNotFoundError:
            logger.warning(f"Composio auth file '{auth_file}' not found")
        except Exception as e:
            logger.error(f"Error loading Composio auth configs: {e}")
        return configs
    
    def _init_provider(self):
        """Initialize LLM provider."""
        try:
            if self._provider_instance:
                # Use provided instance
                self.provider = self._provider_instance
                self.provider_available = True
                # Update config to match provider
                if hasattr(self.provider, '__class__'):
                    provider_name = self.provider.__class__.__name__.lower().replace('provider', '')
                    self.config.provider = provider_name
                # Update billing mode if provider supports it
                if hasattr(self.provider, 'billing_mode'):
                    self.provider.billing_mode = self.config.billing_mode
            else:
                # Create from config
                if self.config.provider == "openai":
                    from .providers import OpenAIProvider
                    self.provider = OpenAIProvider(billing_mode=self.config.billing_mode)
                else:
                    self.provider = get_provider(self.config.provider)
                self.provider_available = True
        except Exception as e:
            logger.warning(f"Provider '{self.config.provider}' initialization failed: {e}")
            self.provider = None
            self.provider_available = False
    
    def _init_tools(self, user_id: Optional[str] = None):
        """Initialize tools."""
        try:
            # Try to initialize tools with configured provider
            tool_provider_name = os.getenv("TOOL_PROVIDER", "composio")
            self.tools = init_tools(provider=tool_provider_name, user_id=user_id)
            
            # Always set tool_provider based on configuration, not on tools availability
            # For Composio, tools may be empty initially until users connect services
            self.tool_provider = tool_provider_name
            
            # Register managed provider tools in the registry
            if self.tools:
                for tool in self.tools:
                    self.tool_registry.register_tool(
                        tool,
                        ToolCategory.MANAGED_PROVIDER,
                        {"provider": tool_provider_name}
                    )
                logger.info(f"Loaded {len(self.tools)} tools via {tool_provider_name}")
            else:
                logger.info(f"Tool provider '{tool_provider_name}' configured, awaiting connections")
            
        except Exception as e:
            logger.warning(f"Failed to load tools: {e}")
            self.tools = []
            self.tool_provider = None
        
        # Store composio auth settings if available
        self.composio_auth_configs = {}
        if self.tool_provider == "composio":
            # Load auth configs from environment
            for key, value in os.environ.items():
                if key.startswith("COMPOSIO_AUTH_CONFIG_"):
                    toolkit = key.replace("COMPOSIO_AUTH_CONFIG_", "")
                    self.composio_auth_configs[toolkit] = value
                    logger.info(f"Found auth config for {toolkit}: {value}")
    
    def register_custom_tool(self, tool_def: Dict[str, Any], handler: Any):
        """
        Register a custom tool with the agent.
        
        Args:
            tool_def: Tool definition in OpenAI function format
            handler: Async function to handle tool calls
        """
        tool_name = tool_def["function"]["name"]
        
        # Register in the tool registry
        self.tool_registry.register_tool(
            tool_def,
            ToolCategory.CUSTOM,
            {"handler": handler}
        )
        
        # Store handler for execution
        self.custom_tool_handlers[tool_name] = handler
        
        logger.info(f"Registered custom tool: {tool_name}")
    
    async def handle_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main message handler that queues messages for sequential processing.
        
        Args:
            payload: The incoming message payload
            
        Returns:
            Response dictionary or JSONResponse object
        """
        try:
            # Validate payload first
            message = Message(**payload)
            
            logger.info(f"Received {message.message_type} from {message.user_id} for conversation {message.conversation_id}")
            
            # Enqueue the message for sequential processing
            await enqueue_message_for_processing(
                message.conversation_id,
                self._process_message_internal,
                payload
            )
            
            # Return immediate acknowledgment
            return {
                "status": "queued",
                "message": "Message queued for processing",
                "conversation_id": message.conversation_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            error_response = {
                "error": str(e),
                "status": "error"
            }
            
            # Return JSONResponse if available (FastAPI context)
            if JSONResponse:
                return JSONResponse(content=error_response, status_code=400)
            return error_response
    
    async def _process_message_internal(self, payload: Dict[str, Any]) -> None:
        """
        Internal message processor that runs in the queue.
        
        This method handles the actual message processing and sends
        the response back through the messaging system.
        """
        try:
            message = Message(**payload)
            
            # Ensure messaging is set up for the conversation
            if self.messaging_enabled and self.messaging_client:
                # Use the existing client but ensure it has the right conversation
                self.messaging_client.conversation_id = message.conversation_id
            
            # Process message - history formatting handles file messages
            response_content = await self.process_message(message)
            
            # Create response
            response = Response(
                content=response_content,
                agent_id=self.agent_id,
                conversation_id=message.conversation_id,
                response_type="agent_response",
                timestamp=datetime.utcnow().isoformat()
            )
            
            # Send response via messaging
            await self._send_response(response, message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Send error response
            error_response = Response(
                content=f"I encountered an error: {str(e)}",
                agent_id=self.agent_id,
                conversation_id=message.conversation_id,
                response_type="agent_response",
                timestamp=datetime.utcnow().isoformat()
            )
            await self._send_response(error_response, message)
    
    async def process_message(
        self, 
        message: Message
    ) -> str:
        """
        Process message using configured LLM provider.
        
        Args:
            message: The message to process
            
        Returns:
            Response content
        """
        if not self.provider_available or not self.provider:
            return f"I'm currently unable to process your request as the {self.config.provider} service is unavailable."
        
        try:
            # Store conversation ID for file operations
            self.current_conversation_id = message.conversation_id
            
            # Store current message for OAuth tool context
            self._current_message = message
            
            # Set current user for dynamic billing mode
            if self.config.billing_mode == "user" and hasattr(self.provider, 'set_current_user'):
                self.provider.set_current_user(message.user_id)
            
            # Reload tools for the specific user if using user billing mode and Composio
            if self.config.billing_mode == "user" and self.tool_provider == "composio":
                # Clear managed provider tools from registry
                for tool_name in list(self.tool_registry.tools[ToolCategory.MANAGED_PROVIDER].keys()):
                    self.tool_registry.unregister_tool(tool_name, ToolCategory.MANAGED_PROVIDER)
                
                # Reinitialize tools for this specific user
                self._init_tools(user_id=message.user_id)
                logger.info(f"Reloaded {len(self.tools)} tools for user {message.user_id}")
            
            # Get conversation history
            from .messaging import get_conversation_history
            history = await get_conversation_history(
                message.conversation_id, 
                limit=10, 
                provider=self.config.provider
            )
            
            # Debug: Log conversation history
            logger.debug(f"Retrieved {len(history) if history else 0} messages from conversation history")
            
            # Build messages list
            messages = []
            
            # Add system prompt
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
            
            # Add history
            if history:
                messages.extend(history)
                logger.debug(f"Added {len(history)} historical messages to conversation")
                # History already includes the current message from backend
                # No need to add it again
            else:
                # No history means this is the first message
                # Need to add it manually since backend might not have stored it yet
                logger.debug("No history found, adding current message")
                messages.append({
                    "role": "user",
                    "content": message.content
                })
            
            # Get all tools from the registry
            all_tools = self.tool_registry.get_all_tools()
            
            # Process with provider
            response = await self.provider.process(
                messages=messages,
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                tools=all_tools if all_tools else None,
                tool_choice="auto" if all_tools else None,
                return_full_response=True if all_tools else False
            )
            
            # Handle tool calls if present
            if isinstance(response, dict) and response.get("tool_calls"):
                # Add assistant message with all tool calls
                # Convert tool_calls to dict format if they're objects
                tool_calls_dict = []
                for tc in response["tool_calls"]:
                    if hasattr(tc, 'model_dump'):
                        # OpenAI object - convert to dict
                        tool_calls_dict.append(tc.model_dump())
                    else:
                        # Already a dict
                        tool_calls_dict.append(tc)
                
                messages.append({
                    "role": "assistant",
                    "content": response.get("content") or "",
                    "tool_calls": tool_calls_dict
                })
                
                # Execute all tool calls through the registry
                context = {
                    "provider": self.provider,
                    "managed_provider": self.tool_provider,
                    "user_id": message.user_id,
                    "custom_handlers": self.custom_tool_handlers,
                    "conversation_id": message.conversation_id,
                    "config": self.config,
                    "messaging_enabled": self.messaging_enabled
                }
                
                tool_results = await self.tool_registry.execute_tool_calls(
                    response["tool_calls"],
                    context
                )
                
                # Add tool results to messages
                for result in tool_results:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": result["tool_call_id"],
                        "content": result["content"]
                    })
                
                # Get final response from LLM after all tool executions
                final_response = await self.provider.process(
                    messages=messages,
                    model=self.config.model,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                
                return final_response
            
            # No tool calls, return regular response
            return response.get("content", "") if isinstance(response, dict) else response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    
    async def health_check(self) -> Dict[str, Any]:
        """Get agent health status."""
        return {
            "status": "healthy",
            "agent_name": self.config.name,
            "agent_version": self.config.version,
            "services": {
                "provider": self.provider_available,
                "provider_name": self.config.provider,
                "tools": len(self.tools) > 0,
                "messaging": self.messaging_enabled
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _send_response(self, response: Response, original_message: Message):
        """Send response via messaging system."""
        try:
            # Prepare metadata
            metadata = {
                "agent_name": self.config.name,
                "agent_version": self.config.version,
                "provider": self.config.provider,
                "model": self.config.model,
                "agent_id": self.agent_id,
            }
            
            if original_message.metadata and "messageId" in original_message.metadata:
                metadata["in_reply_to"] = original_message.metadata["messageId"]
            
            await send_text_message(
                original_message.conversation_id,
                response.content,
                metadata
            )
        except Exception as e:
            logger.error(f"Failed to send response: {e}")
    
    async def check_composio_connection(self, toolkit: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Check if user has an active Composio connection for a toolkit."""
        if self.tool_provider != "composio":
            return {"connected": False, "error": "Composio not configured"}
        
        try:
            from .utils.tools import get_tool_provider
            
            if user_id is None:
                # Use a default/test user
                user_id = "default"
            
            # Initialize or get Composio provider
            composio_provider = get_tool_provider("composio")
            
            # Check specific connection
            return composio_provider.get_connection_status(user_id, toolkit)
            
        except Exception as e:
            logger.error(f"Error checking Composio connection: {e}")
            return {"connected": False, "error": str(e)}
    
    async def connect_composio_app(self, toolkit: str, user_id: str, auth_config: Optional[str] = None) -> Dict[str, Any]:
        """Connect a user to a Composio app/toolkit."""
        if self.tool_provider != "composio":
            return {"success": False, "error": "Composio not configured"}
        
        try:
            from .utils.tools import get_tool_provider
            
            # Get auth config from environment or provided value
            if auth_config is None:
                auth_config = self.composio_auth_configs.get(toolkit)
                if not auth_config:
                    return {
                        "success": False, 
                        "error": f"No auth config found for toolkit '{toolkit}'"
                    }
            
            # Initialize or get Composio provider
            composio_provider = get_tool_provider("composio")
            
            # Attempt connection
            success = await composio_provider.connect_app(
                user_id=user_id,
                toolkit=toolkit,
                auth_config=auth_config
            )
            
            if success:
                # Reinitialize tools for this user
                self._init_tools(user_id=user_id)
                return {
                    "success": True,
                    "message": f"Successfully connected {toolkit} for user {user_id}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to connect {toolkit}"
                }
            
        except Exception as e:
            logger.error(f"Error connecting Composio app: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_composio_auth_in_conversation(
        self, 
        message: Message, 
        toolkit: str,
        auth_config: Optional[str] = None
    ) -> None:
        """
        Handle Composio OAuth flow within a conversation.
        
        This method initiates the OAuth flow and sends the authorization URL
        to the user in the conversation.
        
        Args:
            message: The message object containing user_id and conversation_id
            toolkit: The toolkit/app to connect (e.g., "TWITTER", "GITHUB")
            auth_config: Optional auth config ID (uses environment config if not provided)
        """
        if self.tool_provider != "composio":
            await send_text_message(
                message.conversation_id,
                "⚠️ Tool connections are not configured for this agent."
            )
            return
        
        try:
            from .utils.tools import get_tool_provider
            
            # Get auth config
            if auth_config is None:
                auth_config = self.composio_auth_configs.get(toolkit)
                if not auth_config:
                    await send_text_message(
                        message.conversation_id,
                        f"⚠️ No authorization configuration found for {toolkit}. Please contact support."
                    )
                    return
            
            # Get Composio provider
            composio_provider = get_tool_provider("composio")
            
            # Initiate connection
            connection_info = composio_provider.initiate_connection(
                user_id=message.user_id,
                auth_config_id=auth_config
            )
            
            if connection_info.get("redirect_url"):
                # Send authorization URL to user
                auth_message = f"""🔗 **Connect your {toolkit} account**

To use {toolkit} features, you need to authorize access. Please click the link below to connect your account:

[Authorize {toolkit}]({connection_info['redirect_url']})

After authorizing, send me a message and I'll be able to use {toolkit} on your behalf!"""
                
                await send_text_message(
                    message.conversation_id,
                    auth_message
                )
                
                # Store connection request for potential follow-up
                self._pending_connections = getattr(self, '_pending_connections', {})
                self._pending_connections[f"{message.user_id}:{toolkit}"] = connection_info
                
            else:
                await send_text_message(
                    message.conversation_id,
                    f"⚠️ Failed to generate authorization link for {toolkit}. Please try again later."
                )
                
        except Exception as e:
            logger.error(f"Error handling Composio auth flow: {e}")
            await send_text_message(
                message.conversation_id,
                f"⚠️ An error occurred while setting up {toolkit} connection: {str(e)}"
            )
    
    async def query_llm(
        self,
        prompt: str,
        messages: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        provider: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Make a direct LLM query without tools or conversation context.
        
        This is useful for intermediary processing, analysis, or when the agent
        needs to "think" about something without using tools.
        
        Args:
            prompt: The prompt/question to send to the LLM
            messages: Optional message history (if not provided, uses prompt)
            system_prompt: Optional system prompt (defaults to a simple assistant)
            model: Model to use (defaults to agent's model)
            temperature: Temperature (defaults to agent's temperature)
            max_tokens: Max tokens (defaults to agent's max_tokens)
            provider: Provider to use (defaults to agent's provider)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            The LLM's response as a string
        """
        # Use agent's provider by default
        if provider is None:
            if not self.provider_available or not self.provider:
                raise ValueError(f"Provider {self.config.provider} is not available")
            llm_provider = self.provider
        else:
            # Get a different provider if specified
            from .providers import get_provider
            llm_provider = get_provider(provider)
        
        # Build messages if not provided
        if messages is None:
            messages = []
            
            # Add system prompt
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({
                    "role": "system", 
                    "content": "You are a helpful assistant. Be concise and direct."
                })
            
            # Add user prompt
            messages.append({"role": "user", "content": prompt})
        
        # Use provided parameters or defaults
        model = model or self.config.model
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens
        
        # Make the LLM call without tools
        response = await llm_provider.process(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=None,  # No tools for direct queries
            **kwargs
        )
        
        # Extract string response
        if isinstance(response, dict):
            return response.get("content", "")
        return response