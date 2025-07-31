#!/usr/bin/env python3
"""
Voice chat application using KayGraph.
Demonstrates speech-to-text, LLM processing, and text-to-speech pipeline.
"""

import asyncio
import logging
import argparse
from datetime import datetime
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Graph, AsyncGraph, Node
from voice_nodes import (
    AudioRecorderNode, WhisperSTTNode, MockTTSNode,
    VoiceActivityDetectionNode, ConversationContextNode,
    AudioData
)
from utils.llm import process_voice_query

logger = logging.getLogger(__name__)


class VoiceInputNode(Node):
    """Handle voice input initialization."""
    
    def __init__(self, mode: str = "continuous"):
        super().__init__(node_id="voice_input")
        self.mode = mode  # "continuous" or "push_to_talk"
    
    def exec(self, prep_res):
        """Initialize voice input."""
        logger.info(f"Voice input ready in {self.mode} mode")
        return {"mode": self.mode, "ready": True}
    
    def post(self, shared, prep_res, exec_res):
        """Set up voice input state."""
        shared["voice_mode"] = exec_res["mode"]
        shared["listening"] = True
        return None


class LLMProcessorNode(Node):
    """Process transcribed text with LLM."""
    
    def __init__(self, personality: str = "helpful assistant"):
        super().__init__(node_id="llm_processor", max_retries=2)
        self.personality = personality
    
    def prep(self, shared):
        """Prepare LLM input."""
        return {
            "user_input": shared.get("transcription", ""),
            "conversation_history": shared.get("conversation_history", []),
            "personality": self.personality
        }
    
    def exec(self, prep_res):
        """Process with LLM."""
        if not prep_res["user_input"]:
            return {"response": "I didn't catch that. Could you please repeat?"}
        
        # Use conversation history for context
        response = process_voice_query(
            prep_res["user_input"],
            prep_res["conversation_history"],
            prep_res["personality"]
        )
        
        return {"response": response}
    
    def post(self, shared, prep_res, exec_res):
        """Store LLM response."""
        shared["response_text"] = exec_res["response"]
        logger.info(f"LLM Response: {exec_res['response'][:100]}...")
        return None


class AudioOutputNode(Node):
    """Play audio output (mocked)."""
    
    def prep(self, shared):
        """Get audio to play."""
        return shared.get("audio_output")
    
    def exec(self, audio_data):
        """Play audio."""
        if not audio_data:
            return {"played": False}
        
        logger.info(f"Playing {audio_data.duration:.1f}s of audio...")
        
        # In production, use pyaudio or sounddevice to play
        # stream.write(audio_data.audio_bytes)
        
        import time
        time.sleep(audio_data.duration)  # Simulate playback
        
        return {"played": True, "duration": audio_data.duration}
    
    def post(self, shared, prep_res, exec_res):
        """Update playback state."""
        shared["audio_playing"] = False
        if exec_res["played"]:
            logger.info("Audio playback completed")
        return None


class VoiceChatLoopNode(Node):
    """Control the voice chat loop."""
    
    def __init__(self, max_turns: int = 10):
        super().__init__(node_id="voice_chat_loop")
        self.max_turns = max_turns
        self.turn_count = 0
    
    def exec(self, prep_res):
        """Check if we should continue."""
        self.turn_count += 1
        
        # Check for exit commands in last transcription
        last_text = prep_res.lower()
        exit_commands = ["goodbye", "exit", "quit", "stop", "bye"]
        
        should_exit = any(cmd in last_text for cmd in exit_commands)
        
        return {
            "continue": not should_exit and self.turn_count < self.max_turns,
            "turn": self.turn_count,
            "reason": "exit_command" if should_exit else "max_turns"
        }
    
    def prep(self, shared):
        """Get last transcription."""
        return shared.get("transcription", "")
    
    def post(self, shared, prep_res, exec_res):
        """Determine next action."""
        if exec_res["continue"]:
            logger.info(f"Continuing conversation (turn {exec_res['turn']})")
            return "continue"
        else:
            logger.info(f"Ending conversation: {exec_res['reason']}")
            shared["conversation_ended"] = True
            return "end"


def create_voice_chat_workflow(stt_provider="whisper", tts_provider="mock", personality="helpful"):
    """Create the voice chat workflow graph."""
    
    # Create nodes
    voice_input = VoiceInputNode(mode="continuous")
    recorder = AudioRecorderNode(record_duration=5.0)
    stt = WhisperSTTNode(language="en")
    context = ConversationContextNode()
    llm = LLMProcessorNode(personality=personality)
    tts = MockTTSNode(voice="assistant")
    audio_output = AudioOutputNode()
    chat_loop = VoiceChatLoopNode(max_turns=20)
    
    # Build graph
    graph = AsyncGraph(start=voice_input)
    
    # Main conversation flow
    voice_input >> recorder
    recorder >> stt
    stt >> context
    context >> llm
    llm >> tts
    tts >> audio_output
    audio_output >> chat_loop
    
    # Loop back for next turn
    chat_loop - "continue" >> recorder
    
    # End conversation
    class EndNode(Node):
        def exec(self, prep_res):
            return {"message": "Thank you for chatting! Goodbye!"}
        def post(self, shared, prep_res, exec_res):
            print(f"\n🎤 {exec_res['message']}")
            return None
    
    end_node = EndNode(node_id="end_conversation")
    chat_loop - "end" >> end_node
    
    return graph


async def run_voice_chat(args):
    """Run the voice chat application."""
    print("\n🎤 KayGraph Voice Chat")
    print("=" * 50)
    print(f"STT Provider: {args.stt}")
    print(f"TTS Provider: {args.tts}")
    print(f"Personality: {args.personality}")
    print("\n🎯 Say 'goodbye' or 'exit' to end the conversation")
    print("=" * 50)
    
    # Create workflow
    workflow = create_voice_chat_workflow(
        stt_provider=args.stt,
        tts_provider=args.tts,
        personality=args.personality
    )
    
    # Initialize shared context
    shared = {
        "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "conversation_history": [],
        "save_audio": args.save_audio
    }
    
    if args.save_audio:
        audio_dir = Path(args.save_audio)
        audio_dir.mkdir(exist_ok=True)
        shared["audio_save_path"] = str(audio_dir / f"{shared['session_id']}_recording.wav")
    
    print("\n🎙️  Listening... (this is a simulation)")
    
    # Run workflow
    try:
        await workflow.run_async(shared)
    except KeyboardInterrupt:
        print("\n\n⚡ Conversation interrupted")
    except Exception as e:
        logger.error(f"Error in voice chat: {e}", exc_info=True)
    
    # Show conversation summary
    if shared.get("conversation_history"):
        print("\n📝 Conversation Summary")
        print("=" * 50)
        for msg in shared["conversation_history"]:
            role = "You" if msg["role"] == "user" else "Assistant"
            print(f"{role}: {msg['content']}")
    
    print("\n✅ Voice chat session ended")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="KayGraph Voice Chat")
    
    parser.add_argument("--stt", default="whisper",
                       choices=["whisper", "google", "azure"],
                       help="Speech-to-text provider")
    parser.add_argument("--tts", default="mock",
                       choices=["mock", "elevenlabs", "google", "azure"],
                       help="Text-to-speech provider")
    parser.add_argument("--personality", default="You are a helpful and friendly voice assistant",
                       help="Assistant personality")
    parser.add_argument("--language", default="en",
                       help="Language code (e.g., en, es, fr)")
    parser.add_argument("--save-audio", type=str,
                       help="Directory to save audio recordings")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run voice chat
    asyncio.run(run_voice_chat(args))


if __name__ == "__main__":
    main()