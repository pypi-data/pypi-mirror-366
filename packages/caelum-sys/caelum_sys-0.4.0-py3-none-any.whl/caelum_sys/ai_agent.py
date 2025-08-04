"""
AI Agent SDK - Easy-to-use interface for building AI assistants with CaelumSys.
"""

import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from .ai_integration import (
    AIIntegration,
    AISession,
    CommandResult,
    SafetyLevel,
    ai_do,
    ai_do_sync,
    create_ai_session,
    get_available_functions,
)


class BaseAIProvider(ABC):
    """Abstract base class for AI providers (OpenAI, Anthropic, etc.)."""

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate AI response with optional function calling."""
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI provider for AI agents."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        try:
            import openai  # type: ignore

            self.client = openai.AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate response using OpenAI API."""
        params = {"model": self.model, "messages": messages, **kwargs}

        if functions:
            params["functions"] = functions
            params["function_call"] = "auto"

        response = await self.client.chat.completions.create(**params)
        response_dict: Dict[str, Any] = response.model_dump()
        return response_dict


class OllamaProvider(BaseAIProvider):
    """Ollama provider for local AI models."""

    def __init__(
        self, model: str = "llama3.1", base_url: str = "http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        try:
            import requests

            self.session = requests.Session()
            # Test connection
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code != 200:
                print(f"⚠️ Warning: Cannot connect to Ollama at {self.base_url}")
                print("Make sure Ollama is running: ollama serve")
        except ImportError:
            raise ImportError(
                "Requests package required for Ollama. Already included in caelum-sys."
            )
        except Exception as e:
            print(f"⚠️ Warning: Ollama connection issue: {e}")

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate response using Ollama API."""
        import json

        # Convert messages to Ollama format
        prompt = self._format_messages_for_ollama(messages, functions)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 1000),
            },
        }

        try:
            import asyncio

            import requests

            # Run synchronous request in executor for async compatibility
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/api/generate", json=payload, timeout=60
                ),
            )

            if response.status_code == 200:
                result = response.json()

                # Check if the response contains function calls
                response_text = result.get("response", "")
                function_call = self._extract_function_call(response_text)

                if function_call:
                    return {
                        "choices": [
                            {
                                "message": {
                                    "role": "assistant",
                                    "content": "",
                                    "function_call": function_call,
                                }
                            }
                        ]
                    }
                else:
                    return {
                        "choices": [
                            {"message": {"role": "assistant", "content": response_text}}
                        ]
                    }
            else:
                error_msg = (
                    f"Ollama API error: {response.status_code} - {response.text}"
                )
                return {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": f"Sorry, I encountered an error: {error_msg}",
                            }
                        }
                    ]
                }

        except Exception as e:
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": f"Sorry, I couldn't process your request: {str(e)}",
                        }
                    }
                ]
            }

    def _format_messages_for_ollama(
        self, messages: List[Dict[str, str]], functions: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Convert OpenAI-style messages to Ollama prompt format."""
        prompt_parts = []

        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            elif role == "function":
                name = message.get("name", "unknown")
                prompt_parts.append(f"Function {name} result: {content}")

        # Add function information if available
        if functions:
            prompt_parts.insert(-1, "\nAvailable functions:")
            for func in functions:
                name = func.get("name", "")
                desc = func.get("description", "")
                prompt_parts.insert(-1, f"- {name}: {desc}")

            prompt_parts.insert(
                -1,
                '\nTo use a function, respond with: FUNCTION_CALL: {"name": "function_name", "arguments": {"param": "value"}}',
            )

        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)

    def _extract_function_call(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract function call from Ollama response."""
        import json

        if "FUNCTION_CALL:" in response_text:
            try:
                # Extract JSON part after FUNCTION_CALL:
                json_start = response_text.find("FUNCTION_CALL:") + len(
                    "FUNCTION_CALL:"
                )
                json_part = response_text[json_start:].strip()

                # Try to find JSON object
                if json_part.startswith("{"):
                    # Find matching closing brace
                    brace_count = 0
                    end_pos = 0
                    for i, char in enumerate(json_part):
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                end_pos = i + 1
                                break

                    if end_pos > 0:
                        json_str = json_part[:end_pos]
                        function_data = json.loads(json_str)

                        return {
                            "name": function_data.get("name", ""),
                            "arguments": json.dumps(function_data.get("arguments", {})),
                        }
            except Exception:
                # If parsing fails, return None
                pass

        return None


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude provider for AI agents."""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model
        try:
            import anthropic  # type: ignore

            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Run: pip install anthropic"
            )

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate response using Anthropic API."""
        # Convert OpenAI format to Anthropic format
        system_message = ""
        anthropic_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message += msg["content"] + "\n"
            else:
                anthropic_messages.append(msg)

        if functions:
            # Add function descriptions to system message
            system_message += "\nAvailable functions:\n"
            for func in functions:
                system_message += f"- {func['name']}: {func['description']}\n"

        params = {
            "model": self.model,
            "messages": anthropic_messages,
            "system": system_message,
            "max_tokens": kwargs.get("max_tokens", 1000),
            **kwargs,
        }

        response = await self.client.messages.create(**params)
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": response.content[0].text if response.content else "",
                    }
                }
            ]
        }


@dataclass
class AgentConfig:
    """Configuration for AI agents."""

    name: str
    description: str
    system_prompt: str
    safety_mode: bool = True
    max_tokens: int = 1000
    temperature: float = 0.7
    allowed_commands: Optional[List[str]] = None
    denied_commands: Optional[List[str]] = None
    auto_execute: bool = False  # Whether to auto-execute safe commands
    require_confirmation: bool = True  # For restricted/dangerous commands


class CaelumAgent:
    """Main AI Agent class that combines CaelumSys with AI providers."""

    def __init__(
        self,
        config: AgentConfig,
        ai_provider: BaseAIProvider,
        session_id: Optional[str] = None,
    ):
        self.config = config
        self.ai_provider = ai_provider
        self.session_id = session_id or str(uuid.uuid4())
        self.session = create_ai_session(self.session_id, config.safety_mode)
        self.conversation_history: List[Dict[str, Any]] = []

        # Initialize with system prompt
        if config.system_prompt:
            self.conversation_history.append(
                {"role": "system", "content": self._build_system_prompt()}
            )

    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt."""
        base_prompt = self.config.system_prompt

        system_info = f"""

You are {self.config.name}, {self.config.description}

You have access to CaelumSys, a powerful system automation toolkit with 117+ commands.
You can help users with:
- File operations (create, copy, move, delete files)
- System information (time, date, process monitoring)
- Network operations (ping, DNS lookup, web requests)
- Media controls (volume, music playback)
- Screenshot capture
- Process management
- Git operations
- And much more!

IMPORTANT GUIDELINES:
1. Always use available functions when users request system operations
2. Confirm dangerous operations before executing
3. Provide clear, helpful responses about what you're doing
4. If a command fails, explain why and suggest alternatives

Available Commands: You can see all available commands by asking for help.
"""

        return base_prompt + system_info

    async def chat(self, user_message: str) -> str:
        """Have a conversation with the agent."""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})

        # Get available functions for this session
        functions = get_available_functions(self.session_id)

        # Generate AI response
        response = await self.ai_provider.generate_response(
            messages=self.conversation_history,
            functions=functions if functions else None,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )

        # Process the response
        choice = response["choices"][0]
        message = choice["message"]

        # Handle function calls
        if "function_call" in message and message["function_call"]:
            return await self._handle_function_call(message["function_call"])
        else:
            # Regular text response
            assistant_message = message["content"]
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message}
            )
            return str(assistant_message)

    async def _handle_function_call(self, function_call: Dict[str, Any]) -> str:
        """Handle AI function calls."""
        function_name = function_call["name"]

        try:
            # Parse function arguments
            if isinstance(function_call["arguments"], str):
                arguments = json.loads(function_call["arguments"])
            else:
                arguments = function_call["arguments"]

            # Extract command from arguments
            command = arguments.get("command", function_name)

            # Execute the command
            result = await ai_do(command, self.session_id, **arguments)

            # Add function call and result to conversation history
            self.conversation_history.append(
                {"role": "assistant", "content": "", "function_call": function_call}
            )

            self.conversation_history.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(result.to_dict()),
                }
            )

            # Generate follow-up response
            follow_up = await self.ai_provider.generate_response(
                messages=self.conversation_history,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )

            assistant_response = follow_up["choices"][0]["message"]["content"]
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_response}
            )

            return str(assistant_response)

        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            self.conversation_history.append(
                {"role": "assistant", "content": error_msg}
            )
            return error_msg

    def grant_permission(self, command_name: str):
        """Grant permission for a specific command."""
        self.session.grant_permission(command_name)

    def revoke_permission(self, command_name: str):
        """Revoke permission for a specific command."""
        self.session.revoke_permission(command_name)

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history.copy()

    def get_command_history(self) -> List[CommandResult]:
        """Get the command execution history."""
        return self.session.get_recent_commands()

    def clear_history(self):
        """Clear conversation history (keeps system prompt)."""
        system_messages = [
            msg for msg in self.conversation_history if msg["role"] == "system"
        ]
        self.conversation_history = system_messages


class QuickAgent:
    """Simplified agent for quick setup."""

    @staticmethod
    def create_openai_agent(
        api_key: str,
        name: str = "CaelumSys Assistant",
        description: str = "A helpful AI assistant with system automation capabilities",
        system_prompt: str = "You are a helpful AI assistant with system automation capabilities.",
        model: str = "gpt-4",
    ) -> CaelumAgent:
        """Create an OpenAI-powered agent with minimal setup."""
        config = AgentConfig(
            name=name, description=description, system_prompt=system_prompt
        )

        provider = OpenAIProvider(api_key, model)
        return CaelumAgent(config, provider)

    @staticmethod
    def create_anthropic_agent(
        api_key: str,
        name: str = "CaelumSys Assistant",
        description: str = "A helpful AI assistant with system automation capabilities",
        system_prompt: str = "You are a helpful AI assistant with system automation capabilities.",
        model: str = "claude-3-sonnet-20240229",
    ) -> CaelumAgent:
        """Create an Anthropic-powered agent with minimal setup."""
        config = AgentConfig(
            name=name, description=description, system_prompt=system_prompt
        )

        provider = AnthropicProvider(api_key, model)
        return CaelumAgent(config, provider)

    @staticmethod
    def create_ollama_agent(
        model: str = "llama3.1",
        base_url: str = "http://localhost:11434",
        name: str = "CaelumSys Assistant",
        description: str = "A helpful AI assistant with system automation capabilities",
        system_prompt: str = "You are a helpful AI assistant with system automation capabilities.",
    ) -> CaelumAgent:
        """Create an Ollama-powered agent with minimal setup.

        Args:
            model: Ollama model name (e.g., "llama3.1", "codellama", "mistral")
            base_url: Ollama server URL
            name: Agent name
            description: Agent description
            system_prompt: System prompt for the agent

        Returns:
            Configured CaelumAgent instance

        Example:
            >>> agent = QuickAgent.create_ollama_agent("llama3.1")
            >>> response = await agent.chat("What's the current time?")

        Note:
            Make sure Ollama is running: `ollama serve`
            Download models: `ollama pull llama3.1`
        """
        config = AgentConfig(
            name=name, description=description, system_prompt=system_prompt
        )

        provider = OllamaProvider(model, base_url)
        return CaelumAgent(config, provider)


# Convenience functions for quick setup
def create_openai_agent(api_key: str, **kwargs) -> CaelumAgent:
    """Create OpenAI agent with minimal setup."""
    return QuickAgent.create_openai_agent(api_key, **kwargs)


def create_anthropic_agent(api_key: str, **kwargs) -> CaelumAgent:
    """Create Anthropic agent with minimal setup."""
    return QuickAgent.create_anthropic_agent(api_key, **kwargs)


def create_ollama_agent(model: str = "llama3.1", **kwargs) -> CaelumAgent:
    """Create Ollama agent with minimal setup.

    Args:
        model: Ollama model name (e.g., "llama3.1", "codellama", "mistral")
        **kwargs: Additional configuration options

    Returns:
        Configured CaelumAgent instance

    Example:
        >>> agent = create_ollama_agent("llama3.1")
        >>> response = await agent.chat("What's the current time?")

    Note:
        Make sure Ollama is running: `ollama serve`
        Download models: `ollama pull llama3.1`
    """
    return QuickAgent.create_ollama_agent(model, **kwargs)
