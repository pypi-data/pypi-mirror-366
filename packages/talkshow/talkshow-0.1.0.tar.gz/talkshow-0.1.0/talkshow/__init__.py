"""
TalkShow - Chat History Analysis and Visualization Tool

A tool for analyzing and visualizing chat history from SpecStory plugin.
"""

__version__ = "0.2.0"

# Import main components
from .parser.md_parser import MDParser
from .storage.json_storage import JSONStorage
from .summarizer.rule_summarizer import RuleSummarizer
from .summarizer.llm_summarizer import LLMSummarizer
from .config.manager import ConfigManager

__all__ = [
    "MDParser",
    "JSONStorage", 
    "RuleSummarizer",
    "LLMSummarizer",
    "ConfigManager",
]