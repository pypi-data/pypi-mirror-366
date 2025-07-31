"""
Structured output example using KayGraph.

Demonstrates extracting structured data from unstructured text,
such as parsing resumes into standardized format.
"""

import json
import logging
from typing import Dict, Any, List
from kaygraph import Node, Graph, ValidatedNode
from utils.extraction import extract_resume_info, validate_email, validate_phone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class LoadResumeNode(Node):
    """Load resume text from file or string."""
    
    def prep(self, shared):
        """Get resume source."""
        return {
            "resume_text": shared.get("resume_text", ""),
            "resume_file": shared.get("resume_file", "")
        }
    
    def exec(self, prep_res):
        """Load resume content."""
        if prep_res["resume_text"]:
            return prep_res["resume_text"]
        elif prep_res["resume_file"]:
            try:
                with open(prep_res["resume_file"], 'r') as f:
                    return f.read()
            except Exception as e:
                self.logger.error(f"Failed to load resume file: {e}")
                return ""
        else:
            # Use sample resume
            return self._get_sample_resume()
    
    def post(self, shared, prep_res, exec_res):
        """Store resume text."""
        shared["raw_resume"] = exec_res
        self.logger.info(f"Loaded resume with {len(exec_res)} characters")
        return "default"
    
    def _get_sample_resume(self):
        """Get a sample resume for testing."""
        return """
John Doe
Email: john.doe@email.com
Phone: (555) 123-4567
LinkedIn: linkedin.com/in/johndoe
Location: San Francisco, CA

SUMMARY
Experienced software engineer with 8+ years developing scalable web applications.
Expertise in Python, JavaScript, and cloud technologies. Proven track record of
leading teams and delivering high-quality software solutions.

EXPERIENCE

Senior Software Engineer | TechCorp Inc. | Jan 2020 - Present
- Led team of 5 engineers in developing microservices architecture
- Reduced API response time by 40% through optimization
- Implemented CI/CD pipeline using GitHub Actions and AWS

Software Engineer | StartupXYZ | Jun 2016 - Dec 2019
- Developed full-stack web applications using React and Django
- Designed and implemented RESTful APIs serving 1M+ requests/day
- Mentored junior developers and conducted code reviews

Junior Developer | WebSolutions Co. | May 2015 - May 2016
- Built responsive websites using HTML, CSS, and JavaScript
- Collaborated with design team to implement UI/UX improvements
- Maintained and updated client websites

EDUCATION

Bachelor of Science in Computer Science
University of California, Berkeley | 2011 - 2015
GPA: 3.8/4.0

SKILLS
Programming: Python, JavaScript, Java, SQL
Frameworks: Django, React, Node.js, Express
Tools: Git, Docker, Kubernetes, Jenkins
Cloud: AWS, Google Cloud Platform
Databases: PostgreSQL, MongoDB, Redis

CERTIFICATIONS
- AWS Certified Solutions Architect (2021)
- Google Cloud Professional Developer (2020)
"""


class ExtractInfoNode(Node):
    """Extract structured information from resume text."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(max_retries=2, *args, **kwargs)
    
    def prep(self, shared):
        """Get resume text."""
        return shared.get("raw_resume", "")
    
    def exec(self, resume_text):
        """Extract structured data."""
        return extract_resume_info(resume_text)
    
    def post(self, shared, prep_res, exec_res):
        """Store extracted information."""
        shared["extracted_info"] = exec_res
        self.logger.info(f"Extracted {len(exec_res)} fields from resume")
        return "default"


class ValidateDataNode(ValidatedNode):
    """Validate and clean extracted data."""
    
    def validate_input(self, prep_res):
        """Validate extracted data structure."""
        required_fields = ["personal", "experience", "education", "skills"]
        for field in required_fields:
            if field not in prep_res:
                raise ValueError(f"Missing required field: {field}")
        return prep_res
    
    def prep(self, shared):
        """Get extracted information."""
        return shared.get("extracted_info", {})
    
    def exec(self, extracted_info):
        """Validate and clean data."""
        validated = extracted_info.copy()
        
        # Validate personal info
        if "personal" in validated:
            personal = validated["personal"]
            
            # Validate email
            if "email" in personal:
                if not validate_email(personal["email"]):
                    personal["email_valid"] = False
                else:
                    personal["email_valid"] = True
            
            # Validate phone
            if "phone" in personal:
                cleaned_phone = validate_phone(personal["phone"])
                if cleaned_phone:
                    personal["phone_formatted"] = cleaned_phone
                    personal["phone_valid"] = True
                else:
                    personal["phone_valid"] = False
        
        # Calculate experience metrics
        if "experience" in validated:
            total_years = 0
            for exp in validated["experience"]:
                if "duration_years" in exp:
                    total_years += exp["duration_years"]
            validated["total_experience_years"] = total_years
        
        # Count skills by category
        if "skills" in validated:
            skill_counts = {}
            for category, skills in validated["skills"].items():
                skill_counts[category] = len(skills)
            validated["skill_summary"] = skill_counts
        
        return validated
    
    def post(self, shared, prep_res, exec_res):
        """Store validated data."""
        shared["validated_info"] = exec_res
        return "default"


class FormatOutputNode(Node):
    """Format structured data for output."""
    
    def prep(self, shared):
        """Get validated information and format preference."""
        return {
            "data": shared.get("validated_info", {}),
            "format": shared.get("output_format", "json")
        }
    
    def exec(self, prep_res):
        """Format the data."""
        data = prep_res["data"]
        output_format = prep_res["format"]
        
        if output_format == "json":
            return json.dumps(data, indent=2)
        
        elif output_format == "summary":
            return self._format_summary(data)
        
        elif output_format == "markdown":
            return self._format_markdown(data)
        
        else:
            return str(data)
    
    def post(self, shared, prep_res, exec_res):
        """Store and display formatted output."""
        shared["formatted_output"] = exec_res
        
        print("\n" + "=" * 60)
        print(f"STRUCTURED OUTPUT ({prep_res['format'].upper()})")
        print("=" * 60)
        print(exec_res)
        print("=" * 60)
        
        return "default"
    
    def _format_summary(self, data):
        """Format as human-readable summary."""
        summary = []
        
        # Personal info
        if "personal" in data:
            p = data["personal"]
            summary.append("CANDIDATE SUMMARY")
            summary.append(f"Name: {p.get('name', 'N/A')}")
            summary.append(f"Email: {p.get('email', 'N/A')} ({'✓' if p.get('email_valid') else '✗'})")
            summary.append(f"Phone: {p.get('phone_formatted', p.get('phone', 'N/A'))} ({'✓' if p.get('phone_valid') else '✗'})")
            summary.append(f"Location: {p.get('location', 'N/A')}")
        
        # Experience
        summary.append(f"\nEXPERIENCE")
        summary.append(f"Total Years: {data.get('total_experience_years', 0)}")
        summary.append(f"Positions: {len(data.get('experience', []))}")
        
        # Education
        summary.append(f"\nEDUCATION")
        for edu in data.get("education", []):
            summary.append(f"- {edu.get('degree', 'N/A')} from {edu.get('school', 'N/A')}")
        
        # Skills
        summary.append(f"\nSKILLS SUMMARY")
        for category, count in data.get("skill_summary", {}).items():
            summary.append(f"- {category}: {count} skills")
        
        return "\n".join(summary)
    
    def _format_markdown(self, data):
        """Format as Markdown."""
        md = []
        
        # Header
        if "personal" in data:
            p = data["personal"]
            md.append(f"# {p.get('name', 'Candidate Profile')}")
            md.append(f"\n**Email**: {p.get('email', 'N/A')}")
            md.append(f"**Phone**: {p.get('phone_formatted', p.get('phone', 'N/A'))}")
            md.append(f"**Location**: {p.get('location', 'N/A')}")
        
        # Summary
        if "summary" in data:
            md.append(f"\n## Summary\n{data['summary']}")
        
        # Experience
        md.append("\n## Experience")
        for exp in data.get("experience", []):
            md.append(f"\n### {exp.get('title', 'N/A')} | {exp.get('company', 'N/A')}")
            md.append(f"*{exp.get('period', 'N/A')}*")
            for resp in exp.get("responsibilities", []):
                md.append(f"- {resp}")
        
        # Education
        md.append("\n## Education")
        for edu in data.get("education", []):
            md.append(f"- **{edu.get('degree', 'N/A')}** - {edu.get('school', 'N/A')} ({edu.get('year', 'N/A')})")
        
        # Skills
        md.append("\n## Skills")
        for category, skills in data.get("skills", {}).items():
            md.append(f"- **{category}**: {', '.join(skills)}")
        
        return "\n".join(md)


def create_extraction_graph():
    """Create the structured extraction graph."""
    # Create nodes
    load_node = LoadResumeNode(node_id="load")
    extract_node = ExtractInfoNode(node_id="extract")
    validate_node = ValidateDataNode(node_id="validate")
    format_node = FormatOutputNode(node_id="format")
    
    # Connect pipeline
    load_node >> extract_node >> validate_node >> format_node
    
    # Create graph
    return Graph(start=load_node)


def main():
    """Run the structured output example."""
    print("KayGraph Structured Output Example")
    print("=" * 40)
    
    # Create extraction graph
    graph = create_extraction_graph()
    
    # Test with different output formats
    formats = ["json", "summary", "markdown"]
    
    for fmt in formats:
        print(f"\n\nProcessing resume with {fmt} output...")
        print("-" * 40)
        
        # Initialize shared state
        shared = {
            "output_format": fmt
            # Can also provide: resume_text or resume_file
        }
        
        try:
            # Run extraction
            graph.run(shared)
            
            # Show stats
            if "validated_info" in shared:
                info = shared["validated_info"]
                print(f"\nExtraction Stats:")
                print(f"- Total experience: {info.get('total_experience_years', 0)} years")
                print(f"- Skill categories: {len(info.get('skills', {}))}")
                print(f"- Positions held: {len(info.get('experience', []))}")
            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()