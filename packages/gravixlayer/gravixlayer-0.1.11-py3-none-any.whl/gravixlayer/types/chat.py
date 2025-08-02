from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class ChatCompletionMessage:
    """Chat completion message"""
    role: str
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None


@dataclass  
class ChatCompletionChoice:
    """Chat completion choice"""
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[str] = None


@dataclass
class ChatCompletionUsage:
    """Chat completion usage statistics"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class ChatCompletion:
    """Chat completion response"""
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[ChatCompletionUsage] = None
