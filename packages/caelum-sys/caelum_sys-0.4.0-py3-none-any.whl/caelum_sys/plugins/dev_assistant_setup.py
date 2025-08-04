"""
Dev Assistant Setup Plugin for CaelumSys
Automated setup for personalized development AI assistants
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from caelum_sys.registry import register_command


@register_command("setup dev assistant", safe=False)
def setup_dev_assistant() -> str:
    """Interactive setup wizard for creating a personalized dev assistant."""
    try:
        print("🚀 CaelumSys Dev Assistant Setup Wizard")
        print("=" * 50)
        
        # Collect user preferences
        config = collect_user_preferences()
        
        # Create assistant files
        assistant_dir = create_assistant_directory(config)
        
        # Generate assistant code
        create_assistant_files(assistant_dir, config)
        
        # Install dependencies if needed
        install_dependencies(config)
        
        # Create launch scripts
        create_launch_scripts(assistant_dir, config)
        
        # Generate documentation
        create_documentation(assistant_dir, config)
        
        return f"✅ Dev assistant '{config['name']}' created successfully!\n" \
               f"📁 Location: {assistant_dir}\n" \
               f"🚀 Launch with: python {assistant_dir}/launch.py\n" \
               f"📚 See README.md for customization options"
               
    except Exception as e:
        return f"❌ Failed to setup dev assistant: {str(e)}"

@register_command("setup dev assistant quick {name} {ai_provider}", safe=False)
def setup_dev_assistant_quick(name: str, ai_provider: str) -> str:
    """Quick setup with minimal prompts (providers: openai, anthropic, ollama)."""
    try:
        # Quick configuration
        config = {
            'name': name,
            'description': f"Personal {name} development assistant",
            'ai_provider': ai_provider.lower(),
            'features': ['coding', 'git', 'files', 'system'],
            'personality': 'professional',
            'output_dir': f"dev_assistant_{name.lower().replace(' ', '_')}",
            'api_key_env': f"{ai_provider.upper()}_API_KEY" if ai_provider != 'ollama' else None,
            'model': get_default_model(ai_provider),
            'create_env_file': True,
            'create_launcher': True
        }
        
        # Create assistant
        assistant_dir = create_assistant_directory(config)
        create_assistant_files(assistant_dir, config)
        create_launch_scripts(assistant_dir, config)
        create_documentation(assistant_dir, config)
        
        return f"⚡ Quick dev assistant '{name}' created!\n" \
               f"📁 Location: {assistant_dir}\n" \
               f"🚀 Launch: python {assistant_dir}/launch.py"
               
    except Exception as e:
        return f"❌ Quick setup failed: {str(e)}"

def collect_user_preferences() -> Dict[str, Any]:
    """Interactive wizard to collect user preferences."""
    config: Dict[str, Any] = {}
    
    print("\n📝 Assistant Configuration")
    print("-" * 30)
    
    # Basic info
    config['name'] = input("Assistant name (e.g., 'CodeBuddy'): ").strip() or "DevAssistant"
    config['description'] = input("Brief description: ").strip() or "My personal development assistant"
    
    # AI Provider
    print("\n🤖 Choose AI Provider:")
    print("1. OpenAI (GPT-4, GPT-3.5) - Requires API key")
    print("2. Anthropic (Claude) - Requires API key") 
    print("3. Ollama (Local models) - Free, no API key")
    
    provider_choice = input("Choice (1-3): ").strip()
    provider_map = {'1': 'openai', '2': 'anthropic', '3': 'ollama'}
    config['ai_provider'] = provider_map.get(provider_choice, 'ollama')
    
    # Model selection
    config['model'] = select_model(config['ai_provider'])
    
    # Features
    print("\n🔧 Select Features (space-separated numbers):")
    features_map = {
        '1': 'coding', '2': 'git', '3': 'files', '4': 'system',
        '5': 'web', '6': 'database', '7': 'testing', '8': 'deployment'
    }
    print("1. Code analysis & generation  2. Git operations")
    print("3. File management           4. System monitoring")
    print("5. Web requests & APIs       6. Database operations")
    print("7. Testing assistance        8. Deployment help")
    
    selected = input("Features (e.g., '1 2 3 4'): ").strip().split()
    config['features'] = [features_map[s] for s in selected if s in features_map]
    if not config['features']:
        config['features'] = ['coding', 'git', 'files', 'system']
    
    # Personality
    print("\n🎭 Assistant Personality:")
    print("1. Professional  2. Friendly  3. Concise  4. Detailed")
    personality_map = {'1': 'professional', '2': 'friendly', '3': 'concise', '4': 'detailed'}
    personality_choice = input("Choice (1-4): ").strip()
    config['personality'] = personality_map.get(personality_choice, 'professional')
    
    # Output directory
    default_dir = f"dev_assistant_{config['name'].lower().replace(' ', '_')}"
    config['output_dir'] = input(f"Output directory [{default_dir}]: ").strip() or default_dir
    
    # API key setup
    if config['ai_provider'] != 'ollama':
        config['api_key_env'] = input(f"API key environment variable [{config['ai_provider'].upper()}_API_KEY]: ").strip() or f"{config['ai_provider'].upper()}_API_KEY"
        config['create_env_file'] = input("Create .env template? (y/n) [y]: ").strip().lower() != 'n'
    else:
        config['api_key_env'] = None
        config['create_env_file'] = False
    
    # Advanced options
    config['create_launcher'] = input("Create launch script? (y/n) [y]: ").strip().lower() != 'n'
    config['create_tests'] = input("Create test files? (y/n) [y]: ").strip().lower() != 'n'
    
    return config

def select_model(provider: str) -> str:
    """Select appropriate model based on provider."""
    models = {
        'openai': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        'anthropic': ['claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
        'ollama': ['llama3.1', 'codellama', 'mistral', 'phi3']
    }
    
    if provider not in models:
        return 'gpt-3.5-turbo'
    
    print(f"\n🧠 Available {provider.title()} models:")
    for i, model in enumerate(models[provider], 1):
        print(f"{i}. {model}")
    
    choice = input(f"Model choice (1-{len(models[provider])}) [1]: ").strip()
    try:
        return models[provider][int(choice) - 1]
    except (ValueError, IndexError):
        return models[provider][0]

def get_default_model(provider: str) -> str:
    """Get default model for provider."""
    defaults = {
        'openai': 'gpt-3.5-turbo',
        'anthropic': 'claude-3-haiku-20240307',
        'ollama': 'llama3.1'
    }
    return defaults.get(provider, 'gpt-3.5-turbo')

def create_assistant_directory(config: Dict) -> Path:
    """Create the assistant directory structure."""
    base_dir = Path(config['output_dir'])
    base_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (base_dir / 'config').mkdir(exist_ok=True)
    (base_dir / 'logs').mkdir(exist_ok=True)
    (base_dir / 'plugins').mkdir(exist_ok=True)
    
    if config.get('create_tests', True):
        (base_dir / 'tests').mkdir(exist_ok=True)
    
    return base_dir

def create_assistant_files(assistant_dir: Path, config: Dict) -> None:
    """Generate all assistant files."""
    
    # Main assistant file
    assistant_code = generate_assistant_code(config)
    with open(assistant_dir / 'assistant.py', 'w', encoding='utf-8') as f:
        f.write(assistant_code)
    
    # Configuration file
    config_data = {
        'name': config['name'],
        'description': config['description'],
        'ai_provider': config['ai_provider'],
        'model': config['model'],
        'features': config['features'],
        'personality': config['personality'],
        'api_key_env': config['api_key_env']
    }
    
    with open(assistant_dir / 'config' / 'settings.json', 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)
    
    # System prompt
    system_prompt = generate_system_prompt(config)
    with open(assistant_dir / 'config' / 'system_prompt.txt', 'w', encoding='utf-8') as f:
        f.write(system_prompt)
    
    # Environment file template
    if config.get('create_env_file', False):
        env_content = generate_env_template(config)
        with open(assistant_dir / '.env.template', 'w', encoding='utf-8') as f:
            f.write(env_content)

def generate_assistant_code(config: Dict) -> str:
    """Generate the main assistant Python code."""
    
    # Generate agent creation code based on provider
    if config["ai_provider"] == "openai":
        agent_creation = f'self.agent = create_openai_agent(api_key=os.getenv("{config.get("api_key_env", "OPENAI_API_KEY")}"), model="{config["model"]}", name="{config["name"]}")'
    elif config["ai_provider"] == "anthropic":
        agent_creation = f'self.agent = create_anthropic_agent(api_key=os.getenv("{config.get("api_key_env", "ANTHROPIC_API_KEY")}"), model="{config["model"]}", name="{config["name"]}")'
    elif config["ai_provider"] == "ollama":
        agent_creation = f'self.agent = create_ollama_agent(model="{config["model"]}", name="{config["name"]}")'
    else:
        agent_creation = 'raise ValueError("Unsupported AI provider")'
    
    return f'''"""
{config["name"]} - Personal Development Assistant
Generated by CaelumSys Dev Assistant Setup
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Try to import from development version first, then installed version
try:
    # Add parent directory to path for development (if we're in the dev tree)
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from caelum_sys import create_{config["ai_provider"]}_agent, do
except ImportError:
    # Fall back to installed version
    from caelum_sys import create_{config["ai_provider"]}_agent, do

class {config["name"].replace(" ", "")}:
    def __init__(self):
        """Initialize the development assistant."""
        self.config_dir = Path(__file__).parent / "config"
        self.load_config()
        self.setup_agent()
    
    def load_config(self):
        """Load configuration from settings file."""
        config_file = self.config_dir / "settings.json"
        if config_file.exists():
            with open(config_file) as f:
                self.config = json.load(f)
        else:
            self.config = {{
                "name": "{config["name"]}",
                "description": "{config["description"]}",
                "features": {config["features"]}
            }}
        
        # Load system prompt
        prompt_file = self.config_dir / "system_prompt.txt"
        if prompt_file.exists():
            with open(prompt_file) as f:
                self.system_prompt = f.read().strip()
        else:
            self.system_prompt = "You are a helpful development assistant."
    
    def setup_agent(self):
        """Setup the AI agent with configuration."""
        try:
            {agent_creation}
            print(f"✅ {{self.config['name']}} initialized successfully!")
            print(f"🤖 Using {{self.config.get('ai_provider', 'unknown')}} with model {{self.config.get('model', 'unknown')}}")
        except Exception as e:
            print(f"❌ Failed to initialize agent: {{e}}")
            self.agent = None
    
    async def chat(self, message: str) -> str:
        """Chat with the assistant."""
        if not self.agent:
            return "❌ Assistant not initialized. Please check your configuration."
        
        try:
            response = await self.agent.chat(message)
            return response
        except Exception as e:
            return f"❌ Error: {{str(e)}}"
    
    def start_interactive_mode(self):
        """Start interactive chat mode."""
        print(f"\\n🚀 {{self.config['name']}} is ready!")
        print("💡 Specialized in: " + ", ".join(self.config.get('features', [])))
        print("Type 'exit' to quit, 'help' for commands\\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if not user_input:
                    continue
                
                print("🤖 Assistant: ", end="")
                response = asyncio.run(self.chat(user_input))
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {{e}}")
    
    def show_help(self):
        """Show available commands and features."""
        print("\\n📚 Available Features:")
        features = self.config.get('features', [])
        feature_descriptions = {{
            'coding': '💻 Code analysis, generation, and debugging',
            'git': '📊 Git operations and version control',
            'files': '📁 File management and operations',
            'system': '🖥️ System monitoring and administration',
            'web': '🌐 Web requests and API interactions',
            'database': '🗄️ Database operations and queries',
            'testing': '🧪 Testing assistance and automation',
            'deployment': '🚀 Deployment and DevOps help'
        }}
        
        for feature in features:
            if feature in feature_descriptions:
                print(f"  {{feature_descriptions[feature]}}")
        
        print("\\n💡 Example commands:")
        print("  'What's my git status?'")
        print("  'Create a Python function to sort a list'")
        print("  'Check system memory usage'")
        print("  'Help me debug this error: [paste error]'")
        print()

def main():
    """Main entry point."""
    assistant = {config["name"].replace(" ", "")}()
    assistant.start_interactive_mode()

if __name__ == "__main__":
    main()
'''

def generate_system_prompt(config: Dict) -> str:
    """Generate a personalized system prompt."""
    personality_traits = {
        'professional': 'You are professional, precise, and focused on efficiency.',
        'friendly': 'You are friendly, approachable, and encouraging.',
        'concise': 'You provide brief, to-the-point responses without unnecessary detail.',
        'detailed': 'You provide comprehensive, detailed explanations with examples.'
    }
    
    feature_expertise = {
        'coding': 'code analysis, generation, debugging, and best practices',
        'git': 'version control, Git operations, and repository management',
        'files': 'file system operations, organization, and management',
        'system': 'system administration, monitoring, and troubleshooting',
        'web': 'web development, API interactions, and HTTP requests',
        'database': 'database design, queries, and data management',
        'testing': 'test automation, debugging, and quality assurance',
        'deployment': 'deployment strategies, DevOps, and infrastructure'
    }
    
    expertise_list = [feature_expertise[f] for f in config['features'] if f in feature_expertise]
    
    return f'''You are {config["name"]}, a specialized development assistant created with CaelumSys.

PERSONALITY: {personality_traits.get(config["personality"], "You are helpful and professional.")}

EXPERTISE: You specialize in {", ".join(expertise_list)}.

CAPABILITIES: You have access to 135+ system commands through CaelumSys, including:
- High-performance screen capture and monitoring (160+ FPS)
- File management and Git operations
- System monitoring and process management
- Web requests and API interactions
- Mouse and keyboard automation
- OCR text extraction and image analysis

INTERACTION STYLE:
- Provide practical, actionable solutions
- Use system commands when appropriate
- Explain your reasoning when helpful
- Ask clarifying questions if needed

Remember: You can execute system commands using the CaelumSys framework. Always consider using built-in commands before suggesting manual alternatives.'''

def generate_env_template(config: Dict) -> str:
    """Generate .env template file."""
    if config['ai_provider'] == 'ollama':
        return '''# CaelumSys Dev Assistant Configuration
# No API key needed for Ollama (local models)

# Optional: Customize Ollama server URL
# OLLAMA_HOST=http://localhost:11434
'''
    
    return f'''# CaelumSys Dev Assistant Configuration
# Add your API key below

{config["api_key_env"]}=your_api_key_here

# Optional: Additional configuration
# ASSISTANT_LOG_LEVEL=INFO
# ASSISTANT_MAX_TOKENS=2000
'''

def create_launch_scripts(assistant_dir: Path, config: Dict) -> None:
    """Create convenient launch scripts."""
    if not config.get('create_launcher', True):
        return
    
    # Python launcher
    launcher_code = f'''#!/usr/bin/env python3
"""
Launch script for {config["name"]}
"""

import sys
import os
from pathlib import Path

# Add the assistant directory to Python path
assistant_dir = Path(__file__).parent
sys.path.insert(0, str(assistant_dir))

# Load environment variables if .env exists
env_file = assistant_dir / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

# Import and run the assistant
from assistant import main

if __name__ == "__main__":
    main()
'''
    
    with open(assistant_dir / 'launch.py', 'w', encoding='utf-8') as f:
        f.write(launcher_code)
    
    # Batch file for Windows
    batch_code = f'''@echo off
cd /d "%~dp0"
python launch.py
pause
'''
    
    with open(assistant_dir / 'launch.bat', 'w', encoding='utf-8') as f:
        f.write(batch_code)
    
    # Shell script for Unix
    shell_code = f'''#!/bin/bash
cd "$(dirname "$0")"
python3 launch.py
'''
    
    with open(assistant_dir / 'launch.sh', 'w', encoding='utf-8') as f:
        f.write(shell_code)
    
    # Make shell script executable
    try:
        os.chmod(assistant_dir / 'launch.sh', 0o755)
    except:
        pass  # Windows or permission issues

def install_dependencies(config: Dict) -> None:
    """Install additional dependencies if needed."""
    dependencies = []
    
    # Add dotenv for environment file support
    if config.get('create_env_file', False):
        dependencies.append('python-dotenv')
    
    if dependencies:
        print(f"📦 Installing additional dependencies: {', '.join(dependencies)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + dependencies)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("⚠️ Some dependencies failed to install - you may need to install them manually")

def create_documentation(assistant_dir: Path, config: Dict) -> None:
    """Create comprehensive documentation."""
    readme_content = f'''# {config["name"]} - Personal Development Assistant

> Generated by CaelumSys Dev Assistant Setup

## 🚀 Quick Start

1. **Install dependencies** (if using API-based models):
   ```bash
   pip install python-dotenv  # For environment variables
   ```

2. **Configure API key** (if needed):
   - Copy `.env.template` to `.env`
   - Add your API key to the `.env` file

3. **Launch your assistant**:
   ```bash
   python launch.py
   # or
   ./launch.sh    # Unix/Linux/macOS
   launch.bat     # Windows
   ```

## 🤖 Your Assistant Details

- **Name**: {config["name"]}
- **AI Provider**: {config["ai_provider"].title()}
- **Model**: {config["model"]}
- **Personality**: {config["personality"].title()}
- **Specialized Features**: {", ".join(config["features"])}

## 💡 Features & Capabilities

Your assistant has access to **135+ CaelumSys commands** including:

### 💻 Development Features
- Code analysis and generation
- Git operations and version control
- File management and organization
- System monitoring and administration

### 🚀 High-Performance Vision
- Screen capture and monitoring (160+ FPS)
- Image recognition and template matching
- OCR text extraction from screen
- Gaming-level pixel monitoring

### 🖱️ Automation Capabilities
- Mouse and keyboard control
- UI element detection and interaction
- Process management
- Web requests and API calls

## 📝 Example Commands

Try these commands with your assistant:

```
"What's my current git status?"
"Create a Python function to reverse a string"
"Show me system memory usage"
"Take a screenshot of my desktop"
"Help me debug this error: [paste your error]"
"Create a new file called test.py with hello world"
```

## 🔧 Customization

### Modify System Prompt
Edit `config/system_prompt.txt` to change your assistant's personality and behavior.

### Update Configuration
Edit `config/settings.json` to modify features, model, or other settings.

### Add Custom Plugins
Create custom CaelumSys plugins in the `plugins/` directory for specialized functionality.

## 📁 Project Structure

```
{config["output_dir"]}/
├── assistant.py           # Main assistant code
├── launch.py             # Launch script
├── launch.bat            # Windows launcher
├── launch.sh             # Unix launcher
├── config/
│   ├── settings.json     # Assistant configuration
│   └── system_prompt.txt # AI system prompt
├── logs/                 # Log files
├── plugins/              # Custom plugins
└── README.md            # This file
```

## 🚀 Advanced Usage

### API Integration
```python
from assistant import {config["name"].replace(" ", "")}

# Create instance
assistant = {config["name"].replace(" ", "")}()

# Use programmatically
response = await assistant.chat("Your message here")
print(response)
```

### Custom Commands
Add custom CaelumSys commands by creating plugins in the `plugins/` directory.

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Ensure your `.env` file contains the correct API key
   - Verify the API key has proper permissions

2. **Import Errors**:
   - Make sure CaelumSys is installed: `pip install caelum-sys`
   - Check Python path and virtual environment

3. **Permission Issues**:
   - Some commands require elevated permissions
   - Run with appropriate privileges if needed

### Need Help?

- Check the [CaelumSys documentation](https://github.com/BlackBeardJW/caelum-sys)
- File issues at: https://github.com/BlackBeardJW/caelum-sys/issues

---

**Made with ❤️ using CaelumSys Dev Assistant Setup**
'''
    
    with open(assistant_dir / 'README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

@register_command("list dev assistant templates", safe=True)
def list_dev_assistant_templates() -> str:
    """Show available pre-configured dev assistant templates."""
    templates = {
        'fullstack': {
            'name': 'FullStack Dev Assistant',
            'features': ['coding', 'git', 'files', 'web', 'database'],
            'personality': 'professional',
            'description': 'Complete web development assistant'
        },
        'devops': {
            'name': 'DevOps Assistant',
            'features': ['system', 'deployment', 'git', 'files'],
            'personality': 'concise',
            'description': 'Infrastructure and deployment specialist'
        },
        'ai-researcher': {
            'name': 'AI Research Assistant', 
            'features': ['coding', 'files', 'web', 'testing'],
            'personality': 'detailed',
            'description': 'AI/ML development and research helper'
        },
        'game-dev': {
            'name': 'Game Dev Assistant',
            'features': ['coding', 'files', 'system', 'testing'],
            'personality': 'friendly',
            'description': 'Game development and testing specialist'
        }
    }
    
    result = "🎯 Available Dev Assistant Templates:\n\n"
    for key, template in templates.items():
        result += f"**{key}**: {template['name']}\n"
        result += f"   📝 {template['description']}\n"
        result += f"   🔧 Features: {', '.join(template['features'])}\n"
        result += f"   🎭 Style: {template['personality']}\n\n"
    
    result += "💡 Usage: `caelum-sys \"setup dev assistant template {template_name} {ai_provider}\"`\n"
    result += "Example: `caelum-sys \"setup dev assistant template fullstack ollama\"`"
    
    return result

@register_command("setup dev assistant template {template_name} {ai_provider}", safe=False)
def setup_dev_assistant_template(template_name: str, ai_provider: str) -> str:
    """Setup a pre-configured dev assistant template."""
    templates = {
        'fullstack': {
            'name': 'FullStack Dev Assistant',
            'features': ['coding', 'git', 'files', 'web', 'database'],
            'personality': 'professional',
            'description': 'Complete web development assistant'
        },
        'devops': {
            'name': 'DevOps Assistant', 
            'features': ['system', 'deployment', 'git', 'files'],
            'personality': 'concise',
            'description': 'Infrastructure and deployment specialist'
        },
        'ai-researcher': {
            'name': 'AI Research Assistant',
            'features': ['coding', 'files', 'web', 'testing'],
            'personality': 'detailed', 
            'description': 'AI/ML development and research helper'
        },
        'game-dev': {
            'name': 'Game Dev Assistant',
            'features': ['coding', 'files', 'system', 'testing'],
            'personality': 'friendly',
            'description': 'Game development and testing specialist'
        }
    }
    
    if template_name not in templates:
        return f"❌ Template '{template_name}' not found. Available: {', '.join(templates.keys())}"
    
    if ai_provider not in ['openai', 'anthropic', 'ollama']:
        return f"❌ AI provider '{ai_provider}' not supported. Use: openai, anthropic, ollama"
    
    try:
        template = templates[template_name]
        
        # Create configuration from template
        config = {
            'name': template['name'],
            'description': template['description'],
            'ai_provider': ai_provider.lower(),
            'model': get_default_model(ai_provider),
            'features': template['features'],
            'personality': template['personality'],
            'output_dir': f"dev_assistant_{template_name}",
            'api_key_env': f"{ai_provider.upper()}_API_KEY" if ai_provider != 'ollama' else None,
            'create_env_file': ai_provider != 'ollama',
            'create_launcher': True,
            'create_tests': True
        }
        
        # Create assistant
        assistant_dir = create_assistant_directory(config)
        create_assistant_files(assistant_dir, config)
        create_launch_scripts(assistant_dir, config)
        create_documentation(assistant_dir, config)
        
        return f"✅ {template['name']} created successfully!\n" \
               f"📁 Location: {assistant_dir}\n" \
               f"🚀 Launch: python {assistant_dir}/launch.py\n" \
               f"🔧 Features: {', '.join(template['features'])}"
               
    except Exception as e:
        return f"❌ Template setup failed: {str(e)}"
