"""
Setup script for pyresume package.
"""
from setuptools import setup, find_packages
import pathlib

# Read the contents of README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8") if (here / "README.md").exists() else ""

# Read requirements
def read_requirements(filename):
    """Read requirements from file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []

# Core dependencies
install_requires = [
    "pdfplumber>=0.10.0",
    "python-docx>=1.0.0", 
    "python-dateutil>=2.8.0",
    "phonenumbers>=8.13.0",
    "chardet>=5.0.0",
]

# Optional extras
extras_require = {
    'ocr': [
        'pytesseract>=0.3.10',
        'Pillow>=9.0.0',
    ],
    'ml': [
        'spacy>=3.5.0',
        'scikit-learn>=1.2.0',
        'numpy>=1.21.0',
    ],
    'anthropic': [
        'anthropic>=0.18.0',
    ],
    'openai': [
        'openai>=1.0.0',
    ],
    'llm': [
        'anthropic>=0.18.0',
        'openai>=1.0.0',
    ],
    'dev': [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'pytest-benchmark>=4.0.0',
        'black>=23.0.0',
        'flake8>=6.0.0',
        'mypy>=1.0.0',
        'sphinx>=6.0.0',
        'sphinx-rtd-theme>=1.2.0',
    ],
    'all': [
        # OCR dependencies
        'pytesseract>=0.3.10',
        'Pillow>=9.0.0',
        # ML dependencies  
        'spacy>=3.5.0',
        'scikit-learn>=1.2.0',
        'numpy>=1.21.0',
        # LLM dependencies
        'anthropic>=0.18.0',
        'openai>=1.0.0',
    ]
}

setup(
    name="leverparser",
    version="0.1.0",
    author="PyResume Team",
    author_email="contact@pyresume.dev",
    description="A fast, standalone Python library for parsing resumes with high accuracy and zero external dependencies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wespiper/leverparser",
    project_urls={
        "Bug Reports": "https://github.com/pyresume/pyresume/issues",
        "Source": "https://github.com/pyresume/pyresume",
        "Documentation": "https://pyresume.readthedocs.io/",
    },
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    package_data={
        "pyresume": ["data/*.json"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Topic :: Office/Business",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    # Note: CLI entry point commented out until cli module is implemented
    # entry_points={
    #     "console_scripts": [
    #         "pyresume=pyresume.cli:main",
    #     ],
    # },
    keywords="resume parser cv parsing pdf docx text extraction nlp",
    zip_safe=False,
    
    # Additional metadata
    platforms=["any"],
    license="MIT",
    
    # Testing (deprecated - moved to pyproject.toml)
    # test_suite="tests",
    # tests_require=extras_require["dev"],
    
    # For development installations
    setup_requires=[
        "wheel",
    ],
)