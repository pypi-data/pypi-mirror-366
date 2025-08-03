#!/usr/bin/env python3
"""
Basic usage example for pyresume library.

This example demonstrates how to parse a resume file and extract basic information.
"""

from pyresume import ResumeParser
from pathlib import Path


def main():
    """Demonstrate basic resume parsing."""
    # Initialize the parser
    parser = ResumeParser()
    
    # Example 1: Parse a resume file
    print("=== Basic Resume Parsing ===")
    
    # You would replace this with an actual resume file path
    resume_file = "sample_resume.pdf"  # or .docx, .txt
    
    try:
        # Parse the resume
        resume = parser.parse(resume_file)
        
        # Display basic information
        print(f"Contact Summary: {resume.get_contact_summary()}")
        print(f"Years of Experience: {resume.get_years_experience()}")
        print(f"Number of Jobs: {len(resume.experience)}")
        print(f"Number of Education Entries: {len(resume.education)}")
        print(f"Number of Skills: {len(resume.skills)}")
        
        # Display contact information
        if resume.contact_info.name:
            print(f"\\nName: {resume.contact_info.name}")
        if resume.contact_info.email:
            print(f"Email: {resume.contact_info.email}")
        if resume.contact_info.phone:
            print(f"Phone: {resume.contact_info.phone}")
        
        # Display recent experience
        if resume.experience:
            print("\\n=== Recent Experience ===")
            for i, exp in enumerate(resume.experience[:3]):  # Show first 3 jobs
                print(f"{i+1}. {exp.title} at {exp.company}")
                if exp.start_date:
                    end_date = exp.end_date if exp.end_date else "Present"
                    print(f"   Duration: {exp.start_date} - {end_date}")
        
        # Display education
        if resume.education:
            print("\\n=== Education ===")
            for edu in resume.education:
                print(f"- {edu.degree} from {edu.institution}")
                if edu.graduation_date:
                    print(f"  Graduated: {edu.graduation_date}")
        
        # Display top skills
        if resume.skills:
            print("\\n=== Skills ===")
            for skill in resume.skills[:10]:  # Show first 10 skills
                category = f" ({skill.category})" if skill.category else ""
                proficiency = f" - {skill.proficiency}" if skill.proficiency else ""
                print(f"- {skill.name}{category}{proficiency}")
        
    except FileNotFoundError:
        print(f"Resume file not found: {resume_file}")
        print("Please provide a valid resume file path.")
    except ValueError as e:
        print(f"Error parsing resume: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    # Example 2: Parse raw text
    print("\\n\\n=== Parsing Raw Text ===")
    
    sample_text = """
    John Smith
    john.smith@email.com
    (555) 123-4567
    
    EXPERIENCE
    Senior Software Engineer
    Tech Corporation, San Francisco, CA
    January 2020 - Present
    - Led development of microservices architecture
    - Mentored junior developers
    - Implemented CI/CD pipelines
    
    Software Developer
    StartupXYZ, Austin, TX
    June 2018 - December 2019
    - Built web applications using React and Node.js
    - Collaborated with cross-functional teams
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Texas at Austin
    2014 - 2018
    GPA: 3.7/4.0
    
    SKILLS
    Python, JavaScript, React, Node.js, Docker, Kubernetes, AWS
    """
    
    try:
        resume = parser.parse_text(sample_text)
        
        print(f"Parsed resume for: {resume.get_contact_summary()}")
        print(f"Experience entries: {len(resume.experience)}")
        print(f"Education entries: {len(resume.education)}")
        
        # Convert to dictionary for JSON export
        resume_dict = resume.to_dict()
        print(f"\\nResume data structure has {len(resume_dict)} main sections")
        
    except Exception as e:
        print(f"Error parsing text: {e}")


def demonstrate_supported_formats():
    """Show which file formats are supported."""
    parser = ResumeParser()
    
    print("\\n=== Supported File Formats ===")
    for ext, extractor in parser.extractors.items():
        extractor_name = extractor.__class__.__name__
        print(f"- {ext}: {extractor_name}")
    
    print("\\nTo use pyresume with PDF or DOCX files, make sure you have the required dependencies:")
    print("- For PDF: pip install pdfplumber")
    print("- For DOCX: pip install python-docx")


if __name__ == "__main__":
    main()
    demonstrate_supported_formats()