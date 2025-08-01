from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from flotorch.sdk.utils.http_utils import async_http_post, http_post

LLM_ENDPOINT = "/api/openai/v1/chat/completions"

class LLMResponse(BaseModel):
    'data class for LLM response'
    metadata: Dict[str, Any] 
    content: str


def invoke(messages: List[Dict[str, str]], model_id: str, api_key: str, base_url: str, tools: Optional[List[Dict]] = None, extra_body: Optional[Dict] = None, **kwargs):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_id,
        "messages": messages,
        "extra_body": extra_body or {}
    }

    if tools:
        payload["tools"] = tools

    payload.update(kwargs)

    url = f"{base_url.rstrip('/')}{LLM_ENDPOINT}"
    result = http_post(
        url=url,
        headers=headers,
        json=payload
    )
    return result


async def async_invoke(messages: List[Dict[str, str]], model_id: str, api_key: str, base_url: str, tools: Optional[List[Dict]] = None, extra_body: Optional[Dict] = None, **kwargs):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_id,
        "messages": messages,
        "extra_body": extra_body or {}
    }
    
    # Add tools if provided
    if tools:
        payload["tools"] = tools
    
    # Add any additional kwargs to the payload
    payload.update(kwargs)
    
    result = await async_http_post(
        url=f"{base_url.rstrip('/')}{LLM_ENDPOINT}",
        headers=headers,
        json=payload
    )
    return result

def extract_metadata(response: Dict):
    metadata = {
        "inputTokens": str(response['usage']['prompt_tokens']),
        "outputTokens": str(response['usage']['completion_tokens']),
        "totalTokens": str(response['usage']['total_tokens']),
    }
    # Store raw response for tool call parsing
    metadata['raw_response'] = response
    return metadata

def parse_llm_response(response: Dict) -> LLMResponse:
    try:
        message = response['choices'][0]['message']
        # Handle both content and tool_calls
        if 'content' in message and message['content'] is not None:
            content = message['content']
        elif 'tool_calls' in message:
            # For tool calls, set content to empty and store tool calls in metadata
            content = ""
        else:
            content = ""  # Default empty content if neither content nor tool_calls present
            
        metadata = extract_metadata(response)
        return LLMResponse(metadata=metadata, content=content)
    except (KeyError, IndexError) as e:
        raise ValueError(f"Failed to parse unexpected API response structure: {response}") from e