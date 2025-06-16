# MnemoX Lite - Installation

## Quick Install

1. **Clone repository:**
   ```bash
   git clone <repository-url> mnemox-lite
   cd mnemox-lite
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key in Claude Desktop:**
   Add to your `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "mnemox-lite": {
         "command": "python",
         "args": ["path/to/mnemox-lite/run.py"],
         "env": {
           "GOOGLE_API_KEY": "your-gemini-api-key-here"
         }
       }
     }
   }
   ```

4. **Start MnemoX:**
   ```bash
   python run.py
   ```

## Features

- **System Tray**: Click tray icon to open GUI
- **Memory Storage**: Semantic memory with Qdrant + SQLite
- **MCP Integration**: Use with Claude via `remember` and `recall` tools
- **Modern GUI**: Dark theme, responsive interface

## Requirements

- Python 3.11+
- Google Gemini API key
- Windows/Mac/Linux

## Development

For development with hot reloading:
```bash
pip install -e .
python run.py
```
