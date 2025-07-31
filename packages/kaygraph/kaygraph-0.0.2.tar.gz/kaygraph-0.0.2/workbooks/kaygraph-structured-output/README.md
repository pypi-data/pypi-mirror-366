# KayGraph Structured Output

Extract structured data from unstructured text using KayGraph. This example demonstrates resume parsing but can be adapted for any text extraction task.

## What it does

- **Loads** resume text from file or uses sample data
- **Extracts** structured information (contact, experience, education, skills)
- **Validates** data (email format, phone numbers)
- **Formats** output in multiple formats (JSON, summary, Markdown)

## How to run

```bash
python main.py
```

## Features

- **Information Extraction**: Parse unstructured text into structured data
- **Data Validation**: ValidatedNode ensures data quality
- **Multiple Output Formats**: JSON, human-readable summary, Markdown
- **Error Handling**: Retry mechanism for extraction

## Pipeline Structure

```
LoadResumeNode → ExtractInfoNode → ValidateDataNode → FormatOutputNode
```

## Extracted Fields

- **Personal Info**: Name, email, phone, location, LinkedIn
- **Summary**: Professional summary/objective
- **Experience**: Job titles, companies, periods, responsibilities
- **Education**: Degrees, schools, years, GPA
- **Skills**: Categorized skill lists
- **Certifications**: Professional certifications

## Output Formats

### JSON
```json
{
  "personal": {
    "name": "John Doe",
    "email": "john.doe@email.com",
    "email_valid": true,
    "phone": "(555) 123-4567",
    "phone_valid": true
  },
  "experience": [...],
  "total_experience_years": 8
}
```

### Summary
```
CANDIDATE SUMMARY
Name: John Doe
Email: john.doe@email.com (✓)
Phone: (555) 123-4567 (✓)

EXPERIENCE
Total Years: 8
Positions: 3
```

### Markdown
```markdown
# John Doe

**Email**: john.doe@email.com
**Phone**: (555) 123-4567

## Experience
### Senior Software Engineer | TechCorp Inc.
*Jan 2020 - Present*
- Led team of 5 engineers...
```

## Customization

### Add Custom Extractors
Modify `utils/extraction.py` to extract:
- Publications
- Awards
- Languages
- Projects
- References

### Custom Validation
Add validation for:
- LinkedIn URLs
- GitHub profiles
- Portfolio websites
- Date ranges

### New Output Formats
- HTML
- LaTeX
- CSV
- XML

Perfect for building data extraction pipelines!