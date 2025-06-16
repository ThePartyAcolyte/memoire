# MnemoX Lite 🧠

**Experimental Semantic Memory System for Large Language Models**

> ⚠️ **Experimental Project**: MnemoX Lite is a vibe-coded exploration into semantic memory for LLMs. Built through AI-assisted development, it embodies the same cognitive augmentation principles it attempts to solve. Expect rough edges, unconventional patterns, and iterative improvements.

## What is MnemoX Lite?

MnemoX Lite is an experimental **MCP (Model Context Protocol) server** that tackles one of the fundamental limitations of LLM interactions: **the lack of persistent memory across conversations**.

This is the "lite" version - a testbed for exploring the foundational concepts that will eventually power MnemoX, a broader cognitive extension system. It's built for users of Claude Desktop and Cursor who want to experiment with persistent semantic memory.

### The Core Problem

Current LLMs lose all context when you start a new conversation. Valuable insights, project decisions, and accumulated knowledge disappear into the void. MnemoX Lite experiments with solving this through intelligent, persistent memory that operates transparently in the background.

### The Experimental Approach

Instead of simple storage, MnemoX Lite implements **semantic memory** that:
- Intelligently chunks and contextualizes information
- Uses vector embeddings for semantic search and retrieval
- Automatically curates memory to maintain quality
- Provides natural language querying across conversation boundaries

## How It Works Internally

### Memory Architecture

**Information Flow:**
1. **Intake**: Content gets analyzed and split into semantic chunks (20-150 words each)
2. **Contextualization**: AI identifies and creates emergent contexts automatically
3. **Vectorization**: Google's `text-embedding-004` generates 768-dimensional vectors
4. **Storage**: Qdrant stores vectors, SQLite handles metadata and relationships
5. **Retrieval**: Semantic search finds relevant fragments, AI synthesizes coherent responses
6. **Curation**: System automatically removes conflicts and redundancies

**Intelligence Layer:**
- **Chunking**: Gemini 2.5 Flash identifies natural semantic boundaries
- **Context Detection**: Emergent context creation based on content patterns (core storage operations implemented)
- **Synthesis**: Multi-fragment responses assembled into coherent narratives
- **Memory Curation**: Aggressive conflict resolution and duplicate elimination
- **Fragment Management**: Direct storage operations available (deletion, listing) but not exposed as MCP tools

### Technical Stack

**Processing Engine:**
- **Embedding Model**: `text-embedding-004` (768 dimensions)
- **Cognitive Processing**: `gemini-2.5-flash-preview-05-20`
- **Vector Database**: Qdrant for semantic search
- **Metadata Store**: SQLite for structured data
- **Protocol**: MCP server architecture

**Design Decisions:**
- Google AI APIs chosen for reliability and free tier optimization
- Local-first storage (no cloud dependencies for data)
- Modular architecture with clear separation between core and intelligence layers
- Built for transparent operation - users shouldn't think about the technology

## Current State & Limitations

### ✅ What Works
- **Core Memory Operations**: `remember`, `recall`, `create_project`, `list_projects`
- **Semantic Chunking**: Intelligent content division
- **Context Emergence**: Automatic context detection and creation
- **Project Segregation**: Complete memory isolation between projects
- **Memory Curation**: Automatic conflict resolution and redundancy elimination
- **Claude Desktop Integration**: Transparent MCP operation

### ❌ What's Incomplete
- **GUI Interface**: Functional but inconsistent, visual/operational rough edges
- **Performance Metrics**: No efficiency analysis or optimization data
- **Context Management APIs**: Several context operations throw `NotImplementedError` (listing, hierarchy, deletion)
- **Advanced Fragment Operations**: No direct fragment deletion or listing tools exposed via MCP
- **Performance**: Recall operations can take 20-30 seconds (not optimized for speed)

### ⚠️ Experimental Caveats
- **Vibe-Coded Development**: Built through AI-assisted development - expect unconventional patterns, potential optimization issues, and iterative refinements
- **No Performance Guarantees**: This is exploratory code, not production-optimized
- **Aggressive Curation**: May eliminate information it considers redundant
- **API Dependencies**: Requires Google AI API key, won't work offline
- **Memory Evolution**: System behavior can change as it "learns" usage patterns

## Installation & Setup

### Prerequisites
- Python 3.11+
- Google AI API key ([Get one here](https://makersuite.google.com/app/apikey))
- Claude Desktop or Cursor installed

### Installation

```bash
# Clone repository
git clone https://github.com/ThePartyAcolyte/mnemox-lite
cd mnemox-lite

# Setup Python environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Claude Desktop Configuration

Edit your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mnemox-lite": {
      "command": "/full/path/to/mnemox-lite/venv/Scripts/python.exe",
      "args": ["/full/path/to/mnemox-lite/run.py"],
      "env": {
        "GOOGLE_API_KEY": "your-google-ai-api-key"
      }
    }
  }
}
```

### Verification
- Restart Claude Desktop
- System runs automatically when Claude connects
- Optional GUI accessible via system tray icon
- Claude gains access to memory tools

## Usage

### MCP Tools Available in Claude

**Store Information:**
```
Claude, remember that our Q4 revenue target is $2.5M focused on enterprise clients in healthcare and fintech.
```

**Retrieve Information:**
```
Claude, recall what our revenue targets are for this quarter.
```

**Project Management:**
```
Claude, create project "Product Launch 2024" for organizing our go-to-market strategy.
Claude, list projects to see what memory spaces are available.
```

### Memory Behavior

**Intelligent Processing:** Content automatically gets chunked, contextualized, and embedded for semantic retrieval. The system identifies patterns and creates emergent contexts without manual intervention.

**Natural Querying:** Ask questions in natural language - the system performs semantic search and synthesizes responses from multiple relevant memory fragments.

**Automatic Maintenance:** Memory gets curated continuously to remove conflicts and redundancies, though this can sometimes be overly aggressive.

## Optional GUI Interface

The GUI is **monitoring and configuration only** - not required for operation:

- **Statistics Dashboard**: Real-time fragment counts, API usage, system health
- **Dynamic Configuration**: Adjust similarity thresholds, model selection, search limits
- **System Tray Integration**: Access via tray icon, no need to run separately

## Configuration

### Core Settings (`config.json`)
```json
{
  "embedding": {
    "provider": "google",
    "model": "text-embedding-004"
  },
  "processing": {
    "model": "gemini-2.5-flash-preview-05-20",
    "temperature": 0.3
  },
  "search": {
    "similarity_threshold": 0.54,
    "max_results": 50
  },
  "intelligence": {
    "enable_curation": true,
    "curation_similarity_threshold": 0.9
  }
}
```

### Performance Tuning
- **Similarity Threshold**: Lower = more results, higher = more precision
- **Chunk Size**: Smaller = granular, larger = contextual
- **Curation**: Enable for quality, disable to preserve everything

## Project Structure

```
mnemox-lite/
├── run_mcp.py              # MCP server entry point
├── config.json             # System configuration
├── src/
│   ├── core/              # Infrastructure layer
│   │   ├── embedding/     # Vector generation
│   │   ├── memory/        # CRUD operations
│   │   └── storage/       # Qdrant + SQLite
│   ├── mcp/               # Business logic
│   │   ├── intelligence/  # Cognitive processing
│   │   │   ├── chunking.py       # Semantic segmentation
│   │   │   ├── contextualization.py  # Context detection
│   │   │   ├── synthesis.py      # Response assembly
│   │   │   └── curation.py       # Memory maintenance
│   │   └── server/        # MCP tools
│   ├── gui/               # Optional interface
│   └── models/            # Pydantic data models
├── data/                  # Local storage
└── tests/                 # Test suite
```

## Development Roadmap

### Near-term Improvements
- **GUI Polish**: Fix visual inconsistencies and operational issues
- **Performance Analysis**: Add metrics and efficiency measurements
- **MCP Tool Expansion**: Expose fragment deletion, listing, and context management as MCP tools
- **Context API Completion**: Implement missing context operations (listing, hierarchy, deletion)
- **3D Force Graph**: Visualize fragment relationships and memory structure
- **Navigation Tools**: Better data exploration capabilities

### Research Areas
- **Performance Optimization**: Reduce 20-30s recall times
- **Memory Visualization**: Interactive exploration of semantic relationships
- **Complete Context Management**: Full implementation of hierarchical context operations
- **Advanced Analytics**: Knowledge gap detection and context suggestions

### No Timeline Expectations
This is an experimental "as-is" project. Development happens when it happens, driven by curiosity and practical needs rather than roadmap commitments.

## Philosophical Notes

### On Vibe Coding
This project embodies the same AI-assisted development approach it aims to enable. Built through natural language interaction with AI tools, it reflects both the possibilities and limitations of this development methodology.

### On Obsolescence
Given the rapid pace of AI development, this entire approach may become unnecessary within a year if LLMs develop native long-term memory capabilities. This is exploration, not production infrastructure.

### On Utility
The system appears to be practically useful for maintaining context across conversations, but time will tell whether the approach is sustainable or just an interesting experiment.

## Troubleshooting

### Common Issues
- **API Key Errors**: Verify `claude_desktop_config.json` configuration
- **Import Failures**: Ensure virtual environment is activated
- **Slow Performance**: 20-30s recall times are normal, not a bug
- **Memory Not Persisting**: Check write permissions in `data/` directory

### Debug Information
- **Logs**: Available in `logs/` directory
- **Debug Mode**: Set log level to "DEBUG" in `config.json`
- **MCP Debugging**: Use Claude Desktop Developer Tools

## Contributing

This experimental project welcomes contributions:

**Development Setup:**
```bash
git clone <your-fork>
cd mnemox-lite
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/
```

**Areas for Exploration:**
- Performance optimization and analysis
- GUI improvements and memory visualization
- Edge case testing and robustness improvements
- Alternative embedding providers and models

## Author & Contact

**Developer**: Tomás  
**Email**: butcherwutcher@outlook.com  
**Repository**: https://github.com/ThePartyAcolyte/mnemox-lite

*Built through vibe coding - expect the unexpected.*

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**🔬 Experimental Software Notice**

This is exploratory code built through AI-assisted development. It may contain unconventional patterns, optimization opportunities, and rough edges. Use for experimentation and learning, not production systems.

*Current status: Functional but imperfect. Useful but unpolished. Promising but unpredictable.*