# Demiurg SDK

A powerful AI agent framework for building production-ready conversational agents with support for multiple LLM providers and external tool integrations.

## 🎉 What's New in v0.1.26

- **Scheduled Agents**: New `ScheduledAgent` class for creating agents that can execute tasks on schedules
- **Direct Tool Execution**: Schedule direct execution of Composio tools, OpenAI tools, and custom tools
- **Workflow Support**: Build complex multi-step workflows with conditional logic
- **Natural Language Scheduling**: Parse schedules like "every day at 9am" or "every 30 minutes"
- **Full Agent Capabilities**: Scheduled agents maintain all conversational features

## Features

- 🚀 **Clean API** - Simple, intuitive agent initialization
- 🔌 **Multi-Provider Support** - OpenAI with more providers coming soon
- 💰 **Flexible Billing** - Choose who pays for API calls (builder or end-user)
- 🛠️ **Composio Integration** - Connect to 150+ external services with OAuth
- 📬 **Built-in Messaging** - Queue management and conversation history
- 📁 **Multimodal Support** - Handle images, audio, text, and files
- 🎨 **OpenAI Tools** - Image generation (DALL-E 3), TTS, transcription
- ⚡ **Progress Indicators** - Real-time feedback for long operations
- 🏗️ **Production Ready** - Error handling, logging, and scalability
- ⏰ **Scheduled Agents** - Run tasks automatically on schedules
- 🔄 **Workflow Engine** - Build complex multi-step automations

## Installation

```bash
pip install demiurg
```

## Quick Start

### Simple Agent

```python
from demiurg import Agent, OpenAIProvider

# Create an agent with OpenAI
agent = Agent(OpenAIProvider())

# Or with user-based billing
agent = Agent(OpenAIProvider(), billing="user")
```

### Agent with External Tools (Composio)

```python
from demiurg import Agent, OpenAIProvider, Composio

# Create agent with Twitter and GitHub access
agent = Agent(
    OpenAIProvider(),
    Composio("TWITTER", "GITHUB"),
    billing="user"
)
```

### Custom Configuration

```python
from demiurg import Agent, OpenAIProvider, Config

config = Config(
    name="My Assistant",
    description="A helpful AI assistant",
    model="gpt-4o",
    temperature=0.7,
    show_progress_indicators=True
)

agent = Agent(OpenAIProvider(), config=config)
```

## Core Concepts

### Billing Modes

The SDK supports two billing modes:

- **`"builder"`** (default) - API calls are charged to the agent builder's account
- **`"user"`** - API calls are charged to the end user's account

```python
# Builder pays for all API calls
agent = Agent(OpenAIProvider(), billing="builder")

# End users pay for their own API calls
agent = Agent(OpenAIProvider(), billing="user")
```

### Composio Integration

Connect your agents to external services like Twitter, GitHub, Gmail, and 150+ more:

```python
# Configure Composio tools
agent = Agent(
    OpenAIProvider(),
    Composio("TWITTER", "GITHUB", "GMAIL"),
    billing="user"
)

# Check if user has connected their account
status = await agent.check_composio_connection("TWITTER", user_id)

# Handle OAuth flow in conversation
if not status["connected"]:
    await agent.handle_composio_auth_in_conversation(message, "TWITTER")
```

Create a `composio-tools.txt` file in your project root:
```txt
TWITTER=ac_your_twitter_config_id
GITHUB=ac_your_github_config_id
GMAIL=ac_your_gmail_config_id
```

### Progress Indicators

Long operations automatically show progress messages:

```python
config = Config(show_progress_indicators=True)  # Enabled by default

# Users will see:
# "🎨 Creating your image... This may take a moment."
# "🎵 Transcribing audio... This may take a moment."
```

## Message Handling

### Sending Messages

```python
from demiurg import send_text, send_file

# Send text message
await send_text(conversation_id, "Hello from my agent!")

# Send file with caption
await send_file(
    conversation_id, 
    "/path/to/image.png", 
    caption="Here's your generated image!"
)
```

### Processing Messages

```python
from demiurg import Message

# Process user message
message = Message(
    content="Generate an image of a sunset",
    user_id="user123",
    conversation_id="conv456"
)

response = await agent.process_message(message)
```

### Conversation History

```python
from demiurg import get_conversation_history

# Get formatted history for LLM context
messages = await get_conversation_history(
    conversation_id,
    limit=50,
    provider="openai"  # Formats for specific provider
)
```

## Built-in OpenAI Tools

When using OpenAI provider with tools enabled:

```python
config = Config(use_tools=True)
agent = Agent(OpenAIProvider(), config=config)
```

Available tools:
- **generate_image** - Create images with DALL-E 3
- **text_to_speech** - Convert text to natural speech
- **transcribe_audio** - Transcribe audio files

## Custom Agents

### Basic Custom Agent

```python
from demiurg import Agent, OpenAIProvider, Message

class MyCustomAgent(Agent):
    def __init__(self):
        super().__init__(
            OpenAIProvider(),
            billing="user"
        )
    
    async def process_message(self, message: Message, content=None) -> str:
        # Add custom preprocessing
        if "urgent" in message.content.lower():
            return await self.handle_urgent_request(message)
        
        # Use standard processing
        return await super().process_message(message, content)
```

### Agent with Custom Tools

```python
class ToolAgent(Agent):
    def __init__(self):
        config = Config(use_tools=True)
        super().__init__(OpenAIProvider(), config=config)
        
        # Register custom tool
        self.register_custom_tool(
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"}
                        },
                        "required": ["location"]
                    }
                }
            },
            self.get_weather
        )
    
    async def get_weather(self, location: str) -> str:
        # Implement weather fetching
        return f"Weather in {location}: Sunny, 72°F"
```

## File Handling

The SDK automatically handles various file types:

```python
# Images are analyzed with vision models
# Audio files are automatically transcribed
# Text files have their content extracted

# File size limit: 10MB
# Supported image formats: PNG, JPEG, WEBP, GIF
# Supported audio formats: MP3, WAV, M4A, and more
```

## Error Handling

```python
from demiurg.exceptions import (
    DemiurgError,      # Base exception
    ConfigurationError,# Configuration issues
    MessagingError,    # Messaging failures
    ProviderError,     # LLM provider errors
    FileError,         # File operation failures
    ToolError          # Tool execution errors
)

try:
    response = await agent.process_message(message)
except ProviderError as e:
    # Handle LLM provider issues
    logger.error(f"Provider error: {e}")
except DemiurgError as e:
    # Handle other Demiurg errors
    logger.error(f"Agent error: {e}")
```

## Environment Variables

Required environment variables:

```bash
# Core Configuration
DEMIURG_BACKEND_URL=http://backend:3000  # Backend API URL
DEMIURG_AGENT_TOKEN=your_token          # Authentication token
DEMIURG_AGENT_ID=your_agent_id          # Unique agent identifier

# Provider Keys
OPENAI_API_KEY=your_openai_key          # For OpenAI provider

# Composio Integration (optional)
COMPOSIO_API_KEY=your_composio_key      # For external tools
COMPOSIO_TOOLS=TWITTER,GITHUB,GMAIL    # Comma-separated toolkits

# Advanced Settings
DEMIURG_USER_ID=builder_user_id        # Builder's user ID (for billing)
TOOL_PROVIDER=composio                  # Tool provider selection
```

## Advanced Features

### Message Queue System

The SDK includes automatic message queuing to prevent race conditions:

```python
# Messages are automatically queued per conversation
# Prevents issues when multiple messages arrive simultaneously
# No additional configuration needed - it just works!
```

### Multimodal Capabilities

```python
# Process images with vision models
if message contains image:
    # Automatically analyzed with GPT-4V
    
# Handle audio messages
if message contains audio:
    # Automatically transcribed with Whisper
    
# Text file processing
if message contains text file:
    # Content extracted and provided to LLM
```

### Production Deployment

```python
# Health check endpoint
@app.get("/health")
async def health_check():
    return await agent.health_check()

# Queue status monitoring
@app.get("/queue-status")
async def queue_status():
    return await agent.get_queue_status()
```

## Architecture

The SDK follows a modular architecture:

- **Agent**: Core class that orchestrates everything
- **Providers**: LLM integrations (OpenAI, etc.)
- **ToolRegistry**: Centralized tool management system
  - Model Provider Tools: LLM-specific tools (DALL-E, TTS, etc.)
  - Managed Provider Tools: External services (Composio, etc.)
  - Custom Tools: User-defined functions
- **Messaging**: Communication with Demiurg platform
- **Utils**: File handling, audio processing, etc.

## Best Practices

1. **Always use async/await** - The SDK is built for async operations
2. **Handle errors gracefully** - Use try/except blocks with specific exceptions
3. **Configure billing appropriately** - Choose who pays for API calls
4. **Set up Composio auth configs** - Store in composio-tools.txt
5. **Enable progress indicators** - Better UX for long operations
6. **Use appropriate models** - GPT-4o for complex tasks, GPT-3.5 for simple ones

## Advanced Usage

### Direct LLM Queries

Sometimes you need to make LLM calls without tools or conversation context:

```python
# Use the agent's LLM for analysis
analysis = await agent.query_llm(
    "Analyze this code for security issues: " + code,
    system_prompt="You are a security expert. Be thorough.",
    temperature=0.2
)

# Use a different model or provider
response = await agent.query_llm(
    prompt="Summarize this text",
    model="gpt-3.5-turbo",  # Use a faster model
    max_tokens=150
)
```

### Scheduled Agents

Create agents that can run tasks automatically on schedules:

```python
from demiurg import ScheduledAgent, OpenAIProvider, Composio

class DailyReportAgent(ScheduledAgent):
    def __init__(self):
        super().__init__(
            OpenAIProvider(),
            Composio("TWITTER", "GITHUB")
        )
        
        # Schedule daily report at 9 AM
        self.schedule_task(
            name="daily_report",
            schedule="0 9 * * *",  # Cron expression
            task_type="workflow",
            steps=[
                {
                    "type": "tool",
                    "tool": "GITHUB_LIST_ISSUES",
                    "arguments": {"state": "open"}
                },
                {
                    "type": "llm_query",
                    "prompt": "Summarize these GitHub issues: {{step_0_result}}"
                },
                {
                    "type": "tool",
                    "tool": "TWITTER_CREATE_TWEET",
                    "arguments": {"text": "{{step_1_llm}}"}
                }
            ]
        )

# The agent can chat AND run scheduled tasks
agent = DailyReportAgent()
agent.start_scheduler()
```

### Natural Language Scheduling

```python
# Schedule with natural language
agent.schedule_task(
    name="reminder",
    schedule="every day at 2:30 PM",
    task_type="llm_query",
    prompt="Generate a motivational quote",
    notify_channel=conversation_id
)

# Or use interval scheduling
agent.schedule_task(
    name="check_mentions",
    schedule={"type": "interval", "params": {"minutes": 30}},
    task_type="tool",
    tool_slug="TWITTER_GET_MENTIONS"
)
```

### Complex Workflows

Build multi-step workflows with conditional logic:

```python
agent.schedule_task(
    name="content_pipeline",
    schedule="0 10 * * MON",  # Every Monday at 10 AM
    task_type="workflow",
    steps=[
        # Generate content ideas
        {
            "type": "llm_query",
            "prompt": "Generate 5 blog post ideas about AI"
        },
        # Create image for best idea
        {
            "type": "openai_tool",
            "tool_name": "generate_image",
            "arguments": {
                "prompt": "Illustration for: {{step_0_llm}}"
            }
        },
        # Conditional posting
        {
            "type": "condition",
            "condition": {
                "field": "step_1_openai.success",
                "operator": "==",
                "value": True
            },
            "true_steps": [{
                "type": "tool",
                "tool": "TWITTER_CREATE_TWEET_WITH_IMAGE",
                "arguments": {
                    "text": "New blog idea: {{step_0_llm}}",
                    "image_path": "{{step_1_openai.file_path}}"
                }
            }]
        }
    ]
)
```

## Migration Guide

### From v0.1.17 to v0.1.18

```python
# Custom tools registration changed
# Old way:
self.register_tool(tool_def, handler)

# New way:
self.register_custom_tool(tool_def, handler)
```

### From v0.1.10 to v0.1.11

```python
# Old way
from demiurg import Agent, Config

config = Config(name="My Agent")
agent = Agent(config)

# New way (backward compatible)
from demiurg import Agent, OpenAIProvider

agent = Agent(OpenAIProvider())
```

## Support

- Documentation: https://docs.demiurg.ai
- GitHub Issues: https://github.com/demiurg-ai/demiurg-sdk/issues
- Email: support@demiurg.ai

## License

Copyright © 2024 Demiurg AI. All rights reserved.

This is proprietary software. See LICENSE file for details.