"""
Enhanced MCP Server for Memory Management
Automatically manages memories, knowledge graphs, and tasks with improved features
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from functools import wraps
from collections import defaultdict

# Import FastMCP components
try:
    from fastmcp import FastMCP, Context
except ImportError as e:
    logging.error("FastMCP not installed. Install with: pip install fastmcp")
    raise e

from database import DatabaseManager
from memory_manager import MemoryManager
from sequential_thinking import SequentialThinkingEngine, ThinkingStage
from project_conventions import ProjectConventionLearner

# Configure logging
base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
log_dir = base_dir / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"mcp_memory_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== SERVER CONFIGURATION ====================
class ServerConfig:
    def __init__(self):
        self.max_memory_items = int(os.getenv('MAX_MEMORY_ITEMS', '1000'))
        self.cleanup_interval = int(os.getenv('CLEANUP_INTERVAL_HOURS', '24'))
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.enable_auto_cleanup = os.getenv('ENABLE_AUTO_CLEANUP', 'true').lower() == 'true'
        self.max_concurrent_requests = int(os.getenv('MAX_CONCURRENT_REQUESTS', '5'))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))

config = ServerConfig()

# ==================== PERFORMANCE TRACKING ====================
class PerformanceTracker:
    def __init__(self):
        self.call_times = defaultdict(list)
        self.call_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.start_time = datetime.now()
    
    def track_call(self, tool_name: str, duration: float, success: bool = True):
        self.call_times[tool_name].append(duration)
        self.call_counts[tool_name] += 1
        if not success:
            self.error_counts[tool_name] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        stats = {}
        for tool_name, times in self.call_times.items():
            if times:
                stats[tool_name] = {
                    "call_count": self.call_counts[tool_name],
                    "error_count": self.error_counts[tool_name],
                    "avg_time_ms": round(sum(times) / len(times) * 1000, 2),
                    "max_time_ms": round(max(times) * 1000, 2),
                    "min_time_ms": round(min(times) * 1000, 2),
                    "success_rate": round((self.call_counts[tool_name] - self.error_counts[tool_name]) / self.call_counts[tool_name] * 100, 2)
                }
        
        uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        stats["server_uptime_hours"] = round(uptime_seconds / 3600, 2)
        return stats

perf_tracker = PerformanceTracker()

# Performance tracking decorator
def track_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            raise
        finally:
            duration = time.time() - start_time
            perf_tracker.track_call(func.__name__, duration, success)
    return wrapper

# Initialize MCP server
mcp = FastMCP("Enhanced_MCP_Memory")

# Initialize database and memory manager
data_dir = base_dir / "data"
data_dir.mkdir(exist_ok=True)
db_path = data_dir / "mcp_memory.db"

db_manager = DatabaseManager(str(db_path))
memory_manager = MemoryManager(db_manager)
thinking_engine = SequentialThinkingEngine(db_manager, memory_manager)
convention_learner = ProjectConventionLearner(memory_manager, db_manager)

# Load environment variables
load_dotenv()

# ==================== ENHANCED TOOLS ====================

@mcp.tool()
@track_performance
def health_check() -> str:
    """Check server health and database connectivity"""
    try:
        # Test database
        db_manager.connection.execute("SELECT 1").fetchone()
        
        # Test memory manager
        session_count = 1 if memory_manager.current_project_id else 0
        
        # Get basic stats
        stats = db_manager.get_database_stats()
        
        health_info = {
            "status": "healthy",
            "database": "connected",
            "database_size_mb": round(stats.get('database_size_bytes', 0) / (1024*1024), 2),
            "active_sessions": session_count,
            "current_project": memory_manager.current_project_id[:8] + "..." if memory_manager.current_project_id else None,
            "total_projects": stats.get('projects_count', 0),
            "total_memories": stats.get('memories_count', 0),
            "total_tasks": stats.get('tasks_count', 0),
            "server_uptime_hours": perf_tracker.get_stats().get("server_uptime_hours", 0),
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(health_info, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
@track_performance
def get_performance_stats() -> str:
    """Get server performance statistics"""
    try:
        stats = perf_tracker.get_stats()
        return json.dumps(stats, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to get performance stats: {str(e)}"})

@mcp.tool()
@track_performance
def cleanup_old_data(days_old: int = 30) -> str:
    """Clean up old memories, logs, and completed tasks"""
    try:
        results = db_manager.cleanup_old_data(days_old)
        
        cleanup_summary = {
            "days_threshold": days_old,
            "memories_deleted": results.get("memories_deleted", 0),
            "tasks_deleted": results.get("tasks_deleted", 0),
            "notifications_deleted": results.get("notifications_deleted", 0),
            "cleanup_date": datetime.now().isoformat()
        }
        
        logger.info(f"Cleanup completed: {results}")
        return json.dumps(cleanup_summary, indent=2)
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return json.dumps({"error": f"Cleanup failed: {str(e)}"})

@mcp.tool()
@track_performance
def optimize_memories() -> str:
    """Analyze and optimize memory storage"""
    try:
        results = db_manager.optimize_memories()
        
        optimization_summary = {
            "duplicates_merged": results.get("duplicates_merged", 0),
            "orphaned_relationships_removed": results.get("orphaned_relationships", 0),
            "optimization_complete": True,
            "optimization_date": datetime.now().isoformat()
        }
        
        logger.info(f"Memory optimization completed: {results}")
        return json.dumps(optimization_summary, indent=2)
    except Exception as e:
        logger.error(f"Memory optimization failed: {e}")
        return json.dumps({"error": f"Memory optimization failed: {str(e)}"})

@mcp.tool()
@track_performance
def get_database_stats() -> str:
    """Get comprehensive database statistics"""
    try:
        stats = db_manager.get_database_stats()
        
        # Add calculated metrics
        if stats.get('memories_count', 0) > 0:
            stats['avg_memories_per_project'] = round(stats['memories_count'] / max(stats.get('projects_count', 1), 1), 2)
        if stats.get('tasks_count', 0) > 0:
            stats['avg_tasks_per_project'] = round(stats['tasks_count'] / max(stats.get('projects_count', 1), 1), 2)
            
        stats['database_size_mb'] = round(stats.get('database_size_bytes', 0) / (1024*1024), 2)
        stats['generated_at'] = datetime.now().isoformat()
        
        return json.dumps(stats, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to get database stats: {str(e)}"})

@mcp.tool()
@track_performance
def get_memory_context(query: str = "") -> str:
    """Get current memory context and task reminders for the AI"""
    try:
        context = memory_manager.get_memory_context(query)
        reminder = memory_manager.get_task_reminder()
        
        full_context = []
        if context:
            full_context.append(context)
        if reminder:
            full_context.append(reminder)
            
        return "\n\n".join(full_context) if full_context else "No context available"
    except Exception as e:
        logger.error(f"Error getting memory context: {e}")
        return f"Error retrieving context: {str(e)}"

@mcp.tool()
@track_performance
def create_task(title: str, description: str = "", priority: str = "medium", category: str = "feature") -> str:
    """Create a new task for the current project"""
    try:
        if not memory_manager.current_project_id:
            memory_manager.start_session()
            
        task_id = db_manager.add_task(
            project_id=memory_manager.current_project_id,
            title=title,
            description=description,
            priority=priority,
            category=category,
            metadata={'source': 'manual', 'created_by': 'ai_tool'}
        )
        
        logger.info(f"Created task: {title} [{priority}/{category}]")
        return f"✅ Task created: '{title}' (ID: {task_id[:8]}...)"
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return f"⚠️ Error creating task: {str(e)}"

@mcp.tool()
@track_performance
def get_tasks(status: str = None, limit: int = 20) -> str:
    """Get tasks for the current project"""
    try:
        if not memory_manager.current_project_id:
            return "No active project. Cannot retrieve tasks."
            
        tasks = db_manager.get_tasks(memory_manager.current_project_id, status, limit)
        
        results = []
        for task in tasks:
            results.append({
                'id': task['id'],
                'title': task['title'],
                'description': task['description'],
                'status': task['status'],
                'priority': task['priority'],
                'category': task['category'],
                'created_at': task['created_at']
            })
            
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return f"Error getting tasks: {str(e)}"

@mcp.tool()
@track_performance
def get_project_summary() -> str:
    """Get summary of the current project"""
    try:
        if not memory_manager.current_project_id:
            return "No active project."
            
        summary = db_manager.get_project_summary(memory_manager.current_project_id)
        return json.dumps(summary, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error getting project summary: {e}")
        return f"Error getting project summary: {str(e)}"

# ==================== SEQUENTIAL THINKING TOOLS ====================

@mcp.tool()
@track_performance
def start_thinking_chain(objective: str) -> str:
    """Start a new sequential thinking chain for complex problem solving"""
    try:
        if not memory_manager.current_project_id:
            memory_manager.start_session()
        
        chain_id = thinking_engine.create_thinking_chain(objective)
        
        # Add initial analysis step
        thinking_engine.add_thinking_step(
            chain_id=chain_id,
            stage=ThinkingStage.ANALYSIS,
            title="Problem Analysis",
            content=f"Starting analysis for: {objective}",
            reasoning="Initial step to understand the problem scope and requirements"
        )
        
        logger.info(f"Started thinking chain: {objective}")
        return json.dumps({
            "chain_id": chain_id,
            "objective": objective,
            "status": "started",
            "next_stage": "analysis"
        }, indent=2)
    except Exception as e:
        logger.error(f"Error starting thinking chain: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
@track_performance
def add_thinking_step(chain_id: str, stage: str, title: str, content: str, 
                     reasoning: str = "", confidence: float = 0.7) -> str:
    """Add a step to an existing thinking chain"""
    try:
        # Convert string stage to enum
        stage_enum = ThinkingStage(stage.lower())
        
        step_id = thinking_engine.add_thinking_step(
            chain_id=chain_id,
            stage=stage_enum,
            title=title,
            content=content,
            reasoning=reasoning,
            confidence=confidence
        )
        
        logger.info(f"Added thinking step: {stage} - {title}")
        return json.dumps({
            "step_id": step_id,
            "chain_id": chain_id,
            "stage": stage,
            "title": title,
            "confidence": confidence
        }, indent=2)
    except Exception as e:
        logger.error(f"Error adding thinking step: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
@track_performance
def get_thinking_chain(chain_id: str) -> str:
    """Retrieve a complete thinking chain with all steps"""
    try:
        chain = thinking_engine.get_thinking_chain(chain_id)
        if not chain:
            return json.dumps({"error": "Thinking chain not found"})
        
        return json.dumps(chain.to_dict(), indent=2)
    except Exception as e:
        logger.error(f"Error getting thinking chain: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
@track_performance  
def list_thinking_chains(limit: int = 10) -> str:
    """List recent thinking chains for the current project"""
    try:
        chains = thinking_engine.get_thinking_chains_summary(limit=limit)
        return json.dumps(chains, indent=2)
    except Exception as e:
        logger.error(f"Error listing thinking chains: {e}")
        return json.dumps({"error": str(e)})

# ==================== CONTEXT MANAGEMENT TOOLS ====================

@mcp.tool()
@track_performance
def create_context_summary(content: str, key_points: str = "", decisions: str = "", 
                          actions: str = "") -> str:
    """Create a compressed summary of context to save tokens"""
    try:
        # Parse comma-separated inputs
        key_points_list = [p.strip() for p in key_points.split(',') if p.strip()] if key_points else None
        decisions_list = [d.strip() for d in decisions.split(',') if d.strip()] if decisions else None
        actions_list = [a.strip() for a in actions.split(',') if a.strip()] if actions else None
        
        summary_id = thinking_engine.create_context_summary(
            content=content,
            key_points=key_points_list,
            decisions=decisions_list,
            actions=actions_list
        )
        
        # Get the created summary for response
        cursor = db_manager.connection.cursor()
        cursor.execute("SELECT * FROM context_summaries WHERE id = ?", (summary_id,))
        summary = cursor.fetchone()
        
        result = {
            "summary_id": summary_id,
            "original_tokens": summary['original_token_count'],
            "compressed_tokens": summary['compressed_token_count'],
            "compression_ratio": f"{summary['compression_ratio']:.2%}",
            "key_points": json.loads(summary['key_points']),
            "decisions_made": json.loads(summary['decisions_made']),
            "pending_actions": json.loads(summary['pending_actions'])
        }
        
        logger.info(f"Created context summary with {result['compression_ratio']} compression")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error creating context summary: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
@track_performance
def start_new_chat_session(title: str, objective: str = "", continue_from: str = "") -> str:
    """Start a new chat session, optionally continuing from a previous one"""
    try:
        # If continuing from previous session, get the context first
        continuation_context = ""
        if continue_from:
            continuation_context = thinking_engine.get_session_continuation_context(continue_from)
        
        session_id = thinking_engine.create_chat_session(
            title=title,
            objective=objective,
            parent_session_id=continue_from if continue_from else None
        )
        
        result = {
            "session_id": session_id,
            "title": title,
            "objective": objective,
            "continuation_context": continuation_context if continuation_context else None,
            "status": "started"
        }
        
        logger.info(f"Started new chat session: {title}")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error starting chat session: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
@track_performance
def consolidate_current_session() -> str:
    """Consolidate the current session into a summary for continuation"""
    try:
        if not memory_manager.current_session_id:
            return json.dumps({"error": "No active session to consolidate"})
        
        # Create a temporary chat session for the current MCP session
        temp_session_id = thinking_engine.create_chat_session(
            title=f"MCP Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            objective="Current MCP conversation session"
        )
        
        consolidation_result = thinking_engine.consolidate_chat_session(temp_session_id)
        
        logger.info(f"Consolidated session with {consolidation_result['compression_ratio']:.2%} compression")
        return json.dumps(consolidation_result, indent=2)
    except Exception as e:
        logger.error(f"Error consolidating session: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
@track_performance
def get_optimized_context(max_tokens: int = 4000) -> str:
    """Get optimized context that fits within token limits"""
    try:
        # Get current context
        current_context = memory_manager.get_memory_context()
        current_tokens = thinking_engine.estimate_token_count(current_context)
        
        if current_tokens <= max_tokens:
            return json.dumps({
                "context": current_context,
                "token_count": current_tokens,
                "optimization": "none_needed"
            }, indent=2)
        
        # Need to compress context
        summary_id = thinking_engine.create_context_summary(current_context)
        
        # Get the compressed summary
        cursor = db_manager.connection.cursor()
        cursor.execute("SELECT * FROM context_summaries WHERE id = ?", (summary_id,))
        summary = cursor.fetchone()
        
        # Build optimized context
        optimized_parts = []
        
        # Add key points
        key_points = json.loads(summary['key_points'])
        if key_points:
            optimized_parts.append("## Key Context:")
            for point in key_points[:8]:  # Limit to most important
                optimized_parts.append(f"- {point}")
        
        # Add decisions
        decisions = json.loads(summary['decisions_made'])
        if decisions:
            optimized_parts.append("\n## Decisions Made:")
            for decision in decisions[:5]:
                optimized_parts.append(f"- {decision}")
        
        # Add pending actions
        actions = json.loads(summary['pending_actions'])
        if actions:
            optimized_parts.append("\n## Pending Actions:")
            for action in actions[:6]:
                optimized_parts.append(f"- {action}")
        
        optimized_context = "\n".join(optimized_parts)
        optimized_tokens = thinking_engine.estimate_token_count(optimized_context)
        
        result = {
            "context": optimized_context,
            "token_count": optimized_tokens,
            "original_tokens": current_tokens,
            "compression_ratio": f"{optimized_tokens/current_tokens:.2%}",
            "optimization": "compressed",
            "summary_id": summary_id
        }
        
        logger.info(f"Optimized context: {result['compression_ratio']} compression")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error optimizing context: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
@track_performance
def estimate_token_usage(text: str) -> str:
    """Estimate token count for given text"""
    try:
        token_count = thinking_engine.estimate_token_count(text)
        word_count = len(text.split())
        char_count = len(text)
        
        result = {
            "text_length": char_count,
            "word_count": word_count,
            "estimated_tokens": token_count,
            "tokens_per_word": round(token_count / max(word_count, 1), 2),
            "tokens_per_char": round(token_count / max(char_count, 1), 3)
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error estimating tokens: {e}")
        return json.dumps({"error": str(e)})

# ==================== ENTERPRISE FEATURES ====================

@mcp.tool()
@track_performance
def auto_process_conversation(content: str, interaction_type: str = "conversation") -> str:
    """Automatically process conversation content to extract memories and tasks"""
    try:
        # Process the conversation content
        results = {
            "processed_content": content[:200] + "..." if len(content) > 200 else content,
            "interaction_type": interaction_type,
            "extracted_items": []
        }
        
        # Auto-extract and create memories
        if len(content) > 50:  # Only process substantial content
            memory_id = memory_manager.add_context_memory(
                content=content,
                memory_type="conversation",
                importance=0.6
            )
            results["extracted_items"].append({
                "type": "memory",
                "id": memory_id,
                "content": content[:100] + "..."
            })
        
        # Auto-extract tasks from content
        task_patterns = [
            r'(?:TODO|FIXME|ACTION|TASK):\s*(.+)$',
            r'(?:need to|should|must)\s+(.+)$',
            r'(?:implement|create|build|add|fix)\s+(.+)$',
        ]
        
        import re
        for pattern in task_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches[:3]:  # Limit to 3 auto-extracted tasks
                if len(match.strip()) > 10:
                    try:
                        if memory_manager.current_project_id:
                            task_id = db_manager.add_task(
                                project_id=memory_manager.current_project_id,
                                title=match.strip()[:100],
                                description=f"Auto-extracted from conversation",
                                priority="medium",
                                category="feature"
                            )
                            results["extracted_items"].append({
                                "type": "task",
                                "id": task_id,
                                "title": match.strip()[:100]
                            })
                    except Exception:
                        pass  # Skip if task creation fails
        
        logger.info(f"Auto-processed conversation: {len(results['extracted_items'])} items extracted")
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"Error auto-processing conversation: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
@track_performance
def decompose_task(prompt: str) -> str:
    """Decompose a complex prompt into parent task and subtasks"""
    try:
        if not memory_manager.current_project_id:
            memory_manager.start_session()
        
        # Create parent task
        parent_task_id = db_manager.add_task(
            project_id=memory_manager.current_project_id,
            title=prompt[:100],
            description=prompt,
            priority="high",
            category="feature"
        )
        
        # Simple decomposition - look for natural breakpoints
        subtasks = []
        
        # Pattern-based subtask extraction
        patterns = [
            "setup", "configuration", "implementation", "testing", "documentation"
        ]
        
        for i, pattern in enumerate(patterns):
            if pattern.lower() in prompt.lower() or i < 3:  # Always create basic subtasks
                subtask_titles = {
                    0: f"Setup and Planning for: {prompt[:50]}...",
                    1: f"Core Implementation: {prompt[:50]}...", 
                    2: f"Testing and Validation: {prompt[:50]}...",
                    3: f"Documentation: {prompt[:50]}...",
                    4: f"Final Integration: {prompt[:50]}..."
                }
                
                if i in subtask_titles:
                    subtask_id = db_manager.add_task(
                        project_id=memory_manager.current_project_id,
                        title=subtask_titles[i],
                        description=f"Subtask of: {prompt}",
                        priority="medium",
                        category="feature"
                    )
                    subtasks.append({
                        "id": subtask_id,
                        "title": subtask_titles[i],
                        "order": i + 1
                    })
        
        result = {
            "parent_task": {
                "id": parent_task_id,
                "title": prompt[:100],
                "description": prompt
            },
            "subtasks": subtasks,
            "total_tasks": len(subtasks) + 1
        }
        
        logger.info(f"Decomposed task into {len(subtasks)} subtasks")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error decomposing task: {e}")
        return json.dumps({"error": str(e)})

# ==================== PROJECT CONVENTION TOOLS ====================

@mcp.tool()
@track_performance
def auto_learn_project_conventions() -> str:
    """Automatically learn and remember project-specific conventions, commands, and environment details"""
    try:
        if not memory_manager.current_project_id:
            memory_manager.start_session()
        
        conventions = convention_learner.auto_learn_project_conventions()
        
        # Generate summary
        summary = {
            "project_type": conventions.get('project_type', 'unknown'),
            "environment": {
                "os": conventions.get('environment', {}).get('os'),
                "shell": conventions.get('environment', {}).get('shell'),
                "python_version": conventions.get('environment', {}).get('python_version')
            },
            "commands_learned": len(conventions.get('commands', {})),
            "tools_detected": list(conventions.get('tools', {}).keys()),
            "package_manager": conventions.get('dependencies', {}).get('package_manager'),
            "memories_created": 5  # Approximate number of memory entries created
        }
        
        logger.info(f"Learned project conventions: {conventions.get('project_type')}")
        return json.dumps(summary, indent=2)
    except Exception as e:
        logger.error(f"Error learning project conventions: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
@track_performance
def get_project_conventions() -> str:
    """Get current project conventions and environment details for AI context"""
    try:
        conventions_summary = convention_learner.get_project_conventions_summary()
        return conventions_summary
    except Exception as e:
        logger.error(f"Error getting project conventions: {e}")
        return f"Error getting project conventions: {str(e)}"

@mcp.tool()
@track_performance
def suggest_correct_command(user_command: str) -> str:
    """Suggest correct project-specific command based on learned conventions"""
    try:
        suggestion = convention_learner.suggest_correct_command(user_command)
        
        if suggestion:
            return json.dumps({
                "original_command": user_command,
                "suggestion": suggestion,
                "status": "correction_available"
            }, indent=2)
        else:
            return json.dumps({
                "original_command": user_command,
                "suggestion": "No specific correction found. Command appears acceptable for this project.",
                "status": "no_correction_needed"
            }, indent=2)
    except Exception as e:
        logger.error(f"Error suggesting command correction: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
@track_performance
def remember_project_pattern(pattern_type: str, pattern_name: str, pattern_content: str, 
                           importance: float = 0.8) -> str:
    """Manually remember a specific project pattern or convention"""
    try:
        if not memory_manager.current_project_id:
            memory_manager.start_session()
        
        # Create a structured memory for the pattern
        memory_content = f"""Project Pattern: {pattern_name}
Type: {pattern_type}

{pattern_content}

This is a project-specific pattern that should be followed consistently.
"""
        
        memory_id = memory_manager.add_context_memory(
            content=memory_content,
            memory_type="pattern",
            importance=importance,
            tags=[pattern_type, "pattern", "convention", pattern_name.lower().replace(' ', '-')]
        )
        
        logger.info(f"Remembered project pattern: {pattern_name}")
        return json.dumps({
            "memory_id": memory_id,
            "pattern_type": pattern_type,
            "pattern_name": pattern_name,
            "importance": importance,
            "status": "pattern_remembered"
        }, indent=2)
    except Exception as e:
        logger.error(f"Error remembering project pattern: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
@track_performance
def update_memory_context(query: str = "") -> str:
    """Enhanced memory context that includes project conventions and environment details"""
    try:
        # Get standard memory context
        standard_context = memory_manager.get_memory_context(query)
        
        # Get project conventions
        conventions_context = convention_learner.get_project_conventions_summary()
        
        # Combine contexts
        if conventions_context and "No project conventions" not in conventions_context:
            full_context = f"{standard_context}\n\n{conventions_context}"
        else:
            full_context = f"{standard_context}\n\n💡 Consider running auto_learn_project_conventions() to learn project-specific patterns."
        
        return full_context
    except Exception as e:
        logger.error(f"Error updating memory context: {e}")
        return f"Error updating memory context: {str(e)}"

# ==================== SERVER STARTUP ====================

def initialize_session():
    """Initialize session on server startup"""
    try:
        cwd = os.getcwd()
        memory_manager.start_session(cwd)
        
        # Auto-learn project conventions
        try:
            conventions = convention_learner.auto_learn_project_conventions()
            logger.info(f"Auto-learned conventions for project type: {conventions.get('project_type', 'unknown')}")
        except Exception as e:
            logger.warning(f"Failed to auto-learn project conventions: {e}")
        
        logger.info(f"Session initialized for: {cwd}")
    except Exception as e:
        logger.error(f"Failed to initialize session: {e}")

def main():
    """Main server entry point"""
    try:
        logger.info("🚀 Enhanced MCP Memory Server starting...")
        logger.info(f"📊 Configuration: {config.__dict__}")
        logger.info(f"💾 Database: {db_path}")
        
        # Initialize session
        initialize_session()
        logger.info(f"📁 Current project: {memory_manager.current_project_id}")
        
        # Run the FastMCP server
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        if db_manager:
            db_manager.close()
        logger.info("🛑 Enhanced MCP Memory Server stopped")

if __name__ == "__main__":
    main()