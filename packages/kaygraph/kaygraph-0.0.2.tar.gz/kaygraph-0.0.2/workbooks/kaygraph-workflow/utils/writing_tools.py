"""
Writing utility functions for the workflow example.
"""

import time
from typing import Dict, List, Any

# Available writing styles
WRITING_STYLES = {
    "professional": {
        "tone": "formal",
        "vocabulary": "sophisticated",
        "sentence_length": "varied",
        "voice": "active"
    },
    "casual": {
        "tone": "conversational",
        "vocabulary": "simple",
        "sentence_length": "short",
        "voice": "active"
    },
    "educational": {
        "tone": "instructive",
        "vocabulary": "clear",
        "sentence_length": "medium",
        "voice": "mixed"
    },
    "motivational": {
        "tone": "inspiring",
        "vocabulary": "empowering",
        "sentence_length": "varied",
        "voice": "active"
    }
}


def generate_outline(topic: str, word_count: int) -> Dict[str, Any]:
    """
    Generate a content outline based on topic and target word count.
    
    Args:
        topic: The topic to write about
        word_count: Target word count
        
    Returns:
        Outline structure with sections
    """
    # Simulate processing time
    time.sleep(0.5)
    
    # Calculate sections based on word count
    num_sections = max(3, min(7, word_count // 150))
    
    # Generate outline structure
    outline = {
        "topic": topic,
        "target_word_count": word_count,
        "sections": []
    }
    
    # Add introduction
    outline["sections"].append({
        "type": "introduction",
        "title": "Introduction",
        "points": [
            f"Hook the reader with interesting fact about {topic}",
            "Present the main thesis",
            "Preview what will be covered"
        ]
    })
    
    # Add main sections
    section_titles = [
        "Key Concepts",
        "Main Benefits",
        "Practical Applications",
        "Common Challenges",
        "Best Practices",
        "Future Trends",
        "Case Studies"
    ]
    
    for i in range(num_sections - 2):  # -2 for intro and conclusion
        if i < len(section_titles):
            outline["sections"].append({
                "type": "body",
                "title": section_titles[i],
                "points": [
                    f"Main point about {section_titles[i].lower()}",
                    "Supporting evidence or examples",
                    "Practical implications"
                ]
            })
    
    # Add conclusion
    outline["sections"].append({
        "type": "conclusion",
        "title": "Conclusion",
        "points": [
            "Summarize key takeaways",
            "Reinforce main message",
            "Call to action or next steps"
        ]
    })
    
    return outline


def write_content(topic: str, outline: Dict[str, Any], audience: str) -> Dict[str, Any]:
    """
    Write content based on outline.
    
    Args:
        topic: The topic
        outline: Content outline
        audience: Target audience
        
    Returns:
        Written content structure
    """
    # Simulate writing time
    time.sleep(1.0)
    
    content = {
        "title": topic,
        "audience": audience,
        "sections": [],
        "paragraphs": []
    }
    
    # Write each section
    for section in outline["sections"]:
        section_content = {
            "title": section["title"],
            "type": section["type"],
            "paragraphs": []
        }
        
        # Generate paragraphs based on section type
        if section["type"] == "introduction":
            para = f"In today's world, {topic.lower()} has become increasingly important. "
            para += f"This article explores the key aspects that every {audience} should know. "
            para += "By the end, you'll have a comprehensive understanding of the subject."
            section_content["paragraphs"].append(para)
            
        elif section["type"] == "body":
            para1 = f"When it comes to {section['title'].lower()}, there are several important factors to consider. "
            para1 += f"For {audience}, understanding these concepts is crucial for success. "
            para1 += "Let's dive into the details."
            section_content["paragraphs"].append(para1)
            
            para2 = "Research has shown that implementing these practices can lead to significant improvements. "
            para2 += "Many experts in the field recommend starting with small, manageable steps. "
            para2 += "This approach ensures sustainable progress over time."
            section_content["paragraphs"].append(para2)
            
        elif section["type"] == "conclusion":
            para = f"In conclusion, {topic.lower()} offers numerous benefits and opportunities. "
            para += f"For {audience}, the key is to start implementing these concepts today. "
            para += "Remember, every journey begins with a single step."
            section_content["paragraphs"].append(para)
        
        content["sections"].append(section_content)
        content["paragraphs"].extend(section_content["paragraphs"])
    
    # Add metadata
    content["word_count"] = sum(len(p.split()) for p in content["paragraphs"])
    content["paragraph_count"] = len(content["paragraphs"])
    
    return content


def apply_style(content: Dict[str, Any], style: str) -> Dict[str, Any]:
    """
    Apply writing style to content.
    
    Args:
        content: Written content
        style: Style to apply
        
    Returns:
        Styled content
    """
    # Simulate styling time
    time.sleep(0.5)
    
    style_config = WRITING_STYLES.get(style, WRITING_STYLES["professional"])
    
    styled_content = {
        "title": content["title"],
        "style": style,
        "style_config": style_config,
        "sections": content["sections"].copy(),
        "formatted_content": ""
    }
    
    # Apply style transformations
    formatted_parts = [f"# {content['title']}\n"]
    
    for section in content["sections"]:
        formatted_parts.append(f"\n## {section['title']}\n")
        
        for para in section["paragraphs"]:
            # Apply style-specific transformations
            styled_para = para
            
            if style == "casual":
                # Make more conversational
                styled_para = styled_para.replace("Research has shown", "Studies show")
                styled_para = styled_para.replace("It is important", "It's important")
                styled_para = styled_para.replace("numerous", "many")
                
            elif style == "motivational":
                # Add motivational language
                styled_para = styled_para.replace("can lead to", "will empower you to achieve")
                styled_para = styled_para.replace("important", "essential")
                styled_para = styled_para.replace("benefits", "amazing benefits")
                
            elif style == "educational":
                # Add educational markers
                styled_para = styled_para.replace("Let's dive", "Let's examine")
                styled_para = styled_para.replace("important factors", "key learning points")
                
            formatted_parts.append(f"{styled_para}\n")
    
    styled_content["formatted_content"] = "\n".join(formatted_parts)
    
    return styled_content


if __name__ == "__main__":
    # Test the functions
    outline = generate_outline("Python Programming", 500)
    print("Outline:", outline)
    
    content = write_content("Python Programming", outline, "beginners")
    print(f"\nContent: {content['word_count']} words, {content['paragraph_count']} paragraphs")
    
    styled = apply_style(content, "casual")
    print(f"\nStyled content preview:\n{styled['formatted_content'][:200]}...")