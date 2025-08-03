#!/usr/bin/env python3
"""
Confidence scores example for pyresume library.

This example demonstrates how to work with confidence scores and extraction metadata
to understand the quality and reliability of the parsed resume data.
"""

from pyresume import ResumeParser
from pyresume.models.resume import Resume
import json


class ConfidenceAnalyzer:
    """Analyze confidence scores and extraction quality."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.parser = ResumeParser()
    
    def analyze_resume_confidence(self, resume: Resume) -> dict:
        """
        Analyze confidence scores for different resume sections.
        
        Args:
            resume: Parsed resume object
            
        Returns:
            Dictionary with confidence analysis
        """
        analysis = {
            'overall_confidence': 0.0,
            'section_confidence': {},
            'data_completeness': {},
            'extraction_quality': {},
            'recommendations': []
        }
        
        # Analyze contact information confidence
        contact_confidence = self._analyze_contact_confidence(resume)
        analysis['section_confidence']['contact_info'] = contact_confidence
        
        # Analyze experience section confidence
        experience_confidence = self._analyze_experience_confidence(resume)
        analysis['section_confidence']['experience'] = experience_confidence
        
        # Analyze education section confidence
        education_confidence = self._analyze_education_confidence(resume)
        analysis['section_confidence']['education'] = education_confidence
        
        # Analyze skills section confidence
        skills_confidence = self._analyze_skills_confidence(resume)
        analysis['section_confidence']['skills'] = skills_confidence
        
        # Calculate overall confidence
        confidences = list(analysis['section_confidence'].values())
        analysis['overall_confidence'] = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Analyze data completeness
        analysis['data_completeness'] = self._analyze_completeness(resume)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(resume, analysis)
        
        return analysis
    
    def _analyze_contact_confidence(self, resume: Resume) -> float:
        """Analyze confidence in contact information extraction."""
        confidence = 0.0
        total_fields = 0
        
        # Check each contact field
        contact_fields = [
            resume.contact_info.name,
            resume.contact_info.email,
            resume.contact_info.phone,
            resume.contact_info.address,
            resume.contact_info.linkedin,
            resume.contact_info.github
        ]
        
        for field in contact_fields:
            total_fields += 1
            if field:
                # Basic validation
                if '@' in str(field) and '.' in str(field):  # Email-like
                    confidence += 0.9
                elif any(char.isdigit() for char in str(field)) and len(str(field)) >= 10:  # Phone-like
                    confidence += 0.8
                elif 'linkedin' in str(field).lower() or 'github' in str(field).lower():  # Social links
                    confidence += 0.85
                else:
                    confidence += 0.7  # Name or address
        
        return confidence / total_fields if total_fields > 0 else 0.0
    
    def _analyze_experience_confidence(self, resume: Resume) -> float:
        """Analyze confidence in experience extraction."""
        if not resume.experience:
            return 0.0
        
        total_confidence = 0.0
        
        for exp in resume.experience:
            exp_confidence = 0.0
            field_count = 0
            
            # Check required fields
            if exp.title:
                exp_confidence += 0.3
                field_count += 1
            if exp.company:
                exp_confidence += 0.3
                field_count += 1
            if exp.start_date:
                exp_confidence += 0.2
                field_count += 1
            if exp.description or exp.responsibilities:
                exp_confidence += 0.2
                field_count += 1
            
            # Bonus for date consistency
            if exp.start_date and exp.end_date and exp.start_date <= exp.end_date:
                exp_confidence += 0.1
            elif exp.current and exp.start_date:
                exp_confidence += 0.1
            
            total_confidence += exp_confidence
        
        return total_confidence / len(resume.experience)
    
    def _analyze_education_confidence(self, resume: Resume) -> float:
        """Analyze confidence in education extraction."""
        if not resume.education:
            return 0.0
        
        total_confidence = 0.0
        
        for edu in resume.education:
            edu_confidence = 0.0
            
            if edu.degree:
                edu_confidence += 0.4
            if edu.institution:
                edu_confidence += 0.4
            if edu.graduation_date:
                edu_confidence += 0.2
            
            total_confidence += edu_confidence
        
        return total_confidence / len(resume.education)
    
    def _analyze_skills_confidence(self, resume: Resume) -> float:
        """Analyze confidence in skills extraction."""
        if not resume.skills:
            return 0.0
        
        # Load known skills for validation
        try:
            from pyresume.data.skills import SKILL_CATEGORIES
            known_skills = set()
            for category_skills in SKILL_CATEGORIES.values():
                known_skills.update(skill.lower() for skill in category_skills)
        except:
            # Fallback to common skills
            known_skills = {
                'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'html', 'css',
                'aws', 'docker', 'kubernetes', 'git', 'linux', 'windows', 'macos'
            }
        
        recognized_skills = 0
        for skill in resume.skills:
            if skill.name.lower() in known_skills:
                recognized_skills += 1
        
        recognition_rate = recognized_skills / len(resume.skills) if resume.skills else 0.0
        
        # Confidence based on recognition rate and number of skills
        confidence = recognition_rate * 0.7
        
        # Bonus for reasonable number of skills (5-20 is typical)
        skill_count = len(resume.skills)
        if 5 <= skill_count <= 20:
            confidence += 0.3
        elif skill_count > 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _analyze_completeness(self, resume: Resume) -> dict:
        """Analyze how complete the extracted data is."""
        completeness = {
            'contact_info': 0.0,
            'experience': 0.0,
            'education': 0.0,
            'skills': 0.0,
            'overall': 0.0
        }
        
        # Contact completeness
        contact_fields = [
            resume.contact_info.name,
            resume.contact_info.email,
            resume.contact_info.phone
        ]
        contact_filled = sum(1 for field in contact_fields if field)
        completeness['contact_info'] = contact_filled / len(contact_fields)
        
        # Experience completeness
        if resume.experience:
            exp_completeness = []
            for exp in resume.experience:
                fields = [exp.title, exp.company, exp.start_date]
                filled = sum(1 for field in fields if field)
                exp_completeness.append(filled / len(fields))
            completeness['experience'] = sum(exp_completeness) / len(exp_completeness)
        
        # Education completeness
        if resume.education:
            edu_completeness = []
            for edu in resume.education:
                fields = [edu.degree, edu.institution]
                filled = sum(1 for field in fields if field)
                edu_completeness.append(filled / len(fields))
            completeness['education'] = sum(edu_completeness) / len(edu_completeness)
        
        # Skills completeness (binary - either has skills or doesn't)
        completeness['skills'] = 1.0 if resume.skills else 0.0
        
        # Overall completeness
        section_scores = [
            completeness['contact_info'],
            completeness['experience'],
            completeness['education'],
            completeness['skills']
        ]
        completeness['overall'] = sum(section_scores) / len(section_scores)
        
        return completeness
    
    def _generate_recommendations(self, resume: Resume, analysis: dict) -> list:
        """Generate recommendations for improving extraction quality."""
        recommendations = []
        
        # Check overall confidence
        overall_conf = analysis['overall_confidence']
        if overall_conf < 0.5:
            recommendations.append("Overall extraction confidence is low. Consider preprocessing the resume text or using a different file format.")
        
        # Check contact info
        contact_conf = analysis['section_confidence'].get('contact_info', 0)
        if contact_conf < 0.6:
            recommendations.append("Contact information extraction has low confidence. Verify email and phone number formats.")
        
        # Check experience section
        exp_conf = analysis['section_confidence'].get('experience', 0)
        if exp_conf < 0.6:
            recommendations.append("Experience section extraction needs improvement. Check date formats and job title/company clarity.")
        
        # Check completeness
        completeness = analysis['data_completeness']['overall']
        if completeness < 0.7:
            recommendations.append("Resume data appears incomplete. Some sections may be missing or poorly formatted.")
        
        # Check for missing critical information
        if not resume.contact_info.email:
            recommendations.append("No email address found. This is critical contact information.")
        
        if not resume.experience:
            recommendations.append("No work experience found. Check if the experience section is clearly labeled.")
        
        if not resume.skills:
            recommendations.append("No skills found. Consider adding a dedicated skills section.")
        
        return recommendations
    
    def print_confidence_report(self, resume: Resume):
        """Print a detailed confidence report."""
        analysis = self.analyze_resume_confidence(resume)
        
        print("\\n=== CONFIDENCE ANALYSIS REPORT ===")
        print(f"Overall Confidence: {analysis['overall_confidence']:.2%}")
        
        print("\\n--- Section Confidence Scores ---")
        for section, confidence in analysis['section_confidence'].items():
            status = "✓" if confidence > 0.7 else "⚠" if confidence > 0.4 else "✗"
            print(f"{status} {section.replace('_', ' ').title()}: {confidence:.2%}")
        
        print("\\n--- Data Completeness ---")
        for section, completeness in analysis['data_completeness'].items():
            if section != 'overall':
                status = "✓" if completeness > 0.8 else "⚠" if completeness > 0.5 else "✗"
                print(f"{status} {section.replace('_', ' ').title()}: {completeness:.2%}")
        
        print(f"\\nOverall Completeness: {analysis['data_completeness']['overall']:.2%}")
        
        if analysis['recommendations']:
            print("\\n--- Recommendations ---")
            for i, rec in enumerate(analysis['recommendations'], 1):
                print(f"{i}. {rec}")
        else:
            print("\\n✓ No specific recommendations - extraction quality looks good!")


def main():
    """Demonstrate confidence analysis."""
    parser = ResumeParser()
    analyzer = ConfidenceAnalyzer()
    
    print("=== CONFIDENCE SCORES DEMO ===")
    
    # Example with sample text
    sample_resume_text = """
    John Smith
    john.smith@email.com
    (555) 123-4567
    LinkedIn: linkedin.com/in/johnsmith
    
    PROFESSIONAL EXPERIENCE
    
    Senior Software Engineer
    Tech Corporation, San Francisco, CA
    January 2020 - Present
    • Led development of microservices architecture serving 1M+ users
    • Implemented automated testing and CI/CD pipelines
    • Mentored team of 5 junior developers
    
    Software Developer
    StartupXYZ, Austin, TX
    June 2018 - December 2019
    • Built full-stack web applications using React and Node.js
    • Collaborated with product team to define technical requirements
    • Reduced application load time by 40% through optimization
    
    EDUCATION
    
    Bachelor of Science in Computer Science
    University of Texas at Austin
    Graduated: May 2018
    GPA: 3.7/4.0
    
    TECHNICAL SKILLS
    Programming Languages: Python, JavaScript, Java, TypeScript
    Web Technologies: React, Node.js, Express, HTML, CSS
    Databases: PostgreSQL, MongoDB, Redis
    Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins
    """
    
    try:
        print("Parsing sample resume...")
        resume = parser.parse_text(sample_resume_text)
        
        # Display basic info
        print(f"\\nParsed resume for: {resume.get_contact_summary()}")
        print(f"Experience entries: {len(resume.experience)}")
        print(f"Education entries: {len(resume.education)}")
        print(f"Skills found: {len(resume.skills)}")
        
        # Analyze confidence
        analyzer.print_confidence_report(resume)
        
        # Show detailed analysis as JSON
        analysis = analyzer.analyze_resume_confidence(resume)
        print("\\n=== DETAILED ANALYSIS (JSON) ===")
        print(json.dumps(analysis, indent=2, default=str))
        
    except Exception as e:
        print(f"Error processing resume: {e}")
    
    # Example with poor quality resume
    print("\\n\\n=== LOW QUALITY RESUME EXAMPLE ===")
    
    poor_resume_text = """
    Some random text that doesn't look like a resume
    Contact info is missing
    No clear sections
    Random phone number: 123
    Invalid email: notanemail
    """
    
    try:
        poor_resume = parser.parse_text(poor_resume_text)
        analyzer.print_confidence_report(poor_resume)
        
    except Exception as e:
        print(f"Error processing poor quality resume: {e}")


if __name__ == "__main__":
    main()