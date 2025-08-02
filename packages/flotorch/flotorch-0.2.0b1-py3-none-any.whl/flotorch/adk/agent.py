import os
import sys
# Import warning suppression utilities
from flotorch.adk.utils.warning_utils import SuppressOutput

from flotorch.adk.llm import FlotorchADKLLM
from google.adk.agents import LlmAgent
from google.adk.tools import preload_memory, load_memory
from typing import Any, Dict
from dotenv import load_dotenv
from pydantic import create_model, Field
import httpx
import inspect
import time
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from flotorch.sdk.utils.logging_utils import log_object_creation


load_dotenv()

def schema_to_pydantic_model(name: str, schema: dict):
    """
    Dynamically create a Pydantic model from a JSON schema dict.
    If only one property, use its name (capitalized) plus 'Input' or 'Output' as the model name.
    Otherwise, use the provided name.
    """
    properties = schema.get("properties", {})
    if len(properties) == 1:
        prop_name = next(iter(properties))
        if name.lower().startswith("input"):
            model_name = f"{prop_name.capitalize()}Input"
        elif name.lower().startswith("output"):
            model_name = f"{prop_name.capitalize()}Output"
        else:
            model_name = f"{prop_name.capitalize()}Schema"
    else:
        model_name = name
    fields = {}
    for prop, prop_schema in properties.items():
        field_type = str  # Default to string
        if prop_schema.get("type") == "integer":
            field_type = int
        elif prop_schema.get("type") == "number":
            field_type = float
        elif prop_schema.get("type") == "boolean":
            field_type = bool
        description = prop_schema.get("description", "")
        fields[prop] = (field_type, Field(description=description))
    return create_model(model_name, **fields)


class FlotorchADKAgent:
    """
    Manager/config class for Flotorch agent. Builds LlmAgent from config on demand.
    Supports on-demand config reload based on interval in config['sync'].
    
    Args:
        agent_name: Name of the agent
        enable_memory: Enable memory functionality
        config: Optional custom configuration dict
        custom_tools: List of custom user-defined tools to add to the agent
    
    Usage: 
        flotroch = FlotorchADKClient("agent-one", enable_memory=True, custom_tools=[my_tool])
        agent = flotroch.get_agent()
    """
    def __init__(self, agent_name: str, enable_memory: bool = False, config=None, custom_tools: list = None):
        self.agent_name = agent_name
        self.enable_memory = enable_memory
        self.custom_tools = custom_tools or []
        if config:
            self.config = config
        else:
            self.config = self._fetch_agent_config(agent_name)
        self._agent = self._build_agent_from_config(self.config)
        self._last_reload = time.time()
        self._reload_interval = self.config.get('sync', {}).get('interval', 10000) / 1000  # ms to s
        
        # Log object creation
        log_object_creation("FlotorchADKAgent", agent_name=self.agent_name, memory_enabled=self.enable_memory)

    def _fetch_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Fetch agent config from API. Stubbed for now; replace with real API call.
        """
        # TODO: Replace with real API call
        return {
            "name": agent_name,
            "description": "Example Flotorch agent with memory support.",
            "systemPrompt": """You are a helpful assistant with perfect memory. 
                                Use the context to personalize responses and naturally reference past conversations when relevant.
                                
                                Available tools:
                                - load_memory: Use this to search for specific information from past conversations
                                - get_capital_city: Use for country capital questions
                                - get_weather: Use for weather information
                                - get_current_time: Use for time information

                                
                                Tool usage guidelines:
                                - what ever the output or response that you will get from the tool that should be display as it is to the user no changes to be made.
                                - Try ONE tool at a time for each query, avoid calling multiple tools simultaneously
                                - Use load_memory when you need to recall specific past information
                                - Always be graceful when tools are unavailable
                                - Don't make multiple tool calls in a single response
                                if the tool says the capital of india as "something" it should be returned to the user as it is no corrections should be made.
                                - the response should be as it is that is coming from the tools the response should not be modified it should be display as it is to the user.
                                
                                Your memory automatically loads relevant context, and you can search for more specific information using load_memory.""",
            "llm": {
                "callableName": "openai/gpt-4o-mini"
            },
            "memory": {
                "enabled": self.enable_memory
            },
            "tools":  [
                {
                    "name": "get_capital_city",
                    "description": "Get the capital city of a given country. Use this for questions about capitals.",
                    "type": "MCP",
                    "config": {
                        "transport": "STREAM",
                        "url": "http://localhost:9000/mcp/",
                        "headers": {"Content-Type": "application/json"},
                        "timeout": 2000,
                        "sse_read_timeout": 2000,
                        "terminate_on_close": False,
                        "max_retries": 0
                    }
                },
                {
                    "name": "get_weather",
                    "description": "Get weather information for a specific city. Use this for weather questions.",
                    "type": "MCP",
                    "config": {
                        "transport": "STREAM",
                        "url": "http://localhost:9000/mcp/",
                        "headers": {"Content-Type": "application/json"},
                        "timeout": 2000,
                        "sse_read_timeout": 2000,
                        "terminate_on_close": False,
                        "max_retries": 0
                    }
                },
                {
                    "name": "get_current_time",
                    "description": "Get the current time for a specific city. Use this for time questions.",
                    "type": "MCP",
                    "config": {
                        "transport": "STREAM",
                        "url": "http://localhost:9000/mcp/",
                        "headers": {"Content-Type": "application/json"},
                        "timeout": 2000,
                        "sse_read_timeout": 2000,
                        "terminate_on_close": False,
                        "max_retries": 0
                    }
                }
            ],
            # "inputSchema": {
            #     "type": "object",
            #     "properties": {
            #         "country": {"type": "string", "description": "The country to get the capital city of"}
            #     }
            # },
            # "outputSchema": {
            #     "type": "object",
            #     "properties": {
            #         "capitalCity": {"type": "string", "description": "The capital city of the given country"}
            #     }
            # },
            # "sync": {
            #     "enable": True,
            #     "interval": 10000
            # }
        }

    def _build_tools(self, config: Dict[str, Any]):
        tools = []
        
        # Add memory tools if memory is enabled
        if self.enable_memory:
            tools.append(preload_memory)  # Automatic memory loading (preprocessor)
            # tools.append(load_memory)     # Manual memory search (function tool)
        
        # Add MCP tools with improved error handling
        for tool_cfg in config.get("tools", []):
            if tool_cfg.get("type") == "MCP":
                mcp_conf = tool_cfg["config"]
                try:
                    # Build connection params with better defaults
                    auth_token = os.environ.get("FLOTORCH_AUTH_TOKEN")
                    headers = dict(mcp_conf.get("headers", {}))
                    if auth_token:
                        headers["Authorization"] = f"Bearer {auth_token}"
                    
                    # Use custom silence context manager to suppress ALL output
                    with SuppressOutput():
                        conn_params = StreamableHTTPConnectionParams(
                            url=mcp_conf["url"],
                            headers=headers,
                            timeout=mcp_conf.get("timeout", 2_000) / 1000.0,  # 2s timeout (even shorter)
                            sse_read_timeout=mcp_conf.get("sse_read_timeout", 2_000) / 1000.0,  # 2s timeout
                            terminate_on_close=False,  # Always False to prevent async issues
                            auth_config=None,  # Explicitly set to None to avoid warnings
                            max_retries=0  # No retries to avoid hanging
                        )
                        
                        # Create toolset with error handling
                        toolset = MCPToolset(
                            connection_params=conn_params
                        )
                        
                        # Only add working toolsets
                        tools.append(toolset)
                        
                except Exception as e:
                    # Silently skip failed tools instead of printing warnings
                    continue
        
        # Add custom user-defined tools
        if self.custom_tools:
            tools.extend(self.custom_tools)
        
        return tools

    def _build_agent_from_config(self, config):
        llm = FlotorchADKLLM(
            model_id=config["llm"]["callableName"],
            api_key=os.environ.get("FLOTORCH_API_KEY"),
            base_url=os.environ.get("FLOTORCH_BASE_URL")
        )
        tools = self._build_tools(config)
        input_schema = None
        output_schema = None
        if "inputSchema" in config:
            input_schema = schema_to_pydantic_model("InputSchema", config["inputSchema"])
        if "outputSchema" in config:
            output_schema = schema_to_pydantic_model("OutputSchema", config["outputSchema"])
        return LlmAgent(
            name=config["name"],
            model=llm,
            instruction=config["systemPrompt"],
            description=config["description"],
            tools=tools,
            input_schema=input_schema,
            output_schema=output_schema
        )

    def get_agent(self):
        now = time.time()
        if now - self._last_reload > self._reload_interval:
            new_config = self._fetch_agent_config(self.agent_name)
            if new_config != self.config:
                self.config = new_config
                self._agent = self._build_agent_from_config(new_config)
                self._reload_interval = self.config.get('sync', {}).get('interval', 10000) / 1000
            self._last_reload = now
        return self._agent

    def create_agent(self):
        config = self._fetch_agent_config(self.agent_name)
        self.config = config
        self._agent = self._build_agent_from_config(config)
        self._reload_interval = self.config.get('sync', {}).get('interval', 10000) / 1000
        self._last_reload = time.time()
        return self._agent

    def has_memory(self) -> bool:
        """Check if memory is enabled."""
        return self.enable_memory

# Usage:
# Warning suppressions are automatically applied when importing this module.
# To disable: set environment variable FLOTORCH_NO_AUTO_SUPPRESS=1
# flotroch = FlotorchADKClient("agent-one", enable_memory=True)
# agent = flotroch.get_agent()
# memory_service = FlotorchMemoryService(...)  # Create your memory service
# runner = Runner(agent=agent, memory_service=memory_service, ...)  # Pass memory service to runner
# Now use agent as a normal LlmAgent with memory support! 