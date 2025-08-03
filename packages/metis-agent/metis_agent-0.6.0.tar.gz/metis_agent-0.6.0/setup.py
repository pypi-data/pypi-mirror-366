from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="metis-agent",
    version="0.6.0",
    author="Metis OS Team",
    author_email="cjohnson@metisos.com",
    description="A comprehensive framework for building powerful AI agents with enhanced tools, autonomous capability expansion, blueprint opportunity detection, and intelligent memory management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/metisos/metisos_agentV1",
    project_urls={
        "Documentation": "https://github.com/metisos/metisos_agentV1/blob/main/DOCUMENTATION.md",
        "Bug Tracker": "https://github.com/metisos/metisos_agentV1/issues",
        "Source Code": "https://github.com/metisos/metisos_agentV1",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords="ai, agent, llm, openai, groq, anthropic, huggingface, tools, memory, conversation, context-management, token-aware, intelligent-summarization, blueprint-detection, autonomous-tools, dynamic-generation, capability-expansion, text-analysis, sentiment-analysis, web-scraping, python-execution, advanced-math, nlp, readability-assessment, e2b, code-sandbox, secure-execution, cloud-sandbox",
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "groq>=0.4.0",
        "anthropic>=0.5.0",
        "huggingface-hub>=0.16.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
        "click>=8.0.0",
        "numpy>=1.20.0",
        "cryptography>=36.0.0",
        "pydantic>=1.8.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",  # For advanced web scraping
        "scipy>=1.7.0",  # For advanced mathematical operations
        "sympy>=1.8",    # For symbolic mathematics
        "e2b-code-interpreter>=1.5.0",  # For secure code execution in cloud sandboxes
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "flake8>=3.9.2",
            "mypy>=0.812",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.2",
            "myst-parser>=0.15.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "metis=metis_agent.cli.commands:cli",
        ],
    },
    include_package_data=True,
    license="Apache License 2.0",
)