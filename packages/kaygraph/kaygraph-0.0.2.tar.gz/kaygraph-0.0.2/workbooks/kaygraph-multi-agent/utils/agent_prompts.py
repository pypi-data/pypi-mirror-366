"""
Agent-specific prompts and behaviors for multi-agent system.
"""

from typing import Dict, Any, List


def get_supervisor_prompt(task: str, agent_capabilities: Dict[str, str]) -> str:
    """Get prompt for supervisor agent to plan task delegation."""
    agents_desc = "\n".join([f"- {name}: {desc}" for name, desc in agent_capabilities.items()])
    
    return f"""You are a supervisor agent coordinating a team to complete the following task:

Task: {task}

Available agents and their capabilities:
{agents_desc}

Analyze the task and create a delegation plan. Consider:
1. Which agents are needed for this task?
2. What order should they work in?
3. What specific subtasks should each agent handle?

Provide a structured plan for task delegation."""


def get_researcher_prompt(research_topic: str, specific_questions: List[str] = None) -> str:
    """Get prompt for research agent."""
    questions_text = ""
    if specific_questions:
        questions_text = "\n\nSpecific questions to address:\n" + \
                        "\n".join([f"- {q}" for q in specific_questions])
    
    return f"""You are a research agent tasked with gathering information on:

Topic: {research_topic}
{questions_text}

Conduct thorough research and provide:
1. Key facts and findings
2. Important context and background
3. Relevant statistics or data
4. Credible sources (if available)
5. Areas that need further investigation

Structure your findings clearly for other agents to use."""


def get_writer_prompt(topic: str, research_findings: str, style: str = "informative") -> str:
    """Get prompt for writer agent."""
    return f"""You are a writer agent creating content on:

Topic: {topic}
Writing style: {style}

Research findings provided:
{research_findings}

Create well-structured content that:
1. Is engaging and appropriate for the target audience
2. Incorporates the research findings naturally
3. Maintains the requested writing style
4. Is properly organized with clear sections
5. Includes a compelling introduction and conclusion"""


def get_reviewer_prompt(content: str, review_criteria: List[str] = None) -> str:
    """Get prompt for reviewer agent."""
    criteria_text = ""
    if review_criteria:
        criteria_text = "\n\nReview criteria:\n" + \
                       "\n".join([f"- {c}" for c in review_criteria])
    else:
        criteria_text = """
Review criteria:
- Accuracy and factual correctness
- Clarity and readability
- Structure and organization
- Grammar and style
- Completeness"""
    
    return f"""You are a reviewer agent evaluating the following content:

{content}
{criteria_text}

Provide a detailed review including:
1. Overall assessment
2. Strengths of the content
3. Areas for improvement
4. Specific suggestions for edits
5. Final recommendation (approve/revise)"""


def parse_supervisor_plan(response: str) -> Dict[str, Any]:
    """Parse supervisor's delegation plan."""
    # Simple parsing - in production, use structured output
    plan = {
        "agents_needed": [],
        "task_order": [],
        "agent_tasks": {}
    }
    
    # Mock parsing
    if "research" in response.lower():
        plan["agents_needed"].append("researcher")
        plan["agent_tasks"]["researcher"] = "Gather information on the topic"
    
    if "writ" in response.lower():
        plan["agents_needed"].append("writer")
        plan["agent_tasks"]["writer"] = "Create content based on research"
    
    if "review" in response.lower():
        plan["agents_needed"].append("reviewer")
        plan["agent_tasks"]["reviewer"] = "Review and improve the content"
    
    # Default order
    plan["task_order"] = ["researcher", "writer", "reviewer"]
    
    return plan


def format_final_output(task: str, results: Dict[str, Any]) -> str:
    """Format the final output from all agents."""
    output = f"""Multi-Agent Task Completion Report
=====================================

Original Task: {task}

Agent Contributions:
-------------------
"""
    
    for agent, result in results.items():
        output += f"\n{agent.title()} Agent:\n"
        output += f"{result}\n"
        output += "-" * 40 + "\n"
    
    output += "\nTask Status: Completed Successfully"
    
    return output


# Mock LLM responses for demo
MOCK_RESPONSES = {
    "supervisor": {
        "default": """Task delegation plan:

1. Research Agent: Gather comprehensive information on the topic
2. Writer Agent: Create structured content based on research
3. Reviewer Agent: Review and refine the final content

All agents should collaborate through the shared workspace."""
    },
    "researcher": {
        "default": """Research Findings:

1. Key Facts:
   - Important point 1 with supporting evidence
   - Critical insight 2 backed by data
   - Relevant trend 3 observed in recent studies

2. Context:
   - Historical background provides important perspective
   - Current developments show rapid progress
   - Future implications are significant

3. Data Points:
   - Metric A: 75% increase over baseline
   - Metric B: 2.3x improvement noted
   - Metric C: Consistent across regions

4. Areas for Further Investigation:
   - Aspect X requires deeper analysis
   - Question Y remains unanswered"""
    },
    "writer": {
        "default": """[Title: Comprehensive Analysis of the Topic]

Introduction:
This analysis explores the key aspects of our topic, drawing from extensive research to provide actionable insights.

Main Findings:
Our research reveals three critical points. First, the evidence strongly supports significant improvements in key metrics. Second, historical context illuminates current trends. Third, future implications demand careful consideration.

Detailed Analysis:
[Structured content incorporating research findings with clear sections and smooth transitions]

Conclusion:
The evidence presented demonstrates clear patterns and opportunities. Organizations should consider these findings when planning their strategic approach.

Recommendations:
1. Implement evidence-based strategies
2. Monitor key metrics continuously
3. Prepare for future developments"""
    },
    "reviewer": {
        "default": """Review Assessment:

Overall Rating: Good (8/10)

Strengths:
- Well-structured with clear sections
- Research is properly incorporated
- Writing is clear and engaging
- Conclusions are well-supported

Areas for Improvement:
- Could benefit from more specific examples
- Some technical terms need clarification
- Consider adding visual elements

Specific Edits:
- Paragraph 2: Clarify the metric definitions
- Section 3: Add transition sentence
- Conclusion: Strengthen call-to-action

Recommendation: APPROVE with minor revisions"""
    }
}


def get_mock_response(agent_type: str, prompt: str) -> str:
    """Get mock LLM response for demo purposes."""
    return MOCK_RESPONSES.get(agent_type, {}).get("default", "Mock response for demo")