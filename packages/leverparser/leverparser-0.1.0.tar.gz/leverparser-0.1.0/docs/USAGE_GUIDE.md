# PyResume Usage Guide

This guide covers end-to-end usage of PyResume, including both the regex-based parser and the intelligent parser with LLM support.

## Table of Contents
1. [Installation](#installation)
2. [Basic Usage - Regex Parser](#basic-usage---regex-parser)
3. [Advanced Usage - Intelligent Parser](#advanced-usage---intelligent-parser)
4. [Understanding Lever Compatibility](#understanding-lever-compatibility)
5. [Working with Different File Formats](#working-with-different-file-formats)
6. [Interpreting Results](#interpreting-results)
7. [Best Practices](#best-practices)

## Installation

### Basic Installation
```bash
pip install pyresume
```

### Installation with LLM Support
```bash
# For OpenAI support
pip install pyresume[openai]

# For Anthropic support
pip install pyresume[anthropic]

# For all features including OCR
pip install pyresume[all]
```

### Development Installation
```bash
git clone https://github.com/yourusername/pyresume.git
cd pyresume
pip install -e .[dev]
```

## Basic Usage - Regex Parser

The regex parser is the default parser that works without any API keys or external dependencies.

### Quick Start
```python
from pyresume import ResumeParser

# Create parser instance
parser = ResumeParser()

# Parse a resume file
resume = parser.parse('path/to/resume.pdf')

# Access parsed information
print(f"Name: {resume.contact_info.name}")
print(f"Email: {resume.contact_info.email}")
print(f"Phone: {resume.contact_info.phone}")

# Experience
for exp in resume.experience:
    print(f"{exp.title} at {exp.company}")
    print(f"  {exp.start_date} - {exp.end_date or 'Present'}")
    
# Education
for edu in resume.education:
    print(f"{edu.degree} from {edu.institution}")
```

### Parsing from Text
```python
# Parse from raw text
text = """
JOHN SMITH
john.smith@email.com | 555-123-4567

EXPERIENCE
SOFTWARE ENGINEER
Tech Corp | San Francisco, CA
01/2020 - Present
• Built scalable APIs
"""

resume = parser.parse_text(text)
```

### Confidence Scores
```python
# Check parsing confidence
print(f"Contact Info Confidence: {resume.confidence_scores['contact_info']:.2f}")
print(f"Experience Confidence: {resume.confidence_scores['experience']:.2f}")
print(f"Overall Confidence: {resume.confidence_scores.get('overall', 0):.2f}")
```

## Advanced Usage - Intelligent Parser

The intelligent parser uses LLMs to enhance parsing accuracy and handle complex formats.

### Setup with API Keys
```python
from pyresume import IntelligentResumeParser

# Using Anthropic Claude
parser = IntelligentResumeParser(
    provider='anthropic',
    api_key='your-anthropic-api-key'
)

# Using OpenAI
parser = IntelligentResumeParser(
    provider='openai',
    api_key='your-openai-api-key'
)

# Using environment variables
import os
os.environ['ANTHROPIC_API_KEY'] = 'your-key'
parser = IntelligentResumeParser(provider='anthropic')
```

### Fallback to Regex
```python
# Intelligent parser with automatic fallback
parser = IntelligentResumeParser(
    provider='anthropic',
    use_llm=True,
    fallback_to_regex=True  # Falls back if LLM fails
)

# Parse resume
resume = parser.parse('resume.pdf')
```

### Using Local LLMs
```python
# For local LLM integration (e.g., Ollama)
from pyresume.providers import LocalLLMProvider

# Create custom provider
class OllamaProvider(LocalLLMProvider):
    def parse_with_llm(self, text, prompt_type='full'):
        # Your local LLM implementation
        response = ollama.generate(
            model='llama2',
            prompt=self._build_prompt(text, prompt_type)
        )
        return self._parse_llm_response(response)

# Use with parser
parser = IntelligentResumeParser(provider=OllamaProvider())
```

## Understanding Lever Compatibility

PyResume is designed to approximate Lever ATS parsing behavior. Here's what makes a resume "Lever-friendly":

### Lever-Friendly Format
```
JOHN SMITH
john.smith@email.com | 555-123-4567 | San Francisco, CA

PROFESSIONAL EXPERIENCE

SENIOR SOFTWARE ENGINEER
Tech Corp | San Francisco, CA
01/2020 - Present
• Led team of 5 engineers
• Improved performance by 40%

SOFTWARE ENGINEER
StartupCo | Palo Alto, CA
06/2018 - 12/2019
• Built microservices architecture
• Implemented CI/CD pipeline

EDUCATION

BACHELOR OF SCIENCE IN COMPUTER SCIENCE
University of California, Berkeley | Berkeley, CA
09/2014 - 05/2018
GPA: 3.8/4.0

TECHNICAL SKILLS

Programming: Python, JavaScript, TypeScript, Go
Frameworks: React, Django, Flask, Express
Databases: PostgreSQL, MongoDB, Redis
```

### Key Lever Requirements
1. **Section Headers**: Must be ALL CAPS (EXPERIENCE, EDUCATION, SKILLS)
2. **Job Format**: Title, then Company | Location, then Dates
3. **Date Format**: MM/YYYY preferred (01/2020)
4. **Clear Structure**: No tables, columns, or complex formatting

### Checking Lever Compatibility
```python
# Parse and check confidence scores
resume = parser.parse('resume.pdf')

# High confidence means good Lever compatibility
if resume.confidence_scores['experience'] > 0.8:
    print("Experience section is Lever-compatible")
else:
    print("Experience section may have parsing issues")
    
# Check extraction metadata
metadata = resume.extraction_metadata
print(f"Sections found: {metadata['sections_found']}")
```

## Working with Different File Formats

### PDF Files
```python
# PDF parsing (requires pdfplumber)
resume = parser.parse('resume.pdf')

# Handle PDF-specific issues
if resume.confidence_scores['overall'] < 0.5:
    print("PDF may have complex formatting. Consider using a simpler layout.")
```

### DOCX Files
```python
# DOCX parsing (requires python-docx)
resume = parser.parse('resume.docx')

# DOCX files typically parse better than PDFs
```

### Text Files
```python
# Plain text parsing
resume = parser.parse('resume.txt')

# Text files work best with clear formatting
```

### Direct Text Input
```python
# Parse text directly
with open('resume.txt', 'r') as f:
    text = f.read()
    
resume = parser.parse_text(text)
```

## Interpreting Results

### Understanding the Resume Object
```python
# The Resume object contains:
resume.contact_info    # ContactInfo object
resume.summary         # Summary text (if found)
resume.experience      # List of Experience objects
resume.education       # List of Education objects
resume.skills          # List of Skill objects
resume.certifications  # List of Certification objects
resume.languages       # List of Language objects
resume.projects        # List of Project objects

# Confidence scores for each section
resume.confidence_scores = {
    'contact_info': 0.95,  # How confident in contact extraction
    'experience': 0.85,    # How confident in experience parsing
    'education': 0.90,     # How confident in education parsing
    'skills': 0.80,        # How confident in skills extraction
    'overall': 0.87        # Overall parsing confidence
}

# Metadata about extraction
resume.extraction_metadata = {
    'sections_found': ['experience', 'education', 'skills'],
    'text_length': 2500,
    'has_email': True,
    'has_phone': True,
    'experience_count': 3,
    'education_count': 2
}
```

### Experience Object
```python
for exp in resume.experience:
    print(f"Title: {exp.title}")
    print(f"Company: {exp.company}")
    print(f"Location: {exp.location}")
    print(f"Start Date: {exp.start_date}")
    print(f"End Date: {exp.end_date or 'Present'}")
    print(f"Current: {exp.current}")
    
    # Responsibilities/bullets
    for resp in exp.responsibilities:
        print(f"  • {resp}")
```

### Education Object
```python
for edu in resume.education:
    print(f"Degree: {edu.degree}")
    print(f"Institution: {edu.institution}")
    print(f"Location: {edu.location}")
    print(f"Graduation Date: {edu.graduation_date}")
    print(f"GPA: {edu.gpa}")
    print(f"Honors: {edu.honors}")
```

### Skills Categorization
```python
# Skills are automatically categorized
skills_by_category = {}
for skill in resume.skills:
    category = skill.category or 'other'
    if category not in skills_by_category:
        skills_by_category[category] = []
    skills_by_category[category].append(skill.name)

# Display by category
for category, skills in skills_by_category.items():
    print(f"{category.title()}: {', '.join(skills)}")
```

## Best Practices

### 1. Format Recommendations
```python
def check_resume_format(file_path):
    """Check if resume follows ATS-friendly format."""
    parser = ResumeParser()
    resume = parser.parse(file_path)
    
    recommendations = []
    
    # Check section headers
    if 'experience' not in resume.extraction_metadata['sections_found']:
        recommendations.append("Use 'EXPERIENCE' or 'PROFESSIONAL EXPERIENCE' as section header")
    
    # Check confidence scores
    if resume.confidence_scores['contact_info'] < 0.8:
        recommendations.append("Place contact info at the top in a clear format")
    
    if resume.confidence_scores['experience'] < 0.7:
        recommendations.append("Use standard format: TITLE \\n Company | Location \\n Dates")
    
    return recommendations
```

### 2. Error Handling
```python
from pyresume.exceptions import PyResumeError

try:
    resume = parser.parse('resume.pdf')
except PyResumeError as e:
    print(f"Parsing error: {e}")
    # Fall back to basic extraction
    try:
        text = extract_text_from_file('resume.pdf')
        resume = parser.parse_text(text)
    except Exception as e:
        print(f"Failed to parse resume: {e}")
```

### 3. Batch Processing
```python
import os
from pathlib import Path

def process_resumes(directory):
    """Process all resumes in a directory."""
    parser = IntelligentResumeParser(
        provider='anthropic',
        fallback_to_regex=True
    )
    
    results = []
    for file_path in Path(directory).glob('*.pdf'):
        try:
            resume = parser.parse(str(file_path))
            results.append({
                'file': file_path.name,
                'name': resume.contact_info.name,
                'email': resume.contact_info.email,
                'experience_count': len(resume.experience),
                'confidence': resume.confidence_scores['overall']
            })
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return results
```

### 4. Custom Validation
```python
def validate_resume_completeness(resume):
    """Check if resume has all required sections."""
    issues = []
    
    # Check contact info
    if not resume.contact_info.email:
        issues.append("Missing email address")
    if not resume.contact_info.phone:
        issues.append("Missing phone number")
    
    # Check experience
    if len(resume.experience) == 0:
        issues.append("No experience section found")
    
    # Check education
    if len(resume.education) == 0:
        issues.append("No education section found")
    
    # Check for current position
    has_current = any(exp.current for exp in resume.experience)
    if not has_current:
        issues.append("No current position indicated")
    
    return issues
```

### 5. Integration with ATS Systems
```python
def prepare_for_ats(resume):
    """Convert parsed resume to ATS-friendly format."""
    ats_data = {
        'personal': {
            'name': resume.contact_info.name,
            'email': resume.contact_info.email,
            'phone': resume.contact_info.phone,
            'location': resume.contact_info.address
        },
        'experience': [
            {
                'title': exp.title,
                'company': exp.company,
                'start_date': exp.start_date.isoformat() if exp.start_date else None,
                'end_date': exp.end_date.isoformat() if exp.end_date else None,
                'current': exp.current,
                'description': ' '.join(exp.responsibilities)
            }
            for exp in resume.experience
        ],
        'education': [
            {
                'degree': edu.degree,
                'school': edu.institution,
                'graduation_date': edu.graduation_date.isoformat() if edu.graduation_date else None,
                'gpa': edu.gpa
            }
            for edu in resume.education
        ],
        'skills': [skill.name for skill in resume.skills]
    }
    
    return ats_data
```

## Troubleshooting

### Common Issues

1. **Low Confidence Scores**
   - Check if resume uses standard formatting
   - Ensure section headers are ALL CAPS
   - Avoid tables, columns, or graphics

2. **Missing Sections**
   - Verify section headers match expected patterns
   - Check for proper spacing between sections
   - Ensure consistent formatting throughout

3. **Incorrect Parsing**
   - Use intelligent parser for complex formats
   - Provide clearer section boundaries
   - Follow Lever-friendly formatting guidelines

### Debug Mode
```python
# Enable detailed extraction info
parser = ResumeParser()
resume = parser.parse('resume.pdf')

# Check what was found
print("Sections found:", resume.extraction_metadata['sections_found'])
print("Text length:", resume.extraction_metadata['text_length'])
print("Experience entries:", resume.extraction_metadata['experience_count'])

# Review raw text if needed
print("First 500 chars:", resume.raw_text[:500])
```

## Next Steps

- Review the [API Reference](API_REFERENCE.md) for detailed method documentation
- Check [examples/](../examples/) for more code samples
- See [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute to the project
- Report issues on [GitHub](https://github.com/yourusername/pyresume/issues)