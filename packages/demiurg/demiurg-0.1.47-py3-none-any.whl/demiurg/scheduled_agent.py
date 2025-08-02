"""
Scheduled Agent implementation for Demiurg framework.

This module provides an agent that can execute tasks on schedules while
maintaining full conversational capabilities.
"""

import asyncio
import base64
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from croniter import croniter

from .agent import Agent
from .exceptions import DemiurgError
from .messaging import send_file_message, send_text_message
from .models import Config, Message, ScheduleConfig, ScheduledTask

logger = logging.getLogger(__name__)


class ScheduledAgent(Agent):
    """
    Agent with built-in scheduling capabilities.
    
    This class extends the base Agent to add scheduling functionality,
    allowing agents to execute tasks automatically on defined schedules
    while maintaining all conversational capabilities.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the scheduled agent."""
        super().__init__(*args, **kwargs)
        
        # Initialize scheduler with explicit event loop policy
        self.scheduler = AsyncIOScheduler()
        # Store reference to event loop for async execution
        self._loop = None
        self.scheduled_tasks = {}
        self._user_context_store = {}  # Store user context for scheduled tasks
        self._task_handlers = {
            'tool': self._execute_scheduled_tool,
            'llm_query': self._execute_scheduled_llm_query,
            'workflow': self._execute_scheduled_workflow,
            'openai_tool': self._execute_scheduled_openai_tool,
            'custom_tool': self._execute_scheduled_custom_tool,
        }
        
        # Start scheduler if configured
        if self.config.schedule and self.config.schedule.enabled:
            self._init_scheduled_tasks()
            if self.config.schedule.start_on_init:
                self.start_scheduler()
    
    def _init_scheduled_tasks(self):
        """Initialize scheduled tasks from configuration."""
        if not self.config.schedule:
            return
            
        for task in self.config.schedule.tasks:
            if task.enabled:
                try:
                    self.schedule_task(
                        name=task.name,
                        schedule=task.schedule,
                        task_type=task.task_type,
                        **task.config
                    )
                except Exception as e:
                    logger.error(f"Failed to schedule task '{task.name}': {e}")
    
    def schedule_task(
        self,
        name: str,
        schedule: Union[str, Dict[str, Any]],
        task_type: str,
        **kwargs
    ):
        """
        Schedule a task for execution.
        
        Args:
            name: Unique name for the scheduled task
            schedule: Cron expression string or schedule configuration dict
            task_type: Type of task ('tool', 'llm_query', 'workflow', 'openai_tool', 'custom_tool')
            **kwargs: Task-specific configuration
        """
        # Validate task type
        if task_type not in self._task_handlers:
            raise ValueError(f"Unknown task type: {task_type}")
        
        # Parse schedule
        trigger = self._parse_schedule(schedule)
        
        # Get handler
        handler = self._task_handlers[task_type]
        
        # If in user billing mode, inject current user context into task config
        if self.config.billing_mode == "user" and 'user_id' not in kwargs.get('config', {}):
            config = kwargs.get('config', {})
            config['user_id'] = self._user_context_store.get('current_user_id')
            kwargs['config'] = config
        
        # Create a wrapper to properly handle async execution
        async def async_job_wrapper(config):
            """Wrapper to ensure async job executes properly"""
            try:
                logger.debug(f"Executing scheduled task '{name}' with handler {handler.__name__}")
                result = await handler(config)
                logger.debug(f"Scheduled task '{name}' completed successfully")
                return result
            except Exception as e:
                logger.error(f"Error in scheduled task '{name}': {e}", exc_info=True)
                raise
        
        # Schedule the job
        job = self.scheduler.add_job(
            func=async_job_wrapper,
            trigger=trigger,
            args=[kwargs],
            id=name,
            name=name,
            replace_existing=True,
            misfire_grace_time=300  # 5 minutes grace time
        )
        
        # Store task info
        self.scheduled_tasks[name] = {
            'job': job,
            'type': task_type,
            'config': kwargs,
            'schedule': schedule
        }
        
        logger.info(f"Scheduled task '{name}' of type '{task_type}'")
    
    def _parse_schedule(self, schedule: Union[str, Dict[str, Any]]) -> Union[CronTrigger, IntervalTrigger]:
        """Parse schedule configuration into a trigger."""
        if isinstance(schedule, str):
            # Validate cron expression
            if not croniter.is_valid(schedule):
                raise ValueError(f"Invalid cron expression: {schedule}")
            return CronTrigger.from_crontab(schedule)
        
        elif isinstance(schedule, dict):
            schedule_type = schedule.get('type', 'cron')
            
            if schedule_type == 'cron':
                return CronTrigger(**schedule.get('params', {}))
            elif schedule_type == 'interval':
                return IntervalTrigger(**schedule.get('params', {}))
            elif schedule_type == 'daily':
                # Parse time like "14:00"
                time_str = schedule.get('time', '00:00')
                hour, minute = map(int, time_str.split(':'))
                return CronTrigger(hour=hour, minute=minute)
            else:
                raise ValueError(f"Unknown schedule type: {schedule_type}")
        
        else:
            raise ValueError(f"Invalid schedule format: {type(schedule)}")
    
    async def _execute_scheduled_tool(self, config: Dict[str, Any]):
        """Execute a Composio or custom tool."""
        tool_slug = config.get('tool', config.get('tool_slug', ''))  # Support both formats
        arguments = config.get('arguments', {})
        
        # Get user_id based on billing mode
        if self.config.billing_mode == "user":
            # Use stored user context for user billing mode
            user_id = config.get('user_id', self._user_context_store.get('current_user_id', 'default'))
        else:
            # Use environment variable for builder billing mode
            user_id = config.get('user_id', os.getenv('DEMIURG_USER_ID', 'default'))
            
        notify_channel = config.get('notify_channel')
        
        try:
            # Check if it's a custom tool
            if tool_slug in self.custom_tool_handlers:
                result = await self.custom_tool_handlers[tool_slug](**arguments)
            else:
                # Execute through Composio or other tool provider
                from .utils.tools import get_tool_provider
                
                if self.tool_provider:
                    # For user billing mode, ensure tools are loaded for the correct user
                    if self.config.billing_mode == "user" and self.tool_provider == "composio":
                        # Reload tools for the specific user if different from current
                        await self._reload_tools_for_user(user_id)
                    
                    provider = get_tool_provider(self.tool_provider)
                    result = await provider.execute_tool(
                        tool_name=tool_slug,
                        arguments=arguments,
                        user_id=user_id
                    )
                else:
                    raise ValueError("No tool provider configured")
            
            # Process result with LLM if configured
            if config.get('process_result_with_llm'):
                analysis = await self.query_llm(
                    f"Analyze this tool execution result and provide insights: {json.dumps(result)}",
                    system_prompt="You are analyzing scheduled tool execution results. Be concise."
                )
                
                if notify_channel:
                    await send_text_message(notify_channel, f"📊 {tool_slug} Analysis:\n{analysis}")
            elif notify_channel:
                # Send raw result
                await send_text_message(
                    notify_channel,
                    f"✅ Executed {tool_slug}:\n```json\n{json.dumps(result, indent=2)}\n```"
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_slug}: {e}")
            if notify_channel:
                await send_text_message(
                    notify_channel,
                    f"❌ Failed to execute {tool_slug}: {str(e)}"
                )
            raise
    
    async def _execute_scheduled_openai_tool(self, config: Dict[str, Any]):
        """Execute OpenAI built-in tools directly."""
        tool_name = config['tool_name']
        args = config.get('arguments', {})
        notify_channel = config.get('notify_channel')
        
        try:
            if tool_name == 'generate_image':
                # Direct image generation
                result = await self._generate_image_direct(
                    prompt=args.get('prompt', ''),
                    style=args.get('style', 'vivid'),
                    quality=args.get('quality', 'standard'),
                    size=args.get('size', '1024x1024')
                )
                
                if notify_channel and result['success']:
                    await send_file_message(
                        notify_channel,
                        result['file_path'],
                        caption=f"🎨 Scheduled image: {args.get('prompt', '')[:50]}..."
                    )
                    
            elif tool_name == 'text_to_speech':
                # Direct TTS
                result = await self._text_to_speech_direct(
                    text=args.get('text', ''),
                    voice=args.get('voice', 'alloy'),
                    model=args.get('model', 'tts-1')
                )
                
                if notify_channel and result['success']:
                    await send_file_message(
                        notify_channel,
                        result['file_path'],
                        caption="🔊 Scheduled audio generation"
                    )
                    
            elif tool_name == 'transcribe_audio':
                # Direct transcription
                result = await self._transcribe_audio_direct(
                    audio_path=args.get('audio_path', ''),
                    language=args.get('language')
                )
                
                if notify_channel and result['success']:
                    await send_text_message(
                        notify_channel,
                        f"📝 Transcription:\n{result['text']}"
                    )
            else:
                raise ValueError(f"Unknown OpenAI tool: {tool_name}")
                    
            return result
            
        except Exception as e:
            logger.error(f"Error executing OpenAI tool {tool_name}: {e}")
            if notify_channel:
                await send_text_message(
                    notify_channel,
                    f"❌ Failed to execute {tool_name}: {str(e)}"
                )
            raise
    
    async def _execute_scheduled_llm_query(self, config: Dict[str, Any]):
        """Execute a direct LLM query."""
        prompt = config.get('prompt', '')
        system_prompt = config.get('system_prompt')
        model = config.get('model', self.config.model)
        temperature = config.get('temperature', self.config.temperature)
        notify_channel = config.get('notify_channel')
        save_to_file = config.get('save_to_file')
        
        try:
            # Set user context for provider if in user billing mode
            if self.config.billing_mode == "user" and hasattr(self.provider, 'set_current_user'):
                user_id = config.get('user_id', self._user_context_store.get('current_user_id'))
                self.provider.set_current_user(user_id)
            
            # Execute LLM query
            result = await self.query_llm(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                temperature=temperature
            )
            
            # Save to file if requested
            if save_to_file:
                file_path = Path(save_to_file)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(result)
                logger.info(f"Saved LLM result to {save_to_file}")
                
            # Send notification
            if notify_channel:
                # Truncate if too long
                if len(result) > 3000:
                    result = result[:3000] + "...\n[Truncated]"
                await send_text_message(
                    notify_channel,
                    f"🤖 LLM Query Result:\n\n{result}"
                )
                
            return result
            
        except Exception as e:
            logger.error(f"Error executing LLM query: {e}")
            if notify_channel:
                await send_text_message(
                    notify_channel,
                    f"❌ LLM query failed: {str(e)}"
                )
            raise
    
    async def _execute_scheduled_custom_tool(self, config: Dict[str, Any]):
        """Execute a custom tool."""
        tool_name = config['tool_name']
        arguments = config.get('arguments', {})
        notify_channel = config.get('notify_channel')
        
        try:
            if tool_name in self.custom_tool_handlers:
                result = await self.custom_tool_handlers[tool_name](**arguments)
                
                if notify_channel:
                    await send_text_message(
                        notify_channel,
                        f"✅ Custom tool '{tool_name}' executed:\n{json.dumps(result, indent=2)}"
                    )
                
                return result
            else:
                raise ValueError(f"Custom tool '{tool_name}' not found")
                
        except Exception as e:
            logger.error(f"Error executing custom tool {tool_name}: {e}")
            if notify_channel:
                await send_text_message(
                    notify_channel,
                    f"❌ Custom tool '{tool_name}' failed: {str(e)}"
                )
            raise
    
    async def _execute_scheduled_workflow(self, config: Dict[str, Any]):
        """Execute a multi-step workflow."""
        # Extract actual config if wrapped
        if 'config' in config and isinstance(config['config'], dict):
            actual_config = config['config']
        else:
            actual_config = config
            
        steps = actual_config.get('steps', [])
        context = actual_config.get('initial_context', {})
        notify_channel = actual_config.get('notify_channel')
        workflow_name = actual_config.get('name', 'Unnamed Workflow')
        
        try:
            for i, step in enumerate(steps):
                step_type = step.get('type')
                logger.info(f"Executing workflow step {i+1}/{len(steps)}: {step_type}")
                
                if step_type == 'tool':
                    # Execute tool with context substitution
                    args = self._substitute_context(step.get('arguments', {}), context)
                    result = await self._execute_scheduled_tool({
                        'tool_slug': step['tool'],
                        'arguments': args
                    })
                    # Support custom storage key with store_as
                    store_as = step.get('store_as', f"step_{i}_result")
                    context[store_as] = result
                    
                elif step_type == 'llm_query':
                    # LLM processing step
                    prompt = self._substitute_context(step.get('prompt', ''), context)
                    result = await self.query_llm(prompt)
                    # Support custom storage key with store_as
                    store_as = step.get('store_as', f"step_{i}_llm")
                    context[store_as] = result
                    
                elif step_type == 'openai_tool':
                    # Execute OpenAI tool
                    args = self._substitute_context(step.get('arguments', {}), context)
                    result = await self._execute_scheduled_openai_tool({
                        'tool_name': step['tool_name'],
                        'arguments': args
                    })
                    context[f"step_{i}_openai"] = result
                    
                elif step_type == 'custom_tool':
                    # Execute custom tool
                    args = self._substitute_context(step.get('arguments', {}), context)
                    result = await self._execute_scheduled_custom_tool({
                        'tool_name': step['tool_name'],
                        'arguments': args
                    })
                    context[f"step_{i}_custom"] = result
                    
                elif step_type == 'condition':
                    # Conditional branching
                    condition = step.get('condition')
                    if self._evaluate_condition(condition, context):
                        # Execute true branch
                        if 'true_steps' in step:
                            sub_workflow = {
                                'steps': step['true_steps'],
                                'initial_context': context
                            }
                            sub_result = await self._execute_scheduled_workflow(sub_workflow)
                            context.update(sub_result)
                    elif 'false_steps' in step:
                        # Execute false branch
                        sub_workflow = {
                            'steps': step['false_steps'],
                            'initial_context': context
                        }
                        sub_result = await self._execute_scheduled_workflow(sub_workflow)
                        context.update(sub_result)
                
                # Add delay between steps if configured
                if step.get('delay_seconds'):
                    await asyncio.sleep(step['delay_seconds'])
                        
            # Send final notification
            if notify_channel:
                summary = await self.query_llm(
                    f"Summarize this workflow execution for '{workflow_name}':\n{json.dumps(context, indent=2)}",
                    system_prompt="Provide a concise, human-readable summary of the workflow results."
                )
                await send_text_message(
                    notify_channel,
                    f"✅ Workflow '{workflow_name}' completed:\n{summary}"
                )
                
            return context
            
        except Exception as e:
            logger.error(f"Error executing workflow at step {i}: {e}")
            if notify_channel:
                await send_text_message(
                    notify_channel,
                    f"❌ Workflow '{workflow_name}' failed at step {i+1}: {str(e)}"
                )
            raise
    
    # Direct tool execution methods
    async def _generate_image_direct(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate image directly using OpenAI."""
        if not self.provider or self.config.provider != "openai":
            raise ValueError("Image generation requires OpenAI provider")
            
        try:
            images = await self.provider.generate_image(
                prompt=prompt,
                model="dall-e-3",
                size=kwargs.get('size', '1024x1024'),
                quality=kwargs.get('quality', 'standard'),
                style=kwargs.get('style', 'vivid'),
                response_format='b64_json'
            )
            
            if images and 'b64_json' in images[0]:
                image_data = images[0]
                image_bytes = base64.b64decode(image_data['b64_json'])
                
                # Save to file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_path = Path(f"/tmp/scheduled_image_{timestamp}.png")
                file_path.write_bytes(image_bytes)
                
                return {
                    'success': True,
                    'file_path': str(file_path),
                    'revised_prompt': image_data.get('revised_prompt', prompt)
                }
            else:
                return {'success': False, 'error': 'No image data returned'}
                
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _text_to_speech_direct(self, text: str, **kwargs) -> Dict[str, Any]:
        """Generate speech directly using OpenAI."""
        if not hasattr(self.provider, 'generate_speech'):
            raise ValueError("TTS requires OpenAI provider")
            
        try:
            audio_data = await self.provider.generate_speech(
                text=text,
                voice=kwargs.get('voice', 'alloy'),
                model=kwargs.get('model', 'tts-1')
            )
            
            if audio_data:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_path = Path(f"/tmp/scheduled_audio_{timestamp}.mp3")
                file_path.write_bytes(audio_data)
                
                return {
                    'success': True,
                    'file_path': str(file_path)
                }
            else:
                return {'success': False, 'error': 'No audio data returned'}
                
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _transcribe_audio_direct(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """Transcribe audio directly using OpenAI."""
        if not hasattr(self.provider, 'transcribe'):
            raise ValueError("Transcription requires OpenAI provider")
            
        try:
            # Download file if it's a URL
            if audio_path.startswith(('http://', 'https://')):
                from .utils.files import download_file
                import os
                
                filename = os.path.basename(audio_path.split('?')[0]) or "audio_file"
                local_path = await download_file(audio_path, filename, Path("/tmp"))
                
                if local_path:
                    audio_path = str(local_path)
                else:
                    return {'success': False, 'error': f'Failed to download audio from {audio_path}'}
            
            transcription = await self.provider.transcribe(
                audio_path,
                language=kwargs.get('language')
            )
            
            return {
                'success': True,
                'text': transcription
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _substitute_context(self, obj: Any, context: Dict[str, Any]) -> Any:
        """Recursively substitute context variables in objects."""
        if isinstance(obj, str):
            # Replace {{variable}} with context values
            def replacer(match):
                key = match.group(1)
                value = context
                for part in key.split('.'):
                    if isinstance(value, dict):
                        value = value.get(part, match.group(0))
                    else:
                        return match.group(0)
                return str(value)
            
            return re.sub(r'\{\{([^}]+)\}\}', replacer, obj)
        elif isinstance(obj, dict):
            return {k: self._substitute_context(v, context) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_context(item, context) for item in obj]
        return obj
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a condition against context."""
        field = condition.get('field')
        operator = condition.get('operator', '==')
        value = condition.get('value')
        
        # Navigate nested fields
        context_value = context
        for part in field.split('.'):
            if isinstance(context_value, dict):
                context_value = context_value.get(part)
            else:
                context_value = None
                break
        
        # Evaluate condition
        if operator == '==':
            return context_value == value
        elif operator == '!=':
            return context_value != value
        elif operator == '>':
            return float(context_value) > float(value)
        elif operator == '<':
            return float(context_value) < float(value)
        elif operator == '>=':
            return float(context_value) >= float(value)
        elif operator == '<=':
            return float(context_value) <= float(value)
        elif operator == 'contains':
            return value in str(context_value)
        elif operator == 'exists':
            return context_value is not None
        elif operator == 'not_exists':
            return context_value is None
        
        return False
    
    async def process_message(self, message: Message) -> str:
        """
        Process messages with scheduling awareness.
        
        This method extends the base agent's message processing to handle
        scheduling-related queries and commands.
        """
        # Store user context for scheduled tasks when in user billing mode
        if self.config.billing_mode == "user" and hasattr(message, 'user_id'):
            self._user_context_store['current_user_id'] = message.user_id
            self._user_context_store['current_conversation_id'] = message.conversation_id
        
        user_text = message.content
        
        # Check for scheduling-related queries
        if any(keyword in user_text.lower() for keyword in ['schedule', 'scheduled', 'task', 'tasks']):
            # List scheduled tasks
            if any(word in user_text.lower() for word in ['list', 'show', 'what', 'which']):
                return self._format_scheduled_tasks()
            
            # Pause/resume scheduler
            elif 'pause' in user_text.lower():
                self.pause_scheduler()
                return "⏸️ Scheduler paused. Tasks won't run until resumed."
            elif 'resume' in user_text.lower():
                self.resume_scheduler()
                return "▶️ Scheduler resumed. Tasks will run according to their schedules."
            
            # Remove task
            elif 'remove' in user_text.lower() or 'delete' in user_text.lower():
                # Extract task name with LLM
                task_name = await self.query_llm(
                    f"Extract the task name to remove from: {user_text}. Return only the task name.",
                    temperature=0.1
                )
                if self.remove_task(task_name.strip()):
                    return f"❌ Removed scheduled task: {task_name}"
                else:
                    return f"Task '{task_name}' not found."
        
        # Regular message processing
        return await super().process_message(message)
    
    def _format_scheduled_tasks(self) -> str:
        """Format scheduled tasks for display."""
        if not self.scheduled_tasks:
            return "📅 No scheduled tasks are currently active."
            
        task_list = []
        for name, info in self.scheduled_tasks.items():
            job = info['job']
            next_run = job.next_run_time
            status = "✅ Active" if job.next_run_time else "⏸️ Paused"
            
            task_list.append(
                f"**{name}**\n"
                f"  Type: {info['type']}\n"
                f"  Schedule: {info['schedule']}\n"
                f"  Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S') if next_run else 'N/A'}\n"
                f"  Status: {status}"
            )
            
        return "📅 **Scheduled Tasks:**\n\n" + "\n\n".join(task_list)
    
    def start_scheduler(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info(f"Started scheduler with {len(self.scheduled_tasks)} tasks")
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Stopped scheduler")
    
    def pause_scheduler(self):
        """Pause all scheduled tasks."""
        self.scheduler.pause()
        logger.info("Paused scheduler")
    
    def resume_scheduler(self):
        """Resume all scheduled tasks."""
        self.scheduler.resume()
        logger.info("Resumed scheduler")
    
    def remove_task(self, name: str) -> bool:
        """Remove a scheduled task."""
        if name in self.scheduled_tasks:
            self.scheduler.remove_job(name)
            del self.scheduled_tasks[name]
            logger.info(f"Removed scheduled task: {name}")
            return True
        return False
    
    def get_task_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a scheduled task."""
        return self.scheduled_tasks.get(name)
    
    async def _reload_tools_for_user(self, user_id: str):
        """Reload tools for a specific user in user billing mode."""
        if not user_id or user_id == self._user_context_store.get('last_loaded_user_id'):
            return  # Already loaded for this user
        
        try:
            # Clear managed provider tools from registry
            from .tool_registry import ToolCategory
            for tool_name in list(self.tool_registry.tools[ToolCategory.MANAGED_PROVIDER].keys()):
                self.tool_registry.unregister_tool(tool_name, ToolCategory.MANAGED_PROVIDER)
            
            # Reload tools for the new user
            from .utils.tools import get_tool_provider
            provider = get_tool_provider(self.tool_provider)
            tools = provider.init_tools(
                user_id=user_id,
                enabled_tools=self._composio_toolkits if hasattr(self, '_composio_toolkits') else None
            )
            
            # Register new tools
            for tool in tools:
                # Handle both dictionary and object tool formats
                if isinstance(tool, dict):
                    # Try to get tool name from various possible locations
                    tool_name = tool.get('name')
                    if not tool_name:
                        # Check if it's an OpenAI function format
                        function_data = tool.get('function')
                        if isinstance(function_data, dict):
                            tool_name = function_data.get('name')
                        elif isinstance(function_data, str):
                            # If function is a string, it might be the tool name itself
                            tool_name = function_data
                    
                    if tool_name:
                        self.tool_registry.register_tool(
                            tool_name,
                            tool,
                            ToolCategory.MANAGED_PROVIDER
                        )
                    else:
                        logger.warning(f"Could not extract tool name from: {tool}")
                else:
                    # For OpenAI function objects, pass the whole object
                    self.tool_registry.register_tool(
                        tool,
                        ToolCategory.MANAGED_PROVIDER
                    )
            
            # Update tracking
            self._user_context_store['last_loaded_user_id'] = user_id
            logger.info(f"Reloaded {len(tools)} tools for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to reload tools for user {user_id}: {e}")
            # Continue with existing tools rather than failing