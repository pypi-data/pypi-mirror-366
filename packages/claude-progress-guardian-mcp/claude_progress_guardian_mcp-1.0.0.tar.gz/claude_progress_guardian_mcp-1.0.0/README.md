# Claude Progress Guardian MCP 🛡️

> **Stops the infinite progress bar spam in Claude Code!** 🚫📊  
> Intelligent timeout management that prevents endless progress outputs

[![PyPI version](https://badge.fury.io/py/claude-progress-guardian-mcp.svg)](https://badge.fury.io/py/claude-progress-guardian-mcp)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 😤 The Problem

Ever seen this in Claude Code?
```
🔄 Ollama Pull: qwen3:14b: [░░░░░░░] 0.0% | 2.5MB/8.6GB | 1.2MB/s | ETA: 1시간 20분
🔄 Ollama Pull: qwen3:14b: [░░░░░░░] 0.0% | 2.6MB/8.6GB | 1.2MB/s | ETA: 1시간 20분  
🔄 Ollama Pull: qwen3:14b: [░░░░░░░] 0.0% | 2.7MB/8.6GB | 1.2MB/s | ETA: 1시간 19분
🔄 Ollama Pull: qwen3:14b: [░░░░░░░] 0.0% | 2.8MB/8.6GB | 1.2MB/s | ETA: 1시간 19분
... (continues for 2000+ lines) 😵‍💫
```

**TIMEOUT after 2 minutes** even though your download needs 2 hours! 😡

## 🛡️ The Solution

Claude Progress Guardian MCP **intelligently calculates** timeouts and **prevents progress spam**:

```
📥 qwen3:14b download: 9.4% | 832MB/8.6GB | 7.0MB/s | ETA: 19분
📥 qwen3:14b download: 15.2% | 1.3GB/8.6GB | 7.2MB/s | ETA: 17분
📥 qwen3:14b download: 23.1% | 2.0GB/8.6GB | 7.1MB/s | ETA: 15분
```

**No more spam!** **No more premature timeouts!** ✨

## 🚀 Features

- **🎯 Smart Timeouts**: `qwen3:14b` gets 2 hours, `ls` gets 30 seconds
- **🚫 Anti-Spam**: Progress updates every 5 seconds, not every millisecond
- **🧠 Command Analysis**: Automatically detects Ollama, downloads, builds
- **⚡ Zero Config**: Works immediately with sensible defaults
- **🔧 Extensible**: Add your own task types and timeout rules

## 📦 Installation

```bash
pip install claude-progress-guardian-mcp
```

## 🎯 Quick Start

### 1. Stop Progress Spam Forever
```python
from claude_progress_guardian_mcp import get_ollama_timeout

# Instead of default 2-minute timeout that fails:
timeout_ms = get_ollama_timeout("qwen3:14b") * 1000  # 7,142,000ms (≈2 hours)

# Use with Claude Code Bash tool:
Bash(command="ollama pull qwen3:14b", timeout=timeout_ms)
# No more timeout failures! No more progress spam! 🎉
```

### 2. Smart Timeout for Any Command
```python
from claude_progress_guardian_mcp import suggest_timeout

# Analyze any command intelligently
result = suggest_timeout("docker build -t myapp .", file_size_mb=500)
print(f"Suggested timeout: {result['timeout_display']}")  # "13 minutes"
print(f"Reasoning: {result['reasoning']}")
```

### 3. Clean Progress Monitoring
```python
from claude_progress_guardian_mcp import UniversalProgressMonitor

monitor = UniversalProgressMonitor()
task_id = monitor.start_ollama_pull_task("qwen3:14b")

# Clean, non-spammy updates every 5 seconds
# 📥 qwen3:14b: 15.2% | 1.3GB/8.6GB | 7.2MB/s | ETA: 17분
```

## 🛠️ MCP Server Setup for Claude Code

### Method 1: Automatic Integration (Recommended)
```bash
# Install the guardian
pip install claude-progress-guardian-mcp

# Add to Claude Code MCP config (~/.claude/mcp_servers/config.json)
{
  "progress-guardian": {
    "command": "progress-guardian-server",
    "args": ["--port", "9007"],
    "env": {}
  }
}

# Restart Claude Code - timeouts now automatically optimized! 🎉
```

### Method 2: Manual Integration
```python
# In your scripts, replace hard-coded timeouts:

# OLD (always fails for big downloads):
Bash(command="ollama pull qwen3:14b", timeout=120000)  # 2 minutes ❌

# NEW (intelligently calculated):
from claude_progress_guardian_mcp import get_ollama_timeout
timeout_ms = get_ollama_timeout("qwen3:14b") * 1000  # 2 hours ✅
Bash(command="ollama pull qwen3:14b", timeout=timeout_ms)
```

## 📊 Smart Timeout Examples

| Command | Default Timeout | Guardian Timeout | Why? |
|---------|----------------|------------------|------|
| `ollama pull qwen3:14b` | 2 minutes ❌ | **2 hours** ✅ | 9.3GB model needs time |
| `ollama pull llama3.1:8b` | 2 minutes ❌ | **1 hour** ✅ | 4.7GB model calculation |
| `curl -O bigfile.zip` | 2 minutes ❌ | **13 minutes** ✅ | File size ÷ speed |
| `make -j4` | 2 minutes ❌ | **30 minutes** ✅ | Compilation buffer |
| `ls -la` | 2 minutes 🤷 | **30 seconds** ✅ | Quick command |

## 🔧 Configuration

### Environment Variables
```bash
export PROGRESS_GUARDIAN_MIN_TIMEOUT=30          # Minimum timeout (seconds)
export PROGRESS_GUARDIAN_MAX_TIMEOUT=21600       # Maximum timeout (6 hours)
export PROGRESS_GUARDIAN_UPDATE_INTERVAL=5       # Progress update interval (seconds)
export PROGRESS_GUARDIAN_DEFAULT_SPEED=5.0       # Default download speed (MB/s)
```

### Custom Timeout Rules
```python
from claude_progress_guardian_mcp import SmartTimeout

# Add custom model sizes
SmartTimeout.MODEL_SIZES = {
    "my-custom-model:70b": 35.0,  # 35GB
    "my-tiny-model:1b": 0.6       # 600MB
}

# Custom timeout calculation
timeout = SmartTimeout.calculate_ollama_timeout(35.0)  # For 35GB model
print(f"Custom model timeout: {SmartTimeout.format_timeout_display(timeout)}")
```

## 🎭 Before vs After

### Before (Progress Hell) 😵‍💫
```
🔄 Downloading: [░░░░░░░] 0.1% | 8.4MB/8.6GB | 2.0MB/s | ETA: 1시간 15분
🔄 Downloading: [░░░░░░░] 0.1% | 8.6MB/8.6GB | 2.0MB/s | ETA: 1시간 15분
🔄 Downloading: [░░░░░░░] 0.1% | 9.2MB/8.6GB | 2.1MB/s | ETA: 1시간 10분
🔄 Downloading: [░░░░░░░] 0.1% | 9.3MB/8.6GB | 2.1MB/s | ETA: 1시간 9분
🔄 Downloading: [░░░░░░░] 0.1% | 9.7MB/8.6GB | 2.2MB/s | ETA: 1시간 7분
... (2000+ more lines)
Command timed out after 2m 0.0s ❌
```

### After (Progress Guardian) ✨
```
📥 qwen3:14b download started
📥 qwen3:14b: 5.2% | 450MB/8.6GB | 6.8MB/s | ETA: 20분
📥 qwen3:14b: 15.1% | 1.3GB/8.6GB | 7.2MB/s | ETA: 17분
📥 qwen3:14b: 28.4% | 2.4GB/8.6GB | 7.1MB/s | ETA: 14분
✅ qwen3:14b download completed! (32분 소요) ✅
```

## 🏗️ Architecture

```
Claude Code Bash Tool
         ↓
Progress Guardian MCP ← Analyzes command & calculates smart timeout
         ↓
Smart Timeout Engine ← File size + speed + task type = optimal timeout
         ↓
Anti-Spam Monitor ← Updates every 5s, not every 100ms
         ↓
Clean Progress Output ← Readable, useful, non-overwhelming
```

## 🤝 Contributing

We welcome contributions! The progress bar spam problem affects **everyone** using Claude Code.

```bash
git clone https://github.com/yscha88/claude-progress-guardian-mcp.git
cd claude-progress-guardian-mcp
pip install -e ".[dev]"

# Add your custom timeout rules!
# Fix progress spam issues!
# Make Claude Code better for everyone! 🚀
```

## 📄 License

MIT License - Use freely, contribute back!

## 🙏 Acknowledgments

- Born from **real frustration** with Claude Code progress spam
- **Tested extensively** on large model downloads
- Built for the **Claude Code community**
- **Problem-first solution** - we lived the pain! 😤

## 🆘 Need Help?

**Progress still spamming?** Open an issue with your command.  
**Timeout still too short?** We'll add your use case.  
**New progress pattern?** Let's make it cleaner together.

---

**🛡️ Stop the progress spam. Start the progress guardian.** 

**Made with 😤➡️😌 by someone who was tired of infinite progress bars**