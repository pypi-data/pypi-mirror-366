"""Setup configuration for WorkFrame package."""

import os
from setuptools import setup, find_packages

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read version from package
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'workframe', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="workframe",
    version=get_version(),
    description="Simple Flask-based framework for building business applications quickly",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="WorkFrame Contributors",
    author_email="workframe@example.com",
    url="https://github.com/yourusername/workframe",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "Flask>=2.3.0",
        "Flask-SQLAlchemy>=3.0.0", 
        "Flask-Login>=0.6.0",
        "Werkzeug>=2.3.0",
        "Jinja2>=3.1.0",
        "WTForms>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "sphinx>=5.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business",
    ],
    keywords="flask framework business crud web application",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/workframe/issues",
        "Documentation": "https://github.com/yourusername/workframe",
        "Source Code": "https://github.com/yourusername/workframe",
    },
)