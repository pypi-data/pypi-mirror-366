# KayGraph Voice Chat

This example demonstrates how to build voice-enabled conversational AI using KayGraph. It integrates speech-to-text (STT) and text-to-speech (TTS) with intelligent conversation management.

## Features Demonstrated

1. **Speech-to-Text**: Convert voice input to text using multiple providers
2. **Text-to-Speech**: Generate natural speech from AI responses
3. **Streaming Audio**: Handle real-time audio streams
4. **Voice Activity Detection**: Detect when user starts/stops speaking
5. **Conversation Memory**: Maintain context across voice interactions

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Audio Capture   │────▶│ Speech-to-Text  │────▶│ Process Intent  │
│ (Microphone)    │     │ (STT Node)      │     │ (LLM Node)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Audio Playback  │◀────│ Text-to-Speech  │◀────│ Generate Reply  │
│ (Speaker)       │     │ (TTS Node)      │     │ (Response Node) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Usage

### Basic Voice Chat
```bash
# Start voice chat with default settings
python main.py

# Use specific STT/TTS providers
python main.py --stt whisper --tts elevenlabs

# Set conversation personality
python main.py --personality "friendly assistant"
```

### Advanced Options
```bash
# Enable wake word detection
python main.py --wake-word "hey assistant"

# Use push-to-talk instead of voice activity detection
python main.py --push-to-talk

# Save conversation audio
python main.py --save-audio ./recordings/
```

## Supported Providers

### Speech-to-Text (STT)
- **Whisper** (OpenAI): High accuracy, multiple languages
- **Google Speech**: Fast, streaming support
- **Azure Speech**: Enterprise features
- **Local Whisper**: Privacy-focused, offline

### Text-to-Speech (TTS)
- **ElevenLabs**: Most natural voices
- **Google TTS**: Fast, many languages
- **Azure TTS**: Neural voices
- **Local TTS**: Privacy-focused

## Examples

### 1. Simple Voice Assistant
Basic voice interaction with conversation memory.

### 2. Multi-lingual Support
Automatically detect and respond in user's language.

### 3. Voice-Controlled Actions
Execute commands based on voice input.

### 4. Emotional TTS
Adjust voice tone based on conversation context.

## Key Concepts

### Voice Activity Detection (VAD)
- Detects speech segments in audio stream
- Reduces false triggers and improves UX
- Configurable sensitivity

### Audio Streaming
- Handles real-time audio processing
- Buffering for optimal performance
- Graceful handling of network issues

### Conversation Context
- Maintains conversation history
- Speaker diarization (who said what)
- Emotion and intent tracking

## Production Considerations

1. **Latency Optimization**
   - Use streaming STT for faster response
   - Pre-generate common TTS phrases
   - Local models for critical paths

2. **Error Handling**
   - Fallback to text input on audio issues
   - Retry logic for API failures
   - Graceful degradation

3. **Privacy & Security**
   - Option for local processing
   - Audio data retention policies
   - User consent management

4. **Scalability**
   - Queue audio processing tasks
   - Load balance across providers
   - Cache TTS outputs