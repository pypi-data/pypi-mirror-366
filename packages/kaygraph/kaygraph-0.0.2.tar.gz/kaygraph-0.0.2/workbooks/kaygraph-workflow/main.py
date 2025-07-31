"""
Writing workflow example using KayGraph.

Demonstrates a complete content creation workflow:
1. Outline generation
2. Content writing
3. Style application
"""

import logging
from kaygraph import Node, Graph, ValidatedNode
from utils.writing_tools import (
    generate_outline, write_content, apply_style,
    WRITING_STYLES
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class TopicNode(ValidatedNode):
    """Validate and prepare the topic."""
    
    def validate_input(self, prep_res):
        """Ensure topic is valid."""
        if not prep_res or not prep_res.strip():
            raise ValueError("Topic cannot be empty")
        return prep_res.strip()
    
    def prep(self, shared):
        """Get topic from shared state."""
        return shared.get("topic", "")
    
    def exec(self, topic):
        """Process and enhance topic."""
        # Could add topic analysis here
        return {
            "topic": topic,
            "word_count_target": shared.get("word_count", 500),
            "audience": shared.get("audience", "general")
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store processed topic info."""
        shared["topic_info"] = exec_res
        self.logger.info(f"Topic: {exec_res['topic']}")
        return "default"


class OutlineNode(Node):
    """Generate content outline."""
    
    def prep(self, shared):
        """Get topic information."""
        return shared.get("topic_info", {})
    
    def exec(self, topic_info):
        """Generate outline."""
        outline = generate_outline(
            topic_info["topic"],
            topic_info["word_count_target"]
        )
        self.logger.info(f"Generated outline with {len(outline['sections'])} sections")
        return outline
    
    def post(self, shared, prep_res, exec_res):
        """Store outline."""
        shared["outline"] = exec_res
        return "default"


class WritingNode(Node):
    """Write content based on outline."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(max_retries=2, wait=1, *args, **kwargs)
    
    def prep(self, shared):
        """Prepare writing context."""
        return {
            "topic": shared.get("topic_info", {}).get("topic", ""),
            "outline": shared.get("outline", {}),
            "audience": shared.get("topic_info", {}).get("audience", "general")
        }
    
    def exec(self, context):
        """Write the content."""
        content = write_content(
            context["topic"],
            context["outline"],
            context["audience"]
        )
        
        self.logger.info(f"Written {len(content['paragraphs'])} paragraphs")
        return content
    
    def post(self, shared, prep_res, exec_res):
        """Store written content."""
        shared["content"] = exec_res
        return "default"


class StyleNode(Node):
    """Apply writing style to content."""
    
    def prep(self, shared):
        """Get content and style preference."""
        return {
            "content": shared.get("content", {}),
            "style": shared.get("style", "professional")
        }
    
    def exec(self, context):
        """Apply style to content."""
        styled_content = apply_style(
            context["content"],
            context["style"]
        )
        
        self.logger.info(f"Applied {context['style']} style")
        return styled_content
    
    def post(self, shared, prep_res, exec_res):
        """Store final content."""
        shared["final_content"] = exec_res
        
        # Print result
        print("\n" + "=" * 60)
        print("FINAL CONTENT")
        print("=" * 60)
        print(f"\nTitle: {exec_res['title']}")
        print(f"Style: {exec_res['style']}")
        print(f"\n{exec_res['formatted_content']}")
        print("\n" + "=" * 60)
        
        return "default"


def create_writing_workflow():
    """Create the writing workflow graph."""
    # Create nodes
    topic_node = TopicNode(node_id="topic")
    outline_node = OutlineNode(node_id="outline")
    writing_node = WritingNode(node_id="write")
    style_node = StyleNode(node_id="style")
    
    # Connect workflow
    topic_node >> outline_node >> writing_node >> style_node
    
    # Create graph
    graph = Graph(start=topic_node)
    return graph


def main():
    """Run the writing workflow example."""
    print("KayGraph Writing Workflow")
    print("=" * 40)
    
    # Example topics and styles
    examples = [
        {
            "topic": "The Benefits of Regular Exercise",
            "style": "motivational",
            "word_count": 300,
            "audience": "fitness beginners"
        },
        {
            "topic": "Introduction to Machine Learning",
            "style": "educational",
            "word_count": 500,
            "audience": "tech students"
        },
        {
            "topic": "Sustainable Living Tips",
            "style": "casual",
            "word_count": 400,
            "audience": "general public"
        }
    ]
    
    # Create workflow
    workflow = create_writing_workflow()
    
    # Run examples
    for i, example in enumerate(examples, 1):
        print(f"\n\n{'='*60}")
        print(f"Example {i}: {example['topic']}")
        print(f"{'='*60}")
        
        # Initialize shared state
        shared = example.copy()
        
        try:
            # Run workflow
            workflow.run(shared)
            
            # Show metrics
            print(f"\nWorkflow completed successfully!")
            print(f"- Sections: {len(shared['outline']['sections'])}")
            print(f"- Paragraphs: {len(shared['content']['paragraphs'])}")
            print(f"- Final style: {shared['final_content']['style']}")
            
        except Exception as e:
            print(f"Error in workflow: {e}")


if __name__ == "__main__":
    main()