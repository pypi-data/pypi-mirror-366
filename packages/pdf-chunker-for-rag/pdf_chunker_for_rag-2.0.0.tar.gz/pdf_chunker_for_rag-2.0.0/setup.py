"""
Setup script for PDF Chunker library.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pdf_chunker_for_rag",
    version="2.0.0",
    author="AI Assistant",
    author_email="assistant@example.com",
    description="Production-ready PDF chunking library with intelligent content filtering and strategic header detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/chunk_creation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyMuPDF>=1.23.0",
        "pypdf>=3.0.0",
    ],
    extras_require={
        "nlp": ["spacy>=3.5.0"],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "pdf_chunker_for_rag": ["*.md", "*.txt"],
    },
)
