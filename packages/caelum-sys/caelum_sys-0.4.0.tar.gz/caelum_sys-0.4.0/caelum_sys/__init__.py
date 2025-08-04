"""CaelumSys - Human-friendly system automation toolkit with AI integration"""

from .ai_agent import (
    AgentConfig,
    CaelumAgent,
    QuickAgent,
    create_anthropic_agent,
    create_ollama_agent,
    create_openai_agent,
)

# AI Integration imports
from .ai_integration import (
    AISession,
    CommandResult,
    CommandStatus,
    SafetyLevel,
    ai_do,
    ai_do_sync,
    create_ai_session,
    get_ai_session,
    get_available_functions,
)
from .auto_import_plugins import load_all_plugins
from .core_actions import do
from .registry import get_registered_command_phrases

# Auto-load all plugins when package is imported (quiet mode)
load_all_plugins(verbose=False)

__version__ = "0.4.0"
__author__ = "Joshua Wells"
__description__ = "AI-enhanced system automation toolkit with HIGH-PERFORMANCE vision - 135+ commands, MSS/OpenCV/Tesseract integration, OpenAI/Anthropic/Ollama support"

# Main API exports
__all__ = [
    # Core functionality
    "do",
    "get_registered_command_phrases",
    # AI Integration
    "CommandResult",
    "SafetyLevel",
    "CommandStatus",
    "AISession",
    "create_ai_session",
    "get_ai_session",
    "ai_do",
    "ai_do_sync",
    "get_available_functions",
    # AI Agents
    "CaelumAgent",
    "AgentConfig",
    "QuickAgent",
    "create_openai_agent",
    "create_anthropic_agent",
    "create_ollama_agent",
]
