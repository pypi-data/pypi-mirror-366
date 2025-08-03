# PyResume API Reference

This document provides comprehensive API documentation for the PyResume library.

## Table of Contents

- [Core Classes](#core-classes)
  - [ResumeParser](#resumeparser)
  - [Resume](#resume)
  - [ContactInfo](#contactinfo)
  - [Experience](#experience)
  - [Education](#education)
  - [Skill](#skill)
  - [Project](#project)
  - [Certification](#certification)
- [Extractors](#extractors)
  - [PDFExtractor](#pdfextractor)
  - [DOCXExtractor](#docxextractor)
  - [TextExtractor](#textextractor)
- [Utilities](#utilities)
  - [DateParser](#dateparser)
  - [PhoneParser](#phoneparser)
  - [ResumePatterns](#resumepatterns)
- [Examples](#examples)
- [Error Handling](#error-handling)

## Core Classes

### ResumeParser

The main entry point for parsing resumes from various file formats.

```python
from pyresume import ResumeParser

parser = ResumeParser()
```

#### Methods

##### `parse(file_path: str) -> Resume`

Parse a resume file and return a structured Resume object.

**Parameters:**
- `file_path` (str): Path to the resume file (PDF, DOCX, or TXT)

**Returns:**
- `Resume`: Parsed resume data

**Raises:**
- `FileNotFoundError`: If the file doesn't exist
- `ValueError`: If the file format is not supported
- `Exception`: For parsing errors

**Example:**
```python
parser = ResumeParser()
resume = parser.parse('resume.pdf')
print(f"Name: {resume.contact_info.name}")
```

##### `parse_text(text: str) -> Resume`

Parse resume text directly without reading from a file.

**Parameters:**
- `text` (str): Raw resume text content

**Returns:**
- `Resume`: Parsed resume data

**Example:**
```python
parser = ResumeParser()
text = "John Doe\njohn@email.com\n(555) 123-4567"
resume = parser.parse_text(text)
```

##### `get_supported_formats() -> List[str]`

Get a list of supported file formats.

**Returns:**
- `List[str]`: List of supported file extensions

**Example:**
```python
formats = parser.get_supported_formats()
print(formats)  # ['.pdf', '.docx', '.txt']
```

#### Properties

- `extractors` (Dict): Dictionary mapping file extensions to extractor instances

### Resume

Represents a complete parsed resume with all extracted information.

```python
from pyresume.models.resume import Resume
```

#### Attributes

- `contact_info` (ContactInfo): Contact information
- `summary` (Optional[str]): Professional summary
- `experience` (List[Experience]): Work experience entries
- `education` (List[Education]): Education entries
- `skills` (List[Skill]): Skills and competencies
- `projects` (List[Project]): Personal/professional projects
- `certifications` (List[Certification]): Certifications and licenses
- `languages` (List[str]): Spoken languages
- `raw_text` (str): Original raw text
- `file_path` (Optional[str]): Source file path
- `confidence_scores` (Dict[str, float]): Section-wise confidence scores

#### Methods

##### `get_contact_summary() -> str`

Get a formatted summary of contact information.

**Returns:**
- `str`: Formatted contact summary

**Example:**
```python
summary = resume.get_contact_summary()
print(summary)  # "John Doe <john@email.com>"
```

##### `get_years_experience() -> float`

Calculate total years of work experience.

**Returns:**
- `float`: Total years of experience

**Example:**
```python
years = resume.get_years_experience()
print(f"Experience: {years} years")
```

##### `to_dict() -> Dict[str, Any]`

Convert the resume to a dictionary format.

**Returns:**
- `Dict[str, Any]`: Resume data as dictionary

**Example:**
```python
data = resume.to_dict()
import json
print(json.dumps(data, indent=2, default=str))
```

##### `get_skills_by_category(category: str) -> List[Skill]`

Get skills filtered by category.

**Parameters:**
- `category` (str): Skill category to filter by

**Returns:**
- `List[Skill]`: Skills in the specified category

**Example:**
```python
programming_skills = resume.get_skills_by_category('programming')
for skill in programming_skills:
    print(skill.name)
```

### ContactInfo

Represents contact information extracted from a resume.

#### Attributes

- `name` (Optional[str]): Full name
- `email` (Optional[str]): Email address
- `phone` (Optional[str]): Phone number
- `address` (Optional[str]): Physical address
- `linkedin` (Optional[str]): LinkedIn profile URL
- `github` (Optional[str]): GitHub profile URL
- `website` (Optional[str]): Personal website URL

#### Methods

##### `is_complete() -> bool`

Check if essential contact information is present.

**Returns:**
- `bool`: True if name, email, and phone are all present

### Experience

Represents a work experience entry.

#### Attributes

- `title` (Optional[str]): Job title
- `company` (Optional[str]): Company name
- `start_date` (Optional[str]): Start date (YYYY-MM-DD format)
- `end_date` (Optional[str]): End date (YYYY-MM-DD format)
- `current` (bool): Whether this is the current position
- `description` (Optional[str]): Job description
- `responsibilities` (List[str]): List of responsibilities
- `location` (Optional[str]): Work location
- `confidence_score` (float): Extraction confidence (0.0-1.0)

#### Methods

##### `duration_months() -> Optional[int]`

Calculate the duration of this position in months.

**Returns:**
- `Optional[int]`: Duration in months, None if dates are missing

##### `is_current_position() -> bool`

Check if this is the current position.

**Returns:**
- `bool`: True if current or end_date is None

### Education

Represents an education entry.

#### Attributes

- `degree` (Optional[str]): Degree name
- `institution` (Optional[str]): Institution name
- `field` (Optional[str]): Field of study
- `graduation_date` (Optional[str]): Graduation date
- `gpa` (Optional[float]): GPA if mentioned
- `honors` (Optional[str]): Academic honors
- `location` (Optional[str]): Institution location
- `confidence_score` (float): Extraction confidence

### Skill

Represents a skill or competency.

#### Attributes

- `name` (str): Skill name
- `category` (Optional[str]): Skill category (programming, tools, etc.)
- `proficiency` (Optional[str]): Proficiency level
- `confidence_score` (float): Extraction confidence

### Project

Represents a personal or professional project.

#### Attributes

- `name` (str): Project name
- `description` (Optional[str]): Project description
- `technologies` (List[str]): Technologies used
- `url` (Optional[str]): Project URL
- `start_date` (Optional[str]): Start date
- `end_date` (Optional[str]): End date

### Certification

Represents a certification or license.

#### Attributes

- `name` (str): Certification name
- `issuer` (Optional[str]): Issuing organization
- `date_issued` (Optional[str]): Issue date
- `expiry_date` (Optional[str]): Expiration date
- `credential_id` (Optional[str]): Credential ID

## Extractors

### PDFExtractor

Extracts text from PDF files using pdfplumber.

```python
from pyresume.extractors.pdf import PDFExtractor

extractor = PDFExtractor()
text = extractor.extract('resume.pdf')
```

#### Methods

##### `extract(file_path: str) -> str`

Extract text from a PDF file.

**Parameters:**
- `file_path` (str): Path to PDF file

**Returns:**
- `str`: Extracted text content

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `Exception`: For PDF reading errors

### DOCXExtractor

Extracts text from Microsoft Word documents.

```python
from pyresume.extractors.docx import DOCXExtractor

extractor = DOCXExtractor()
text = extractor.extract('resume.docx')
```

#### Methods

##### `extract(file_path: str) -> str`

Extract text from a DOCX file.

**Parameters:**
- `file_path` (str): Path to DOCX file

**Returns:**
- `str`: Extracted text content

### TextExtractor

Handles plain text files with encoding detection.

```python
from pyresume.extractors.text import TextExtractor

extractor = TextExtractor()
text = extractor.extract('resume.txt')
```

#### Methods

##### `extract(file_path: str) -> str`

Extract text from a plain text file.

**Parameters:**
- `file_path` (str): Path to text file

**Returns:**
- `str`: File content with proper encoding

## Utilities

### DateParser

Utility for parsing and normalizing dates from resume text.

```python
from pyresume.utils.dates import DateParser

parser = DateParser()
```

#### Methods

##### `parse_date(date_str: str) -> Optional[str]`

Parse a date string and return normalized format.

**Parameters:**
- `date_str` (str): Raw date string

**Returns:**
- `Optional[str]`: Normalized date (YYYY-MM-DD) or None

**Example:**
```python
date = parser.parse_date("January 2020")
print(date)  # "2020-01-01"
```

##### `parse_date_range(text: str) -> Tuple[Optional[str], Optional[str]]`

Parse a date range from text.

**Parameters:**
- `text` (str): Text containing date range

**Returns:**
- `Tuple[Optional[str], Optional[str]]`: (start_date, end_date)

### PhoneParser

Utility for parsing and formatting phone numbers.

```python
from pyresume.utils.phones import PhoneParser

parser = PhoneParser()
```

#### Methods

##### `parse_phone(phone_str: str) -> Optional[str]`

Parse and format a phone number.

**Parameters:**
- `phone_str` (str): Raw phone number string

**Returns:**
- `Optional[str]`: Formatted phone number or None

### ResumePatterns

Contains regex patterns for resume parsing.

```python
from pyresume.utils.patterns import ResumePatterns

patterns = ResumePatterns()
```

#### Properties

- `email_pattern`: Regex for email addresses
- `phone_pattern`: Regex for phone numbers
- `date_patterns`: List of date regex patterns
- `section_headers`: Common section header patterns
- `skill_categories`: Dictionary of skill categories

## Examples

### Basic Parsing

```python
from pyresume import ResumeParser

parser = ResumeParser()
resume = parser.parse('resume.pdf')

print(f"Name: {resume.contact_info.name}")
print(f"Email: {resume.contact_info.email}")
print(f"Phone: {resume.contact_info.phone}")
print(f"Experience: {resume.get_years_experience()} years")
```

### Batch Processing

```python
from pathlib import Path
from pyresume import ResumeParser

parser = ResumeParser()
resume_dir = Path('resumes/')

results = []
for resume_file in resume_dir.glob('*.pdf'):
    try:
        resume = parser.parse(str(resume_file))
        results.append({
            'file': resume_file.name,
            'name': resume.contact_info.name,
            'email': resume.contact_info.email,
            'experience_years': resume.get_years_experience()
        })
    except Exception as e:
        print(f"Error parsing {resume_file}: {e}")

# Save results
import json
with open('resume_analysis.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
```

### Confidence Analysis

```python
from pyresume import ResumeParser

parser = ResumeParser()
resume = parser.parse('resume.pdf')

# Check overall confidence
if resume.confidence_scores.get('overall', 0) < 0.7:
    print("Warning: Low confidence in parsing results")

# Check specific sections
contact_confidence = resume.confidence_scores.get('contact_info', 0)
if contact_confidence < 0.8:
    print("Contact information may need manual review")

# Analyze completeness
required_fields = ['name', 'email', 'phone']
missing_fields = []
for field in required_fields:
    if not getattr(resume.contact_info, field):
        missing_fields.append(field)

if missing_fields:
    print(f"Missing required fields: {missing_fields}")
```

### Custom Skill Detection

```python
from pyresume import ResumeParser
from pyresume.utils.patterns import ResumePatterns

# Extend skill categories
patterns = ResumePatterns()
patterns.skill_categories['data_science'] = [
    'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
    'Pandas', 'NumPy', 'Scikit-learn', 'Jupyter'
]

parser = ResumeParser()
resume = parser.parse('data_scientist_resume.pdf')

# Filter data science skills
data_skills = resume.get_skills_by_category('data_science')
print(f"Data Science Skills: {[skill.name for skill in data_skills]}")
```

## Error Handling

PyResume provides comprehensive error handling for common scenarios:

### File Errors

```python
from pyresume import ResumeParser

parser = ResumeParser()

try:
    resume = parser.parse('nonexistent.pdf')
except FileNotFoundError:
    print("Resume file not found")
except ValueError as e:
    print(f"Unsupported file format: {e}")
```

### Parsing Errors

```python
try:
    resume = parser.parse('corrupted.pdf')
except Exception as e:
    print(f"Parsing failed: {e}")
    # Resume object may still be returned with partial data
    if hasattr(e, 'partial_resume'):
        partial_resume = e.partial_resume
        print(f"Partial data extracted: {partial_resume.contact_info.email}")
```

### Validation

```python
resume = parser.parse('resume.pdf')

# Validate critical fields
if not resume.contact_info.email:
    print("Warning: No email address found")

if not resume.experience:
    print("Warning: No work experience found")

if resume.get_years_experience() == 0:
    print("Warning: Unable to calculate experience years")
```

## Performance Considerations

### Memory Usage

```python
# For large files, consider processing in chunks
import gc

for resume_file in large_resume_list:
    resume = parser.parse(resume_file)
    # Process resume
    process_resume(resume)
    # Clear memory
    del resume
    gc.collect()
```

### Batch Optimization

```python
# Reuse parser instance for better performance
parser = ResumeParser()

# Process multiple files
for file_path in file_paths:
    resume = parser.parse(file_path)
    # Process each resume
```

### Caching

```python
# Consider caching parsed results for repeated access
import pickle

def parse_with_cache(file_path):
    cache_path = f"{file_path}.cache"
    
    try:
        with open(cache_path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        resume = parser.parse(file_path)
        with open(cache_path, 'wb') as f:
            pickle.dump(resume, f)
        return resume
```

---

For more examples and advanced usage patterns, see the [examples/](../examples/) directory and the main [README.md](../README.md).