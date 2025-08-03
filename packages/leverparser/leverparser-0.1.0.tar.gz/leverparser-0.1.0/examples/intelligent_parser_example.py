#!/usr/bin/env python3
"""
Intelligent Parser example for PyResume - Using LLMs for enhanced parsing
"""

import os
from pyresume import IntelligentResumeParser


def example_with_anthropic():
    """Example using Anthropic Claude for parsing."""
    print("=== Intelligent Parser with Anthropic Claude ===\n")
    
    # Method 1: Direct API key
    parser = IntelligentResumeParser(
        provider='anthropic',
        api_key='your-anthropic-api-key-here'  # Replace with your actual key
    )
    
    # Method 2: Using environment variable (recommended)
    # os.environ['ANTHROPIC_API_KEY'] = 'your-anthropic-api-key'
    # parser = IntelligentResumeParser(provider='anthropic')
    
    # Sample resume with complex formatting
    complex_resume = """
    Wesley Piper | Software Engineer
    wes.piper@gmail.com • 402.981.0715 • Stafford County, VA
    
    SUMMARY
    Engineer with 10+ years building human-centered technology systems. Currently 
    researching AI's impact on education through Scribe Tree Writer, an experimental 
    platform that transforms AI from answer-provider to thinking partner.
    
    PROFESSIONAL EXPERIENCE
    
    PBS Distribution, Arlington, VA — Senior Software Engineer
    May 2023 - Present
    • Led development of enterprise Product Information Management system serving 
      100+ employees across departments
    • Reduced training time by 30% through intuitive interface design based on 
      user research and cognitive load principles
    • Built scalable state management with React Query for real-time data sync
    
    Foreign Policy Magazine, Washington, DC — Software Engineer
    August 2021 - May 2023
    • Increased subscriptions 40% through complete rebuild of subscription services 
      using React, Angular, and RESTful APIs
    • Improved user retention 25% by redesigning onboarding experience with 
      data-driven UX optimizations and A/B testing
    
    EDUCATION
    
    Queen's University Belfast — M.A. English, 2009
    Creighton University — B.S. Digital Design & Development, 2013
    
    SKILLS
    Languages: Python, TypeScript, JavaScript, PHP
    Frontend: React, Next.js, Vue, Angular
    Backend: Node.js, Django, Flask
    """
    
    try:
        # Parse with LLM assistance
        resume = parser.parse_text(complex_resume)
        
        print("✅ Successfully parsed with Anthropic Claude")
        print(f"Name: {resume.contact_info.name}")
        print(f"Email: {resume.contact_info.email}")
        print(f"Experience positions: {len(resume.experience)}")
        print(f"Confidence score: {resume.confidence_scores.get('overall', 0):.2%}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have a valid API key set")


def example_with_openai():
    """Example using OpenAI GPT for parsing."""
    print("\n\n=== Intelligent Parser with OpenAI GPT ===\n")
    
    # Set up parser with OpenAI
    parser = IntelligentResumeParser(
        provider='openai',
        api_key='your-openai-api-key-here',  # Replace with your actual key
        model='gpt-4'  # Optional: specify model
    )
    
    # Parse a PDF file with complex layout
    try:
        # You would use an actual file path here
        # resume = parser.parse('complex_resume.pdf')
        
        # For demo, we'll use text
        resume = parser.parse_text("John Doe\njohn@example.com\nSoftware Engineer at Tech Corp")
        
        print("✅ Successfully parsed with OpenAI")
        print(f"Parsed name: {resume.contact_info.name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_with_fallback():
    """Example showing LLM with regex fallback."""
    print("\n\n=== Intelligent Parser with Fallback ===\n")
    
    # Configure parser to fall back to regex if LLM fails
    parser = IntelligentResumeParser(
        provider='anthropic',
        use_llm=True,
        fallback_to_regex=True,  # Enable fallback
        api_key=os.environ.get('ANTHROPIC_API_KEY')  # May be None
    )
    
    sample_text = """
    JANE SMITH
    jane.smith@email.com | 555-123-4567
    
    EXPERIENCE
    SENIOR DEVELOPER
    Tech Company | San Francisco, CA
    01/2020 - Present
    • Built scalable applications
    • Led team of 5 developers
    
    EDUCATION
    BS COMPUTER SCIENCE
    Stanford University | Stanford, CA
    2016 - 2020
    """
    
    try:
        resume = parser.parse_text(sample_text)
        
        # Check if LLM was used or fallback
        if parser.last_parse_used_llm:
            print("✅ Parsed with LLM")
        else:
            print("ℹ️  Parsed with regex fallback (no API key or LLM failed)")
        
        print(f"Name: {resume.contact_info.name}")
        print(f"Experience: {len(resume.experience)} positions")
        print(f"Education: {len(resume.education)} degrees")
        
    except Exception as e:
        print(f"Error: {e}")


def example_local_llm():
    """Example of integrating with a local LLM."""
    print("\n\n=== Local LLM Integration Example ===\n")
    
    # This is a template for integrating with local LLMs like Ollama
    from pyresume.providers.base import BaseLLMProvider
    
    class LocalLLMProvider(BaseLLMProvider):
        """Custom provider for local LLM."""
        
        def __init__(self, model_name='llama2', base_url='http://localhost:11434'):
            self.model_name = model_name
            self.base_url = base_url
        
        def parse_with_llm(self, text: str, prompt_type: str = 'full') -> dict:
            """Parse resume using local LLM."""
            # Here you would implement the actual call to your local LLM
            # For example, using Ollama:
            
            # import requests
            # prompt = self._build_prompt(text, prompt_type)
            # response = requests.post(
            #     f"{self.base_url}/api/generate",
            #     json={"model": self.model_name, "prompt": prompt}
            # )
            # return self._parse_llm_response(response.json()['response'])
            
            # For demo, return mock data
            return {
                'contact_info': {'name': 'Local LLM Parse'},
                'experience': [],
                'education': [],
                'skills': []
            }
    
    # Use local LLM provider
    parser = IntelligentResumeParser(
        provider=LocalLLMProvider(),
        fallback_to_regex=True
    )
    
    print("ℹ️  Local LLM provider template created")
    print("   Implement the parse_with_llm method to connect to your local model")


def example_batch_processing():
    """Example of batch processing with intelligent parser."""
    print("\n\n=== Batch Processing with Intelligent Parser ===\n")
    
    # Configure parser for batch processing
    parser = IntelligentResumeParser(
        provider='anthropic',
        api_key=os.environ.get('ANTHROPIC_API_KEY'),
        fallback_to_regex=True,
        use_llm=True
    )
    
    # Sample resumes to process
    resumes = [
        """John Developer | john@dev.com | Senior Engineer at TechCorp""",
        """Jane Designer | jane@design.com | UX Lead at DesignStudio""",
        """Bob Manager | bob@manage.com | Product Manager at StartupXYZ"""
    ]
    
    results = []
    for i, resume_text in enumerate(resumes):
        try:
            resume = parser.parse_text(resume_text)
            results.append({
                'index': i + 1,
                'name': resume.contact_info.name,
                'email': resume.contact_info.email,
                'used_llm': parser.last_parse_used_llm,
                'confidence': resume.confidence_scores.get('overall', 0)
            })
        except Exception as e:
            results.append({
                'index': i + 1,
                'error': str(e)
            })
    
    # Display results
    print("Batch Processing Results:")
    for result in results:
        if 'error' in result:
            print(f"  {result['index']}. ❌ Error: {result['error']}")
        else:
            llm_status = "LLM" if result['used_llm'] else "Regex"
            print(f"  {result['index']}. {result['name']} ({result['email']}) "
                  f"- {llm_status} - Confidence: {result['confidence']:.2%}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("PyResume Intelligent Parser Examples")
    print("=" * 60)
    
    # Check for API keys
    has_anthropic = bool(os.environ.get('ANTHROPIC_API_KEY'))
    has_openai = bool(os.environ.get('OPENAI_API_KEY'))
    
    if not has_anthropic and not has_openai:
        print("\n⚠️  No API keys found in environment variables.")
        print("   Set ANTHROPIC_API_KEY or OPENAI_API_KEY to use LLM features.")
        print("   The parser will fall back to regex-based parsing.\n")
    
    # Run examples
    example_with_fallback()  # This works without API keys
    
    if has_anthropic:
        example_with_anthropic()
    
    if has_openai:
        example_with_openai()
    
    example_local_llm()
    example_batch_processing()
    
    print("\n" + "=" * 60)
    print("For more examples, see the documentation at:")
    print("https://github.com/yourusername/pyresume")


if __name__ == "__main__":
    main()