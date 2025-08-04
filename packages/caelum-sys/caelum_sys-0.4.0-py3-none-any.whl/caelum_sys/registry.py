"""Command Registry System for CaelumSys with AI Integration Support"""

import inspect
from typing import Any, Callable, Dict, List, Optional

# Global registry to store all registered commands
registry = {}


def register_command(trigger, safe=True, description=None, parameters=None):
    """Decorator to register a command with the CaelumSys system.

    Args:
        trigger: The command phrase that triggers this function
        safe: Whether this command is safe to execute (default: True)
        description: Description for AI function calling (auto-generated if None)
        parameters: OpenAI-style parameters schema for function calling
    """

    def wrapper(func):
        # Auto-generate description from docstring if not provided
        if description is None:
            func_description = func.__doc__ or f"Execute command: {trigger}"
            func_description = func_description.strip().split("\n")[
                0
            ]  # First line only
        else:
            func_description = description

        # Auto-generate parameters from function signature if not provided
        if parameters is None:
            func_parameters = _generate_parameters_from_signature(func)
        else:
            func_parameters = parameters

        # Determine safety level
        safety_level = "safe" if safe else "restricted"

        # Store in registry
        registry[trigger.lower()] = {
            "func": func,
            "safe": safe,
            "description": func_description,
            "parameters": func_parameters,
            "safety_level": safety_level,
        }

        # Register with AI integration (avoid circular import)
        _register_with_ai_integration(
            trigger.lower(), func_description, func_parameters, safety_level
        )

        return func

    return wrapper


def _register_with_ai_integration(
    command_name: str, description: str, parameters: Dict[str, Any], safety_level: str
):
    """Register command with AI integration system."""
    try:
        from .ai_integration import FunctionSchema, SafetyLevel, ai_integration

        # Convert safety level
        if safety_level == "safe":
            level = SafetyLevel.SAFE
        elif safety_level == "restricted":
            level = SafetyLevel.RESTRICTED
        else:
            level = SafetyLevel.DANGEROUS

        schema = FunctionSchema(
            name=command_name.replace(" ", "_"),
            description=description,
            parameters=parameters,
            safety_level=level,
        )
        ai_integration.register_function_schema(command_name, schema)
    except ImportError:
        # AI integration not available, skip
        pass


def _generate_parameters_from_signature(func: Callable) -> Dict[str, Any]:
    """Auto-generate OpenAI-style parameters from function signature."""
    sig = inspect.signature(func)
    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        param_type = "string"  # Default type
        param_desc = f"Parameter {param_name}"

        # Try to infer type from annotation
        if param.annotation != inspect.Parameter.empty:
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"
            elif param.annotation == list:
                param_type = "array"
            elif param.annotation == dict:
                param_type = "object"

        properties[param_name] = {"type": param_type, "description": param_desc}

        # Add to required if no default value
        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    return {"type": "object", "properties": properties, "required": required}


def get_registered_command(command):
    """Retrieve a registered command function by its trigger phrase."""
    command_data = registry.get(command.lower(), {})
    return command_data.get("func", None)


def get_registered_command_phrases():
    """Get a list of all registered command phrases."""
    return list(registry.keys())


def get_safe_registry():
    """Get only the commands marked as 'safe' for execution."""
    return {
        command_phrase: command_data["func"]
        for command_phrase, command_data in registry.items()
        if command_data.get("safe", True)
    }


def get_ai_functions() -> List[Dict[str, Any]]:
    """Get all commands formatted as OpenAI-style functions."""
    functions = []
    for command_phrase, command_data in registry.items():
        functions.append(
            {
                "name": command_phrase.replace(" ", "_"),
                "description": command_data.get(
                    "description", f"Execute command: {command_phrase}"
                ),
                "parameters": command_data.get(
                    "parameters",
                    {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": f"The command to execute: {command_phrase}",
                            }
                        },
                        "required": ["command"],
                    },
                ),
            }
        )
    return functions


def get_command_metadata(command: str) -> Optional[Dict[str, Any]]:
    """Get metadata for a specific command."""
    return registry.get(command.lower())


def clear_registry():
    """Clear all registered commands from the registry (mainly for testing)."""
    global registry
    registry.clear()


def get_registry_stats():
    """Get statistics about the current registry state."""
    total_commands = len(registry)
    safe_commands = len(get_safe_registry())

    return {
        "total": total_commands,
        "safe": safe_commands,
        "unsafe": total_commands - safe_commands,
    }
