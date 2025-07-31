#!/usr/bin/env python3
"""
Main Gradio interface examples for KayGraph.
"""

import argparse
import logging
from pathlib import Path
import time

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Graph, AsyncGraph
from gradio_nodes import (
    GradioInterfaceNode, ChatInterfaceNode, ImageProcessingNode,
    AudioProcessingNode, FileUploadNode, MultiModalNode,
    ProgressTrackingNode, GradioComponent
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mock gradio import
class MockGradio:
    """Mock Gradio for demonstration."""
    class Interface:
        def __init__(self, fn, inputs, outputs, **kwargs):
            self.fn = fn
            self.inputs = inputs
            self.outputs = outputs
            self.kwargs = kwargs
            logger.info(f"Created Gradio interface: {kwargs.get('title', 'Untitled')}")
        
        def launch(self, **kwargs):
            logger.info(f"Launching interface on port {kwargs.get('server_port', 7860)}")
            logger.info("Visit http://localhost:7860 to use the interface")
            # In production, this would actually launch the server
    
    class Blocks:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
        
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
        
        def launch(self, **kwargs):
            logger.info(f"Launching Blocks app on port {kwargs.get('server_port', 7860)}")
    
    class Textbox:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
    
    class Image:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
    
    class Audio:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
    
    class File:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
    
    class Button:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
        
        def click(self, fn, inputs, outputs):
            logger.info("Button click handler registered")
    
    class Markdown:
        def __init__(self, value):
            self.value = value
    
    class Row:
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
    
    class Column:
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
    
    class Tab:
        def __init__(self, label):
            self.label = label
        
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
    
    class Chatbot:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
    
    class Progress:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
        
        def __call__(self, value, desc=""):
            logger.info(f"Progress: {value} - {desc}")

# Use mock gradio
gr = MockGradio()


def create_chat_interface():
    """Create a chat interface with KayGraph."""
    # Build the workflow
    chat_node = ChatInterfaceNode(
        system_prompt="I'm a helpful KayGraph assistant.",
        max_history=20
    )
    
    graph = Graph(start=chat_node)
    
    def chat_function(message, history):
        """Process chat message through KayGraph."""
        shared = {
            "chat_message": message,
            "chat_history": history or []
        }
        
        graph.run(shared)
        
        response = shared.get("chat_response", "Sorry, I couldn't process that.")
        return response
    
    # Create Gradio interface
    interface = gr.Interface(
        fn=chat_function,
        inputs=[
            gr.Textbox(lines=2, placeholder="Enter your message here..."),
            "state"  # For history
        ],
        outputs="text",
        title="KayGraph Chat Assistant",
        description="Chat with a KayGraph-powered assistant",
        examples=[
            ["Hello, how are you?", []],
            ["What can you help me with?", []],
            ["Tell me about KayGraph", []]
        ]
    )
    
    return interface


def create_image_processing_interface():
    """Create an image processing interface."""
    # Build the workflow
    image_node = ImageProcessingNode(
        operations=["resize", "rotate", "filter", "enhance"]
    )
    
    graph = Graph(start=image_node)
    
    def process_image(image, operations):
        """Process image through KayGraph."""
        shared = {
            "input_image": image,
            "selected_operations": operations
        }
        
        graph.run(shared)
        
        # Return processed image and metadata
        return shared.get("output_image", image), str(shared.get("image_metadata", {}))
    
    # Create interface
    interface = gr.Interface(
        fn=process_image,
        inputs=[
            gr.Image(type="filepath", label="Upload Image"),
            gr.CheckboxGroup(
                choices=["resize", "rotate", "filter", "enhance"],
                label="Select Operations",
                value=["resize"]
            )
        ],
        outputs=[
            gr.Image(label="Processed Image"),
            gr.Textbox(label="Processing Info")
        ],
        title="KayGraph Image Processor",
        description="Process images using KayGraph workflows"
    )
    
    return interface


def create_multimodal_interface():
    """Create a multi-modal interface."""
    # Build the workflow
    multi_node = MultiModalNode()
    graph = Graph(start=multi_node)
    
    def process_multimodal(text, image, audio, file):
        """Process multiple input types."""
        shared = {
            "input_text": text,
            "input_image": image,
            "input_audio": audio,
            "input_file": file
        }
        
        graph.run(shared)
        
        results = shared.get("multimodal_results", {})
        return json.dumps(results, indent=2)
    
    # Create interface
    interface = gr.Interface(
        fn=process_multimodal,
        inputs=[
            gr.Textbox(label="Text Input", placeholder="Enter text..."),
            gr.Image(label="Image Input", type="filepath"),
            gr.Audio(label="Audio Input", type="filepath"),
            gr.File(label="File Input")
        ],
        outputs=gr.Textbox(label="Analysis Results", lines=10),
        title="KayGraph Multi-Modal Analyzer",
        description="Analyze multiple input types with KayGraph"
    )
    
    return interface


def create_document_interface():
    """Create a document processing interface."""
    # Build the workflow
    upload_node = FileUploadNode(
        allowed_types=[".txt", ".pdf", ".docx", ".md"],
        max_size_mb=10.0
    )
    
    graph = Graph(start=upload_node)
    
    def process_document(file):
        """Process uploaded document."""
        if not file:
            return "Please upload a file"
        
        shared = {"file_path": file.name if hasattr(file, 'name') else str(file)}
        
        try:
            graph.run(shared)
            result = shared.get("file_upload_result", {})
            return f"File: {result.get('name', 'Unknown')}\n" \
                   f"Type: {result.get('type', 'Unknown')}\n" \
                   f"Size: {result.get('size', 'Unknown')}\n\n" \
                   f"Preview:\n{result.get('preview', 'No preview available')}"
        except Exception as e:
            return f"Error processing file: {str(e)}"
    
    # Create interface
    interface = gr.Interface(
        fn=process_document,
        inputs=gr.File(label="Upload Document"),
        outputs=gr.Textbox(label="Document Analysis", lines=10),
        title="KayGraph Document Analyzer",
        description="Analyze documents with KayGraph"
    )
    
    return interface


def create_progress_interface():
    """Create interface with progress tracking."""
    # Build the workflow
    progress_node = ProgressTrackingNode(total_steps=5)
    graph = Graph(start=progress_node)
    
    def process_with_progress(input_text, progress=gr.Progress()):
        """Process with progress updates."""
        shared = {"input_data": input_text}
        
        # Run the node and get progress updates
        node_result = progress_node.run(shared)
        
        # Simulate progress updates
        for update in progress_node.exec(input_text):
            progress(
                update["progress"],
                desc=update["message"]
            )
            time.sleep(0.5)
        
        return "Processing complete! ✅"
    
    # Create interface
    interface = gr.Interface(
        fn=process_with_progress,
        inputs=gr.Textbox(label="Input", placeholder="Enter something to process..."),
        outputs=gr.Textbox(label="Result"),
        title="KayGraph Progress Demo",
        description="See progress tracking with KayGraph"
    )
    
    return interface


def create_blocks_app():
    """Create a more complex Blocks-based app."""
    with gr.Blocks(title="KayGraph Advanced Demo") as demo:
        gr.Markdown("# 🚀 KayGraph Advanced Interface")
        gr.Markdown("Explore different KayGraph capabilities in one place")
        
        with gr.Tab("Chat"):
            chatbot = gr.Chatbot()
            msg = gr.Textbox(label="Message", placeholder="Type a message...")
            clear = gr.Button("Clear")
            
            # In production, you would wire up the chat functionality here
            
        with gr.Tab("Image Processing"):
            with gr.Row():
                with gr.Column():
                    img_input = gr.Image(label="Input Image")
                    img_ops = gr.CheckboxGroup(
                        ["resize", "rotate", "filter", "enhance"],
                        label="Operations"
                    )
                    img_btn = gr.Button("Process", variant="primary")
                
                with gr.Column():
                    img_output = gr.Image(label="Output Image")
                    img_info = gr.Textbox(label="Processing Info")
            
            # In production, wire up image processing
            
        with gr.Tab("Multi-Modal"):
            gr.Markdown("### Upload different types of content")
            
            mm_text = gr.Textbox(label="Text")
            mm_image = gr.Image(label="Image")
            mm_audio = gr.Audio(label="Audio")
            mm_file = gr.File(label="File")
            mm_analyze = gr.Button("Analyze All", variant="primary")
            mm_output = gr.JSON(label="Analysis Results")
            
            # In production, wire up multi-modal analysis
        
        with gr.Tab("About"):
            gr.Markdown("""
            ### About KayGraph + Gradio
            
            This demo showcases how KayGraph workflows can be integrated with Gradio interfaces:
            
            - **Chat Interface**: Build conversational AI with memory
            - **Image Processing**: Create image manipulation pipelines
            - **Multi-Modal**: Handle multiple input types
            - **Progress Tracking**: Show real-time progress
            
            KayGraph provides the workflow engine, while Gradio provides the UI.
            """)
    
    return demo


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="KayGraph Gradio Interface Examples"
    )
    
    parser.add_argument(
        "--interface",
        choices=["chat", "image", "document", "multimodal", "progress", "blocks"],
        default="chat",
        help="Interface type to launch"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public sharing link"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port to run on"
    )
    
    args = parser.parse_args()
    
    logger.info(f"🎨 Starting KayGraph Gradio {args.interface} interface...")
    
    # Create the appropriate interface
    if args.interface == "chat":
        interface = create_chat_interface()
    elif args.interface == "image":
        interface = create_image_processing_interface()
    elif args.interface == "document":
        interface = create_document_interface()
    elif args.interface == "multimodal":
        interface = create_multimodal_interface()
    elif args.interface == "progress":
        interface = create_progress_interface()
    elif args.interface == "blocks":
        interface = create_blocks_app()
    
    # Launch the interface
    interface.launch(
        share=args.share,
        server_port=args.port,
        server_name="0.0.0.0" if args.share else "127.0.0.1"
    )
    
    # Keep running
    logger.info("Interface is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == "__main__":
    import json  # Add missing import
    main()