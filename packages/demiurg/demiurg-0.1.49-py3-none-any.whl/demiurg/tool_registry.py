"""
Tool Registry System for Managing Mixed Tool Categories

This module provides a clean architecture for handling multiple tool categories:
- Model Provider Tools (OpenAI, Anthropic, etc.)
- Managed Provider Tools (Composio, Pipedream, etc.)
- Custom Tools (User-defined tools)
"""

import json
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .utils.tools import get_tool_provider

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Categories of tools in the system"""
    MODEL_PROVIDER = "model_provider"      # OpenAI, Anthropic, Google model-specific tools
    MANAGED_PROVIDER = "managed_provider"  # Composio, Pipedream, etc.
    CUSTOM = "custom"                      # User-defined tools


class ToolExecutor(ABC):
    """Abstract base class for tool executors"""
    
    @abstractmethod
    async def execute(self, tool_calls: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute tool calls and return results.
        
        Args:
            tool_calls: List of tool calls to execute
            context: Execution context with provider info, user_id, etc.
            
        Returns:
            List of results with 'tool_call_id' and 'content'
        """
        pass


class ModelProviderExecutor(ToolExecutor):
    """Executor for model provider tools (OpenAI, Anthropic, etc.)"""
    
    async def execute(self, tool_calls: List[Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute model provider specific tools."""
        provider = context.get("provider")
        if not provider:
            logger.error("No provider in context for ModelProviderExecutor")
            return [{
                "tool_call_id": call.id if hasattr(call, 'id') else call["id"],
                "content": "Error: No provider available"
            } for call in tool_calls]
        
        # Import necessary modules for OpenAI tools
        import base64
        from pathlib import Path
        from demiurg.messaging import send_file_message, send_text_message
        
        results = []
        conversation_id = context.get("conversation_id")
        
        for call in tool_calls:
            # Handle both dict and OpenAI object formats
            if hasattr(call, 'function'):
                tool_name = call.function.name
                args = json.loads(call.function.arguments)
                tool_call_id = call.id
            else:
                tool_name = call["function"]["name"]
                args = json.loads(call["function"]["arguments"])
                tool_call_id = call["id"]
            
            logger.info(f"Executing model provider tool: {tool_name}")
            
            try:
                # Handle OpenAI specific tools
                if tool_name == "generate_image":
                    # Send progress indicator if enabled
                    config = context.get("config")
                    if config and config.show_progress_indicators and conversation_id:
                        await send_text_message(
                            conversation_id,
                            "🎨 Generating image with DALL-E 3..."
                        )
                    
                    # Generate image using DALL-E
                    prompt = args.get("prompt", "")
                    style = args.get("style", "vivid")
                    quality = args.get("quality", "standard")
                    
                    images = await provider.generate_image(
                        prompt=prompt,
                        model="dall-e-3",
                        size="1024x1024",
                        quality=quality,
                        style=style,
                        response_format="b64_json"
                    )
                    
                    if images and 'b64_json' in images[0]:
                        image_data = images[0]
                        image_bytes = base64.b64decode(image_data['b64_json'])
                        save_path = Path(f"/tmp/dalle_generated_{hash(prompt)}.png")
                        save_path.write_bytes(image_bytes)
                        
                        # Send as file if conversation_id is available
                        if conversation_id:
                            await send_file_message(
                                conversation_id,
                                str(save_path),
                                caption="DALL-E 3 generated image",
                                metadata={
                                    "source": "dall-e-3",
                                    "prompt": prompt,
                                    "revised_prompt": image_data.get('revised_prompt', prompt)
                                }
                            )
                        
                        result = f"Successfully generated image for: '{prompt}'"
                        if 'revised_prompt' in image_data:
                            result += f"\\nRevised prompt: {image_data['revised_prompt']}"
                    else:
                        result = "Failed to generate image"
                
                elif tool_name == "text_to_speech":
                    # Send progress indicator if enabled
                    config = context.get("config")
                    if config and config.show_progress_indicators and conversation_id:
                        await send_text_message(
                            conversation_id,
                            "🔊 Converting text to speech..."
                        )
                    
                    # Convert text to speech
                    text = args.get("text", "")
                    voice = args.get("voice", "alloy")
                    model = args.get("model", "tts-1")
                    
                    if hasattr(provider, "generate_speech"):
                        audio_data = await provider.generate_speech(
                            text=text,
                            voice=voice,
                            model=model
                        )
                        
                        if audio_data:
                            save_path = Path(f"/tmp/tts_output_{hash(text)}.mp3")
                            save_path.write_bytes(audio_data)
                            
                            # Send as file if conversation_id is available
                            if conversation_id:
                                await send_file_message(
                                    conversation_id,
                                    str(save_path),
                                    caption="Text-to-speech audio",
                                    metadata={
                                        "source": "openai-tts",
                                        "text": text[:100] + "..." if len(text) > 100 else text,
                                        "voice": voice
                                    }
                                )
                            
                            result = f"Successfully generated speech for text (voice: {voice})"
                        else:
                            result = "Failed to generate speech"
                    else:
                        result = "Text-to-speech not available"
                
                elif tool_name == "transcribe_audio":
                    # Send progress indicator if enabled
                    config = context.get("config")
                    if config and config.show_progress_indicators and conversation_id:
                        await send_text_message(
                            conversation_id,
                            "🎤 Transcribing audio file..."
                        )
                    
                    # Transcribe audio file
                    audio_path = args.get("audio_path") or args.get("file_path", "")
                    
                    # If audio_path is a URL, download it first
                    if audio_path.startswith(('http://', 'https://')):
                        from demiurg.utils.files import download_file
                        import os
                        
                        # Extract filename from URL
                        filename = os.path.basename(audio_path.split('?')[0])
                        if not filename:
                            filename = "audio_file"
                        
                        # Download to temp directory
                        local_path = await download_file(audio_path, filename, Path("/tmp"))
                        
                        if local_path:
                            audio_path = str(local_path)
                            logger.info(f"Downloaded audio file from URL to {audio_path}")
                        else:
                            result = f"Failed to download audio file from URL: {audio_path}"
                            results.append({
                                "tool_call_id": tool_call_id,
                                "content": result
                            })
                            continue
                    
                    if hasattr(provider, "transcribe"):
                        transcription = await provider.transcribe(audio_path)
                        result = f"Transcription: {transcription}"
                    else:
                        result = "Audio transcription not available"
                
                else:
                    # Check if provider has specific method for this tool
                    method_name = f"execute_{tool_name}"
                    if hasattr(provider, method_name):
                        result = await getattr(provider, method_name)(**args)
                    else:
                        result = {"error": f"Provider doesn't support tool: {tool_name}"}
                
                # Convert result to string if needed
                if not isinstance(result, str):
                    result = json.dumps(result)
                
                results.append({
                    "tool_call_id": tool_call_id,
                    "content": result
                })
            except Exception as e:
                logger.error(f"Error executing {tool_name}: {e}")
                results.append({
                    "tool_call_id": tool_call_id,
                    "content": f"Error executing {tool_name}: {str(e)}"
                })
        
        return results


class ManagedProviderExecutor(ToolExecutor):
    """Executor for managed provider tools (Composio, Pipedream, etc.)"""
    
    async def execute(self, tool_calls: List[Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute managed provider tools."""
        provider_name = context.get("managed_provider", "composio")
        user_id = context.get("user_id")
        
        logger.info(f"Executing {len(tool_calls)} managed provider tools via {provider_name}")
        
        try:
            # Get the managed provider instance
            provider = get_tool_provider(provider_name)
            
            # Create OpenAI-style response object for Composio
            # Composio expects response.choices[0].message.tool_calls
            from types import SimpleNamespace
            
            # Create mock response structure that Composio expects
            message = SimpleNamespace(tool_calls=tool_calls)
            choice = SimpleNamespace(message=message)
            response = SimpleNamespace(choices=[choice])
            
            # Use provider's handle_tool_calls method
            results = provider.handle_tool_calls(response=response, user_id=user_id)
            
            # Normalize results to our format
            normalized = []
            
            if isinstance(results, list):
                # Multiple results
                for i, result in enumerate(results):
                    call_id = tool_calls[i].id if hasattr(tool_calls[i], 'id') else tool_calls[i]["id"]
                    normalized.append({
                        "tool_call_id": call_id,
                        "content": json.dumps(result) if not isinstance(result, str) else result
                    })
            else:
                # Single result
                call_id = tool_calls[0].id if hasattr(tool_calls[0], 'id') else tool_calls[0]["id"]
                normalized.append({
                    "tool_call_id": call_id,
                    "content": json.dumps(results) if not isinstance(results, str) else results
                })
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error executing managed provider tools: {e}")
            return [{
                "tool_call_id": call.id if hasattr(call, 'id') else call["id"],
                "content": f"Error: {str(e)}"
            } for call in tool_calls]


class CustomToolExecutor(ToolExecutor):
    """Executor for custom user-defined tools"""
    
    async def execute(self, tool_calls: List[Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute custom tools."""
        custom_handlers = context.get("custom_handlers", {})
        results = []
        
        for call in tool_calls:
            # Handle both dict and OpenAI object formats
            if hasattr(call, 'function'):
                tool_name = call.function.name
                args = json.loads(call.function.arguments)
                tool_call_id = call.id
            else:
                tool_name = call["function"]["name"]
                args = json.loads(call["function"]["arguments"])
                tool_call_id = call["id"]
            
            logger.info(f"Executing custom tool: {tool_name}")
            
            try:
                if tool_name in custom_handlers:
                    handler = custom_handlers[tool_name]
                    result = await handler(**args)
                    
                    # Convert result to string if needed
                    if not isinstance(result, str):
                        result = json.dumps(result)
                else:
                    result = f"Error: No handler registered for custom tool: {tool_name}"
                
                results.append({
                    "tool_call_id": tool_call_id,
                    "content": result
                })
            except Exception as e:
                logger.error(f"Error executing custom tool {tool_name}: {e}")
                results.append({
                    "tool_call_id": tool_call_id,
                    "content": f"Error executing {tool_name}: {str(e)}"
                })
        
        return results


class ToolRegistry:
    """Central registry for managing all tool categories"""
    
    def __init__(self):
        """Initialize the tool registry."""
        self.tools = {
            ToolCategory.MODEL_PROVIDER: {},
            ToolCategory.MANAGED_PROVIDER: {},
            ToolCategory.CUSTOM: {}
        }
        
        self.executors = {
            ToolCategory.MODEL_PROVIDER: ModelProviderExecutor(),
            ToolCategory.MANAGED_PROVIDER: ManagedProviderExecutor(),
            ToolCategory.CUSTOM: CustomToolExecutor()
        }
        
        logger.info("Initialized ToolRegistry")
    
    def register_tool(self, tool_def: Dict[str, Any], category: ToolCategory, metadata: Optional[Dict[str, Any]] = None):
        """
        Register a tool with its category and metadata.
        
        Args:
            tool_def: Tool definition (OpenAI function format)
            category: Tool category
            metadata: Additional metadata about the tool
        """
        tool_name = tool_def["function"]["name"]
        self.tools[category][tool_name] = {
            "definition": tool_def,
            "metadata": metadata or {}
        }
        logger.info(f"Registered tool '{tool_name}' in category {category.value}")
    
    def unregister_tool(self, tool_name: str, category: Optional[ToolCategory] = None):
        """
        Unregister a tool.
        
        Args:
            tool_name: Name of the tool to unregister
            category: Specific category to remove from (None = all categories)
        """
        if category:
            if tool_name in self.tools[category]:
                del self.tools[category][tool_name]
                logger.info(f"Unregistered tool '{tool_name}' from category {category.value}")
        else:
            # Remove from all categories
            for cat in ToolCategory:
                if tool_name in self.tools[cat]:
                    del self.tools[cat][tool_name]
                    logger.info(f"Unregistered tool '{tool_name}' from category {cat.value}")
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tool definitions for passing to LLM.
        
        Returns:
            List of all tool definitions
        """
        all_tools = []
        for category_tools in self.tools.values():
            all_tools.extend([t["definition"] for t in category_tools.values()])
        return all_tools
    
    def get_tools_by_category(self, category: ToolCategory) -> List[Dict[str, Any]]:
        """
        Get all tools in a specific category.
        
        Args:
            category: Tool category
            
        Returns:
            List of tool definitions in that category
        """
        return [t["definition"] for t in self.tools[category].values()]
    
    def categorize_tool_call(self, tool_call: Any) -> ToolCategory:
        """
        Determine which category a tool call belongs to.
        
        Args:
            tool_call: Tool call from LLM (dict or ChatCompletionMessageToolCall)
            
        Returns:
            Tool category
            
        Raises:
            ValueError: If tool is not registered
        """
        # Handle both dict and OpenAI object formats
        if hasattr(tool_call, 'function'):
            tool_name = tool_call.function.name
        else:
            tool_name = tool_call["function"]["name"]
        
        for category, tools in self.tools.items():
            if tool_name in tools:
                return category
        
        raise ValueError(f"Unknown tool: {tool_name}")
    
    async def execute_tool_calls(self, tool_calls: List[Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute tool calls, routing to appropriate executors.
        
        Args:
            tool_calls: List of tool calls from LLM (dicts or ChatCompletionMessageToolCall objects)
            context: Execution context containing provider, user_id, etc.
            
        Returns:
            List of tool results with 'tool_call_id' and 'content'
        """
        # Group tool calls by category
        categorized_calls = defaultdict(list)
        
        for call in tool_calls:
            try:
                category = self.categorize_tool_call(call)
                categorized_calls[category].append(call)
            except ValueError as e:
                logger.error(f"Failed to categorize tool call: {e}")
                # Return error for unknown tools
                call_id = call.id if hasattr(call, 'id') else call["id"]
                return [{
                    "tool_call_id": call_id,
                    "content": str(e)
                }]
        
        # Execute by category
        all_results = []
        
        for category, calls in categorized_calls.items():
            logger.info(f"Executing {len(calls)} tools in category {category.value}")
            executor = self.executors[category]
            results = await executor.execute(calls, context)
            all_results.extend(results)
        
        # Sort results by original order
        tool_call_id_to_result = {r["tool_call_id"]: r for r in all_results}
        sorted_results = []
        for call in tool_calls:
            call_id = call.id if hasattr(call, 'id') else call["id"]
            if call_id in tool_call_id_to_result:
                sorted_results.append(tool_call_id_to_result[call_id])
        
        return sorted_results
    
    def clear(self):
        """Clear all registered tools."""
        for category in ToolCategory:
            self.tools[category].clear()
        logger.info("Cleared all registered tools")
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about registered tools."""
        return {
            category.value: len(tools)
            for category, tools in self.tools.items()
        }