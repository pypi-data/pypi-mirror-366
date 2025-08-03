# Contributing to PyResume

We love your input! We want to make contributing to PyResume as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## 🚀 Quick Start for Contributors

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork locally**:
   ```bash
   git clone https://github.com/your-username/pyresume.git
   cd pyresume
   ```

3. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .[dev]
   ```

4. **Run tests to verify setup**:
   ```bash
   pytest
   ```

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with the following guidelines:
   - Write clear, documented code
   - Add tests for new functionality
   - Update documentation as needed
   - Follow our coding standards

3. **Run the test suite**:
   ```bash
   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=pyresume --cov-report=html
   
   # Run specific test file
   pytest tests/test_parser.py -v
   ```

4. **Check code quality**:
   ```bash
   # Format code
   black pyresume/
   
   # Check style
   flake8 pyresume/
   
   # Type checking
   mypy pyresume/
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

6. **Push to your fork and submit a pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Development Guidelines

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **Flake8** for style checking
- **MyPy** for type checking
- **pytest** for testing

#### Code Formatting
```bash
# Format all Python files
black pyresume/ tests/ examples/

# Check formatting without making changes
black --check pyresume/
```

#### Style Guide
- Follow PEP 8
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep line length under 88 characters (Black default)

#### Example Code Style
```python
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class Experience:
    """Represents a work experience entry from a resume.
    
    Args:
        title: Job title or position name
        company: Company or organization name
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format, None if current
        description: Job description or responsibilities
        location: Work location (city, state/country)
    """
    title: Optional[str] = None
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None


def parse_experience_section(text: str) -> List[Experience]:
    """Parse the experience section of a resume.
    
    Args:
        text: Raw text from the experience section
        
    Returns:
        List of Experience objects extracted from the text
        
    Raises:
        ValueError: If the text cannot be parsed
    """
    # Implementation here
    pass
```

### Testing Guidelines

#### Test Structure
- Place tests in the `tests/` directory
- Mirror the source code structure in test files
- Use descriptive test function names

#### Test Categories
1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test complete parsing workflows
3. **Fixture Tests**: Test with real resume examples

#### Writing Tests
```python
import pytest
from pyresume import ResumeParser
from pyresume.models.resume import Resume


class TestResumeParser:
    """Test cases for the ResumeParser class."""
    
    def test_parse_contact_info_with_email(self):
        """Test parsing contact information containing email."""
        parser = ResumeParser()
        text = "John Doe\\njohn.doe@email.com\\n(555) 123-4567"
        
        resume = parser.parse_text(text)
        
        assert resume.contact_info.name == "John Doe"
        assert resume.contact_info.email == "john.doe@email.com"
        assert resume.contact_info.phone == "(555) 123-4567"
    
    def test_parse_invalid_file_raises_error(self):
        """Test that parsing non-existent file raises appropriate error."""
        parser = ResumeParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse("non_existent_file.pdf")
    
    @pytest.mark.integration
    def test_parse_complete_resume_fixture(self):
        """Integration test using complete resume fixture."""
        parser = ResumeParser()
        resume = parser.parse("tests/fixtures/resume_standard.txt")
        
        # Verify all major sections were parsed
        assert resume.contact_info.name is not None
        assert resume.contact_info.email is not None
        assert len(resume.experience) > 0
        assert len(resume.education) > 0
        assert len(resume.skills) > 0
```

#### Test Fixtures
We provide several test fixtures for development:

- `resume_standard.txt`: Well-formatted professional resume
- `resume_minimal.txt`: Basic resume with minimal information
- `resume_complex.txt`: Complex formatting and multiple sections
- `resume_edge_cases.txt`: Special characters and edge cases
- `resume_international.txt`: Non-English resume example
- `resume_malformed.txt`: Poorly structured resume

### Documentation

#### Docstring Style
Use Google-style docstrings:

```python
def extract_skills(text: str, categories: Dict[str, List[str]]) -> List[Skill]:
    """Extract skills from resume text using predefined categories.
    
    This function searches for skills mentioned in the resume text and
    categorizes them based on the provided skill categories dictionary.
    
    Args:
        text: Resume text to search for skills
        categories: Dictionary mapping category names to lists of skills
        
    Returns:
        List of Skill objects found in the text, with categories assigned
        
    Raises:
        ValueError: If categories dictionary is empty or malformed
        
    Example:
        >>> categories = {"programming": ["Python", "Java"]}
        >>> skills = extract_skills("I know Python and Java", categories)
        >>> len(skills)
        2
    """
```

#### README Updates
When adding new features, update the README.md with:
- New API examples
- Updated feature lists
- Performance impact (if significant)

## 🐛 Bug Reports

Great bug reports tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

### Bug Report Template

```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Parse resume with '...'
2. Access field '....'
3. See error

**Expected Behavior**
A clear description of what you expected to happen.

**Actual Behavior**
What actually happened, including any error messages.

**Resume Sample**
If possible, provide a minimal resume example that reproduces the issue.
(Please remove any personal information)

**Environment**
- OS: [e.g. Windows 10, macOS 12.1, Ubuntu 20.04]
- Python Version: [e.g. 3.9.7]
- PyResume Version: [e.g. 0.1.0]
- Dependencies: [output of `pip list | grep -E "(pdfplumber|python-docx)"`]

**Additional Context**
Add any other context about the problem here.
```

## 💡 Feature Requests

We welcome feature requests! Please provide:

1. **Use Case**: Describe the problem you're trying to solve
2. **Proposed Solution**: How you think it should work
3. **Alternatives**: Other solutions you've considered
4. **Impact**: Who would benefit from this feature

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions or features you've considered.

**Use Case**
Provide a concrete example of how this feature would be used.

**Additional context**
Add any other context or screenshots about the feature request here.
```

## 🎯 Priority Areas

We're especially interested in contributions in these areas:

### High Priority
- **Performance Optimization**: Faster parsing algorithms
- **Accuracy Improvements**: Better pattern recognition
- **International Support**: Non-English resume parsing
- **File Format Support**: Additional format extractors

### Medium Priority
- **ML Integration**: Optional machine learning features
- **API Enhancements**: More flexible configuration options
- **Testing**: Additional test fixtures and edge cases
- **Documentation**: Tutorials and advanced examples

### Low Priority (but welcome!)
- **UI Tools**: Visual debugging tools
- **Benchmarking**: Performance comparison utilities
- **Integrations**: Framework-specific helpers
- **Advanced Features**: OCR, template detection

## 📋 Pull Request Process

1. **Fork and branch**: Create a feature branch from `main`
2. **Implement**: Make your changes with tests and documentation
3. **Test**: Ensure all tests pass and coverage doesn't decrease
4. **Document**: Update relevant documentation
5. **Submit**: Create a pull request with a clear description

### Pull Request Template

When submitting a PR, please include:

```markdown
**Description**
Brief description of what this PR does.

**Changes Made**
- Added/modified/removed X
- Fixed issue with Y
- Improved Z

**Testing**
- [ ] All existing tests pass
- [ ] Added tests for new functionality
- [ ] Manual testing completed

**Documentation**
- [ ] Updated README if needed
- [ ] Added/updated docstrings
- [ ] Updated examples if applicable

**Checklist**
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] No sensitive data included
```

### Review Process

1. **Automated Checks**: CI will run tests and style checks
2. **Code Review**: Maintainers will review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, your PR will be merged

## 🏆 Recognition

Contributors are recognized in several ways:

- **README Credits**: All contributors listed in README
- **Release Notes**: Major contributions noted in releases
- **GitHub**: Contributor status and commit history
- **Community**: Recognition in discussions and issues

## 📧 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: contact@pyresume.dev for private matters

## 📜 Code of Conduct

### Our Pledge

We are committed to making participation in our project a harassment-free experience for everyone, regardless of:

- Age, body size, disability, ethnicity, gender identity and expression
- Level of experience, nationality, personal appearance
- Race, religion, or sexual identity and orientation

### Our Standards

Examples of behavior that contributes to creating a positive environment:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

### Enforcement

Project maintainers have the right and responsibility to remove, edit, or reject:

- Comments, commits, code, wiki edits, issues, and other contributions
- That are not aligned with this Code of Conduct

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at contact@pyresume.dev.

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to PyResume! 🎉