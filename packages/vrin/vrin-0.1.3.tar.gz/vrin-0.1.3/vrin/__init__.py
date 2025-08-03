"""
VRIN Memory Orchestration - AI-powered knowledge management and retrieval.

This package provides a simple interface for storing and retrieving knowledge
using natural language queries, with automatic fact extraction and reasoning.
"""

from .client import VRIN
from .exceptions import VRINError, VRINAuthenticationError, VRINRateLimitError, VRINTimeoutError

__version__ = "0.1.3"
__author__ = "VRIN Team"
__email__ = "contact@vrin.ai"

__all__ = [
    "VRIN",
    "VRINError", 
    "VRINAuthenticationError",
    "VRINRateLimitError",
    "VRINTimeoutError"
] 