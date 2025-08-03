# Getting Started with PyResume

Welcome to PyResume! This guide will help you get up and running with resume parsing in just a few minutes.

## 📋 Table of Contents

- [Quick Installation](#quick-installation)
- [Basic Usage](#basic-usage)
- [Understanding the Data](#understanding-the-data)
- [Working with Different Formats](#working-with-different-formats)
- [Handling Errors](#handling-errors)
- [Next Steps](#next-steps)

## ⚡ Quick Installation

### 1. Install PyResume

```bash
# Basic installation
pip install pyresume

# Or with all optional dependencies
pip install pyresume[all]
```

### 2. Verify Installation

```python
import pyresume
print(f"PyResume version: {pyresume.__version__}")
print(f"Supported formats: {pyresume.get_supported_formats()}")
```

### 3. Install Format-Specific Dependencies (if needed)

```bash
# For PDF support
pip install pdfplumber

# For Word document support  
pip install python-docx

# For enhanced phone number parsing
pip install phonenumbers
```

## 🚀 Basic Usage

### Your First Resume Parse

Let's start with a simple example:

```python
from pyresume import ResumeParser

# Create a parser instance
parser = ResumeParser()

# Parse a resume file
resume = parser.parse('path/to/your/resume.pdf')

# Access the parsed data
print(f"Name: {resume.contact_info.name}")
print(f"Email: {resume.contact_info.email}")
print(f"Phone: {resume.contact_info.phone}")
print(f"Years of Experience: {resume.get_years_experience()}")
```

### Parse Text Directly

You can also parse resume text directly without a file:

```python
from pyresume import ResumeParser

resume_text = """
John Smith
Software Engineer
john.smith@email.com
(555) 123-4567
LinkedIn: linkedin.com/in/johnsmith

EXPERIENCE
Senior Software Engineer
Tech Corporation, San Francisco, CA
January 2020 - Present
• Led development of microservices architecture
• Mentored team of 5 junior developers

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley
2014 - 2018

SKILLS
Python, JavaScript, React, AWS, Docker
"""

parser = ResumeParser()
resume = parser.parse_text(resume_text)
print(f"Parsed resume for: {resume.contact_info.name}")
```

## 🔍 Understanding the Data

PyResume organizes resume data into logical sections:

### Contact Information

```python
contact = resume.contact_info

print(f"Name: {contact.name}")
print(f"Email: {contact.email}")
print(f"Phone: {contact.phone}")
print(f"LinkedIn: {contact.linkedin}")
print(f"GitHub: {contact.github}")
print(f"Address: {contact.address}")
```

### Work Experience

```python
print(f"Found {len(resume.experience)} job(s):")

for i, job in enumerate(resume.experience, 1):
    print(f"\\n{i}. {job.title} at {job.company}")
    print(f"   Duration: {job.start_date} to {job.end_date or 'Present'}")
    print(f"   Location: {job.location}")
    
    if job.responsibilities:
        print("   Responsibilities:")
        for responsibility in job.responsibilities[:3]:  # Show first 3
            print(f"   • {responsibility}")
```

### Education

```python
print(f"\\nEducation ({len(resume.education)} entries):")

for edu in resume.education:
    print(f"• {edu.degree} from {edu.institution}")
    if edu.graduation_date:
        print(f"  Graduated: {edu.graduation_date}")
    if edu.gpa:
        print(f"  GPA: {edu.gpa}")
```

### Skills

```python
print(f"\\nSkills ({len(resume.skills)} found):")

# Group skills by category
from collections import defaultdict
skills_by_category = defaultdict(list)

for skill in resume.skills:
    category = skill.category or 'Other'
    skills_by_category[category].append(skill.name)

for category, skills in skills_by_category.items():
    print(f"\\n{category}:")
    for skill in skills:
        print(f"  • {skill}")
```

### Projects and Certifications

```python
# Projects
if resume.projects:
    print(f"\\nProjects ({len(resume.projects)}):")
    for project in resume.projects:
        print(f"• {project.name}")
        if project.description:
            print(f"  {project.description}")
        if project.technologies:
            print(f"  Technologies: {', '.join(project.technologies)}")

# Certifications
if resume.certifications:
    print(f"\\nCertifications ({len(resume.certifications)}):")
    for cert in resume.certifications:
        print(f"• {cert.name}")
        if cert.issuer:
            print(f"  Issued by: {cert.issuer}")
        if cert.date_issued:
            print(f"  Date: {cert.date_issued}")
```

## 📄 Working with Different Formats

### PDF Files

```python
# PDF resumes work out of the box
resume = parser.parse('resume.pdf')
print(f"Extracted {len(resume.raw_text)} characters from PDF")
```

### Word Documents (.docx)

```python
# DOCX files are also supported
resume = parser.parse('resume.docx')
print(f"Successfully parsed Word document")
```

### Plain Text Files

```python
# Text files work great too
resume = parser.parse('resume.txt')
print(f"Parsed plain text resume")
```

### Checking File Support

```python
import os
from pathlib import Path

def check_file_support(file_path):
    """Check if a file format is supported."""
    extension = Path(file_path).suffix.lower()
    supported_formats = parser.get_supported_formats()
    
    if extension in supported_formats:
        print(f"✅ {extension} files are supported")
        return True
    else:
        print(f"❌ {extension} files are not supported")
        print(f"Supported formats: {supported_formats}")
        return False

# Check your file
check_file_support('my_resume.pdf')
```

## 🛠️ Handling Errors

### Basic Error Handling

```python
from pyresume import ResumeParser

parser = ResumeParser()

try:
    resume = parser.parse('resume.pdf')
    print("✅ Resume parsed successfully!")
    
except FileNotFoundError:
    print("❌ Resume file not found. Please check the file path.")
    
except ValueError as e:
    print(f"❌ File format not supported: {e}")
    
except Exception as e:
    print(f"❌ Unexpected error during parsing: {e}")
```

### Validating Results

```python
def validate_resume(resume):
    """Validate that essential information was extracted."""
    issues = []
    
    # Check contact information
    if not resume.contact_info.name:
        issues.append("No name found")
    if not resume.contact_info.email:
        issues.append("No email address found")
    if not resume.contact_info.phone:
        issues.append("No phone number found")
    
    # Check experience
    if not resume.experience:
        issues.append("No work experience found")
    
    # Check education
    if not resume.education:
        issues.append("No education history found")
    
    # Report issues
    if issues:
        print("⚠️  Validation issues found:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("✅ Resume validation passed!")
    
    return len(issues) == 0

# Validate your parsed resume
resume = parser.parse('resume.pdf')
is_valid = validate_resume(resume)
```

### Working with Confidence Scores

```python
def analyze_confidence(resume):
    """Analyze the confidence of extracted data."""
    
    # Overall confidence
    overall_conf = resume.confidence_scores.get('overall', 0)
    print(f"Overall Confidence: {overall_conf:.1%}")
    
    # Section-specific confidence
    sections = ['contact_info', 'experience', 'education', 'skills']
    
    for section in sections:
        conf = resume.confidence_scores.get(section, 0)
        status = "✅" if conf > 0.8 else "⚠️" if conf > 0.5 else "❌"
        print(f"{status} {section.replace('_', ' ').title()}: {conf:.1%}")
    
    # Recommendations
    if overall_conf < 0.7:
        print("\\n💡 Recommendations:")
        print("   • Consider preprocessing the resume file")
        print("   • Check for unusual formatting or layouts")
        print("   • Verify file quality and text clarity")

# Analyze confidence for your resume
analyze_confidence(resume)
```

## 📊 Export and Analysis

### Convert to Dictionary

```python
# Convert resume to dictionary for easy manipulation
resume_dict = resume.to_dict()

# Pretty print the structure
import json
print(json.dumps(resume_dict, indent=2, default=str))
```

### Export to JSON

```python
import json
from datetime import datetime

def export_resume_json(resume, output_file):
    """Export resume to JSON file."""
    
    data = {
        'exported_at': datetime.now().isoformat(),
        'pyresume_version': pyresume.__version__,
        'resume_data': resume.to_dict()
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"✅ Resume exported to {output_file}")

# Export your resume
export_resume_json(resume, 'parsed_resume.json')
```

### Create Summary Report

```python
def create_summary_report(resume):
    """Create a summary report of the parsed resume."""
    
    report = f"""
📋 RESUME PARSING SUMMARY
========================

👤 CONTACT INFORMATION
Name: {resume.contact_info.name or 'Not found'}
Email: {resume.contact_info.email or 'Not found'}
Phone: {resume.contact_info.phone or 'Not found'}
LinkedIn: {resume.contact_info.linkedin or 'Not found'}

💼 PROFESSIONAL SUMMARY
Years of Experience: {resume.get_years_experience():.1f}
Number of Jobs: {len(resume.experience)}
Current Position: {resume.experience[0].title if resume.experience else 'Not found'}
Current Company: {resume.experience[0].company if resume.experience else 'Not found'}

🎓 EDUCATION
Degrees: {len(resume.education)}
Latest Degree: {resume.education[0].degree if resume.education else 'Not found'}
Latest Institution: {resume.education[0].institution if resume.education else 'Not found'}

🛠️ SKILLS & COMPETENCIES
Total Skills: {len(resume.skills)}
Skill Categories: {len(set(skill.category for skill in resume.skills if skill.category))}

📈 PARSING CONFIDENCE
Overall: {resume.confidence_scores.get('overall', 0):.1%}
Contact Info: {resume.confidence_scores.get('contact_info', 0):.1%}
Experience: {resume.confidence_scores.get('experience', 0):.1%}
Education: {resume.confidence_scores.get('education', 0):.1%}
Skills: {resume.confidence_scores.get('skills', 0):.1%}
"""
    
    return report

# Generate and print summary
summary = create_summary_report(resume)
print(summary)
```

## 🎯 Next Steps

Now that you've got the basics down, here are some next steps to explore:

### 1. Batch Processing

Process multiple resumes at once:

```python
# See examples/batch_processing.py for a complete example
from pathlib import Path

resume_dir = Path('resumes/')
results = []

for resume_file in resume_dir.glob('*.pdf'):
    resume = parser.parse(str(resume_file))
    results.append({
        'file': resume_file.name,
        'name': resume.contact_info.name,
        'email': resume.contact_info.email,
        'experience_years': resume.get_years_experience()
    })

print(f"Processed {len(results)} resumes")
```

### 2. Advanced Analysis

Dive deeper into the extracted data:

```python
# See examples/confidence_scores.py for detailed analysis
from pyresume.examples.confidence_scores import ConfidenceAnalyzer

analyzer = ConfidenceAnalyzer()
analysis = analyzer.analyze_resume_confidence(resume)
analyzer.print_confidence_report(resume)
```

### 3. Custom Processing

Extend PyResume for your specific needs:

```python
# Add custom skill categories
from pyresume.utils.patterns import ResumePatterns

patterns = ResumePatterns()
patterns.skill_categories['data_science'] = [
    'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch'
]

# Custom validation rules
def custom_validation(resume):
    """Add your own validation logic."""
    # Your custom validation code here
    pass
```

### 4. Integration

Integrate PyResume into your applications:

```python
# Web application example
from flask import Flask, request, jsonify
from pyresume import ResumeParser

app = Flask(__name__)
parser = ResumeParser()

@app.route('/parse-resume', methods=['POST'])
def parse_resume_endpoint():
    file = request.files['resume']
    resume = parser.parse(file)
    return jsonify(resume.to_dict())
```

## 📚 Additional Resources

- **[API Reference](API_REFERENCE.md)**: Complete API documentation
- **[Examples](../examples/)**: Real-world usage examples
- **[Contributing](../CONTRIBUTING.md)**: How to contribute to PyResume
- **[GitHub Issues](https://github.com/pyresume/pyresume/issues)**: Report bugs or request features

## 🤝 Getting Help

If you run into issues:

1. **Check the examples** in the `examples/` directory
2. **Read the API documentation** for detailed method descriptions
3. **Search existing issues** on GitHub
4. **Create a new issue** if you can't find a solution
5. **Join the discussion** in GitHub Discussions

Happy parsing! 🎉