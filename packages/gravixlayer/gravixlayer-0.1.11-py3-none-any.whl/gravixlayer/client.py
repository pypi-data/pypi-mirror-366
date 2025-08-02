import os
import json
import requests
from typing import Optional, Dict, Any, List, Union
from .resources.chat.completions import ChatCompletions
from .types.chat import ChatCompletion


class GravixLayer:
    """
    Main GravixLayer client - OpenAI compatible interface
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 60.0,
        max_retries: Optional[int] = 3,
        **kwargs
    ):
        self.api_key = api_key or os.environ.get("GRAVIXLAYER_API_KEY")
        self.base_url = base_url or "https://api.gravixlayer.com/v1/inference"
        self.timeout = timeout
        self.max_retries = max_retries
        
        if not self.api_key:
            raise ValueError("API key must be provided either as argument or GRAVIXLAYER_API_KEY environment variable")
        
        # Initialize resources
        self.chat = ChatResource(self)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request to GravixLayer API"""
        
        # Construct the full URL
        if endpoint:
            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        else:
            url = self.base_url
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "gravixlayer-python/0.1.0"
        }
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout,
                    **kwargs
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code in [429, 502, 503, 504] and attempt < self.max_retries:
                    import time
                    time.sleep(2 ** attempt)
                    continue
                else:
                    response.raise_for_status()
                    
            except requests.RequestException as e:
                if attempt == self.max_retries:
                    raise e
                import time
                time.sleep(2 ** attempt)
        
        return response



class ChatResource:
    """Chat resource for completions"""
    
    def __init__(self, client: GravixLayer):
        self.client = client
        self.completions = ChatCompletions(client)


# Alias for OpenAI compatibility
OpenAI = GravixLayer
