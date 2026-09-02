from setuptools import setup, find_packages

setup(
    name="auto-research-agent",
    version="0.1.0",
    description="AutoResearch Multi-Agent System - Autonomous research with multi-agent collaboration and self-evolution",
    author="AutoResearch Team",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.8.0",
        "langchain>=0.1.0",
        "pydantic>=2.0.0",
        "streamlit>=1.28.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "pytest>=7.4.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
