#!/usr/bin/env python3
"""
Gradio integration nodes for KayGraph.
Enables building interactive ML interfaces with KayGraph workflows.
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
import base64
import io

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, AsyncNode, ValidatedNode

logger = logging.getLogger(__name__)


@dataclass
class GradioComponent:
    """Represents a Gradio UI component."""
    type: str  # textbox, image, audio, etc.
    label: str
    properties: Dict[str, Any]
    value: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "label": self.label,
            "properties": self.properties,
            "value": self.value
        }


class GradioInterfaceNode(Node):
    """Base node for Gradio interface integration."""
    
    def __init__(self, 
                 inputs: List[GradioComponent],
                 outputs: List[GradioComponent],
                 title: str = "KayGraph Interface",
                 description: str = ""):
        super().__init__(node_id="gradio_interface")
        self.inputs = inputs
        self.outputs = outputs
        self.title = title
        self.description = description
        self.interface = None
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare interface data."""
        return {
            "user_inputs": shared.get("gradio_inputs", {}),
            "interface_config": {
                "title": self.title,
                "description": self.description,
                "inputs": [inp.to_dict() for inp in self.inputs],
                "outputs": [out.to_dict() for out in self.outputs]
            }
        }
    
    def exec(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process inputs through the interface."""
        user_inputs = context["user_inputs"]
        
        logger.info(f"🎨 Processing Gradio inputs: {list(user_inputs.keys())}")
        
        # Here you would normally process the inputs
        # For demo, we'll just transform them
        results = {}
        
        for key, value in user_inputs.items():
            if isinstance(value, str):
                results[key] = f"Processed: {value}"
            else:
                results[key] = value
        
        return {
            "results": results,
            "interface_config": context["interface_config"]
        }
    
    def post(self, shared: Dict[str, Any], context: Dict, result: Dict[str, Any]) -> None:
        """Store interface results."""
        shared["gradio_results"] = result["results"]
        shared["interface_ready"] = True
    
    def create_interface_function(self, graph):
        """Create function for Gradio interface."""
        def process(*args):
            # Map inputs to shared context
            shared = {}
            for i, (arg, input_comp) in enumerate(zip(args, self.inputs)):
                shared[f"input_{input_comp.label}"] = arg
            
            # Run the graph
            graph.run(shared)
            
            # Extract outputs
            results = []
            for output_comp in self.outputs:
                result = shared.get(f"output_{output_comp.label}", "")
                results.append(result)
            
            return results if len(results) > 1 else results[0]
        
        return process


class StreamingNode(AsyncNode):
    """Node for streaming outputs in Gradio."""
    
    def __init__(self, stream_type: str = "text"):
        super().__init__(node_id="streaming")
        self.stream_type = stream_type
    
    async def exec_async(self, text: str) -> Iterator[str]:
        """Stream text output."""
        if self.stream_type == "text":
            # Simulate streaming text generation
            words = text.split()
            accumulated = ""
            
            for word in words:
                accumulated += word + " "
                await asyncio.sleep(0.1)  # Simulate generation delay
                yield accumulated.strip()
        
        elif self.stream_type == "tokens":
            # Stream individual tokens
            for char in text:
                await asyncio.sleep(0.05)
                yield char


class ChatInterfaceNode(ValidatedNode):
    """Specialized node for chat interfaces."""
    
    def __init__(self, 
                 system_prompt: str = "You are a helpful assistant.",
                 max_history: int = 10):
        super().__init__(node_id="chat_interface")
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.conversation_history = []
    
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate chat input."""
        if "message" not in data:
            raise ValueError("Message is required")
        
        if not isinstance(data["message"], str):
            raise ValueError("Message must be a string")
        
        return data
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare chat context."""
        return {
            "message": shared.get("chat_message", ""),
            "history": shared.get("chat_history", []),
            "user_id": shared.get("user_id", "default")
        }
    
    def exec(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process chat message."""
        message = context["message"]
        history = context["history"]
        
        logger.info(f"💬 Processing chat message: {message[:50]}...")
        
        # Add to history
        history.append({"role": "user", "content": message})
        
        # Generate response (mock)
        response = self._generate_response(message, history)
        
        # Add response to history
        history.append({"role": "assistant", "content": response})
        
        # Trim history if needed
        if len(history) > self.max_history * 2:
            history = history[-(self.max_history * 2):]
        
        return {
            "response": response,
            "history": history,
            "turn_count": len(history) // 2
        }
    
    def _generate_response(self, message: str, history: List[Dict]) -> str:
        """Generate chat response (mock)."""
        # In production, this would call an LLM
        responses = {
            "hello": "Hello! How can I help you today?",
            "how are you": "I'm doing well, thank you for asking!",
            "bye": "Goodbye! Have a great day!"
        }
        
        # Simple keyword matching
        message_lower = message.lower()
        for keyword, response in responses.items():
            if keyword in message_lower:
                return response
        
        return f"I understand you said: '{message}'. How can I assist you further?"
    
    def post(self, shared: Dict[str, Any], context: Dict, result: Dict[str, Any]) -> None:
        """Store chat results."""
        shared["chat_response"] = result["response"]
        shared["chat_history"] = result["history"]
        shared["turn_count"] = result["turn_count"]


class ImageProcessingNode(Node):
    """Node for image processing in Gradio."""
    
    def __init__(self, operations: List[str] = None):
        super().__init__(node_id="image_processing")
        self.operations = operations or ["resize", "filter", "enhance"]
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare image data."""
        return {
            "image": shared.get("input_image"),
            "operations": shared.get("selected_operations", self.operations)
        }
    
    def exec(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process image."""
        image_data = context["image"]
        operations = context["operations"]
        
        logger.info(f"🖼️ Processing image with operations: {operations}")
        
        # Mock image processing
        # In production, use PIL/OpenCV
        processed_image = image_data  # Mock: return same image
        
        metadata = {
            "original_size": "1024x768",  # Mock
            "processed_size": "512x384",  # Mock
            "operations_applied": operations,
            "processing_time": 0.5
        }
        
        return {
            "processed_image": processed_image,
            "metadata": metadata
        }
    
    def post(self, shared: Dict[str, Any], context: Dict, result: Dict[str, Any]) -> None:
        """Store processed image."""
        shared["output_image"] = result["processed_image"]
        shared["image_metadata"] = result["metadata"]


class AudioProcessingNode(AsyncNode):
    """Node for audio processing in Gradio."""
    
    def __init__(self, task: str = "transcribe"):
        super().__init__(node_id="audio_processing")
        self.task = task
    
    async def exec_async(self, audio_data: Any) -> Dict[str, Any]:
        """Process audio asynchronously."""
        logger.info(f"🎵 Processing audio for task: {self.task}")
        
        # Mock audio processing
        import asyncio
        await asyncio.sleep(1.0)  # Simulate processing
        
        if self.task == "transcribe":
            result = {
                "text": "This is a mock transcription of the audio.",
                "confidence": 0.95,
                "duration": 5.2
            }
        elif self.task == "analyze":
            result = {
                "features": {
                    "pitch": "medium",
                    "tempo": 120,
                    "energy": 0.7
                },
                "classification": "speech"
            }
        else:
            result = {"task": self.task, "status": "completed"}
        
        return result


class FileUploadNode(ValidatedNode):
    """Node for handling file uploads in Gradio."""
    
    def __init__(self, 
                 allowed_types: List[str] = None,
                 max_size_mb: float = 10.0):
        super().__init__(node_id="file_upload")
        self.allowed_types = allowed_types or [".txt", ".pdf", ".csv", ".json"]
        self.max_size_mb = max_size_mb
    
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate uploaded file."""
        file_path = data.get("file_path")
        
        if not file_path:
            raise ValueError("No file uploaded")
        
        # Check file extension
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.allowed_types:
            raise ValueError(f"File type {file_ext} not allowed. Allowed: {self.allowed_types}")
        
        # Check file size (mock)
        # In production, check actual file size
        
        return data
    
    def exec(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process uploaded file."""
        file_path = file_data["file_path"]
        
        logger.info(f"📁 Processing file: {file_path}")
        
        # Mock file processing
        file_info = {
            "name": Path(file_path).name,
            "type": Path(file_path).suffix,
            "size": "1.2 MB",  # Mock
            "preview": "File contents preview...",  # Mock
            "metadata": {
                "lines": 100,  # Mock
                "encoding": "utf-8"
            }
        }
        
        return file_info


class MultiModalNode(Node):
    """Node for handling multiple input types."""
    
    def __init__(self):
        super().__init__(node_id="multimodal")
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all input modalities."""
        return {
            "text": shared.get("input_text"),
            "image": shared.get("input_image"),
            "audio": shared.get("input_audio"),
            "file": shared.get("input_file")
        }
    
    def exec(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process multi-modal inputs."""
        logger.info("🎯 Processing multi-modal inputs")
        
        results = {
            "modalities_present": [],
            "analysis": {}
        }
        
        # Check which modalities are present
        if inputs.get("text"):
            results["modalities_present"].append("text")
            results["analysis"]["text"] = {
                "length": len(inputs["text"]),
                "language": "en"  # Mock
            }
        
        if inputs.get("image"):
            results["modalities_present"].append("image")
            results["analysis"]["image"] = {
                "format": "PNG",  # Mock
                "dimensions": "1024x768"
            }
        
        if inputs.get("audio"):
            results["modalities_present"].append("audio")
            results["analysis"]["audio"] = {
                "duration": "5.2s",  # Mock
                "format": "WAV"
            }
        
        if inputs.get("file"):
            results["modalities_present"].append("file")
            results["analysis"]["file"] = {
                "type": "document",
                "pages": 10  # Mock
            }
        
        # Generate combined analysis
        results["combined_summary"] = f"Received {len(results['modalities_present'])} inputs: " + \
                                     ", ".join(results["modalities_present"])
        
        return results
    
    def post(self, shared: Dict[str, Any], context: Dict, result: Dict[str, Any]) -> None:
        """Store multi-modal results."""
        shared["multimodal_results"] = result
        shared["modalities_count"] = len(result["modalities_present"])


class ProgressTrackingNode(Node):
    """Node that reports progress for Gradio progress bars."""
    
    def __init__(self, total_steps: int = 5):
        super().__init__(node_id="progress_tracking")
        self.total_steps = total_steps
        self.current_step = 0
    
    def exec(self, data: Any) -> Iterator[Dict[str, Any]]:
        """Execute with progress updates."""
        for i in range(self.total_steps):
            self.current_step = i + 1
            
            # Simulate work
            time.sleep(0.5)
            
            # Yield progress update
            yield {
                "step": self.current_step,
                "total": self.total_steps,
                "progress": self.current_step / self.total_steps,
                "message": f"Processing step {self.current_step} of {self.total_steps}..."
            }
        
        yield {
            "step": self.total_steps,
            "total": self.total_steps,
            "progress": 1.0,
            "message": "Processing complete!",
            "result": "Final result here"
        }


if __name__ == "__main__":
    # Test Gradio nodes
    import asyncio
    
    # Test chat interface
    chat = ChatInterfaceNode()
    shared = {"chat_message": "Hello, how are you?", "chat_history": []}
    result = chat.run(shared)
    print(f"Chat response: {shared['chat_response']}")
    
    # Test image processing
    image = ImageProcessingNode()
    shared = {"input_image": "mock_image_data", "selected_operations": ["resize", "enhance"]}
    result = image.run(shared)
    print(f"Image metadata: {shared['image_metadata']}")
    
    # Test multi-modal
    multi = MultiModalNode()
    shared = {
        "input_text": "Test text",
        "input_image": "mock_image",
        "input_audio": None,
        "input_file": "document.pdf"
    }
    result = multi.run(shared)
    print(f"Multi-modal analysis: {shared['multimodal_results']}")