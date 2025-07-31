"""
Voice processing nodes for KayGraph.
Handles speech-to-text, text-to-speech, and audio processing.
"""

import logging
import time
import wave
import json
from typing import Dict, Any, Optional, Tuple, List
from abc import abstractmethod
import io
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, AsyncNode, ValidatedNode

logger = logging.getLogger(__name__)


class AudioData:
    """Container for audio data with metadata."""
    
    def __init__(self, 
                 audio_bytes: bytes,
                 sample_rate: int = 16000,
                 channels: int = 1,
                 sample_width: int = 2):
        self.audio_bytes = audio_bytes
        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_width = sample_width
        self.duration = len(audio_bytes) / (sample_rate * channels * sample_width)
    
    def to_wav_bytes(self) -> bytes:
        """Convert to WAV format bytes."""
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(self.sample_width)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(self.audio_bytes)
        return wav_buffer.getvalue()
    
    @classmethod
    def from_wav_file(cls, filepath: str) -> 'AudioData':
        """Load from WAV file."""
        with wave.open(filepath, 'rb') as wav_file:
            audio_bytes = wav_file.readframes(wav_file.getnframes())
            return cls(
                audio_bytes=audio_bytes,
                sample_rate=wav_file.getframerate(),
                channels=wav_file.getnchannels(),
                sample_width=wav_file.getsampwidth()
            )


class BaseSpeechToTextNode(ValidatedNode):
    """Base class for speech-to-text nodes."""
    
    def __init__(self,
                 language: str = "en",
                 model: str = "base",
                 confidence_threshold: float = 0.5,
                 node_id: Optional[str] = None):
        super().__init__(node_id=node_id or "speech_to_text")
        self.language = language
        self.model = model
        self.confidence_threshold = confidence_threshold
    
    def validate_input(self, audio_data: AudioData) -> AudioData:
        """Validate audio input."""
        if not isinstance(audio_data, AudioData):
            raise ValueError("Input must be AudioData object")
        
        if audio_data.duration > 300:  # 5 minutes max
            raise ValueError("Audio too long (max 5 minutes)")
        
        if audio_data.duration < 0.1:
            raise ValueError("Audio too short (min 0.1 seconds)")
        
        return audio_data
    
    def prep(self, shared: Dict[str, Any]) -> AudioData:
        """Get audio data from shared context."""
        audio_data = shared.get("audio_input")
        if not audio_data:
            raise ValueError("No audio input provided")
        return audio_data
    
    @abstractmethod
    def exec(self, audio_data: AudioData) -> Dict[str, Any]:
        """Convert speech to text. Override in subclasses."""
        pass
    
    def validate_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate STT output."""
        if "text" not in result:
            raise ValueError("STT result missing 'text' field")
        
        if result.get("confidence", 1.0) < self.confidence_threshold:
            logger.warning(f"Low confidence transcription: {result['confidence']}")
        
        return result
    
    def post(self, shared: Dict[str, Any], audio_data: AudioData, result: Dict[str, Any]) -> str:
        """Store transcription result."""
        shared["transcription"] = result["text"]
        shared["transcription_metadata"] = {
            "confidence": result.get("confidence", 1.0),
            "language": result.get("language", self.language),
            "duration": audio_data.duration,
            "timestamp": time.time()
        }
        
        logger.info(f"Transcribed: '{result['text']}' (confidence: {result.get('confidence', 1.0)})")
        
        # Determine next action based on confidence
        if result.get("confidence", 1.0) < self.confidence_threshold:
            return "low_confidence"
        
        return None  # Continue to next node


class WhisperSTTNode(BaseSpeechToTextNode):
    """Speech-to-text using OpenAI Whisper (mocked)."""
    
    def exec(self, audio_data: AudioData) -> Dict[str, Any]:
        """Transcribe audio using Whisper."""
        # In production, use OpenAI Whisper API or local model
        logger.info(f"Transcribing {audio_data.duration:.1f}s of audio with Whisper")
        
        # Mock transcription
        time.sleep(audio_data.duration * 0.3)  # Simulate processing
        
        # In real implementation:
        # response = openai.Audio.transcribe(
        #     model="whisper-1",
        #     file=audio_data.to_wav_bytes(),
        #     language=self.language
        # )
        
        return {
            "text": "Hello, this is a test transcription",
            "confidence": 0.95,
            "language": self.language,
            "segments": [
                {"start": 0.0, "end": 1.5, "text": "Hello,"},
                {"start": 1.5, "end": 3.0, "text": "this is a test transcription"}
            ]
        }


class BaseTextToSpeechNode(ValidatedNode):
    """Base class for text-to-speech nodes."""
    
    def __init__(self,
                 voice: str = "default",
                 speed: float = 1.0,
                 pitch: float = 1.0,
                 node_id: Optional[str] = None):
        super().__init__(node_id=node_id or "text_to_speech")
        self.voice = voice
        self.speed = speed
        self.pitch = pitch
    
    def validate_input(self, text: str) -> str:
        """Validate text input."""
        if not text or not isinstance(text, str):
            raise ValueError("Input must be non-empty string")
        
        if len(text) > 5000:
            raise ValueError("Text too long (max 5000 characters)")
        
        return text.strip()
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get text to synthesize from shared context."""
        text = shared.get("response_text", shared.get("text_to_speak"))
        if not text:
            raise ValueError("No text to synthesize")
        return text
    
    @abstractmethod
    def exec(self, text: str) -> AudioData:
        """Convert text to speech. Override in subclasses."""
        pass
    
    def validate_output(self, audio_data: AudioData) -> AudioData:
        """Validate TTS output."""
        if audio_data.duration > 300:
            logger.warning("Generated audio is very long")
        
        return audio_data
    
    def post(self, shared: Dict[str, Any], text: str, audio_data: AudioData) -> None:
        """Store generated audio."""
        shared["audio_output"] = audio_data
        shared["tts_metadata"] = {
            "text": text,
            "voice": self.voice,
            "duration": audio_data.duration,
            "timestamp": time.time()
        }
        
        logger.info(f"Generated {audio_data.duration:.1f}s of audio for: '{text[:50]}...'")
        return None


class MockTTSNode(BaseTextToSpeechNode):
    """Mock TTS for testing."""
    
    def exec(self, text: str) -> AudioData:
        """Generate mock audio."""
        logger.info(f"Generating speech for: '{text[:50]}...'")
        
        # Simulate processing time
        time.sleep(len(text) * 0.01)
        
        # Generate mock audio (silence)
        duration = len(text) * 0.06  # Rough estimate
        sample_rate = 16000
        num_samples = int(duration * sample_rate)
        
        # In real implementation, call TTS API
        # audio_bytes = tts_api.synthesize(text, voice=self.voice)
        
        # Mock: generate silence
        audio_bytes = b'\x00' * (num_samples * 2)  # 16-bit samples
        
        return AudioData(
            audio_bytes=audio_bytes,
            sample_rate=sample_rate,
            channels=1,
            sample_width=2
        )


class VoiceActivityDetectionNode(Node):
    """Detect voice activity in audio stream."""
    
    def __init__(self,
                 energy_threshold: float = 0.01,
                 silence_duration: float = 1.0,
                 node_id: Optional[str] = None):
        super().__init__(node_id=node_id or "voice_activity_detection")
        self.energy_threshold = energy_threshold
        self.silence_duration = silence_duration
    
    def prep(self, shared: Dict[str, Any]) -> AudioData:
        """Get audio stream chunk."""
        return shared.get("audio_chunk")
    
    def exec(self, audio_chunk: AudioData) -> Dict[str, Any]:
        """Analyze audio for voice activity."""
        if not audio_chunk:
            return {"has_voice": False, "energy": 0.0}
        
        # Calculate energy (simple RMS)
        # In production, use proper VAD library like webrtcvad
        audio_array = list(audio_chunk.audio_bytes)
        energy = sum(x**2 for x in audio_array) / len(audio_array) if audio_array else 0
        
        has_voice = energy > self.energy_threshold
        
        return {
            "has_voice": has_voice,
            "energy": energy,
            "duration": audio_chunk.duration
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Dict[str, Any]) -> str:
        """Update voice activity state."""
        shared["voice_active"] = exec_res["has_voice"]
        shared["audio_energy"] = exec_res["energy"]
        
        # Track silence duration
        if not exec_res["has_voice"]:
            silence_time = shared.get("silence_start_time")
            if silence_time is None:
                shared["silence_start_time"] = time.time()
            elif time.time() - silence_time > self.silence_duration:
                # End of speech detected
                return "end_of_speech"
        else:
            shared["silence_start_time"] = None
            return "voice_detected"
        
        return None  # Continue listening


class AudioRecorderNode(AsyncNode):
    """Record audio from microphone (mocked for example)."""
    
    def __init__(self,
                 sample_rate: int = 16000,
                 chunk_duration: float = 0.5,
                 node_id: Optional[str] = None):
        super().__init__(node_id=node_id or "audio_recorder")
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.recording = False
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare recording parameters."""
        return {
            "record_duration": shared.get("record_duration", 5.0),
            "save_path": shared.get("audio_save_path")
        }
    
    async def exec_async(self, params: Dict[str, Any]) -> AudioData:
        """Record audio (mocked)."""
        import asyncio
        
        logger.info(f"Recording audio for {params['record_duration']}s...")
        
        # In production, use pyaudio or sounddevice
        # stream = pyaudio.PyAudio().open(...)
        
        # Mock recording
        await asyncio.sleep(params['record_duration'])
        
        # Generate mock audio
        num_samples = int(params['record_duration'] * self.sample_rate)
        audio_bytes = b'\x00' * (num_samples * 2)  # Silent audio
        
        audio_data = AudioData(
            audio_bytes=audio_bytes,
            sample_rate=self.sample_rate,
            channels=1,
            sample_width=2
        )
        
        # Save if requested
        if params['save_path']:
            with wave.open(params['save_path'], 'wb') as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(self.sample_rate)
                f.writeframes(audio_bytes)
            logger.info(f"Saved recording to {params['save_path']}")
        
        return audio_data
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], audio_data: AudioData) -> None:
        """Store recorded audio."""
        shared["recorded_audio"] = audio_data
        shared["recording_metadata"] = {
            "duration": audio_data.duration,
            "timestamp": time.time()
        }
        return None


class ConversationContextNode(Node):
    """Manage conversation context for voice chat."""
    
    def __init__(self, max_history: int = 10, node_id: Optional[str] = None):
        super().__init__(node_id=node_id or "conversation_context")
        self.max_history = max_history
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare conversation update."""
        return {
            "user_text": shared.get("transcription"),
            "assistant_text": shared.get("response_text"),
            "metadata": {
                "timestamp": time.time(),
                "confidence": shared.get("transcription_metadata", {}).get("confidence"),
                "voice_used": shared.get("tts_metadata", {}).get("voice")
            }
        }
    
    def exec(self, update: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Update conversation history."""
        # This would integrate with a proper conversation manager
        return []  # Return updated history
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], history: List[Dict[str, Any]]) -> None:
        """Update shared conversation context."""
        if "conversation_history" not in shared:
            shared["conversation_history"] = []
        
        # Add user message
        if prep_res["user_text"]:
            shared["conversation_history"].append({
                "role": "user",
                "content": prep_res["user_text"],
                "timestamp": prep_res["metadata"]["timestamp"],
                "audio": True
            })
        
        # Add assistant response
        if prep_res["assistant_text"]:
            shared["conversation_history"].append({
                "role": "assistant",
                "content": prep_res["assistant_text"],
                "timestamp": time.time(),
                "audio": True
            })
        
        # Trim history
        if len(shared["conversation_history"]) > self.max_history * 2:
            shared["conversation_history"] = shared["conversation_history"][-self.max_history * 2:]
        
        return None


if __name__ == "__main__":
    # Test voice nodes
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Voice Processing Nodes...")
    
    # Test STT
    stt = WhisperSTTNode()
    mock_audio = AudioData(audio_bytes=b'\x00' * 32000, sample_rate=16000)
    
    shared = {"audio_input": mock_audio}
    stt.run(shared)
    print(f"Transcription: {shared.get('transcription')}")
    
    # Test TTS
    tts = MockTTSNode(voice="assistant")
    shared["response_text"] = "Hello! How can I help you today?"
    tts.run(shared)
    
    output_audio = shared.get("audio_output")
    print(f"Generated audio: {output_audio.duration:.1f}s")
    
    # Test VAD
    vad = VoiceActivityDetectionNode()
    shared["audio_chunk"] = AudioData(audio_bytes=b'\x10' * 1600, sample_rate=16000)
    action = vad.run(shared)
    print(f"Voice detected: {shared.get('voice_active')}")