#!/usr/bin/env python3
"""
KayGraph Template Generator - Create starter code for common patterns

Usage:
    python generate_templates.py <pattern> <name> [--output-dir PATH]
    
Examples:
    python generate_templates.py node MyTask
    python generate_templates.py agent ResearchAgent
    python generate_templates.py rag DocumentQA
"""

import os
import sys
from pathlib import Path
import argparse
from datetime import datetime

TEMPLATES = {
    "node": {
        "description": "Basic node with prep/exec/post lifecycle",
        "files": {
            "nodes.py": '''"""
{name} Node Implementation
Generated on: {date}
"""
from kaygraph import Node


class {class_name}Node(Node):
    """
    {description}
    
    This node follows the standard 3-phase lifecycle:
    1. prep: Read from shared store
    2. exec: Process data (pure computation)
    3. post: Write results to shared store
    """
    
    def prep(self, shared):
        """Prepare data for execution"""
        # Read required data from shared store
        input_data = shared.get("{input_key}", None)
        if input_data is None:
            raise ValueError("{input_key} not found in shared store")
        return input_data
    
    def exec(self, prep_res):
        """Execute the main logic - NO shared access here"""
        # TODO: Implement your processing logic
        # Example: result = process_data(prep_res)
        result = f"Processed: {{prep_res}}"
        return result
    
    def post(self, shared, prep_res, exec_res):
        """Store results and determine next action"""
        # Write results to shared store
        shared["{output_key}"] = exec_res
        
        # Return next action (None means "default")
        return None
''',
            "main.py": '''"""
{name} - Main entry point
Generated on: {date}
"""
from kaygraph import Graph
from nodes import {class_name}Node


def main():
    # Create the graph
    graph = Graph()
    
    # Create and add nodes
    {var_name}_node = {class_name}Node("{node_id}")
    graph.add_node({var_name}_node)
    
    # Define the flow (if multiple nodes)
    # node1 >> node2  # Default action
    # node1 >> ("success", node2)  # Named action
    
    # Prepare shared context
    shared = {{
        "{input_key}": "Your input data here"
    }}
    
    # Run the graph
    graph.run(shared)
    
    # Display results
    print(f"Result: {{shared.get('{output_key}')}}")


if __name__ == "__main__":
    main()
''',
        }
    },
    
    "async_node": {
        "description": "Async node for I/O-bound operations",
        "files": {
            "nodes.py": '''"""
{name} Async Node Implementation
Generated on: {date}
"""
from kaygraph import AsyncNode
import asyncio


class {class_name}Node(AsyncNode):
    """
    Async node for {description}
    
    Use this pattern for:
    - API calls
    - Database operations
    - File I/O
    - Network requests
    """
    
    async def prep(self, shared):
        """Prepare data for async execution"""
        input_data = shared.get("{input_key}", None)
        if input_data is None:
            raise ValueError("{input_key} not found in shared store")
        return input_data
    
    async def exec(self, prep_res):
        """Execute async operations - NO shared access here"""
        # TODO: Implement your async logic
        # Example: result = await async_api_call(prep_res)
        await asyncio.sleep(0.1)  # Simulate async work
        result = f"Async processed: {{prep_res}}"
        return result
    
    async def post(self, shared, prep_res, exec_res):
        """Store results asynchronously"""
        shared["{output_key}"] = exec_res
        return None
''',
        }
    },
    
    "batch_node": {
        "description": "Batch processing node for data collections",
        "files": {
            "nodes.py": '''"""
{name} Batch Node Implementation
Generated on: {date}
"""
from kaygraph import BatchNode


class {class_name}Node(BatchNode):
    """
    Batch processing node for {description}
    
    Processes collections of items efficiently.
    Each item goes through prep/exec/post independently.
    """
    
    def prep(self, shared):
        """Prepare batch data"""
        items = shared.get("{input_key}", [])
        if not items:
            raise ValueError("No items to process in {input_key}")
        return items
    
    def exec(self, item):
        """Process individual item - called for each item"""
        # TODO: Process each item
        result = f"Processed item: {{item}}"
        return result
    
    def post(self, shared, items, results):
        """Store all results after batch processing"""
        shared["{output_key}"] = results
        
        # Optional: Store summary
        shared["{output_key}_count"] = len(results)
        return None
''',
        }
    },
    
    "agent": {
        "description": "Autonomous agent with decision-making",
        "files": {
            "nodes.py": '''"""
{name} Agent Implementation
Generated on: {date}
"""
from kaygraph import Node


class ObserveNode(Node):
    """Observe the environment and gather information"""
    
    def prep(self, shared):
        return shared.get("environment", {{}})
    
    def exec(self, environment):
        # TODO: Implement observation logic
        observation = {{
            "status": "observed",
            "data": environment
        }}
        return observation
    
    def post(self, shared, prep_res, exec_res):
        shared["observation"] = exec_res
        return "think"  # Next: thinking


class ThinkNode(Node):
    """Analyze observations and plan actions"""
    
    def prep(self, shared):
        return {{
            "observation": shared.get("observation"),
            "history": shared.get("history", [])
        }}
    
    def exec(self, data):
        # TODO: Implement reasoning logic
        # This is where you'd call an LLM for decision making
        thought = {{
            "analysis": "Based on observation...",
            "next_action": "act",
            "confidence": 0.8
        }}
        return thought
    
    def post(self, shared, prep_res, exec_res):
        shared["thought"] = exec_res
        
        # Update history
        history = shared.get("history", [])
        history.append(exec_res)
        shared["history"] = history
        
        return exec_res["next_action"]


class ActNode(Node):
    """Execute the planned action"""
    
    def prep(self, shared):
        return shared.get("thought")
    
    def exec(self, thought):
        # TODO: Implement action execution
        action_result = {{
            "action": "performed_action",
            "success": True,
            "output": "Action completed"
        }}
        return action_result
    
    def post(self, shared, prep_res, exec_res):
        shared["last_action"] = exec_res
        
        # Decide whether to continue or stop
        if exec_res["success"]:
            return "observe"  # Continue the loop
        else:
            return "error"  # Handle error
''',
            "graph.py": '''"""
{name} Agent Graph Configuration
Generated on: {date}
"""
from kaygraph import Graph
from nodes import ObserveNode, ThinkNode, ActNode


def create_agent_graph():
    """Create the agent decision-making graph"""
    graph = Graph()
    
    # Create nodes
    observe = ObserveNode("observe")
    think = ThinkNode("think")
    act = ActNode("act")
    
    # Add nodes to graph
    graph.add_node(observe)
    graph.add_node(think)
    graph.add_node(act)
    
    # Define the agent loop
    observe >> ("think", think)
    think >> ("act", act)
    act >> ("observe", observe)  # Loop back
    
    # Optional: Add error handling
    # error_handler = ErrorNode("error")
    # graph.add_node(error_handler)
    # act >> ("error", error_handler)
    
    return graph
''',
            "main.py": '''"""
{name} Agent - Main entry point
Generated on: {date}
"""
from graph import create_agent_graph


def main():
    # Create the agent graph
    graph = create_agent_graph()
    
    # Initialize shared context
    shared = {{
        "environment": {{
            "task": "Your task description",
            "constraints": [],
            "resources": []
        }},
        "history": [],
        "max_iterations": 5
    }}
    
    # Run the agent
    graph.run(shared, start_node="observe")
    
    # Display results
    print(f"Final thought: {{shared.get('thought')}}")
    print(f"Last action: {{shared.get('last_action')}}")
    print(f"History length: {{len(shared.get('history', []))}}")


if __name__ == "__main__":
    main()
''',
        }
    },
    
    "rag": {
        "description": "Retrieval-Augmented Generation pipeline",
        "files": {
            "nodes.py": '''"""
{name} RAG Implementation
Generated on: {date}
"""
from kaygraph import Node, BatchNode


class ChunkDocumentsNode(BatchNode):
    """Split documents into chunks for processing"""
    
    def prep(self, shared):
        return shared.get("documents", [])
    
    def exec(self, document):
        # TODO: Implement chunking logic
        # Simple example - split by paragraphs
        chunks = document.split("\\n\\n")
        return [{{
            "text": chunk.strip(),
            "source": "document",
            "index": i
        }} for i, chunk in enumerate(chunks) if chunk.strip()]
    
    def post(self, shared, docs, all_chunks):
        # Flatten nested list of chunks
        flat_chunks = [chunk for doc_chunks in all_chunks for chunk in doc_chunks]
        shared["chunks"] = flat_chunks
        return "embed"


class EmbedChunksNode(BatchNode):
    """Generate embeddings for chunks"""
    
    def prep(self, shared):
        return shared.get("chunks", [])
    
    def exec(self, chunk):
        # TODO: Generate real embeddings
        # Example: embedding = generate_embedding(chunk["text"])
        import hashlib
        fake_embedding = [float(ord(c)) for c in hashlib.md5(
            chunk["text"].encode()).hexdigest()[:8]]
        
        return {{
            "chunk": chunk,
            "embedding": fake_embedding
        }}
    
    def post(self, shared, chunks, embeddings):
        shared["embeddings"] = embeddings
        return "index"


class CreateIndexNode(Node):
    """Create searchable index from embeddings"""
    
    def prep(self, shared):
        return shared.get("embeddings", [])
    
    def exec(self, embeddings):
        # TODO: Create real vector index
        # Example: index = create_faiss_index(embeddings)
        index = {{
            "type": "simple_index",
            "embeddings": embeddings,
            "dimension": len(embeddings[0]["embedding"]) if embeddings else 0
        }}
        return index
    
    def post(self, shared, prep_res, exec_res):
        shared["index"] = exec_res
        return None  # End of indexing phase


class RetrieveNode(Node):
    """Retrieve relevant chunks for query"""
    
    def prep(self, shared):
        return {{
            "query": shared.get("query"),
            "index": shared.get("index"),
            "top_k": shared.get("top_k", 3)
        }}
    
    def exec(self, data):
        # TODO: Implement vector search
        # Example: results = search_index(data["index"], data["query"], data["top_k"])
        
        # Mock retrieval - return top chunks
        results = data["index"]["embeddings"][:data["top_k"]]
        return results
    
    def post(self, shared, prep_res, exec_res):
        shared["retrieved_chunks"] = exec_res
        return "generate"


class GenerateAnswerNode(Node):
    """Generate answer using retrieved context"""
    
    def prep(self, shared):
        return {{
            "query": shared.get("query"),
            "context": shared.get("retrieved_chunks", [])
        }}
    
    def exec(self, data):
        # TODO: Call LLM with context
        # Example: answer = generate_answer_with_llm(data["query"], data["context"])
        
        context_text = "\\n".join([
            chunk["chunk"]["text"] for chunk in data["context"]
        ])
        
        answer = f"""Based on the context, here's the answer to "{{data['query']}}":
        
        [Generated answer would go here]
        
        Context used: {{len(data['context'])}} chunks"""
        
        return answer
    
    def post(self, shared, prep_res, exec_res):
        shared["answer"] = exec_res
        return None  # End of pipeline
''',
            "graph.py": '''"""
{name} RAG Graph Configuration
Generated on: {date}
"""
from kaygraph import Graph
from nodes import (
    ChunkDocumentsNode, EmbedChunksNode, CreateIndexNode,
    RetrieveNode, GenerateAnswerNode
)


def create_indexing_graph():
    """Create the offline indexing graph"""
    graph = Graph()
    
    # Indexing nodes
    chunk = ChunkDocumentsNode("chunk")
    embed = EmbedChunksNode("embed")
    index = CreateIndexNode("index")
    
    graph.add_node(chunk)
    graph.add_node(embed)
    graph.add_node(index)
    
    # Define flow
    chunk >> ("embed", embed)
    embed >> ("index", index)
    
    return graph


def create_query_graph():
    """Create the online query graph"""
    graph = Graph()
    
    # Query nodes
    retrieve = RetrieveNode("retrieve")
    generate = GenerateAnswerNode("generate")
    
    graph.add_node(retrieve)
    graph.add_node(generate)
    
    # Define flow
    retrieve >> ("generate", generate)
    
    return graph
''',
        }
    },
    
    "workflow": {
        "description": "Multi-step workflow orchestration",
        "files": {
            "nodes.py": '''"""
{name} Workflow Implementation
Generated on: {date}
"""
from kaygraph import Node, ValidatedNode


class ValidateInputNode(ValidatedNode):
    """Validate workflow inputs"""
    
    input_schema = {{
        "type": "object",
        "properties": {{
            "{input_key}": {{"type": "string"}},
            "config": {{"type": "object"}}
        }},
        "required": ["{input_key}"]
    }}
    
    def prep(self, shared):
        return {{
            "{input_key}": shared.get("{input_key}"),
            "config": shared.get("config", {{}})
        }}
    
    def exec(self, inputs):
        # Validation happens automatically via ValidatedNode
        return {{"validated": True, "inputs": inputs}}
    
    def post(self, shared, prep_res, exec_res):
        shared["validated_inputs"] = exec_res
        return "process"


class ProcessStep1Node(Node):
    """First processing step"""
    
    def prep(self, shared):
        return shared.get("validated_inputs")
    
    def exec(self, validated_data):
        # TODO: Implement step 1 logic
        result = {{
            "step": 1,
            "status": "completed",
            "output": f"Processed: {{validated_data}}"
        }}
        return result
    
    def post(self, shared, prep_res, exec_res):
        shared["step1_result"] = exec_res
        
        # Conditional routing
        if exec_res["status"] == "completed":
            return "step2"
        else:
            return "error"


class ProcessStep2Node(Node):
    """Second processing step"""
    
    def prep(self, shared):
        return {{
            "step1": shared.get("step1_result"),
            "config": shared.get("config", {{}})
        }}
    
    def exec(self, data):
        # TODO: Implement step 2 logic
        result = {{
            "step": 2,
            "status": "completed",
            "output": f"Enhanced: {{data['step1']['output']}}"
        }}
        return result
    
    def post(self, shared, prep_res, exec_res):
        shared["step2_result"] = exec_res
        return "finalize"


class FinalizeNode(Node):
    """Finalize workflow and prepare output"""
    
    def prep(self, shared):
        return {{
            "step1": shared.get("step1_result"),
            "step2": shared.get("step2_result")
        }}
    
    def exec(self, results):
        # TODO: Combine results and create final output
        final_output = {{
            "status": "success",
            "steps_completed": 2,
            "final_result": results["step2"]["output"],
            "summary": "Workflow completed successfully"
        }}
        return final_output
    
    def post(self, shared, prep_res, exec_res):
        shared["{output_key}"] = exec_res
        return None  # End workflow
''',
        }
    }
}


def generate_template(template_type, name, output_dir):
    """Generate template files for the specified pattern"""
    if template_type not in TEMPLATES:
        print(f"Error: Unknown template type '{template_type}'")
        print(f"Available templates: {', '.join(TEMPLATES.keys())}")
        return False
    
    template = TEMPLATES[template_type]
    
    # Create output directory
    output_path = Path(output_dir) / name.lower().replace(" ", "_")
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate variable names
    class_name = "".join(word.capitalize() for word in name.split())
    var_name = "_".join(name.lower().split())
    node_id = var_name
    
    # Common replacements
    replacements = {
        "{name}": name,
        "{class_name}": class_name,
        "{var_name}": var_name,
        "{node_id}": node_id,
        "{input_key}": f"{var_name}_input",
        "{output_key}": f"{var_name}_output",
        "{description}": template["description"],
        "{date}": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Generate files
    for filename, content in template["files"].items():
        file_content = content
        for key, value in replacements.items():
            file_content = file_content.replace(key, value)
        
        file_path = output_path / filename
        with open(file_path, 'w') as f:
            f.write(file_content)
        print(f"✓ Created: {file_path}")
    
    # Create utils directory if needed
    if template_type in ["agent", "rag"]:
        utils_dir = output_path / "utils"
        utils_dir.mkdir(exist_ok=True)
        
        # Create __init__.py
        (utils_dir / "__init__.py").touch()
        
        # Create placeholder LLM wrapper
        llm_wrapper = utils_dir / "call_llm.py"
        with open(llm_wrapper, 'w') as f:
            f.write('''"""
LLM wrapper - implement your preferred LLM here
"""

def call_llm(prompt, **kwargs):
    """
    Call your LLM of choice
    
    Args:
        prompt: The prompt to send
        **kwargs: Additional parameters (temperature, max_tokens, etc.)
    
    Returns:
        str: LLM response
    """
    # TODO: Implement your LLM call
    # Example with OpenAI:
    # response = openai.chat.completions.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": prompt}],
    #     **kwargs
    # )
    # return response.choices[0].message.content
    
    return f"[LLM would process: {prompt[:50]}...]"
''')
        print(f"✓ Created: {llm_wrapper}")
    
    # Create requirements.txt
    req_path = output_path / "requirements.txt"
    with open(req_path, 'w') as f:
        f.write("kaygraph\n")
        if template_type == "rag":
            f.write("# For embeddings and vector search:\n")
            f.write("# numpy\n# faiss-cpu\n")
        if template_type in ["agent", "rag"]:
            f.write("# For LLM calls:\n")
            f.write("# openai\n# anthropic\n# litellm\n")
    print(f"✓ Created: {req_path}")
    
    # Create README
    readme_path = output_path / "README.md"
    with open(readme_path, 'w') as f:
        f.write(f"""# {name}

{template['description']}

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Implement TODOs in the code:
   - Complete the processing logic in `nodes.py`
   - Add any utility functions needed

3. Run the application:
   ```bash
   python main.py
   ```

## Structure

- `nodes.py` - Node implementations
- `main.py` - Entry point
""")
        if "graph.py" in template["files"]:
            f.write("- `graph.py` - Graph configuration\n")
        if template_type in ["agent", "rag"]:
            f.write("- `utils/` - Utility functions (LLM calls, etc.)\n")
        
        f.write(f"""
## Pattern: {template_type}

This template implements the {template_type} pattern with KayGraph.

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
""")
    print(f"✓ Created: {readme_path}")
    
    print(f"\n✅ Successfully generated {template_type} template: {output_path}")
    print(f"\n📝 Next steps:")
    print(f"1. cd {output_path}")
    print(f"2. Review and implement TODOs in the generated code")
    print(f"3. Run with: python main.py")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate KayGraph template code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available templates:
  node         - Basic node with prep/exec/post lifecycle
  async_node   - Async node for I/O operations  
  batch_node   - Batch processing for collections
  agent        - Autonomous agent with observe/think/act loop
  rag          - Retrieval-Augmented Generation pipeline
  workflow     - Multi-step workflow orchestration

Examples:
  python generate_templates.py node MyTask
  python generate_templates.py agent ResearchBot
  python generate_templates.py rag DocumentQA --output-dir ./projects
"""
    )
    
    parser.add_argument("template", 
                       choices=list(TEMPLATES.keys()),
                       help="Template type to generate")
    parser.add_argument("name", 
                       help="Name for your component")
    parser.add_argument("--output-dir", 
                       default="./generated",
                       help="Output directory (default: ./generated)")
    
    args = parser.parse_args()
    
    success = generate_template(args.template, args.name, args.output_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()