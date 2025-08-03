#!/usr/bin/env python3
"""
Batch processing example for pyresume library.

This example shows how to process multiple resume files and analyze them in bulk.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from pyresume import ResumeParser


class ResumeBatchProcessor:
    """Process multiple resumes and generate reports."""
    
    def __init__(self):
        """Initialize the batch processor."""
        self.parser = ResumeParser()
        self.results = []
        self.errors = []
    
    def process_directory(self, directory_path: str, recursive: bool = False) -> List[Dict[str, Any]]:
        """
        Process all resume files in a directory.
        
        Args:
            directory_path: Path to directory containing resumes
            recursive: Whether to search subdirectories
            
        Returns:
            List of parsed resume data
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Supported file extensions
        supported_extensions = {'.pdf', '.docx', '.txt'}
        
        # Find all resume files
        pattern = "**/*" if recursive else "*"
        resume_files = []
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                resume_files.append(file_path)
        
        print(f"Found {len(resume_files)} resume files to process...")
        
        # Process each file
        for i, file_path in enumerate(resume_files, 1):
            print(f"Processing {i}/{len(resume_files)}: {file_path.name}")
            
            try:
                resume = self.parser.parse(str(file_path))
                
                # Create summary data
                summary = {
                    'file_name': file_path.name,
                    'file_path': str(file_path),
                    'file_type': file_path.suffix.lower(),
                    'contact_name': resume.contact_info.name,
                    'email': resume.contact_info.email,
                    'phone': resume.contact_info.phone,
                    'years_experience': resume.get_years_experience(),
                    'num_jobs': len(resume.experience),
                    'num_education': len(resume.education),
                    'num_skills': len(resume.skills),
                    'num_projects': len(resume.projects),
                    'num_certifications': len(resume.certifications),
                    'has_summary': bool(resume.summary),
                    'skills_list': [skill.name for skill in resume.skills],
                    'companies': [exp.company for exp in resume.experience if exp.company],
                    'universities': [edu.institution for edu in resume.education if edu.institution],
                    'processing_success': True
                }
                
                self.results.append(summary)
                
            except Exception as e:
                error_info = {
                    'file_name': file_path.name,
                    'file_path': str(file_path),
                    'error': str(e),
                    'error_type': type(e).__name__
                }
                self.errors.append(error_info)
                print(f"  Error processing {file_path.name}: {e}")
        
        return self.results
    
    def generate_csv_report(self, output_path: str):
        """Generate a CSV report of all processed resumes."""
        if not self.results:
            print("No results to export.")
            return
        
        # Define CSV columns
        csv_columns = [
            'file_name', 'contact_name', 'email', 'phone',
            'years_experience', 'num_jobs', 'num_education',
            'num_skills', 'num_projects', 'num_certifications',
            'has_summary', 'companies', 'universities'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            
            for result in self.results:
                # Convert lists to comma-separated strings for CSV
                row = result.copy()
                row['companies'] = '; '.join(row.get('companies', []))
                row['universities'] = '; '.join(row.get('universities', []))
                
                # Only include columns that exist in CSV schema
                filtered_row = {k: v for k, v in row.items() if k in csv_columns}
                writer.writerow(filtered_row)
        
        print(f"CSV report saved to: {output_path}")
    
    def generate_json_report(self, output_path: str):
        """Generate a detailed JSON report."""
        report = {
            'summary': {
                'total_files_processed': len(self.results) + len(self.errors),
                'successful_parses': len(self.results),
                'failed_parses': len(self.errors),
                'success_rate': len(self.results) / (len(self.results) + len(self.errors)) * 100 if (len(self.results) + len(self.errors)) > 0 else 0
            },
            'results': self.results,
            'errors': self.errors
        }
        
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(report, jsonfile, indent=2, default=str)
        
        print(f"JSON report saved to: {output_path}")
    
    def analyze_skills(self) -> Dict[str, int]:
        """Analyze skills across all resumes."""
        skill_counts = {}
        
        for result in self.results:
            for skill in result.get('skills_list', []):
                skill_lower = skill.lower().strip()
                skill_counts[skill_lower] = skill_counts.get(skill_lower, 0) + 1
        
        # Sort by frequency
        sorted_skills = dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True))
        return sorted_skills
    
    def analyze_companies(self) -> Dict[str, int]:
        """Analyze companies across all resumes."""
        company_counts = {}
        
        for result in self.results:
            for company in result.get('companies', []):
                if company:
                    company_lower = company.lower().strip()
                    company_counts[company_lower] = company_counts.get(company_lower, 0) + 1
        
        sorted_companies = dict(sorted(company_counts.items(), key=lambda x: x[1], reverse=True))
        return sorted_companies
    
    def print_analytics(self):
        """Print analytics summary."""
        if not self.results:
            print("No results to analyze.")
            return
        
        print("\\n=== BATCH PROCESSING ANALYTICS ===")
        print(f"Total resumes processed: {len(self.results)}")
        print(f"Processing errors: {len(self.errors)}")
        
        # Experience analytics
        experiences = [r['years_experience'] for r in self.results if r['years_experience']]
        if experiences:
            avg_experience = sum(experiences) / len(experiences)
            print(f"Average years of experience: {avg_experience:.1f}")
            print(f"Experience range: {min(experiences):.1f} - {max(experiences):.1f} years")
        
        # Skills analytics
        print(f"\\n=== TOP SKILLS ===")
        skills = self.analyze_skills()
        for skill, count in list(skills.items())[:10]:
            print(f"{skill}: {count} resumes")
        
        # Companies analytics
        print(f"\\n=== TOP COMPANIES ===")
        companies = self.analyze_companies()
        for company, count in list(companies.items())[:10]:
            print(f"{company}: {count} resumes")


def main():
    """Demonstrate batch processing."""
    processor = ResumeBatchProcessor()
    
    # Example usage
    resume_directory = "sample_resumes"  # Replace with actual directory
    
    print("=== RESUME BATCH PROCESSING DEMO ===")
    print(f"Looking for resumes in: {resume_directory}")
    
    try:
        # Process all resumes in directory
        results = processor.process_directory(resume_directory, recursive=True)
        
        # Generate reports
        processor.generate_csv_report("resume_analysis.csv")
        processor.generate_json_report("resume_analysis.json")
        
        # Print analytics
        processor.print_analytics()
        
        print(f"\\nProcessing complete! Processed {len(results)} resumes successfully.")
        
    except FileNotFoundError:
        print(f"Directory '{resume_directory}' not found.")
        print("\\nTo use this example:")
        print("1. Create a directory with resume files (PDF, DOCX, or TXT)")
        print("2. Update the 'resume_directory' variable in this script")
        print("3. Run the script again")
        
        # Demonstrate with mock data
        print("\\n=== MOCK DATA DEMONSTRATION ===")
        demonstrate_with_mock_data(processor)


def demonstrate_with_mock_data(processor: ResumeBatchProcessor):
    """Demonstrate analytics with mock data."""
    # Create some mock results for demonstration
    mock_results = [
        {
            'file_name': 'resume1.pdf',
            'contact_name': 'John Doe',
            'email': 'john@email.com',
            'years_experience': 5.2,
            'num_jobs': 3,
            'skills_list': ['Python', 'JavaScript', 'React', 'SQL'],
            'companies': ['Google', 'Microsoft']
        },
        {
            'file_name': 'resume2.docx',
            'contact_name': 'Jane Smith',
            'email': 'jane@email.com',
            'years_experience': 8.1,
            'num_jobs': 4,
            'skills_list': ['Java', 'Python', 'AWS', 'Docker'],
            'companies': ['Amazon', 'Netflix']
        },
        {
            'file_name': 'resume3.txt',
            'contact_name': 'Bob Johnson',
            'email': 'bob@email.com',
            'years_experience': 3.5,
            'num_jobs': 2,
            'skills_list': ['JavaScript', 'Node.js', 'React', 'MongoDB'],
            'companies': ['Startup Inc', 'Tech Corp']
        }
    ]
    
    processor.results = mock_results
    processor.print_analytics()


if __name__ == "__main__":
    main()