# Enhanced MCP Memory

> **⚡ Optimized for Claude Sonnet 4** - This MCP server works best with Claude Sonnet 4 for optimal performance and AI-powered features.

An enhanced MCP (Model Context P### 🏗️ Project Convention Learning
- **Automatic environment detection** - OS, shell, tools, and runtime versions
- **Project type recognition** - Node.js, Python, Rust, Go, Java, MCP servers, etc.
- **Command pattern learning** - Extracts npm scripts, Makefile targets, and project commands
- **Tool configuration detection** - IDEs, linters, CI/CD, build tools, and testing frameworks
- **Dependency management** - Package managers, lock files, and installation commands
- **Smart command suggestions** - Corrects user commands based on project conventions
- **Windows-specific optimizations** - Proper path separators and command formats
- **Memory integration** - Stores learned conventions for AI context and future reference

### 📊 Enterprise Performance Monitoringotocol) server for intelligent memory and task management, designed for AI assistants and development workflows. Features semantic search, automatic task extraction, knowledge graphs, and comprehensive project management.

## ✨ Key Features

### 🧠 Intelligent Memory Management
- **Semantic search** using sentence-transformers for natural language queries
- **Automatic memory classification** with importance scoring
- **Duplicate detection** and content deduplication
- **File path associations** for code-memory relationships
- **Knowledge graph relationships** with automatic similarity detection

### � Sequential Thinking Engine
- **Structured reasoning chains** with 5-stage process (analysis, planning, execution, validation, reflection)
- **Enterprise-grade context management** with automatic token optimization
- **Conversation continuity** across sessions with intelligent summarization
- **Real-time token estimation** and compression (30-70% reduction)
- **Auto-extraction** of key points, decisions, and action items

### �📋 Advanced Task Management
- **Auto-task extraction** from conversations and code comments
- **Priority and category management** with validation
- **Status tracking** (pending, in_progress, completed, cancelled)
- **Task-memory relationships** in knowledge graph
- **Project-based organization**
- **Complex task decomposition** into manageable subtasks

### 🔧 Enterprise Features
- **Performance monitoring** with detailed metrics
- **Health checks** and system diagnostics
- **Automatic cleanup** of old data and duplicates
- **Database optimization** tools
- **Comprehensive logging** and error tracking
- **Token usage analytics** and optimization recommendations

### 🚀 Easy Deployment
- **uvx compatible** for one-command installation
- **Zero-configuration** startup with sensible defaults
- **Environment variable** configuration
- **Cross-platform** support (Windows, macOS, Linux)

## 🏗️ Project Structure

```
enhanced-mcp-memory/
├── mcp_server_enhanced.py    # Main MCP server with FastMCP integration
├── memory_manager.py         # Core memory/task logic and project detection
├── sequential_thinking.py    # Enterprise thinking chains and context optimization
├── database.py              # Database operations with retry mechanisms
├── requirements.txt         # Python dependencies
├── setup.py                # Package configuration
├── data/                   # SQLite database storage
├── logs/                   # Application logs
└── tests/                  # Comprehensive test suite
```

## 🚀 Quick Start

### Option 1: Using uvx (Recommended)

```bash
# Install and run with uvx
uvx enhanced-mcp-memory
```

### Option 2: Manual Installation

```bash
# Clone and install
git clone https://github.com/cbunting99/enhanced-mcp-memory.git
cd enhanced-mcp-memory
pip install -e .

# Run the server
enhanced-mcp-memory
```

### Option 3: Development Setup

```bash
# Clone repository
git clone https://github.com/cbunting99/enhanced-mcp-memory.git
cd enhanced-mcp-memory

# Install dependencies
pip install -r requirements.txt

# Run directly
python mcp_server_enhanced.py
```

## ⚙️ MCP Configuration

Add to your MCP client configuration:

### For uvx installation:
```json
{
  "mcpServers": {
    "memory-manager": {
      "command": "uvx",
      "args": ["enhanced-mcp-memory"],
      "env": {
        "LOG_LEVEL": "INFO",
        "MAX_MEMORY_ITEMS": "1000",
        "ENABLE_AUTO_CLEANUP": "true"
      }
    }
  }
}
```

### For local installation:
```json
{
  "mcpServers": {
    "memory-manager": {
      "command": "python",
      "args": ["mcp_server_enhanced.py"],
      "cwd": "/path/to/enhanced-mcp-memory",
      "env": {
        "LOG_LEVEL": "INFO",
        "MAX_MEMORY_ITEMS": "1000",
        "ENABLE_AUTO_CLEANUP": "true"
      }
    }
  }
}
```

## 🛠️ Available Tools

### Core Memory Tools
- `get_memory_context(query)` - Get relevant memories and context
- `create_task(title, description, priority, category)` - Create new tasks
- `get_tasks(status, limit)` - Retrieve tasks with filtering
- `get_project_summary()` - Get comprehensive project overview

### Sequential Thinking Tools
- `start_thinking_chain(objective)` - Begin structured reasoning process
- `add_thinking_step(chain_id, stage, title, content, reasoning)` - Add reasoning steps
- `get_thinking_chain(chain_id)` - Retrieve complete thinking chain
- `list_thinking_chains(limit)` - List recent thinking chains

### Context Management Tools  
- `create_context_summary(content, key_points, decisions, actions)` - Compress context for token optimization
- `start_new_chat_session(title, objective, continue_from)` - Begin new conversation with optional continuation
- `consolidate_current_session()` - Compress current session for handoff
- `get_optimized_context(max_tokens)` - Get token-optimized context
- `estimate_token_usage(text)` - Estimate token count for planning

### Enterprise Auto-Processing
- `auto_process_conversation(content, interaction_type)` - Extract memories and tasks automatically
- `decompose_task(prompt)` - Break complex tasks into subtasks

### Project Convention Tools
- `auto_learn_project_conventions(project_path)` - Automatically detect and learn project patterns
- `get_project_conventions_summary()` - Get formatted summary of learned conventions
- `suggest_correct_command(user_command)` - Suggest project-appropriate command corrections
- `remember_project_pattern(pattern_type, pattern, description)` - Manually store project patterns
- `update_memory_context()` - Refresh memory context with latest project conventions

### System Management Tools
- `health_check()` - Check server health and connectivity
- `get_performance_stats()` - Get detailed performance metrics
- `cleanup_old_data(days_old)` - Clean up old memories and tasks
- `optimize_memories()` - Remove duplicates and optimize storage
- `get_database_stats()` - Get comprehensive database statistics

## 🏗️ Project Convention Learning

The Enhanced MCP Memory Server automatically learns and remembers project-specific conventions to prevent AI assistants from suggesting incorrect commands or approaches:

### Automatic Detection
- **Operating System**: Windows vs Unix, preferred shell and commands
- **Project Type**: Node.js, Python, Rust, Go, Java, MCP servers, FastAPI, Django
- **Development Tools**: IDEs, linters, formatters, CI/CD configurations
- **Package Management**: npm, yarn, pip, poetry, cargo, go modules
- **Build Systems**: Vite, Webpack, Make, batch scripts, shell scripts

### Smart Command Suggestions
```bash
# Instead of generic commands, suggests project-specific ones:
User types: "node server.js"
AI suggests: "Use 'npm run dev' instead for this project"

User types: "python main.py" 
AI suggests: "Use 'uvicorn main:app --reload' for this FastAPI project"
```

### Windows Optimization
- Automatically detects Windows environment
- Uses `cmd.exe` and Windows-appropriate path separators
- Suggests Windows-compatible commands (e.g., `dir` instead of `ls`)
- Handles Windows-specific Python and Node.js patterns

### Memory Integration
All learned conventions are stored as high-importance memories that:
- Appear in AI context for every interaction
- Persist across sessions and project switches
- Include environment warnings and project-specific guidance
- Prevent repeated incorrect command suggestions

## 🔧 Configuration Options

Configure via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MAX_MEMORY_ITEMS` | `1000` | Maximum memories per project |
| `MAX_CONTEXT_TOKENS` | `8000` | Token threshold for auto-compression |
| `CLEANUP_INTERVAL_HOURS` | `24` | Auto-cleanup interval |
| `ENABLE_AUTO_CLEANUP` | `true` | Enable automatic cleanup |
| `MAX_CONCURRENT_REQUESTS` | `5` | Max concurrent requests |
| `REQUEST_TIMEOUT` | `30` | Request timeout in seconds |

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Run all tests including new sequential thinking and convention tests
python tests\test_enhanced_features.py
python tests\test_new_project_system.py
python tests\test_project_tools.py
python tests\test_sequential_thinking.py
python tests\test_project_conventions.py

# Or run comprehensive test runner
python run_tests.py
```

The test suite validates:
- ✅ Sequential thinking chains and token optimization
- ✅ Context compression achieving 30-70% reduction
- ✅ Project convention learning and persistence
- ✅ Memory storage and retrieval
- ✅ Task creation and management
- ✅ Performance monitoring and health checks
- ✅ Windows-specific command detection
- ✅ MCP protocol compliance

# Test MCP protocol
python test_mcp_protocol.py

# Run complete test suite
python run_tests.py
```

## 📊 Performance & Monitoring

The server includes built-in performance tracking:

- **Response time monitoring** for all tools
- **Success rate tracking** with error counts
- **Memory usage statistics**
- **Database performance metrics**
- **Automatic health checks**

Access via the `get_performance_stats()` and `health_check()` tools.

## 🗄️ Database

- **SQLite** for reliable, file-based storage
- **Automatic schema migrations** for updates
- **Comprehensive indexing** for fast queries
- **Built-in backup and optimization** tools
- **Cross-platform compatibility**

Default location: `./data/mcp_memory.db`

## 🔍 Semantic Search

Powered by sentence-transformers for intelligent memory retrieval:

- **Natural language queries** - "Find memories about database optimization"
- **Similarity-based matching** using embeddings
- **Configurable similarity thresholds**
- **Automatic model downloading** (~90MB on first run)

## 🧠 Sequential Thinking

Enterprise-grade structured reasoning system:

- **5-stage thinking process**: Analysis → Planning → Execution → Validation → Reflection
- **Token optimization**: Real-time estimation and compression (30-70% reduction)
- **Context continuity**: Intelligent session handoffs with preserved context
- **Auto-extraction**: Automatically identifies key points, decisions, and action items
- **Performance tracking**: Monitor reasoning chains and optimization metrics

## 💼 Enterprise Token Management

Advanced context optimization for high-scale deployments:

- **Smart compression**: Pattern-based extraction preserves essential information
- **Token estimation**: Real-time calculation for planning and budgeting
- **Context summarization**: Automatic conversion of conversations to actionable summaries
- **Session consolidation**: Seamless handoffs between conversation sessions
- **Performance analytics**: Detailed metrics on compression ratios and response times

## 📝 Logging

Comprehensive logging system:

- **Daily log rotation** in `./logs/` directory
- **Structured logging** with timestamps and levels
- **Performance tracking** integrated
- **Error tracking** with stack traces

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/cbunting99/enhanced-mcp-memory/issues)
- **Documentation**: [README](https://github.com/cbunting99/enhanced-mcp-memory#readme)
- **Discussions**: [GitHub Discussions](https://github.com/cbunting99/enhanced-mcp-memory/discussions)

## 🏷️ Version History

- **v1.2.0** - Enhanced MCP server with performance monitoring and health checks
- **v1.1.0** - Added semantic search and knowledge graph features
- **v1.0.0** - Initial release with basic memory and task management