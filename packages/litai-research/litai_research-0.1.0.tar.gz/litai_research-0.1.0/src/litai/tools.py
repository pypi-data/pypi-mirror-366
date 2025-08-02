"""Tool definitions for natural language interface."""

from typing import Any, TypedDict


class ToolParameter(TypedDict):
    """Parameter definition for a tool."""
    
    type: str
    description: str
    required: bool
    enum: list[str] | None


class ToolDefinition(TypedDict):
    """Definition of a tool that can be called by the LLM."""
    
    name: str
    description: str
    parameters: dict[str, ToolParameter]


LITAI_TOOLS: list[ToolDefinition] = [
    {
        "name": "find_papers",
        "description": "Search for academic papers on a specific topic using Semantic Scholar",
        "parameters": {
            "query": {
                "type": "string",
                "description": "The search query or topic to find papers about",
                "required": True,
                "enum": None
            },
            "limit": {
                "type": "integer", 
                "description": "Maximum number of papers to return (default: 10)",
                "required": False,
                "enum": None
            }
        }
    },
    {
        "name": "add_paper",
        "description": "Add a paper from search results to the user's library",
        "parameters": {
            "paper_number": {
                "type": "integer",
                "description": "The number of the paper from search results to add (1-based index)",
                "required": True,
                "enum": None
            }
        }
    },
    {
        "name": "list_papers",
        "description": "List all papers currently in the user's library",
        "parameters": {}
    },
    {
        "name": "remove_paper",
        "description": "Remove a paper from the user's library",
        "parameters": {
            "paper_number": {
                "type": "integer",
                "description": "The number of the paper in the library to remove (1-based index)",
                "required": True,
                "enum": None
            }
        }
    },
    {
        "name": "read_paper",
        "description": "Extract and display key points from a paper in the library",
        "parameters": {
            "paper_number": {
                "type": "integer",
                "description": "The number of the paper in the library to read (1-based index)",
                "required": True,
                "enum": None
            }
        }
    },
    {
        "name": "synthesize_papers",
        "description": "Generate a synthesis across papers to answer a research question",
        "parameters": {
            "question": {
                "type": "string",
                "description": "The research question to answer by synthesizing information from papers",
                "required": True,
                "enum": None
            }
        }
    },
    {
        "name": "show_search_results",
        "description": "Display the cached search results from the last search",
        "parameters": {}
    },
    {
        "name": "fetch_hf_papers",
        "description": "Browse recent papers from Hugging Face (view only)",
        "parameters": {}
    },
    {
        "name": "clear_screen",
        "description": "Clear the console screen",
        "parameters": {}
    }
]


def get_openai_tools() -> list[dict[str, Any]]:
    """Convert tool definitions to OpenAI function calling format."""
    openai_tools = []
    
    for tool in LITAI_TOOLS:
        properties = {}
        required = []
        
        for param_name, param_def in tool["parameters"].items():
            properties[param_name] = {
                "type": param_def["type"],
                "description": param_def["description"]
            }
            if param_def.get("enum"):
                properties[param_name]["enum"] = param_def["enum"]
            if param_def.get("required", False):
                required.append(param_name)
        
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
        openai_tools.append(openai_tool)
    
    return openai_tools


def get_anthropic_tools() -> list[dict[str, Any]]:
    """Convert tool definitions to Anthropic tool use format."""
    anthropic_tools = []
    
    for tool in LITAI_TOOLS:
        properties = {}
        required = []
        
        for param_name, param_def in tool["parameters"].items():
            properties[param_name] = {
                "type": param_def["type"],
                "description": param_def["description"]
            }
            if param_def.get("enum"):
                properties[param_name]["enum"] = param_def["enum"]
            if param_def.get("required", False):
                required.append(param_name)
        
        anthropic_tool = {
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
        anthropic_tools.append(anthropic_tool)
    
    return anthropic_tools