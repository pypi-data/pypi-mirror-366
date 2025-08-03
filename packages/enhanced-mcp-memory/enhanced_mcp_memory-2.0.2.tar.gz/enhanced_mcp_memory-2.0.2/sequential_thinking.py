"""
Sequential Thinking Engine for Enhanced MCP Memory Server
Provides structured reasoning chains, context consolidation, and token optimization

Copyright 2025 Chris Bunting.
"""

import json
import logging
import hashlib
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import re

class ThinkingStage(Enum):
    """Stages of sequential thinking process"""
    ANALYSIS = "analysis"
    PLANNING = "planning"
    EXECUTION = "execution"
    VALIDATION = "validation"
    REFLECTION = "reflection"

@dataclass
class ThinkingStep:
    """Individual step in the thinking process"""
    id: str
    stage: ThinkingStage
    title: str
    content: str
    reasoning: str
    confidence: float
    dependencies: List[str]
    outputs: List[str]
    timestamp: datetime
    token_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['stage'] = self.stage.value
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class ThinkingChain:
    """Complete reasoning chain with metadata"""
    id: str
    project_id: str
    session_id: str
    objective: str
    steps: List[ThinkingStep]
    status: str  # 'active', 'completed', 'paused', 'archived'
    created_at: datetime
    updated_at: datetime
    total_tokens: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['steps'] = [step.to_dict() for step in self.steps]
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

@dataclass
class ContextSummary:
    """Compressed context summary for token optimization"""
    id: str
    project_id: str
    session_id: str
    original_token_count: int
    compressed_token_count: int
    compression_ratio: float
    key_points: List[str]
    decisions_made: List[str]
    pending_actions: List[str]
    context_hash: str
    created_at: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data

class SequentialThinkingEngine:
    """
    Enterprise-grade sequential thinking and context management system
    """
    
    def __init__(self, db_manager, memory_manager):
        self.db = db_manager
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(__name__)
        
        # Token counting patterns (approximate)
        self.token_patterns = {
            'word': 0.75,  # Average tokens per word
            'char': 0.25,  # Average tokens per character
        }
        
        # Context compression thresholds
        self.max_context_tokens = 8000  # Maximum context before compression
        self.target_compression_ratio = 0.3  # Target 30% of original size
        
        self._ensure_thinking_tables()
    
    def _ensure_thinking_tables(self):
        """Create tables for sequential thinking if they don't exist"""
        cursor = self.db.connection.cursor()
        
        # Thinking chains table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS thinking_chains (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            session_id TEXT,
            objective TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_tokens INTEGER DEFAULT 0,
            metadata TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """)
        
        # Thinking steps table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS thinking_steps (
            id TEXT PRIMARY KEY,
            chain_id TEXT,
            stage TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            reasoning TEXT,
            confidence REAL DEFAULT 0.5,
            dependencies TEXT,  -- JSON array
            outputs TEXT,       -- JSON array
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            token_count INTEGER DEFAULT 0,
            FOREIGN KEY (chain_id) REFERENCES thinking_chains(id)
        )
        """)
        
        # Context summaries table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS context_summaries (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            session_id TEXT,
            original_token_count INTEGER,
            compressed_token_count INTEGER,
            compression_ratio REAL,
            key_points TEXT,      -- JSON array
            decisions_made TEXT,  -- JSON array
            pending_actions TEXT, -- JSON array
            context_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """)
        
        # Chat sessions table for conversation continuity
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            parent_session_id TEXT,  -- For session chains
            title TEXT,
            objective TEXT,
            status TEXT DEFAULT 'active',  -- 'active', 'completed', 'archived'
            token_count INTEGER DEFAULT 0,
            message_count INTEGER DEFAULT 0,
            summary TEXT,
            key_context TEXT,  -- JSON compressed context
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """)
        
        self.db.connection.commit()
    
    def estimate_token_count(self, text: str) -> int:
        """Estimate token count for text"""
        if not text:
            return 0
        
        # Simple estimation based on words and characters
        words = len(text.split())
        chars = len(text)
        
        # Use word-based estimation as primary, character-based as fallback
        token_estimate = max(
            int(words * self.token_patterns['word']),
            int(chars * self.token_patterns['char'])
        )
        
        return token_estimate
    
    def create_thinking_chain(self, objective: str, project_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Create a new sequential thinking chain"""
        if not project_id:
            project_id = self.memory_manager.current_project_id
        
        if not session_id:
            session_id = self.memory_manager.current_session_id
        
        chain_id = str(uuid.uuid4())
        now = datetime.now()
        
        cursor = self.db.connection.cursor()
        cursor.execute("""
        INSERT INTO thinking_chains (id, project_id, session_id, objective, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (chain_id, project_id, session_id, objective, now.isoformat(), now.isoformat()))
        
        self.db.connection.commit()
        
        self.logger.info(f"Created thinking chain: {objective[:50]}...")
        return chain_id
    
    def add_thinking_step(self, chain_id: str, stage: ThinkingStage, title: str, 
                         content: str, reasoning: str = "", confidence: float = 0.7,
                         dependencies: Optional[List[str]] = None, outputs: Optional[List[str]] = None) -> str:
        """Add a step to the thinking chain"""
        step_id = str(uuid.uuid4())
        token_count = self.estimate_token_count(f"{title} {content} {reasoning}")
        
        cursor = self.db.connection.cursor()
        cursor.execute("""
        INSERT INTO thinking_steps 
        (id, chain_id, stage, title, content, reasoning, confidence, dependencies, outputs, token_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            step_id, chain_id, stage.value, title, content, reasoning, confidence,
            json.dumps(dependencies or []), json.dumps(outputs or []), token_count
        ))
        
        # Update chain token count
        cursor.execute("""
        UPDATE thinking_chains 
        SET total_tokens = total_tokens + ?, updated_at = ?
        WHERE id = ?
        """, (token_count, datetime.now().isoformat(), chain_id))
        
        self.db.connection.commit()
        
        self.logger.info(f"Added thinking step: {stage.value} - {title}")
        return step_id
    
    def get_thinking_chain(self, chain_id: str) -> Optional[ThinkingChain]:
        """Retrieve a complete thinking chain"""
        cursor = self.db.connection.cursor()
        
        # Get chain metadata
        cursor.execute("""
        SELECT * FROM thinking_chains WHERE id = ?
        """, (chain_id,))
        chain_row = cursor.fetchone()
        
        if not chain_row:
            return None
        
        # Get all steps
        cursor.execute("""
        SELECT * FROM thinking_steps WHERE chain_id = ? ORDER BY timestamp
        """, (chain_id,))
        step_rows = cursor.fetchall()
        
        steps = []
        for row in step_rows:
            step = ThinkingStep(
                id=row['id'],
                stage=ThinkingStage(row['stage']),
                title=row['title'],
                content=row['content'],
                reasoning=row['reasoning'] or "",
                confidence=row['confidence'],
                dependencies=json.loads(row['dependencies'] or '[]'),
                outputs=json.loads(row['outputs'] or '[]'),
                timestamp=datetime.fromisoformat(row['timestamp']),
                token_count=row['token_count']
            )
            steps.append(step)
        
        chain = ThinkingChain(
            id=chain_row['id'],
            project_id=chain_row['project_id'],
            session_id=chain_row['session_id'],
            objective=chain_row['objective'],
            steps=steps,
            status=chain_row['status'],
            created_at=datetime.fromisoformat(chain_row['created_at']),
            updated_at=datetime.fromisoformat(chain_row['updated_at']),
            total_tokens=chain_row['total_tokens']
        )
        
        return chain
    
    def create_context_summary(self, content: str, key_points: Optional[List[str]] = None,
                             decisions: Optional[List[str]] = None, actions: Optional[List[str]] = None,
                             project_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Create a compressed context summary"""
        if not project_id:
            project_id = self.memory_manager.current_project_id
        
        if not session_id:
            session_id = self.memory_manager.current_session_id
        
        # Calculate token counts
        original_tokens = self.estimate_token_count(content)
        
        # Auto-extract if not provided
        if not key_points:
            key_points = self._extract_key_points(content)
        if not decisions:
            decisions = self._extract_decisions(content)
        if not actions:
            actions = self._extract_actions(content)
        
        # Calculate compressed size
        compressed_content = {
            'key_points': key_points,
            'decisions_made': decisions,
            'pending_actions': actions
        }
        compressed_tokens = self.estimate_token_count(json.dumps(compressed_content))
        compression_ratio = compressed_tokens / max(original_tokens, 1)
        
        # Generate content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        summary_id = str(uuid.uuid4())
        cursor = self.db.connection.cursor()
        cursor.execute("""
        INSERT INTO context_summaries 
        (id, project_id, session_id, original_token_count, compressed_token_count, 
         compression_ratio, key_points, decisions_made, pending_actions, context_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            summary_id, project_id, session_id, original_tokens, compressed_tokens,
            compression_ratio, json.dumps(key_points), json.dumps(decisions), 
            json.dumps(actions), content_hash
        ))
        
        self.db.connection.commit()
        
        self.logger.info(f"Created context summary: {compression_ratio:.2%} compression")
        return summary_id
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content using pattern matching"""
        key_points = []
        
        # Look for bullet points, numbered lists, or key phrases
        patterns = [
            r'^\s*[-*+]\s+(.+)$',  # Bullet points
            r'^\s*\d+\.\s+(.+)$',  # Numbered lists
            r'(?:Key|Important|Note|TODO|FIXME):\s*(.+)$',  # Key phrases
            r'## (.+)$',  # Headers
        ]
        
        lines = content.split('\n')
        for line in lines:
            for pattern in patterns:
                match = re.search(pattern, line, re.MULTILINE | re.IGNORECASE)
                if match:
                    point = match.group(1).strip()
                    if len(point) > 10 and point not in key_points:
                        key_points.append(point)
        
        # Limit to most important points
        return key_points[:10]
    
    def _extract_decisions(self, content: str) -> List[str]:
        """Extract decisions made from content"""
        decisions = []
        
        decision_patterns = [
            r'(?:decided|chosen|selected|agreed):\s*(.+)$',
            r'(?:decision|choice|conclusion):\s*(.+)$',
            r'(?:will|shall|must)\s+(.+)$',
        ]
        
        lines = content.split('\n')
        for line in lines:
            for pattern in decision_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    decision = match.group(1).strip()
                    if len(decision) > 10 and decision not in decisions:
                        decisions.append(decision)
        
        return decisions[:5]
    
    def _extract_actions(self, content: str) -> List[str]:
        """Extract pending actions from content"""
        actions = []
        
        action_patterns = [
            r'(?:TODO|FIXME|ACTION|NEXT):\s*(.+)$',
            r'(?:need to|should|must)\s+(.+)$',
            r'(?:implement|create|build|add|fix)\s+(.+)$',
        ]
        
        lines = content.split('\n')
        for line in lines:
            for pattern in action_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    action = match.group(1).strip()
                    if len(action) > 10 and action not in actions:
                        actions.append(action)
        
        return actions[:8]
    
    def create_chat_session(self, title: str, objective: str = "", 
                           parent_session_id: Optional[str] = None) -> str:
        """Create a new chat session for conversation continuity"""
        session_id = str(uuid.uuid4())
        project_id = self.memory_manager.current_project_id
        
        cursor = self.db.connection.cursor()
        cursor.execute("""
        INSERT INTO chat_sessions 
        (id, project_id, parent_session_id, title, objective)
        VALUES (?, ?, ?, ?, ?)
        """, (session_id, project_id, parent_session_id, title, objective))
        
        self.db.connection.commit()
        
        self.logger.info(f"Created chat session: {title}")
        return session_id
    
    def consolidate_chat_session(self, session_id: str) -> Dict[str, Any]:
        """Consolidate a chat session into a summary for continuation"""
        # Get all memories and tasks for this session
        cursor = self.db.connection.cursor()
        
        # Get session info
        cursor.execute("""
        SELECT * FROM chat_sessions WHERE id = ?
        """, (session_id,))
        session = cursor.fetchone()
        
        if not session:
            raise ValueError(f"Chat session {session_id} not found")
        
        # Get related memories
        cursor.execute("""
        SELECT * FROM memories 
        WHERE project_id = ? AND created_at >= ?
        ORDER BY importance_score DESC, created_at DESC
        LIMIT 20
        """, (session['project_id'], session['created_at']))
        memories = cursor.fetchall()
        
        # Get related tasks
        cursor.execute("""
        SELECT * FROM tasks 
        WHERE project_id = ? AND created_at >= ?
        ORDER BY priority DESC, created_at DESC
        LIMIT 10
        """, (session['project_id'], session['created_at']))
        tasks = cursor.fetchall()
        
        # Create comprehensive summary
        content_parts = []
        
        # Session context
        content_parts.append(f"Session: {session['title']}")
        if session['objective']:
            content_parts.append(f"Objective: {session['objective']}")
        
        # Key memories
        if memories:
            content_parts.append("Key Context:")
            for memory in memories[:10]:
                content_parts.append(f"- [{memory['type']}] {memory['title']}")
        
        # Important tasks
        if tasks:
            content_parts.append("Tasks:")
            for task in tasks:
                content_parts.append(f"- [{task['status']}] {task['title']} ({task['priority']})")
        
        full_content = "\n".join(content_parts)
        
        # Create context summary
        summary_id = self.create_context_summary(
            content=full_content,
            project_id=session['project_id'],
            session_id=session_id
        )
        
        # Get the created summary
        cursor.execute("""
        SELECT * FROM context_summaries WHERE id = ?
        """, (summary_id,))
        summary_row = cursor.fetchone()
        
        # Update session with summary
        cursor.execute("""
        UPDATE chat_sessions 
        SET status = 'completed', key_context = ?, summary = ?, updated_at = ?
        WHERE id = ?
        """, (
            json.dumps({
                'key_points': json.loads(summary_row['key_points']),
                'decisions': json.loads(summary_row['decisions_made']),
                'actions': json.loads(summary_row['pending_actions'])
            }),
            f"Session completed with {len(memories)} memories and {len(tasks)} tasks",
            datetime.now().isoformat(),
            session_id
        ))
        
        self.db.connection.commit()
        
        return {
            'session_id': session_id,
            'summary_id': summary_id,
            'compression_ratio': summary_row['compression_ratio'],
            'original_tokens': summary_row['original_token_count'],
            'compressed_tokens': summary_row['compressed_token_count'],
            'key_context': json.loads(summary_row['key_points']),
            'decisions_made': json.loads(summary_row['decisions_made']),
            'pending_actions': json.loads(summary_row['pending_actions'])
        }
    
    def get_session_continuation_context(self, session_id: str) -> str:
        """Get optimized context for continuing from a previous session"""
        cursor = self.db.connection.cursor()
        
        cursor.execute("""
        SELECT * FROM chat_sessions WHERE id = ?
        """, (session_id,))
        session = cursor.fetchone()
        
        if not session or not session['key_context']:
            return "No continuation context available"
        
        key_context = json.loads(session['key_context'])
        
        context_parts = [
            f"## Continuing from: {session['title']}",
            f"Objective: {session['objective']}" if session['objective'] else "",
            "",
            "### Key Context:",
        ]
        
        for point in key_context.get('key_points', [])[:5]:
            context_parts.append(f"- {point}")
        
        if key_context.get('decisions'):
            context_parts.extend([
                "",
                "### Decisions Made:",
            ])
            for decision in key_context['decisions'][:3]:
                context_parts.append(f"- {decision}")
        
        if key_context.get('actions'):
            context_parts.extend([
                "",
                "### Pending Actions:",
            ])
            for action in key_context['actions'][:5]:
                context_parts.append(f"- {action}")
        
        return "\n".join(filter(None, context_parts))
    
    def get_thinking_chains_summary(self, project_id: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """Get summary of recent thinking chains"""
        if not project_id:
            project_id = self.memory_manager.current_project_id
        
        cursor = self.db.connection.cursor()
        cursor.execute("""
        SELECT tc.*, COUNT(ts.id) as step_count
        FROM thinking_chains tc
        LEFT JOIN thinking_steps ts ON tc.id = ts.chain_id
        WHERE tc.project_id = ?
        GROUP BY tc.id
        ORDER BY tc.updated_at DESC
        LIMIT ?
        """, (project_id, limit))
        
        chains = []
        for row in cursor.fetchall():
            chains.append({
                'id': row['id'],
                'objective': row['objective'],
                'status': row['status'],
                'step_count': row['step_count'],
                'total_tokens': row['total_tokens'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        return chains
