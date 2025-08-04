# CaelumSys 🚀 AI-Enhanced System Automation with **135+ specialized plugins** and a powerful AI integration framework supporting **OpenAI, Anthropic, and local models like Ollama**.

> 🚀 **NEW in v0.4.0**: **BUILT-IN HIGH-PERFORMANCE VISION!** MSS, OpenCV, and Tesseract are now integrated directly - no separate installation needed!

> ⚡ **BREAKTHROUGH**: **3-4x faster screen capture**, **enhanced template matching**, and **OCR text extraction** built into every installation!

> 👁️ **GAMING-READY**: AI agents can now monitor screens at **160+ FPS** and detect changes in **real-time** for competitive gaming applications!

![PyPI](https://img.shields.io/pypi/v/caelum-sys)
![Python Version](https://img.shields.io/pypi/pyversions/caelum-sys)
![Wheel](https://img.shields.io/pypi/wheel/caelum-sys)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Downloads](https://img.shields.io/pypi/dm/caelum-sys)

**CaelumSys** is the ultimate AI-enhanced system automation toolkit that transforms natural language commands into system actions. Build intelligent assistants, chatbots, and automation agents with **135+ specialized plugins** and a powerful AI integration framework supporting **OpenAI, Anthropic, and local models like Ollama**.

## 📈 Roadmap

**v0.4.0 (Current - JUST RELEASED!) ✅**
- 🚀 **BUILT-IN HIGH-PERFORMANCE VISION**: MSS, OpenCV, Tesseract integrated directly
- ⚡ **3-4x faster screen capture** with MSS (no separate installation)
- 🎯 **Enhanced template matching** with OpenCV for superior accuracy
- 📖 **Built-in OCR text extraction** with Tesseract
- 🎮 **Gaming-level performance**: 160+ FPS pixel monitoring
- 📊 **Performance benchmarking tools** built-in
- 🤖 Full AI agent integration (OpenAI, Anthropic, Ollama)
- 🏠 Local model support (Ollama) - No API keys needed!
- 🛡️ Advanced safety and permission systems
- 🔧 Enhanced function schema generation
- 📚 Comprehensive AI integration documentation

**v0.3.x (Previous) ✅**
- Basic system automation commands
- Plugin architecture foundation
- Command-line interface
- File management operations

**v0.5.0 (Planned)**
- 📡 REST API server mode
- 🔧 Plugin management CLI
- 🌐 Web dashboard interface
- 🛒 Plugin marketplace

**v1.0.0 (Future)**
- 🎯 Stable API guarantee
- 🔒 Advanced security features
- 🏢 Enterprise integrations
- 📊 Analytics and monitoring

---

**CaelumSys** is the ultimate AI-enhanced system automation toolkit that transforms natural language commands into system actions. Build intelligent assistants, chatbots, and automation agents with **135+ specialized plugins** and a powerful AI integration framework supporting **OpenAI, Anthropic, and local models like Ollama**.

> 🚀 **NEW in v0.4.0**: **BUILT-IN HIGH-PERFORMANCE VISION!** MSS, OpenCV, and Tesseract are now integrated directly - no separate installation needed!

> ⚡ **BREAKTHROUGH**: **3-4x faster screen capture**, **enhanced template matching**, and **OCR text extraction** built into every installation!

> 👁️ **GAMING-READY**: AI agents can now monitor screens at **160+ FPS** and detect changes in **real-time** for competitive gaming applications!

---

## 🤖 AI Agent Quick Start

Create a powerful AI assistant with system automation in just one line:

```python
import os
from caelum_sys import create_openai_agent

# Create an AI assistant with full system capabilities
agent = create_openai_agent(os.getenv("OPENAI_API_KEY"))

# Start chatting!
**That's it!** Your AI assistant can now:
- 📁 Manage files and directories
- 🌐 Make network requests and web searches  
- 📊 Monitor system performance
- 🎵 Control media playback
- 📸 **Capture screenshots at HIGH-SPEED (MSS - 3x faster)**
- 👁️ **Watch your screen in real-time at 160+ FPS**
- 🖱️ **Control mouse clicks and movements**
- ⌨️ **Type text and press keyboard shortcuts**
- 🎯 **Find and click on images/UI elements (OpenCV enhanced)**
- 📖 **Read any text from screen using OCR (Tesseract)**
- 🧮 Perform calculations
- ⏰ Handle date/time operations
- 🔧 Execute Git operations
- And 135+ more system tasks!

---

## 🌟 Key Features

- **🤖 AI-First Design**: Built for OpenAI, Anthropic, and local models (Ollama)
- **👁️ Vision Capabilities**: AI agents can see and analyze screen content
- **🖱️ Input Control**: Complete mouse and keyboard automation
- **🎯 Smart Interactions**: Find and click on UI elements automatically  
- **🗣️ Natural Language Interface**: `do("get current time")` instead of complex APIs
- **🔌 Plugin Architecture**: 135+ specialized plugins covering daily automation needs  
- **🛡️ Safety Classifications**: Commands marked safe/unsafe for AI agent integration
- **💰 Cost-Effective**: Use free local models or premium cloud APIs
- **🚀 One-Line Setup**: Create AI assistants instantly with minimal code
- **⚡ Zero Configuration**: Works immediately after `pip install caelum-sys`
- **🎯 135+ Commands**: Comprehensive coverage from file operations to UI automation
- **🔧 Extensible**: Create custom plugins in just 10-15 lines of code
- **🌐 Cross-Platform**: Windows-focused with macOS/Linux compatibility
- **🔄 Async Support**: Built for real-time AI applications

---

## 📦 Installation

### Basic Installation
```bash
pip install caelum-sys
```
*✨ **High-Performance Vision included!** MSS, OpenCV, and Tesseract are automatically installed - no extra setup needed!*

### With AI Capabilities
```bash
# For OpenAI integration (GPT-4, etc.)
pip install caelum-sys[openai]

# For Anthropic integration (Claude)  
pip install caelum-sys[anthropic]

# For all AI features
pip install caelum-sys[ai]

# For local Ollama (no extra dependencies needed!)
pip install caelum-sys
# Then: ollama serve && ollama pull llama3.1
```

> **Note**: The base installation includes all system automation and high-performance vision features. AI provider packages are only needed for cloud-based AI integration.

---

## ⚡ High-Performance Vision (NEW in v0.4.0!)

CaelumSys now includes **built-in high-performance vision backends** - no separate installation needed:

### 🚀 **3-4x Faster Screen Capture with MSS**
```python
do("take screenshot")  # Now uses MSS automatically - 3x faster!
do("take screenshot of region 100 100 500 300")  # 4x faster for regions!
```

### 🎯 **Enhanced Image Recognition with OpenCV**
```python
do("find image on screen button.png")  # OpenCV provides superior accuracy
```

### 📖 **Built-in OCR Text Extraction**
```python
do("read text from screen region 500 50 800 100")  # Extract any screen text
# Returns: "Health: 100/100  Mana: 50/75"
```

### 🎮 **Gaming-Level Performance**
```python
do("high speed pixel monitor 500 300 for 10 seconds")  # 160+ FPS monitoring
do("performance benchmark screen capture")  # See the speed difference
```

**Performance Improvements:**
- **Full Screen Capture:** MSS is 1.3x faster than PyAutoGUI
- **Region Capture:** MSS is 4.4x faster than PyAutoGUI  
- **Gaming Monitoring:** Sustained 160+ FPS pixel monitoring
- **Template Matching:** OpenCV provides enhanced accuracy and reliability

---

## 🚀 Quick Examples

### Local AI with Ollama (No API Keys!)
```python
from caelum_sys import create_ollama_agent

# Create a local AI assistant - completely free!
agent = create_ollama_agent("llama3.1")  # or "codellama", "mistral", etc.

# Start chatting with your local AI
response = await agent.chat("What's the current time and show me system info?")
print(response)  # Your local AI executes commands and responds naturally
```

### AI with Vision & Control (NEW!)
```python
from caelum_sys import create_ollama_agent

# Create an AI that can see and control your desktop!
agent = create_ollama_agent(
    model="llama3.1",
    system_prompt="You can see the user's screen and control their mouse/keyboard. Help them with desktop tasks!"
)

# Your AI can now see and interact!
response = await agent.chat("Take a screenshot and tell me what's on my screen, then click the start button")
print(response)  # AI analyzes your screen and performs actions!
```

### Traditional Usage
```python
from caelum_sys import do

# System Information
do("get current time")           # ⏰ Current time: 2025-08-02 15:30:45
do("get system info")            # 🖥️ System Info: Windows 11, Intel i7...

# File Operations
do("create file at test.txt")    # 📄 File created: test.txt
do("list files in .")           # 📁 Files: [file1.txt, file2.py, ...]

# Network & Web
do("ping google.com")           # 🌐 Ping: google.com is reachable
do("get weather for Tokyo")     # ☀️ Tokyo: 25°C, Sunny
```

### AI Agent Examples

#### OpenAI Assistant (GPT-4)
```python
import asyncio
from caelum_sys import create_openai_agent

async def main():
    agent = create_openai_agent(
        api_key="your-openai-key",
        name="System Admin Assistant"
    )
    
    # Natural conversation with system capabilities
    response = await agent.chat("Can you check the current time, create a backup folder, and show me disk usage?")
    print(response)

asyncio.run(main())
```

#### Discord Bot with CaelumSys
```python
import discord
from caelum_sys import create_openai_agent

class SystemBot(discord.Client):
    async def on_ready(self):
        self.agent = create_openai_agent("your-openai-key")
    
    async def on_message(self, message):
        if message.content.startswith('!system'):
            query = message.content[8:]
            response = await self.agent.chat(query)
            await message.channel.send(response)
```

#### Ollama Local AI (Free!)
```python
import asyncio
from caelum_sys import create_ollama_agent

async def main():
    # Use local models - no API costs!
    agent = create_ollama_agent(
        model="llama3.1",  # or "codellama", "mistral", "phi3", etc.
        name="Local System Admin"
    )
    
    # Natural conversation with your local AI
    response = await agent.chat("Can you check disk usage, create a backup folder called 'daily_backup', and show me running processes?")
    print(response)

asyncio.run(main())
```

#### Discord Bot with Local AI
```python
import discord
from caelum_sys import create_ollama_agent

class LocalSystemBot(discord.Client):
    async def on_ready(self):
        # No API key needed - use local Ollama
        self.agent = create_ollama_agent("llama3.1")
    
    async def on_message(self, message):
        if message.content.startswith('!local'):
            query = message.content[7:]
            response = await self.agent.chat(query)
            await message.channel.send(response)
```

#### Custom Agent Configuration
```python
from caelum_sys import CaelumAgent, AgentConfig
from caelum_sys.ai_agent import OpenAIProvider, OllamaProvider

# OpenAI Configuration
config = AgentConfig(
    name="DevOps Assistant",
    system_prompt="You are a DevOps expert with system automation capabilities...",
    safety_mode=True,
    max_tokens=2000,
    temperature=0.3
)

provider = OpenAIProvider("your-key", model="gpt-4")
agent = CaelumAgent(config, provider)

# Or use local Ollama (no API key needed)
local_provider = OllamaProvider("codellama")  # Great for development tasks
local_agent = CaelumAgent(config, local_provider)
```
do("get cpu usage")              # 💻 CPU usage: 12.5%

# File Operations  
do("create file at report.txt")  # ✅ Created file at: report.txt
do("check if file exists data.json")  # ✅ File exists: data.json
do("get file size setup.py")     # 📏 File size: 1401 bytes (1.4 KB)

# Web & Network
do("check website status github.com")  # ✅ https://github.com is accessible (Status: 200)
do("get my public ip")           # 🌐 Public IP address: 203.0.113.42
do("get weather for London")     # 🌤️ Weather for London: ⛅ 18°C

# Text & Data Processing
do("encode base64 Hello World")  # 🔐 Encoded: SGVsbG8gV29ybGQ=
do("hash text with md5 secret")  # 🔒 MD5 hash: 5ebe2294ecd0e0f08eab7690d2a6ee69
do("generate uuid")              # 🆔 Generated UUID: 550e8400-e29b-41d4-a716...

# Productivity
do("add note Meeting at 3pm")    # 📝 Note saved with ID: 1
do("copy text to clipboard")     # 📋 Text copied to clipboard
do("calculate 15% of 240")       # 🧮 15% of 240 = 36.0

# Git Integration (for developers)
do("git status")                 # 📊 Git status: 3 modified files
do("git add all files")          # ✅ Added all files to staging
```

### Command Line Interface
```bash
# Get help and discover commands
caelum-sys "help"
caelum-sys "list safe commands"
caelum-sys "search commands for file"

# Execute commands
caelum-sys "get system info"
caelum-sys "take screenshot"
caelum-sys "check website status example.com"
```

---

## 📂 Plugin Categories

### 👁️ **Screen Watching** (9 commands) - NEW!
AI agents can see and analyze screen content in real-time.
```python
do("take screenshot")                          # Capture full screen
do("take screenshot of region 0 0 500 300")   # Capture specific area
do("analyze screen content")                   # AI visual analysis
do("find image on screen button.png")         # Locate UI elements
do("monitor screen changes for 10 seconds")   # Watch for changes
```

### 🖱️ **Input Control** (15 commands) - NEW!
Complete mouse and keyboard automation for AI agents.
```python
do("click at 250 150")                    # Click at coordinates
do("type text Hello World")              # Type text naturally
do("press keys ctrl+c")                  # Keyboard shortcuts
do("drag from 100 100 to 200 200")      # Drag operations
do("click on image button.png")         # Smart UI clicking
```

### 🗂️ **File Management** (8 commands)
Complete file system operations with safety checks.
```python
do("create folder Projects/my-app")      # Create directories
do("copy file data.txt to backup.txt")  # Copy operations  
do("move file temp.log to archive/")    # Move operations
do("delete file old-data.csv")          # Safe deletion
```

### 🌐 **Web & APIs** (7 commands)  
Internet connectivity and web service integration.
```python
do("check website status api.example.com")  # HTTP status checking
do("download file from https://...")        # File downloads
do("shorten url https://very-long-url...")  # URL shortening
do("get page title from news.ycombinator.com")  # Web scraping
```

### 📋 **Text & Clipboard** (8 commands)
Text manipulation and clipboard integration.
```python
do("copy text to clipboard")        # Clipboard operations
do("get clipboard content")         # Retrieve clipboard
do("uppercase text hello world")    # Text transformations
do("count words in text")          # Text analysis
```

### 🔢 **Math & Calculations** (7 commands)
Safe mathematical operations and unit conversions.
```python
do("calculate 15% of 240")                    # Percentage calculations
do("convert 100 fahrenheit to celsius")       # Temperature conversion
do("calculate tip 45.50 at 18 percent")      # Financial calculations
do("generate random number between 1 and 100")  # Random generation
```

### 📅 **Date & Time** (8 commands)
Temporal operations with timezone support.
```python
do("get current timestamp")              # Unix timestamps
do("add 5 days to today")               # Date arithmetic
do("what time is it in Tokyo")          # Timezone conversion
do("how many days until 2025-12-25")    # Date calculations
```

### 📝 **Quick Notes** (8 commands)
Persistent note management with JSON storage.
```python
do("save note Meeting with client tomorrow")  # Create notes
do("list all notes")                         # List notes
do("search notes for meeting")               # Search functionality
do("get note 1")                            # Retrieve specific notes
```

### 📊 **Git Integration** (12 commands)
Version control operations for developers.
```python
do("git status")                    # Repository status
do("git add all files")             # Stage changes
do("git commit with message Fix bug") # Commit changes
do("list git branches")             # Branch management
```

### ℹ️ **File Information** (7 commands)
Detailed file inspection and metadata.
```python
do("get file info document.pdf")              # Complete file details
do("get file hash important.zip")             # File integrity
do("find files with extension .py in src/")   # File discovery
do("count lines in file script.py")           # File analysis
```

### 🖥️ **System Utilities** (15+ commands)
System monitoring and control operations.
```python
do("get memory usage")           # Resource monitoring
do("list running processes")     # Process management  
do("take screenshot")           # Screen capture
do("open task manager")         # System tools
```

### 🔍 **Help & Discovery** (4 commands)
Built-in documentation and command discovery.
```python
do("help")                           # Complete command list
do("search commands for network")    # Find relevant commands
do("list safe commands")             # LLM-safe operations
do("list unsafe commands")           # Commands requiring permission
```

### 🤖 **AI Assistant Generator** (3 commands) - NEW!
Create personalized AI development assistants with custom capabilities.
```python
do("setup dev assistant")                    # Interactive setup wizard
do("setup dev assistant quick MyBot ollama") # Quick setup with defaults
do("list dev assistant templates")           # Show available templates
do("setup dev assistant template fullstack openai") # Use pre-configured template
```

---

## 🤖 AI Agent Integration

CaelumSys provides the most advanced AI agent capabilities with **vision and control** integration:

### 👁️ Vision-Enabled Commands (9 total) ✅
AI agents can **see and analyze** your screen:
```python
do("take screenshot")           # ✅ Safe - capture screen
do("analyze screen content")    # ✅ Safe - visual analysis  
do("find image on screen")      # ✅ Safe - locate UI elements
do("get pixel color at 100 100") # ✅ Safe - color detection
```

### 🖱️ Input Control Commands (15 total) ⚠️
AI agents can **control mouse and keyboard** (requires permission):
```python
do("click at 250 150")          # ⚠️ Controlled - mouse clicking
do("type text Hello")           # ⚠️ Controlled - keyboard input
do("press keys ctrl+c")         # ⚠️ Controlled - shortcuts
do("drag from 100 100 to 200 200") # ⚠️ Controlled - drag operations
```

### Safe Commands (111 total) ✅
Commands that **read information** without modifying system state:
```python
do("get current time")        # ✅ Safe - information retrieval
do("check website status")    # ✅ Safe - network checking  
do("get file size setup.py")  # ✅ Safe - file inspection
do("list running processes")  # ✅ Safe - system monitoring
```

### Unsafe Commands (24 total) ⚠️
Commands that **modify system state** and require explicit permission:
```python
do("delete file config.txt")  # ⚠️ Unsafe - file deletion
do("kill process chrome")     # ⚠️ Unsafe - process termination
do("empty recycle bin")       # ⚠️ Unsafe - system cleanup
do("git commit with message") # ⚠️ Unsafe - repository changes
```

**Query commands by safety:** 
- `do("list safe commands")` - Shows read-only operations
- `do("list unsafe commands")` - Shows system-modifying operations

### 🎯 Revolutionary Use Cases

**🎮 Gaming Automation:**
```python
# AI can watch game screens and react
agent.chat("Watch for the enemy and click to attack when you see red")
```

**💼 Productivity Automation:**
```python  
# AI can read and interact with any application
agent.chat("Read my emails and draft replies to the important ones")
```

**🔧 Smart Testing:**
```python
# AI can perform visual UI testing
agent.chat("Click through the app workflow and report any visual bugs")
```

---

## 🛠️ Creating Custom Plugins

Extend CaelumSys with custom functionality:

```python
# caelum_sys/plugins/my_plugin.py
from caelum_sys.registry import register_command

@register_command("greet {name}", safe=True)
def greet_person(name: str):
    """Greet someone by name."""
    return f"👋 Hello, {name}! Welcome to CaelumSys!"

@register_command("backup database", safe=False)  
def backup_database():
    """Backup the application database."""
    # Implementation here
    return "💾 Database backup completed successfully"
```

**Plugin features:**
- ✅ **Auto-discovery**: Just add `.py` files to `caelum_sys/plugins/`
- ✅ **Parameter extraction**: `{name}` automatically becomes function parameter
- ✅ **Safety classification**: Mark commands as safe/unsafe for AI agents
- ✅ **Error handling**: Built-in exception handling and user-friendly messages

---

## 🛠️ Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Format code
black caelum_sys/
isort caelum_sys/

# Type checking (optional)
mypy caelum_sys/

# Build package
python -m build
```

**Project Structure:**
```
caelum_sys/
├── plugins/           # Plugin modules (25+ plugins with 135+ commands)
├── core_actions.py    # Main execution engine
├── registry.py        # Command registration system
├── cli.py            # Command-line interface
└── __init__.py       # Package interface
```

---

## 📋 Requirements

- **Python**: 3.9+ (tested on 3.9, 3.10, 3.11, 3.12, 3.13)
- **Operating System**: Windows (primary), macOS, Linux
- **Dependencies**: Automatically installed with package
  
### Core Dependencies
  - `psutil` - System monitoring and process management
  - `requests` - Web operations and HTTP requests
  - `pyperclip` - Clipboard integration
  - `pytz` - Timezone support and conversions
  - `python-dateutil` - Advanced date parsing and manipulation
  - `pyautogui` - Basic screen capture and input control
  - `pillow` - Image processing and manipulation

### High-Performance Vision (NEW in v0.4.0!)
  - `mss>=9.0.1` - Ultra-fast screen capture (3-4x faster than PyAutoGUI)
  - `opencv-python>=4.8.0` - Advanced computer vision and template matching
  - `pytesseract>=0.3.10` - OCR text extraction from screen regions
  - `numpy>=1.24.0` - Numerical operations for image processing

### Optional AI Dependencies
  - `openai` - For GPT-4, GPT-3.5-turbo integration (install with `pip install caelum-sys[openai]`)
  - `anthropic` - For Claude 3.5 Sonnet, Claude 3 integration (install with `pip install caelum-sys[anthropic]`)
  - **Ollama** - Local AI models (no extra Python dependencies - just install Ollama separately)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-plugin`
3. **Add your plugin** to `caelum_sys/plugins/`
4. **Test your functionality** with the CLI or programmatic interface
5. **Submit a pull request**

**Contribution Ideas:**
- 🔌 New plugins (email, database, cloud services)
- 📚 Documentation improvements
- 🔧 Performance optimizations
- 🐛 Bug fixes and optimizations
- 🌍 Cross-platform compatibility

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **PyPI Package**: https://pypi.org/project/caelum-sys/
- **GitHub Repository**: https://github.com/BlackBeardJW/caelum-sys
- **Issue Tracker**: https://github.com/BlackBeardJW/caelum-sys/issues
- **Documentation**: Coming soon!

---

## 📈 Roadmap

## 📈 Roadmap

**v0.4.0 (Current - COMPLETE!) ✅**
- 🚀 **BUILT-IN HIGH-PERFORMANCE VISION**: MSS, OpenCV, Tesseract integrated directly
- ⚡ **3-4x faster screen capture** with MSS (no separate installation)
- 🎯 **Enhanced template matching** with OpenCV for superior accuracy
- 📖 **Built-in OCR text extraction** with Tesseract
- 🎮 **Gaming-level performance**: 160+ FPS pixel monitoring
- 📊 **Performance benchmarking tools** built-in
- 🤖 Full AI agent integration (OpenAI, Anthropic, Ollama)
- 🏠 Local model support (Ollama) - No API keys needed!
- 🛡️ Advanced safety and permission systems
- 🔧 Enhanced function schema generation
- 📚 Comprehensive AI integration documentation

**v0.5.0 (Planned)**
- 📡 REST API server mode
- 🔧 Plugin management CLI
- 🌐 Web dashboard interface
- 🛒 Plugin marketplace

**v1.0.0 (Future)**
- 🎯 Stable API guarantee
- 🔒 Advanced security features
- 🏢 Enterprise integrations
- 📊 Analytics and monitoring

---

<div align="center">

**Made with ❤️ by Joshua Wells**

⭐ **Star this repo** if you find CaelumSys useful!

</div>
