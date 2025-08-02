"""
GravixLayer Python SDK - OpenAI Compatible
"""

__version__ = "0.1.0"

from .client import GravixLayer
from .types.chat import (
    ChatCompletion,
    ChatCompletionMessage,
    ChatCompletionChoice,
    ChatCompletionUsage,
)

# For OpenAI compatibility
OpenAI = GravixLayer

__all__ = [
    "GravixLayer",
    "OpenAI",  # Alias for compatibility
    "ChatCompletion",
    "ChatCompletionMessage", 
    "ChatCompletionChoice",
    "ChatCompletionUsage",
]
