"""
Audio processing utilities for Demiurg agents.
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# OpenAI supported audio formats
OPENAI_SUPPORTED_FORMATS = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'}


def get_audio_format(file_path: Path) -> str:
    """Get the audio format from file extension."""
    return file_path.suffix.lower().lstrip('.')


def is_format_supported(format: str) -> bool:
    """Check if audio format is supported by OpenAI."""
    return format.lower() in OPENAI_SUPPORTED_FORMATS


async def convert_audio_to_wav(
    input_path: Path,
    output_path: Optional[Path] = None,
    sample_rate: int = 16000,
    channels: int = 1,
    timeout: float = 30.0
) -> Path:
    """
    Convert audio file to WAV format using ffmpeg.
    
    Args:
        input_path: Path to input audio file
        output_path: Path for output file (default: temp file)
        sample_rate: Target sample rate in Hz
        channels: Number of audio channels (1=mono, 2=stereo)
        timeout: Conversion timeout in seconds
        
    Returns:
        Path to converted WAV file
        
    Raises:
        Exception: If conversion fails
    """
    try:
        # Generate output path if not provided
        if output_path is None:
            temp_dir = Path(tempfile.gettempdir()) / "demiurg_audio_conversions"
            temp_dir.mkdir(exist_ok=True)
            output_path = temp_dir / f"{input_path.stem}_converted.wav"
        
        # Build ffmpeg command
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-acodec', 'pcm_s16le',  # 16-bit PCM
            '-ar', str(sample_rate),   # Sample rate
            '-ac', str(channels),      # Audio channels
            '-y',                      # Overwrite output
            str(output_path)
        ]
        
        logger.info(f"Converting audio: {input_path} -> {output_path}")
        
        # Run conversion
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise Exception(f"ffmpeg failed: {result.stderr}")
        
        logger.info(f"Audio conversion successful: {output_path}")
        return output_path
        
    except subprocess.TimeoutExpired:
        logger.error(f"Audio conversion timed out after {timeout}s")
        raise Exception("Audio conversion timed out")
    except FileNotFoundError:
        logger.error("ffmpeg not found. Please install ffmpeg.")
        raise Exception("ffmpeg not found. Please install ffmpeg for audio conversion.")
    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        raise


async def ensure_supported_format(
    file_path: Path,
    preferred_format: str = 'wav'
) -> Tuple[Path, bool]:
    """
    Ensure audio file is in a supported format, converting if necessary.
    
    Args:
        file_path: Path to audio file
        preferred_format: Preferred format if conversion needed
        
    Returns:
        Tuple of (file_path, was_converted)
    """
    format = get_audio_format(file_path)
    
    if is_format_supported(format):
        logger.info(f"Audio format '{format}' is supported")
        return file_path, False
    
    logger.info(f"Audio format '{format}' not supported, converting to {preferred_format}")
    
    # Convert to preferred format
    converted_path = await convert_audio_to_wav(file_path)
    return converted_path, True


def check_ffmpeg_available() -> bool:
    """Check if ffmpeg is available on the system."""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            timeout=5.0
        )
        return result.returncode == 0
    except:
        return False