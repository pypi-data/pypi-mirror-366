"""
AI Integration layer for CaelumSys - Making system automation AI-agent ready.
"""

import asyncio
import json
import time
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union


class SafetyLevel(Enum):
    """Safety classification for commands."""

    SAFE = "safe"  # Safe for AI agents to use freely
    RESTRICTED = "restricted"  # Requires permission/confirmation
    DANGEROUS = "dangerous"  # Should not be used by AI without explicit approval


class CommandStatus(Enum):
    """Execution status of commands."""

    SUCCESS = "success"
    ERROR = "error"
    PERMISSION_DENIED = "permission_denied"
    NOT_AVAILABLE = "not_available"


@dataclass
class CommandResult:
    """Structured result for AI-friendly command responses."""

    status: CommandStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None
    execution_time_ms: Optional[float] = None
    command_id: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result["status"] = self.status.value
        return result

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @property
    def success(self) -> bool:
        """Check if command executed successfully."""
        return self.status == CommandStatus.SUCCESS

    @property
    def failed(self) -> bool:
        """Check if command failed."""
        return self.status == CommandStatus.ERROR


@dataclass
class FunctionSchema:
    """OpenAI-compatible function schema for AI agents."""

    name: str
    description: str
    parameters: Dict[str, Any]
    safety_level: SafetyLevel = SafetyLevel.SAFE

    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class AISession:
    """Session management for AI agent interactions."""

    def __init__(self, session_id: str, safety_mode: bool = True):
        self.session_id = session_id
        self.safety_mode = safety_mode
        self.command_history: List[CommandResult] = []
        self.permissions: Dict[str, bool] = {}
        self.created_at = time.time()
        self.last_activity = time.time()

    def add_result(self, result: CommandResult):
        """Add command result to session history."""
        self.command_history.append(result)
        self.last_activity = time.time()

    def get_recent_commands(self, limit: int = 10) -> List[CommandResult]:
        """Get recent command results."""
        return self.command_history[-limit:]

    def has_permission(self, command_name: str) -> bool:
        """Check if session has permission for a command."""
        return self.permissions.get(command_name, not self.safety_mode)

    def grant_permission(self, command_name: str):
        """Grant permission for a specific command."""
        self.permissions[command_name] = True

    def revoke_permission(self, command_name: str):
        """Revoke permission for a specific command."""
        self.permissions[command_name] = False


class AIIntegration:
    """Main AI integration interface for CaelumSys."""

    def __init__(self):
        self.sessions: Dict[str, AISession] = {}
        self.function_schemas: Dict[str, FunctionSchema] = {}
        self._middleware: List[Callable] = []

    def create_session(self, session_id: str, safety_mode: bool = True) -> AISession:
        """Create a new AI session."""
        session = AISession(session_id, safety_mode)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[AISession]:
        """Get existing session."""
        return self.sessions.get(session_id)

    def register_function_schema(self, command_name: str, schema: FunctionSchema):
        """Register a function schema for AI agents."""
        self.function_schemas[command_name] = schema

    def get_available_functions(
        self, session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all available functions in OpenAI format."""
        session = self.get_session(session_id) if session_id else None
        functions = []

        for name, schema in self.function_schemas.items():
            # Filter based on safety level and permissions
            if session and session.safety_mode:
                if schema.safety_level == SafetyLevel.DANGEROUS:
                    if not session.has_permission(name):
                        continue
                elif schema.safety_level == SafetyLevel.RESTRICTED:
                    if not session.has_permission(name):
                        continue

            functions.append(schema.to_openai_format())

        return functions

    def add_middleware(self, middleware: Callable):
        """Add middleware for command processing."""
        self._middleware.append(middleware)

    async def execute_command_async(
        self, command: str, session_id: Optional[str] = None, **kwargs
    ) -> CommandResult:
        """Execute command asynchronously with AI enhancements."""
        start_time = time.time()
        session = self.get_session(session_id) if session_id else None

        try:
            # Apply middleware
            for middleware in self._middleware:
                if asyncio.iscoroutinefunction(middleware):
                    command, kwargs = await middleware(command, session, **kwargs)
                else:
                    command, kwargs = middleware(command, session, **kwargs)

            # Import the main do function
            from .core_actions import do

            # Execute the command
            if asyncio.iscoroutinefunction(do):
                result_message = await do(command, **kwargs)
            else:
                # Run in executor to avoid blocking
                loop = asyncio.get_event_loop()
                result_message = await loop.run_in_executor(
                    None, lambda: do(command, **kwargs)
                )

            # Create structured result
            result = CommandResult(
                status=CommandStatus.SUCCESS,
                message=result_message,
                execution_time_ms=(time.time() - start_time) * 1000,
                command_id=f"{session_id}_{int(start_time)}" if session_id else None,
            )

            # Add to session history
            if session:
                session.add_result(result)

            return result

        except PermissionError as e:
            result = CommandResult(
                status=CommandStatus.PERMISSION_DENIED,
                message=f"Permission denied: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
            if session:
                session.add_result(result)
            return result

        except Exception as e:
            result = CommandResult(
                status=CommandStatus.ERROR,
                message=f"Command failed: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
            if session:
                session.add_result(result)
            return result

    def execute_command_sync(
        self, command: str, session_id: Optional[str] = None, **kwargs
    ) -> CommandResult:
        """Execute command synchronously with AI enhancements."""
        start_time = time.time()
        session = self.get_session(session_id) if session_id else None

        try:
            # Apply middleware (sync only for now)
            for middleware in self._middleware:
                if not asyncio.iscoroutinefunction(middleware):
                    command, kwargs = middleware(command, session, **kwargs)

            # Import the main do function
            from .core_actions import do

            # Execute the command synchronously
            result_message = do(command, **kwargs)

            # Create structured result
            result = CommandResult(
                status=CommandStatus.SUCCESS,
                message=result_message,
                execution_time_ms=(time.time() - start_time) * 1000,
                command_id=f"{session_id}_{int(start_time)}" if session_id else None,
            )

            # Add to session history
            if session:
                session.add_result(result)

            return result

        except PermissionError as e:
            result = CommandResult(
                status=CommandStatus.PERMISSION_DENIED,
                message=f"Permission denied: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
            if session:
                session.add_result(result)
            return result

        except Exception as e:
            result = CommandResult(
                status=CommandStatus.ERROR,
                message=f"Command failed: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
            if session:
                session.add_result(result)
            return result


# Global AI integration instance
ai_integration = AIIntegration()


# Convenience functions for easy integration
def create_ai_session(session_id: str, safety_mode: bool = True) -> AISession:
    """Create a new AI session."""
    return ai_integration.create_session(session_id, safety_mode)


def get_ai_session(session_id: str) -> Optional[AISession]:
    """Get existing AI session."""
    return ai_integration.get_session(session_id)


async def ai_do(
    command: str, session_id: Optional[str] = None, **kwargs
) -> CommandResult:
    """AI-enhanced async command execution."""
    return await ai_integration.execute_command_async(command, session_id, **kwargs)


def ai_do_sync(
    command: str, session_id: Optional[str] = None, **kwargs
) -> CommandResult:
    """AI-enhanced sync command execution."""
    return ai_integration.execute_command_sync(command, session_id, **kwargs)


def get_available_functions(session_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get available functions for AI agents."""
    return ai_integration.get_available_functions(session_id)
