"""LLM client for LitAI."""

import os
from typing import Any
from dataclasses import dataclass
import tiktoken
import json

import structlog
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from anthropic import AsyncAnthropic
from anthropic.types import Message as AnthropicMessage

logger = structlog.get_logger()


@dataclass
class TokenUsage:
    """Token usage and cost information."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""
    
    id: str
    name: str
    arguments: dict[str, Any]


class LLMClient:
    """Unified LLM client with auto-detection for OpenAI and Anthropic."""

    def __init__(self):
        """Initialize the LLM client with auto-detection."""
        self.provider: str | None = None
        self.client: AsyncOpenAI | AsyncAnthropic | None = None
        self.model: str | None = None

        # Auto-detect provider based on environment variables
        if os.getenv("OPENAI_API_KEY"):
            self.provider = "openai"
            self.client = AsyncOpenAI()
            self.model = "gpt-4.1-nano-2025-04-14"
            logger.info("llm_provider_detected", provider="openai", model=self.model)
        elif os.getenv("ANTHROPIC_API_KEY"):
            self.provider = "anthropic"
            self.client = AsyncAnthropic()
            self.model = "claude-3-sonnet-20240229"
            logger.info("llm_provider_detected", provider="anthropic", model=self.model)
        else:
            raise ValueError(
                "No API key found. Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY "
                "environment variable."
            )
    
    async def close(self) -> None:
        """Close the client connections properly."""
        if self.client:
            try:
                await self.client.close()
            except Exception:
                # Ignore errors during cleanup
                pass

    async def test_connection(self) -> tuple[str, TokenUsage]:
        """Test the LLM connection with a simple prompt.

        Returns:
            tuple of (response text, token usage info)
        """
        test_prompt = "Say 'Hello from LitAI' and nothing else."
        response = await self.complete(test_prompt, max_tokens=10)
        return response["content"], response["usage"]

    async def complete(
        self,
        prompt: str | list[dict[str, Any]],
        max_tokens: int = 1000,
        temperature: float = 0.0,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Complete a prompt using the configured LLM.

        Args:
            prompt: The prompt to complete (string or list of messages)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            tools: Optional list of tools for function calling

        Returns:
            dict containing:
                - content: The generated text
                - usage: TokenUsage object with token counts and cost
                - tool_calls: Optional list of ToolCall objects
        """
        if self.provider == "openai":
            return await self._complete_openai(prompt, max_tokens, temperature, tools)
        elif self.provider == "anthropic":
            return await self._complete_anthropic(prompt, max_tokens, temperature, tools)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    async def _complete_openai(
        self,
        prompt: str | list[dict[str, Any]],
        max_tokens: int,
        temperature: float,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Complete using OpenAI API."""
        if not self.client or not isinstance(self.client, AsyncOpenAI):
            raise ValueError("OpenAI client not initialized")
        
        # Handle both string prompts and message lists
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt
            
        response: ChatCompletion = await self.client.chat.completions.create(
            model=self.model or "gpt-4.1-nano-2025-04-14",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=tools if tools else None,
        )

        message = response.choices[0].message
        usage = response.usage

        if not usage:
            raise ValueError("No usage information returned from OpenAI API")

        # Calculate cost (approximate pricing as of 2024)
        prompt_cost = usage.prompt_tokens * 0.01 / 1000  # $0.01 per 1K tokens
        completion_cost = usage.completion_tokens * 0.03 / 1000  # $0.03 per 1K tokens
        total_cost = prompt_cost + completion_cost

        result = {
            "content": message.content or "",
            "usage": TokenUsage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                estimated_cost=total_cost,
            ),
        }
        
        # Add tool calls if present
        if message.tool_calls:
            tool_calls = []
            for tc in message.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                ))
            result["tool_calls"] = tool_calls
            
        return result

    async def _complete_anthropic(
        self,
        prompt: str | list[dict[str, Any]],
        max_tokens: int,
        temperature: float,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Complete using Anthropic API."""
        if not self.client or not isinstance(self.client, AsyncAnthropic):
            raise ValueError("Anthropic client not initialized")
        
        # Handle both string prompts and message lists
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
            prompt_text = prompt
        else:
            messages = []
            system_msg = None
            prompt_text = ""
            
            # Extract system message and format other messages
            for msg in prompt:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                    prompt_text += msg["content"] + "\n"
                else:
                    messages.append(msg)
                    prompt_text += msg.get("content", "") + "\n"
        
        # Count tokens using tiktoken (approximation for Claude)
        prompt_tokens = self._count_tokens(prompt_text)

        response: AnthropicMessage = await self.client.messages.create(
            model=self.model or "claude-3-sonnet-20240229",
            messages=messages,
            system=system_msg if 'system_msg' in locals() else None,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=tools if tools else None,
        )

        # Extract content and tool calls from response
        content = ""
        tool_calls = []
        
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text
            elif hasattr(block, "type") and block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input
                ))
        
        # Calculate tokens
        completion_text = content + json.dumps([{"name": tc.name, "args": tc.arguments} for tc in tool_calls])
        completion_tokens = self._count_tokens(completion_text)
        total_tokens = prompt_tokens + completion_tokens

        # Calculate cost (approximate pricing for Claude 3 Sonnet)
        prompt_cost = prompt_tokens * 0.003 / 1000  # $0.003 per 1K tokens
        completion_cost = completion_tokens * 0.015 / 1000  # $0.015 per 1K tokens
        total_cost = prompt_cost + completion_cost

        result = {
            "content": content,
            "usage": TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost=total_cost,
            ),
        }
        
        # Add tool calls if present
        if tool_calls:
            result["tool_calls"] = tool_calls
            
        return result

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken.

        This is an approximation for non-OpenAI models.
        """
        try:
            encoding = tiktoken.encoding_for_model("gpt-4")
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        return len(encoding.encode(text))

    def estimate_cost(self, prompt: str, response: str) -> TokenUsage:
        """Estimate the cost of a prompt/response pair.

        Args:
            prompt: The input prompt
            response: The generated response

        Returns:
            TokenUsage object with cost estimate
        """
        prompt_tokens = self._count_tokens(prompt)
        completion_tokens = self._count_tokens(response)
        total_tokens = prompt_tokens + completion_tokens

        if self.provider == "openai":
            prompt_cost = prompt_tokens * 0.01 / 1000
            completion_cost = completion_tokens * 0.03 / 1000
        elif self.provider == "anthropic":
            prompt_cost = prompt_tokens * 0.003 / 1000
            completion_cost = completion_tokens * 0.015 / 1000
        else:
            prompt_cost = completion_cost = 0

        total_cost = prompt_cost + completion_cost

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=total_cost,
        )
