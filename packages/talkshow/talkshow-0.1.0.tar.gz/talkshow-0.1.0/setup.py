"""Setup configuration for TalkShow package."""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="talkshow",
    version="0.1.0",
    author="TalkShow Team",
    author_email="team@talkshow.dev",
    description="Chat History Analysis and Visualization Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/talkshow/talkshow",
    project_urls={
        "Bug Reports": "https://github.com/talkshow/talkshow/issues",
        "Source": "https://github.com/talkshow/talkshow",
        "Documentation": "https://talkshow.readthedocs.io",
    },
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "llm": [
            "litellm>=1.0.0",
        ],
        "web": [
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
        ],
        "cli": [
            "click>=8.0.0",
            "rich>=13.0.0",
            "pyyaml>=6.0.0",
            "psutil>=5.9.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "talkshow=talkshow.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "talkshow": ["config/*.yaml"],
    },
    keywords="chat, history, analysis, visualization, markdown, llm",
    zip_safe=False,
)