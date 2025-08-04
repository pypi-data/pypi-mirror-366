"""
CaelumSys AI Integration Showcase - Complete Example
"""

import asyncio
import json
from caelum_sys import (
    # Core functionality
    do, get_registered_command_phrases,
    
    # AI Integration
    create_ai_session, ai_do_sync, get_available_functions,
    CommandResult, SafetyLevel,
    
    # AI Agents (Note: Requires API keys)
    AgentConfig, QuickAgent
)


def showcase_basic_usage():
    """Showcase traditional CaelumSys usage."""
    print("🚀 CaelumSys Basic Usage")
    print("=" * 30)
    
    # Traditional simple usage
    commands = [
        "get current time",
        "get system info", 
        "calculate 25 * 4 + 10",
        "get python version"
    ]
    
    for cmd in commands:
        result = do(cmd)
        print(f"Command: {cmd}")
        print(f"Result: {result}")
        print()


def showcase_ai_enhanced():
    """Showcase AI-enhanced structured responses."""
    print("🤖 AI-Enhanced Structured Responses")
    print("=" * 40)
    
    # Create AI session
    session = create_ai_session("showcase_session", safety_mode=True)
    print(f"Created session: {session.session_id}")
    print()
    
    # Execute commands with structured responses
    commands = [
        "get current time",
        "list files in .", 
        "get memory usage",
        "ping google.com"
    ]
    
    for cmd in commands:
        result = ai_do_sync(cmd, session.session_id)
        print(f"Command: {cmd}")
        print(f"Status: {result.status.value}")
        print(f"Message: {result.message}")
        print(f"Execution: {result.execution_time_ms:.2f}ms")
        print(f"Timestamp: {result.timestamp}")
        print()
    
    # Show session history
    history = session.get_recent_commands()
    print(f"Session executed {len(history)} commands")
    print()


def showcase_function_schemas():
    """Showcase AI function schemas for agents."""
    print("📋 AI Function Schemas (OpenAI Compatible)")
    print("=" * 45)
    
    functions = get_available_functions()
    print(f"Total functions available: {len(functions)}")
    print()
    
    # Show detailed examples
    categories = {}
    for func in functions:
        name = func['name']
        category = name.split('_')[0] if '_' in name else 'other'
        if category not in categories:
            categories[category] = []
        categories[category].append(func)
    
    # Show a few categories
    for category, funcs in list(categories.items())[:5]:
        print(f"📦 {category.title()} ({len(funcs)} functions)")
        for func in funcs[:2]:  # Show first 2 in each category
            print(f"   • {func['name']}: {func['description']}")
        if len(funcs) > 2:
            print(f"   ... and {len(funcs) - 2} more")
        print()


def showcase_mock_ai_conversation():
    """Showcase what an AI conversation would look like."""
    print("💬 Mock AI Agent Conversation")
    print("=" * 35)
    
    # Simulate AI agent interactions
    print("👤 User: What's the current time and system information?")
    
    # AI would execute these commands:
    time_result = ai_do_sync("get current time")
    system_result = ai_do_sync("get system info")
    
    mock_response = f"""
🤖 Assistant: I'll get that information for you right away!

**Current Time:** {time_result.message}

**System Information:** {system_result.message}

Is there anything specific about your system you'd like me to check or help you with?
"""
    
    print(mock_response)
    
    print("👤 User: Can you create a backup folder and show me disk usage?")
    
    # AI would execute these:
    create_result = ai_do_sync("create directory at backup_folder")
    disk_result = ai_do_sync("get disk usage")
    
    mock_response2 = f"""
🤖 Assistant: I've completed both tasks for you:

**Folder Creation:** {create_result.message}

**Disk Usage:** {disk_result.message}

The backup folder is now ready for use. Would you like me to help you copy any specific files to it?
"""
    
    print(mock_response2)


def showcase_safety_features():
    """Showcase safety and permission features."""
    print("🛡️ Safety & Permission System")
    print("=" * 32)
    
    session = create_ai_session("safety_demo", safety_mode=True)
    
    print("✅ Safe commands (automatically allowed):")
    safe_commands = [
        "get current time",
        "calculate 10 + 5", 
        "get system info"
    ]
    
    for cmd in safe_commands:
        result = ai_do_sync(cmd, session.session_id)
        print(f"   {cmd}: {result.status.value}")
    
    print("\n🔒 Permission system:")
    print(f"   Session has {len(session.permissions)} explicit permissions")
    print(f"   Safety mode: {session.safety_mode}")
    print(f"   Commands executed: {len(session.command_history)}")


async def showcase_agent_framework():
    """Showcase the agent framework (without API keys)."""
    print("🤖 AI Agent Framework")
    print("=" * 25)
    
    # Show configuration options
    config = AgentConfig(
        name="System Administrator Assistant",
        description="An AI assistant specialized in system administration",
        system_prompt="""You are a helpful system administrator with access to CaelumSys automation tools.
        You can help with file management, system monitoring, process control, and general automation tasks.
        Always explain what you're doing and ask for confirmation on potentially dangerous operations.""",
        safety_mode=True,
        max_tokens=1500,
        temperature=0.3,
        auto_execute=False,
        require_confirmation=True
    )
    
    print("✅ Agent Configuration:")
    print(f"   Name: {config.name}")
    print(f"   Safety Mode: {config.safety_mode}")
    print(f"   Max Tokens: {config.max_tokens}")
    print(f"   Temperature: {config.temperature}")
    print(f"   Auto Execute: {config.auto_execute}")
    print()
    
    print("🔧 To create a real agent with OpenAI:")
    print("""
    from caelum_sys import create_openai_agent
    
    agent = create_openai_agent(
        api_key="your-openai-api-key",
        name="My System Assistant",
        system_prompt="Custom instructions here..."
    )
    
    response = await agent.chat("Help me organize my files")
    """)
    
    print("🔧 To create a real agent with Anthropic:")
    print("""
    from caelum_sys import create_anthropic_agent
    
    agent = create_anthropic_agent(
        api_key="your-anthropic-api-key", 
        model="claude-3-sonnet-20240229"
    )
    
    response = await agent.chat("What's my system status?")
    """)


def show_integration_examples():
    """Show integration examples for popular frameworks."""
    print("🔗 Integration Examples")
    print("=" * 25)
    
    print("💬 Discord Bot Integration:")
    print("""
import discord
from caelum_sys import create_openai_agent

class SystemBot(discord.Client):
    async def on_ready(self):
        self.agent = create_openai_agent(api_key="your-key")
    
    async def on_message(self, message):
        if message.content.startswith('!system'):
            query = message.content[8:]
            response = await self.agent.chat(query)
            await message.channel.send(response)
""")
    
    print("\n🌐 Web API with FastAPI:")
    print("""
from fastapi import FastAPI
from caelum_sys import create_openai_agent

app = FastAPI()
agent = create_openai_agent(api_key="your-key")

@app.post("/chat")
async def chat(query: str):
    response = await agent.chat(query)
    return {"response": response}
""")
    
    print("\n🤖 Slack Bot Integration:")
    print("""
from slack_bolt import App
from caelum_sys import create_anthropic_agent

app = App(token="your-slack-token")
agent = create_anthropic_agent(api_key="your-key")

@app.message("system")
async def handle_system(message, say):
    response = await agent.chat(message['text'])
    await say(response)
""")


async def main():
    """Run the complete showcase."""
    print("🌟 CaelumSys v0.4.0 - AI Integration Showcase")
    print("=" * 60)
    print("The Ultimate AI-Enhanced System Automation Toolkit")
    print("=" * 60)
    print()
    
    # Run all showcases
    showcase_basic_usage()
    print("\n" + "="*80 + "\n")
    
    showcase_ai_enhanced() 
    print("\n" + "="*80 + "\n")
    
    showcase_function_schemas()
    print("\n" + "="*80 + "\n")
    
    showcase_mock_ai_conversation()
    print("\n" + "="*80 + "\n")
    
    showcase_safety_features()
    print("\n" + "="*80 + "\n")
    
    await showcase_agent_framework()
    print("\n" + "="*80 + "\n")
    
    show_integration_examples()
    print("\n" + "="*80 + "\n")
    
    # Summary
    print("🎉 SUMMARY")
    print("=" * 12)
    print("CaelumSys v0.4.0 provides:")
    print("✅ 117+ system automation commands")
    print("✅ AI-first design with structured responses") 
    print("✅ OpenAI & Anthropic agent integration")
    print("✅ Built-in safety and permission systems")
    print("✅ One-line agent creation")
    print("✅ Cross-platform compatibility")
    print("✅ Zero-configuration setup")
    print()
    print("Ready to build the next generation of AI assistants! 🚀")
    print()
    print("Get started:")
    print("  pip install caelum-sys[openai]")
    print("  pip install caelum-sys[anthropic]") 
    print("  pip install caelum-sys[ai]  # All AI features")


if __name__ == "__main__":
    asyncio.run(main())
