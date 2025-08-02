from typing import Dict, Any, List, Optional, Union, Iterator
import json
from ...types.chat import ChatCompletion, ChatCompletionChoice, ChatCompletionMessage, ChatCompletionUsage


class ChatCompletions:
    """Chat completions resource"""
    
    def __init__(self, client):
        self.client = client
    
    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ChatCompletion, Iterator[ChatCompletion]]:
        """
        Create a chat completion
        
        Args:
            model: Model to use for completion
            messages: List of messages in the conversation
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            top_p: Top-p sampling parameter
            frequency_penalty: Frequency penalty (-2 to 2)
            presence_penalty: Presence penalty (-2 to 2)
            stop: Stop sequences
            stream: Whether to stream responses
            **kwargs: Additional parameters
        
        Returns:
            ChatCompletion object or iterator for streaming
        """
        
        # Prepare request data
        data = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        # Add optional parameters
        if temperature is not None:
            data["temperature"] = temperature
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if top_p is not None:
            data["top_p"] = top_p
        if frequency_penalty is not None:
            data["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            data["presence_penalty"] = presence_penalty
        if stop is not None:
            data["stop"] = stop
            
        # Add any additional kwargs
        data.update(kwargs)
        
        if stream:
            return self._create_stream(data)
        else:
            return self._create_non_stream(data)
    
    def _create_non_stream(self, data: Dict[str, Any]) -> ChatCompletion:
        """Create non-streaming completion"""
        
        # Use the correct OpenAI-compatible endpoint
        response = self.client._make_request("POST", "chat/completions", data)
        response_data = response.json()
        
        # Convert to ChatCompletion format
        return self._parse_response(response_data)

    def _create_stream(self, data: Dict[str, Any]) -> Iterator[ChatCompletion]:
        """Create streaming completion"""
        
        # Use the correct OpenAI-compatible endpoint
        response = self.client._make_request("POST", "chat/completions", data, stream=True)
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    line = line[6:]  # Remove 'data: ' prefix
                    
                if line.strip() == '[DONE]':
                    break
                    
                try:
                    chunk_data = json.loads(line)
                    yield self._parse_response(chunk_data, is_stream=True)
                except json.JSONDecodeError:
                    continue

    
    def _parse_response(self, response_data: Dict[str, Any], is_stream: bool = False) -> ChatCompletion:
        """Parse API response to ChatCompletion format"""
        
        # Handle different response formats from GravixLayer
        if "choices" in response_data:
            choices = []
            for choice in response_data["choices"]:
                message = ChatCompletionMessage(
                    role=choice.get("message", {}).get("role", "assistant"),
                    content=choice.get("message", {}).get("content", "")
                )
                
                choices.append(ChatCompletionChoice(
                    index=choice.get("index", 0),
                    message=message,
                    finish_reason=choice.get("finish_reason")
                ))
        else:
            # Handle direct content response
            content = response_data.get("content", "")
            if isinstance(response_data, str):
                content = response_data
            
            message = ChatCompletionMessage(role="assistant", content=content)
            choices = [ChatCompletionChoice(index=0, message=message, finish_reason="stop")]
        
        # Usage information
        usage = None
        if "usage" in response_data:
            usage = ChatCompletionUsage(
                prompt_tokens=response_data["usage"].get("prompt_tokens", 0),
                completion_tokens=response_data["usage"].get("completion_tokens", 0),
                total_tokens=response_data["usage"].get("total_tokens", 0)
            )
        
        return ChatCompletion(
            id=response_data.get("id", "chatcmpl-" + str(hash(str(response_data)))),
            object="chat.completion" if not is_stream else "chat.completion.chunk",
            created=response_data.get("created", int(__import__("time").time())),
            model=response_data.get("model", "unknown"),
            choices=choices,
            usage=usage
        )
