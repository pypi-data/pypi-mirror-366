"""
Extraction utilities for structured output example.
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime


def extract_resume_info(resume_text: str) -> Dict[str, Any]:
    """
    Extract structured information from resume text.
    
    Args:
        resume_text: Raw resume text
        
    Returns:
        Structured resume data
    """
    lines = resume_text.strip().split('\n')
    
    extracted = {
        "personal": extract_personal_info(resume_text),
        "summary": extract_summary(lines),
        "experience": extract_experience(resume_text),
        "education": extract_education(resume_text),
        "skills": extract_skills(resume_text),
        "certifications": extract_certifications(resume_text)
    }
    
    return extracted


def extract_personal_info(text: str) -> Dict[str, str]:
    """Extract personal contact information."""
    info = {}
    
    # Extract name (usually first line)
    lines = text.strip().split('\n')
    if lines:
        # First non-empty line is likely the name
        for line in lines:
            if line.strip() and not any(keyword in line.lower() for keyword in ['email', 'phone', 'linkedin']):
                info["name"] = line.strip()
                break
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        info["email"] = email_match.group(0)
    
    # Extract phone
    phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        info["phone"] = phone_match.group(0)
    
    # Extract LinkedIn
    linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_match:
        info["linkedin"] = linkedin_match.group(0)
    
    # Extract location
    location_pattern = r'(?:Location:|Based in:?)\s*([^\\n]+)'
    location_match = re.search(location_pattern, text, re.IGNORECASE)
    if location_match:
        info["location"] = location_match.group(1).strip()
    else:
        # Try to find city, state pattern
        city_state_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*),\s*([A-Z]{2})\b'
        city_state_match = re.search(city_state_pattern, text)
        if city_state_match:
            info["location"] = city_state_match.group(0)
    
    return info


def extract_summary(lines: List[str]) -> str:
    """Extract professional summary."""
    summary_started = False
    summary_lines = []
    
    for i, line in enumerate(lines):
        if re.search(r'^(SUMMARY|OBJECTIVE|PROFILE)', line, re.IGNORECASE):
            summary_started = True
            continue
        
        if summary_started:
            # Stop at next section
            if re.search(r'^(EXPERIENCE|EDUCATION|SKILLS|WORK)', line, re.IGNORECASE):
                break
            
            if line.strip():
                summary_lines.append(line.strip())
    
    return " ".join(summary_lines)


def extract_experience(text: str) -> List[Dict[str, Any]]:
    """Extract work experience."""
    experiences = []
    
    # Split by common experience headers
    exp_sections = re.split(r'\n(?=(?:Senior |Junior |Lead |Staff )?(?:Software |Data |Product |Project )?(?:Engineer|Developer|Manager|Analyst|Designer|Architect))', text)
    
    for section in exp_sections:
        if not section.strip():
            continue
        
        lines = section.strip().split('\n')
        if not lines:
            continue
        
        # Try to parse job title line
        title_line = lines[0]
        exp_entry = {}
        
        # Pattern: Title | Company | Period
        title_pattern = r'^([^|]+)\s*\|\s*([^|]+)\s*\|\s*(.+)$'
        title_match = re.match(title_pattern, title_line)
        
        if title_match:
            exp_entry["title"] = title_match.group(1).strip()
            exp_entry["company"] = title_match.group(2).strip()
            exp_entry["period"] = title_match.group(3).strip()
            
            # Try to calculate duration
            duration = calculate_duration(exp_entry["period"])
            if duration:
                exp_entry["duration_years"] = duration
            
            # Extract responsibilities (bullet points)
            responsibilities = []
            for line in lines[1:]:
                if line.strip().startswith(('-', '•', '*')):
                    responsibilities.append(line.strip()[1:].strip())
            
            if responsibilities:
                exp_entry["responsibilities"] = responsibilities
            
            experiences.append(exp_entry)
    
    return experiences


def extract_education(text: str) -> List[Dict[str, Any]]:
    """Extract education information."""
    education = []
    
    # Find education section
    edu_section_pattern = r'EDUCATION\s*\n(.*?)(?=\n(?:SKILLS|CERTIFICATIONS|PROJECTS|$))'
    edu_match = re.search(edu_section_pattern, text, re.IGNORECASE | re.DOTALL)
    
    if edu_match:
        edu_text = edu_match.group(1)
        
        # Pattern for degree lines
        degree_pattern = r'(Bachelor|Master|PhD|Ph\.D\.|B\.S\.|M\.S\.|B\.A\.|M\.A\.|MBA)[^\n]+\n([^\n]+)'
        
        for match in re.finditer(degree_pattern, edu_text, re.IGNORECASE):
            edu_entry = {
                "degree": match.group(0).split('\n')[0].strip(),
                "school": match.group(2).strip()
            }
            
            # Extract year
            year_pattern = r'\b(19|20)\d{2}\b'
            year_matches = re.findall(year_pattern, match.group(0))
            if year_matches:
                if len(year_matches) >= 2:
                    edu_entry["year"] = f"{year_matches[0]} - {year_matches[-1]}"
                else:
                    edu_entry["year"] = year_matches[0]
            
            # Extract GPA if present
            gpa_pattern = r'GPA:?\s*([\d.]+)'
            gpa_match = re.search(gpa_pattern, match.group(0))
            if gpa_match:
                edu_entry["gpa"] = gpa_match.group(1)
            
            education.append(edu_entry)
    
    return education


def extract_skills(text: str) -> Dict[str, List[str]]:
    """Extract skills by category."""
    skills = {}
    
    # Find skills section
    skills_section_pattern = r'SKILLS\s*\n(.*?)(?=\n(?:CERTIFICATIONS|PROJECTS|AWARDS|$))'
    skills_match = re.search(skills_section_pattern, text, re.IGNORECASE | re.DOTALL)
    
    if skills_match:
        skills_text = skills_match.group(1)
        lines = skills_text.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                # Category: skill1, skill2, skill3
                parts = line.split(':', 1)
                category = parts[0].strip()
                skill_list = [s.strip() for s in parts[1].split(',')]
                skills[category] = skill_list
    
    return skills


def extract_certifications(text: str) -> List[str]:
    """Extract certifications."""
    certifications = []
    
    # Find certifications section
    cert_section_pattern = r'CERTIFICATIONS?\s*\n(.*?)(?=\n(?:PROJECTS|AWARDS|$))'
    cert_match = re.search(cert_section_pattern, text, re.IGNORECASE | re.DOTALL)
    
    if cert_match:
        cert_text = cert_match.group(1)
        lines = cert_text.strip().split('\n')
        
        for line in lines:
            if line.strip() and line.strip().startswith(('-', '•', '*')):
                certifications.append(line.strip()[1:].strip())
            elif line.strip() and not line.isupper():
                certifications.append(line.strip())
    
    return certifications


def calculate_duration(period_str: str) -> Optional[float]:
    """Calculate duration in years from period string."""
    # Pattern: Month Year - Month Year or Month Year - Present
    pattern = r'(\w+)\s+(\d{4})\s*-\s*(\w+|Present)\s*(\d{4})?'
    match = re.search(pattern, period_str)
    
    if match:
        start_year = int(match.group(2))
        
        if match.group(3).lower() == 'present':
            end_year = datetime.now().year
        elif match.group(4):
            end_year = int(match.group(4))
        else:
            return None
        
        # Rough calculation (could be improved with month parsing)
        return end_year - start_year
    
    return None


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> Optional[str]:
    """Validate and format phone number."""
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    
    # Check if valid length (10 digits for US)
    if len(digits) == 10:
        # Format as (XXX) XXX-XXXX
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        # Remove country code
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    
    return None


if __name__ == "__main__":
    # Test extraction
    sample = """
    John Doe
    Email: john@example.com
    Phone: 555-123-4567
    
    SUMMARY
    Experienced developer.
    
    EXPERIENCE
    Software Engineer | TechCorp | Jan 2020 - Present
    - Built awesome things
    """
    
    result = extract_resume_info(sample)
    print(json.dumps(result, indent=2))