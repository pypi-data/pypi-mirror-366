"""
OpenAI-specific tools for function calling.
"""

# Define tools for OpenAI function calling
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "generate_image",
            "description": "Generate an image using DALL-E 3 based on a text prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The text prompt describing the image to generate"
                    },
                    "style": {
                        "type": "string",
                        "enum": ["vivid", "natural"],
                        "description": "The style of the generated image",
                        "default": "vivid"
                    },
                    "quality": {
                        "type": "string",
                        "enum": ["standard", "hd"],
                        "description": "The quality of the generated image",
                        "default": "standard"
                    }
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "text_to_speech",
            "description": "Convert text to speech using OpenAI's TTS models",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to convert to speech"
                    },
                    "voice": {
                        "type": "string",
                        "enum": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                        "description": "The voice to use for speech synthesis",
                        "default": "alloy"
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "transcribe_audio",
            "description": "Transcribe audio from a file path or URL when explicitly requested by the user. Note: Audio messages are automatically transcribed, so this is only needed for manual transcription requests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "audio_path": {
                        "type": "string",
                        "description": "Path or URL to the audio file to transcribe"
                    }
                },
                "required": ["audio_path"]
            }
        }
    }
]