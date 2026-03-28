"""
SplitMind Core - Privacy protection and task orchestration.

A lightweight, zero-dependency (except pydantic) core library for:
- Sensitive information detection and redaction
- Task splitting and aggregation
- Privacy-preserving text processing

Example:
    >>> from splitmind_core import PrivacyHandler
    >>> handler = PrivacyHandler()
    >>> redacted, mapping = handler.redact("Phone: 13812345678")
    >>> print(redacted)
    Phone: [REDACTED_PHONE_1]
"""

from splitmind_core.privacy import PrivacyHandler, PrivacyReport, SensitiveInfo
from splitmind_core.splitter import TaskSplitter, TaskSplitResult, SubTask, TaskType
from splitmind_core.aggregator import ResultAggregator, AggregatedResult, SubTaskResult, AggregationStrategy

__version__ = "0.1.0"
__all__ = [
    # Privacy
    "PrivacyHandler",
    "PrivacyReport",
    "SensitiveInfo",
    # Task
    "TaskSplitter",
    "TaskSplitResult",
    "SubTask",
    "TaskType",
    # Aggregation
    "ResultAggregator",
    "AggregatedResult",
    "SubTaskResult",
    "AggregationStrategy",
]
