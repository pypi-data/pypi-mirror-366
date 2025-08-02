"""
OpenAI provider implementation for Demiurg agents.
"""

import base64
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from openai import AsyncOpenAI, OpenAI

from ..exceptions import ProviderError
from .base import Provider

logger = logging.getLogger(__name__)


class OpenAIProvider(Provider):
    """OpenAI LLM provider implementation."""
    
    def __init__(self, billing_mode: str = "builder"):
        """
        Initialize OpenAI client.
        
        Args:
            billing_mode: "builder" (use env DEMIURG_USER_ID) or "user" (use dynamic user_id)
        """
        self.billing_mode = billing_mode
        self.base_url = os.getenv('OPENAI_BASE_URL', 'http://demiurg-openai-proxy:3001/v1')
        self._current_user_id = None  # For dynamic user mode
        
        try:
            # Initialize clients without headers (will be set per request in user mode)
            if billing_mode == "builder":
                # Builder mode: use fixed headers
                default_headers = {
                    'X-Session-Id': os.getenv('DEMIURG_SESSION_ID'),
                    'X-Agent-Id': os.getenv('DEMIURG_AGENT_ID'),
                    'X-User-Id': os.getenv('DEMIURG_USER_ID'),
                }
                self.client = OpenAI(base_url=self.base_url, default_headers=default_headers)
                self.async_client = AsyncOpenAI(base_url=self.base_url, default_headers=default_headers)
            else:
                # User mode: no default headers, will be set per request
                self.client = OpenAI(base_url=self.base_url)
                self.async_client = AsyncOpenAI(base_url=self.base_url)
            
            self.available = True
        except Exception as e:
            logger.warning(f"OpenAI client initialization failed: {e}")
            self.client = None
            self.async_client = None
            self.available = False
    
    def set_current_user(self, user_id: Optional[str]):
        """Set the current user ID for dynamic billing mode."""
        self._current_user_id = user_id
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers based on billing mode and current user."""
        headers = {
            'X-Session-Id': os.getenv('DEMIURG_SESSION_ID', ''),
            'X-Agent-Id': os.getenv('DEMIURG_AGENT_ID', ''),
        }
        
        if self.billing_mode == "builder":
            headers['X-User-Id'] = os.getenv('DEMIURG_USER_ID', '')
        elif self.billing_mode == "user" and self._current_user_id:
            headers['X-User-Id'] = self._current_user_id
        
        return headers
    
    async def process(
        self,
        messages: List[Dict[str, Any]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Union[str, Dict[str, Any]]:
        """
        Process messages using OpenAI's chat completion API.
        
        Args:
            messages: List of messages in OpenAI format
            model: OpenAI model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            tools: Optional list of tools for function calling
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            Generated response text or full response dict if return_full_response=True
            
        Raises:
            ProviderError: If OpenAI is not available or request fails
        """
        if not self.available or not self.async_client:
            raise ProviderError("OpenAI client is not available")
        
        try:
            # Check if we should return full response
            return_full_response = kwargs.pop('return_full_response', False)
            
            # Log request summary
            logger.debug(f"OpenAI request: model={model}, messages={len(messages)}, temp={temperature}, max_tokens={max_tokens}")
            
            # Log message types summary
            if logger.isEnabledFor(logging.DEBUG):
                msg_summary = []
                for msg in messages:
                    role = msg.get('role', 'unknown')
                    if isinstance(msg.get('content'), str):
                        content_preview = msg.get('content', '')[:50] + '...' if len(msg.get('content', '')) > 50 else msg.get('content', '')
                        msg_summary.append(f"{role}: {content_preview}")
                    elif isinstance(msg.get('content'), list):
                        parts = msg.get('content', [])
                        part_types = [p.get('type', 'unknown') for p in parts]
                        msg_summary.append(f"{role}: multimodal [{', '.join(part_types)}]")
                    if msg.get('tool_calls'):
                        msg_summary.append(f"{role}: {len(msg.get('tool_calls', []))} tool calls")
                logger.debug(f"Messages: {' | '.join(msg_summary)}")
            
            # Prepare request
            request_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs  # Allow additional parameters
            }
            
            # Add modalities for audio models
            if self.is_audio_model(model):
                request_params["modalities"] = ["text", "audio"]
                # Add audio configuration if not already present
                if "audio" not in request_params:
                    request_params["audio"] = {
                        "voice": "alloy",
                        "format": "wav"
                    }
            
            if tools:
                request_params["tools"] = tools
            
            # Make API call with dynamic headers if in user mode
            if self.billing_mode == "user":
                # Need to create a new client with updated headers for this request
                headers = self._get_headers()
                temp_client = AsyncOpenAI(base_url=self.base_url, default_headers=headers)
                completion = await temp_client.chat.completions.create(**request_params)
            else:
                # Use the default client in builder mode
                completion = await self.async_client.chat.completions.create(**request_params)
            
            # Handle response
            response_message = completion.choices[0].message
            
            # Check if response contains audio
            audio_data = None
            if hasattr(response_message, 'audio') and response_message.audio:
                audio_data = {
                    "data": response_message.audio.data if hasattr(response_message.audio, 'data') else None,
                    "transcript": response_message.audio.transcript if hasattr(response_message.audio, 'transcript') else None,
                    "id": response_message.audio.id if hasattr(response_message.audio, 'id') else None,
                    "expires_at": response_message.audio.expires_at if hasattr(response_message.audio, 'expires_at') else None
                }
            
            if return_full_response:
                response_dict = {
                    "content": response_message.content,
                    "tool_calls": response_message.tool_calls,
                    "finish_reason": completion.choices[0].finish_reason,
                    "usage": completion.usage.model_dump() if completion.usage else None,
                    "model": completion.model
                }
                if audio_data:
                    response_dict["audio"] = audio_data
                return response_dict
            
            # Return content or audio transcript (tool handling should be done by the agent)
            if response_message.content:
                return response_message.content
            elif audio_data and audio_data.get("transcript"):
                return audio_data["transcript"]
            else:
                return ""
            
        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            raise ProviderError(f"OpenAI request failed: {str(e)}")
    
    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format messages for OpenAI's expected format.
        
        OpenAI expects messages with 'role' and 'content' fields.
        Roles can be: 'system', 'user', 'assistant', 'tool'
        
        Args:
            messages: Generic message format
            
        Returns:
            OpenAI-formatted messages
        """
        formatted = []
        for msg in messages:
            # If already in OpenAI format, use as-is
            if 'role' in msg and 'content' in msg:
                formatted.append(msg)
            # Convert from generic format
            elif 'sender_type' in msg:
                if msg['sender_type'] == 'user':
                    formatted.append({
                        'role': 'user',
                        'content': msg.get('content', '')
                    })
                elif msg['sender_type'] == 'agent':
                    formatted.append({
                        'role': 'assistant',
                        'content': msg.get('content', '')
                    })
                elif msg['sender_type'] == 'system':
                    formatted.append({
                        'role': 'system',
                        'content': msg.get('content', '')
                    })
        
        return formatted
    
    async def transcribe(self, file_path: str, model: str = "whisper-1", **kwargs) -> str:
        """
        Transcribe audio using OpenAI's speech-to-text models.
        
        Args:
            file_path: Path to audio file
            model: Model to use (whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe)
            **kwargs: Additional parameters (language, prompt, etc.)
            
        Returns:
            Transcribed text
            
        Raises:
            ProviderError: If transcription fails
        """
        if not self.available or not self.async_client:
            raise ProviderError("OpenAI client is not available")
        
        try:
            with open(file_path, 'rb') as audio_file:
                if self.billing_mode == "user":
                    headers = self._get_headers()
                    temp_client = AsyncOpenAI(base_url=self.base_url, default_headers=headers)
                    transcription = await temp_client.audio.transcriptions.create(
                        model=model,
                        file=audio_file,
                        response_format=kwargs.get('response_format', 'text'),
                        **kwargs
                    )
                else:
                    transcription = await self.async_client.audio.transcriptions.create(
                        model=model,
                        file=audio_file,
                        response_format=kwargs.get('response_format', 'text'),
                        **kwargs
                    )
                return transcription
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise ProviderError(f"Audio transcription failed: {str(e)}")
    
    def is_vision_model(self, model: str) -> bool:
        """Check if a model supports vision capabilities."""
        vision_models = ['gpt-4o', 'gpt-4-vision-preview', 'gpt-4-turbo', 'gpt-4.1', 'o1']
        return any(model.startswith(vm) for vm in vision_models)
    
    def is_audio_model(self, model: str) -> bool:
        """Check if a model supports native audio input/output capabilities."""
        audio_models = ['gpt-4o-audio-preview', 'gpt-4o-mini-audio-preview']
        return any(model.startswith(am) for am in audio_models)
    
    async def generate_speech(
        self, 
        text: str, 
        model: str = "tts-1",
        voice: str = "alloy",
        response_format: str = "mp3",
        **kwargs
    ) -> bytes:
        """
        Generate speech from text using OpenAI's TTS models.
        
        Args:
            text: Text to convert to speech
            model: TTS model (tts-1, tts-1-hd, gpt-4o-mini-tts)
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            response_format: Audio format (mp3, opus, aac, flac, wav, pcm)
            **kwargs: Additional parameters (speed, etc.)
            
        Returns:
            Audio data as bytes
            
        Raises:
            ProviderError: If TTS generation fails
        """
        if not self.available or not self.async_client:
            raise ProviderError("OpenAI client is not available")
        
        try:
            if self.billing_mode == "user":
                headers = self._get_headers()
                temp_client = AsyncOpenAI(base_url=self.base_url, default_headers=headers)
                response = await temp_client.audio.speech.create(
                    model=model,
                    voice=voice,
                    input=text,
                    response_format=response_format,
                    **kwargs
                )
            else:
                response = await self.async_client.audio.speech.create(
                    model=model,
                    voice=voice,
                    input=text,
                    response_format=response_format,
                    **kwargs
                )
            
            # For async client, we need to use aread() to get the bytes
            audio_data = await response.aread()
            logger.info(f"Generated audio: {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise ProviderError(f"Speech generation failed: {str(e)}")
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        n: int = 1,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate images using DALL-E or GPT-Image models.
        
        Args:
            prompt: Text prompt for image generation
            model: Model to use (dall-e-2, dall-e-3, gpt-image-1)
            size: Image size (model-dependent)
            quality: Quality level (standard, hd) - DALL-E 3 only
            style: Style (vivid, natural) - DALL-E 3 only
            n: Number of images (1 for DALL-E 3)
            **kwargs: Additional parameters
            
        Returns:
            List of image data dicts with 'url' or 'b64_json' keys
            
        Raises:
            ProviderError: If image generation fails
        """
        if not self.available or not self.async_client:
            raise ProviderError("OpenAI client is not available")
        
        try:
            # Prepare parameters
            params = {
                "model": model,
                "prompt": prompt,
                "n": n,
                **kwargs
            }
            
            # Add model-specific parameters
            if model == "dall-e-3":
                params["size"] = size
                params["quality"] = quality
                params["style"] = style
                # Request base64 format to avoid URL expiration
                params["response_format"] = kwargs.get("response_format", "b64_json")
            elif model == "dall-e-2":
                params["size"] = size
                # Request base64 format to avoid URL expiration
                params["response_format"] = kwargs.get("response_format", "b64_json")
            # gpt-image-1 doesn't need size/quality/style
            
            if self.billing_mode == "user":
                headers = self._get_headers()
                temp_client = AsyncOpenAI(base_url=self.base_url, default_headers=headers)
                response = await temp_client.images.generate(**params)
            else:
                response = await self.async_client.images.generate(**params)
            
            # Format response
            images = []
            for image in response.data:
                image_data = {}
                if hasattr(image, 'url'):
                    image_data['url'] = image.url
                if hasattr(image, 'b64_json'):
                    image_data['b64_json'] = image.b64_json
                if hasattr(image, 'revised_prompt'):
                    image_data['revised_prompt'] = image.revised_prompt
                images.append(image_data)
            
            return images
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise ProviderError(f"Image generation failed: {str(e)}")
    
    async def edit_image(
        self,
        image_path: str,
        prompt: str,
        mask_path: Optional[str] = None,
        model: str = "dall-e-2",
        size: str = "1024x1024",
        n: int = 1,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Edit an image using DALL-E 2 or GPT-Image-1.
        
        Args:
            image_path: Path to image to edit
            prompt: Description of changes
            mask_path: Optional mask indicating areas to edit
            model: Model to use
            size: Output size
            n: Number of variations
            **kwargs: Additional parameters
            
        Returns:
            List of edited image data
            
        Raises:
            ProviderError: If image editing fails
        """
        if not self.available or not self.async_client:
            raise ProviderError("OpenAI client is not available")
        
        try:
            with open(image_path, 'rb') as image_file:
                if mask_path:
                    with open(mask_path, 'rb') as mask_file:
                        response = await self.async_client.images.edit(
                            model=model,
                            image=image_file,
                            mask=mask_file,
                            prompt=prompt,
                            size=size,
                            n=n,
                            **kwargs
                        )
                else:
                    response = await self.async_client.images.edit(
                        model=model,
                        image=image_file,
                        prompt=prompt,
                        size=size,
                        n=n,
                        **kwargs
                    )
            
            # Format response
            images = []
            for image in response.data:
                image_data = {}
                if hasattr(image, 'url'):
                    image_data['url'] = image.url
                if hasattr(image, 'b64_json'):
                    image_data['b64_json'] = image.b64_json
                images.append(image_data)
            
            return images
            
        except Exception as e:
            logger.error(f"Error editing image: {e}")
            raise ProviderError(f"Image editing failed: {str(e)}")
    
    def format_image_content(self, image_data: Union[str, bytes], mime_type: str = "image/jpeg") -> Dict[str, Any]:
        """
        Format image data for inclusion in chat messages.
        
        Args:
            image_data: Base64 string, bytes, or file path
            mime_type: MIME type of the image
            
        Returns:
            Formatted image content for OpenAI API
        """
        # Handle different input types
        if isinstance(image_data, str):
            if image_data.startswith('data:'):
                # Already formatted
                return {
                    "type": "image_url",
                    "image_url": {"url": image_data}
                }
            elif image_data.startswith('http'):
                # URL
                return {
                    "type": "image_url", 
                    "image_url": {"url": image_data}
                }
            else:
                # File path or base64
                if '/' in image_data or '\\' in image_data:
                    # File path
                    with open(image_data, 'rb') as f:
                        image_bytes = f.read()
                    base64_data = base64.b64encode(image_bytes).decode('utf-8')
                else:
                    # Assume base64
                    base64_data = image_data
        elif isinstance(image_data, bytes):
            base64_data = base64.b64encode(image_data).decode('utf-8')
        else:
            raise ValueError(f"Unsupported image data type: {type(image_data)}")
        
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{base64_data}"
            }
        }
    
    def format_audio_content(self, audio_data: Union[str, bytes], mime_type: str = "audio/wav") -> Dict[str, Any]:
        """
        Format audio data for inclusion in chat messages (for audio-capable models).
        
        Args:
            audio_data: Base64 string, bytes, or file path
            mime_type: MIME type of the audio
            
        Returns:
            Formatted audio content for OpenAI API
        """
        # Handle different input types
        if isinstance(audio_data, str):
            if '/' in audio_data or '\\' in audio_data:
                # File path
                with open(audio_data, 'rb') as f:
                    audio_bytes = f.read()
                base64_data = base64.b64encode(audio_bytes).decode('utf-8')
            else:
                # Assume base64
                base64_data = audio_data
        elif isinstance(audio_data, bytes):
            base64_data = base64.b64encode(audio_data).decode('utf-8')
        else:
            raise ValueError(f"Unsupported audio data type: {type(audio_data)}")
        
        return {
            "type": "input_audio",
            "input_audio": {
                "data": base64_data,
                "format": mime_type.split('/')[-1]  # Extract format from MIME type
            }
        }