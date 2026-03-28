"""
SplitMind - Privacy-preserving multi-agent task orchestration system.

A system that splits tasks for privacy protection, distributes them to 
different AI providers, and aggregates the results.
"""

from splitmind.core.splitter import TaskSplitter, SubTask
from splitmind.core.aggregator import ResultAggregator
from splitmind.core.privacy import PrivacyHandler
from splitmind.core.engine import SplitMindEngine
from splitmind.providers.base import BaseProvider
from splitmind.providers.registry import ProviderRegistry

__version__ = "0.1.0"
__all__ = [
    "SplitMindEngine",
    "TaskSplitter",
    "SubTask",
    "ResultAggregator",
    "PrivacyHandler",
    "BaseProvider",
    "ProviderRegistry",
]
