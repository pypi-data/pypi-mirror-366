# KayGraph Gradio Integration

This example demonstrates how to build interactive AI interfaces using Gradio with KayGraph workflows, enabling rapid prototyping of ML applications with rich UI components.

## Features

1. **Interactive Interfaces**: Build web UIs for KayGraph workflows
2. **Multi-Modal Support**: Handle text, image, audio, and video
3. **Real-time Processing**: Stream results as they're generated
4. **Component Library**: Rich set of input/output components
5. **Sharing & Deployment**: Easy sharing and deployment options

## Quick Start

```bash
# Install dependencies
pip install gradio

# Run basic demo
python main.py

# Run with sharing enabled
python main.py --share

# Run specific interface
python main.py --interface chat
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Gradio UI     │────▶│  Interface Node │────▶│ KayGraph Flow   │
│  (Components)   │     │   (Handler)     │     │  (Processing)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ↑                                                │
         └────────────── Results ─────────────────────────┘
```

## Example Interfaces

### 1. Chat Interface
```python
# Interactive chat with memory
python main.py --interface chat
```

### 2. Image Processing Pipeline
```python
# Multi-step image processing
python main.py --interface image
```

### 3. Document Analysis
```python
# Upload and analyze documents
python main.py --interface document
```

### 4. Audio Transcription
```python
# Real-time audio processing
python main.py --interface audio
```

### 5. Multi-Modal Assistant
```python
# Combined text, image, audio
python main.py --interface multimodal
```

## Key Components

### 1. GradioInterfaceNode
Base node for Gradio integration:
- Define input/output components
- Handle user interactions
- Map to KayGraph workflows

### 2. StreamingNode
Enable streaming outputs:
- Real-time text generation
- Progressive image rendering
- Live audio streaming

### 3. ComponentNode
Manage Gradio components:
- Dynamic component creation
- State management
- Event handling

### 4. ChatInterfaceNode
Specialized chat interface:
- Message history
- Streaming responses
- Multi-turn conversations

## Usage Examples

### Basic Interface
```python
def create_interface():
    return gr.Interface(
        fn=process_with_kaygraph,
        inputs=gr.Textbox(label="Input"),
        outputs=gr.Textbox(label="Output"),
        title="KayGraph Demo"
    )
```

### Custom Layout
```python
with gr.Blocks() as demo:
    gr.Markdown("# KayGraph Assistant")
    
    with gr.Row():
        input_text = gr.Textbox(label="Query")
        submit_btn = gr.Button("Process")
    
    output = gr.Textbox(label="Result")
    
    submit_btn.click(
        fn=workflow.run,
        inputs=input_text,
        outputs=output
    )
```

### Streaming Interface
```python
def stream_response(message, history):
    graph = build_streaming_graph()
    for chunk in graph.stream({"message": message}):
        yield chunk
```

## Advanced Features

### 1. Progress Tracking
```python
def process_with_progress(input_data, progress=gr.Progress()):
    progress(0, desc="Starting...")
    
    # Run workflow with progress updates
    for i, step in enumerate(workflow_steps):
        result = step.run(input_data)
        progress((i+1)/len(workflow_steps), desc=f"Step {i+1}")
    
    return result
```

### 2. File Handling
```python
def process_file(file):
    # Handle uploaded file
    graph = FileProcessingGraph()
    return graph.run({"file_path": file.name})
```

### 3. Multi-Step Forms
```python
with gr.Blocks() as demo:
    with gr.Tab("Step 1"):
        # First step inputs
    with gr.Tab("Step 2"):
        # Second step inputs
    with gr.Tab("Results"):
        # Final results
```

### 4. Real-time Updates
```python
def live_update():
    while True:
        yield get_current_state()
        time.sleep(1)

demo = gr.Interface(
    live_update,
    None,
    "text",
    live=True
)
```

## Component Types

### Input Components
- **Textbox**: Text input
- **Image**: Image upload/webcam
- **Audio**: Audio recording/upload
- **Video**: Video upload
- **File**: Generic file upload
- **Slider**: Numeric input
- **Dropdown**: Selection input
- **Checkbox**: Boolean input
- **Radio**: Single choice
- **CheckboxGroup**: Multiple choice

### Output Components
- **Textbox**: Text display
- **Image**: Image display
- **Audio**: Audio playback
- **Video**: Video playback
- **Label**: Classification results
- **JSON**: Structured data
- **HTML**: Rich content
- **Dataframe**: Tabular data
- **Plot**: Charts and graphs
- **Gallery**: Image collection

## Deployment

### Local Development
```bash
python app.py
# Access at http://localhost:7860
```

### Public Sharing
```bash
python app.py --share
# Get public URL for 72 hours
```

### Hugging Face Spaces
```bash
# Create space on HuggingFace
# Push your code
git push origin main
```

### Docker Deployment
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["python", "app.py"]
```

## Configuration

```python
interface_config = {
    "title": "KayGraph AI Assistant",
    "description": "Powered by KayGraph workflows",
    "theme": "default",  # or "dark", "compact"
    "analytics_enabled": False,
    "show_error_details": True,
    "cache_examples": True,
    "queue": {
        "enabled": True,
        "max_workers": 4
    }
}
```

## Best Practices

1. **Input Validation**: Validate inputs before processing
2. **Error Handling**: Show user-friendly error messages
3. **Progress Feedback**: Use progress bars for long operations
4. **Caching**: Cache results for common inputs
5. **Rate Limiting**: Implement rate limits for public deployments

## Integration Examples

### With RAG Pipeline
```python
# Document Q&A interface
interface = create_rag_interface(
    index_path="./index",
    model="gpt-3.5-turbo"
)
```

### With Image Generation
```python
# Text-to-image interface
interface = create_image_gen_interface(
    model="stable-diffusion",
    steps=50
)
```

### With Data Analysis
```python
# CSV analysis interface
interface = create_data_analysis_interface(
    allowed_operations=["filter", "aggregate", "visualize"]
)
```

## Troubleshooting

- **Port in use**: Change port with `--port 7861`
- **Memory issues**: Enable queue for large files
- **Slow loading**: Use async processing
- **CORS errors**: Configure allowed origins