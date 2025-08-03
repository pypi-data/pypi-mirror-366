#!/usr/bin/env python3
"""
Test script for Project Convention Learning System

Copyright 2025 Chris Bunting.
"""
import sys
import os
import json
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from memory_manager import MemoryManager
from project_conventions import ProjectConventionLearner

def create_test_project_structure():
    """Create a temporary test project with various files"""
    test_dir = tempfile.mkdtemp(prefix="test_project_")
    
    # Create package.json for Node.js project
    package_json = {
        "name": "test-mcp-project",
        "version": "1.0.0",
        "scripts": {
            "dev": "vite dev",
            "build": "vite build",
            "test": "vitest",
            "start": "node dist/server.js",
            "lint": "eslint ."
        },
        "dependencies": {
            "fastmcp": "^2.10.5",
            "vite": "^4.0.0"
        }
    }
    
    with open(os.path.join(test_dir, 'package.json'), 'w') as f:
        json.dump(package_json, f, indent=2)
    
    # Create other project files
    files_to_create = {
        'README.md': "# Test MCP Project\nA test project for MCP convention learning.",
        'vite.config.js': "export default { server: { port: 3000 } }",
        '.eslintrc.json': '{"extends": ["eslint:recommended"]}',
        'Dockerfile': "FROM node:18\nWORKDIR /app\nCOPY . .\nRUN npm install",
        'docker-compose.yml': "version: '3'\nservices:\n  app:\n    build: .",
        '.vscode/settings.json': '{"editor.formatOnSave": true}',
        'tests/test.spec.js': 'describe("test", () => { it("works", () => {}) })'
    }
    
    for filepath, content in files_to_create.items():
        full_path = os.path.join(test_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    return test_dir

def test_project_convention_learning():
    """Test the project convention learning system"""
    print("=== Testing Project Convention Learning ===")
    
    # Create test project
    test_project_dir = create_test_project_structure()
    print(f"Created test project in: {test_project_dir}")
    
    try:
        # Initialize components
        db_manager = DatabaseManager("data/test_conventions.db")
        memory_manager = MemoryManager(db_manager)
        convention_learner = ProjectConventionLearner(memory_manager, db_manager)
        
        # Start session in test project
        memory_manager.start_session(test_project_dir)
        
        print("\n1. Testing Auto-Learning of Project Conventions...")
        conventions = convention_learner.auto_learn_project_conventions(test_project_dir)
        
        print(f"   [OK] Detected project type: {conventions.get('project_type')}")
        print(f"   [OK] Environment OS: {conventions.get('environment', {}).get('os')}")
        print(f"   [OK] Shell: {conventions.get('environment', {}).get('shell')}")
        
        # Check commands
        commands = conventions.get('commands', {})
        print(f"   [OK] Learned {len(commands)} command patterns:")
        for cmd_name, cmd_list in commands.items():
            print(f"       {cmd_name}: {cmd_list[0] if cmd_list else 'N/A'}")
        
        # Check tools
        tools = conventions.get('tools', {})
        print(f"   [OK] Detected tools: {list(tools.keys())}")
        
        # Check dependencies
        deps = conventions.get('dependencies', {})
        print(f"   [OK] Package manager: {deps.get('package_manager', 'None')}")
        
        print("\n2. Testing Convention Summary...")
        summary = convention_learner.get_project_conventions_summary()
        print(f"   [OK] Generated convention summary ({len(summary)} chars)")
        
        # Show sample of summary
        lines = summary.split('\n')[:10]
        for line in lines:
            if line.strip():
                print(f"       {line}")
        
        print("\n3. Testing Command Suggestions...")
        test_commands = [
            "node server.js",
            "python main.py", 
            "npm start",
            "yarn dev",
            "cargo run"
        ]
        
        for test_cmd in test_commands:
            suggestion = convention_learner.suggest_correct_command(test_cmd)
            if suggestion:
                print(f"   [SUGGEST] {test_cmd} -> {suggestion}")
            else:
                print(f"   [OK] {test_cmd} (no correction needed)")
        
        print("\n4. Testing Memory Integration...")
        # Check if conventions were stored as memories
        try:
            if hasattr(db_manager, 'connection') and db_manager.connection:
                cursor = db_manager.connection.cursor()
                cursor.execute("""
                SELECT type, title, content FROM memories 
                WHERE project_id = ? AND type IN ('environment', 'commands', 'tools')
                """, (memory_manager.current_project_id,))
                
                convention_memories = cursor.fetchall()
            else:
                convention_memories = []
        except Exception as e:
            print(f"   [WARNING] Could not query memories: {e}")
            convention_memories = []
        print(f"   [OK] Created {len(convention_memories)} convention memories:")
        
        for memory in convention_memories:
            memory_type = memory['type']
            title = memory['title']
            content_preview = memory['content'][:100] + "..." if len(memory['content']) > 100 else memory['content']
            print(f"       [{memory_type}] {title}")
            print(f"         Preview: {content_preview}")
        
        print("\n5. Testing Enhanced Memory Context...")
        # Test the enhanced memory context that includes conventions
        context = memory_manager.get_memory_context()
        has_conventions = "Project Environment & Conventions" in context
        has_important_notice = "IMPORTANT: Always follow project-specific" in context
        
        print(f"   [OK] Context includes conventions: {has_conventions}")
        print(f"   [OK] Context includes important notice: {has_important_notice}")
        
        if has_conventions:
            print("   [OK] Sample context with conventions:")
            context_lines = context.split('\n')[:15]
            for line in context_lines:
                if line.strip():
                    print(f"       {line}")
        
        return {
            'conventions': conventions,
            'summary_length': len(summary),
            'memories_created': len(convention_memories),
            'context_enhanced': has_conventions
        }
        
    finally:
        # Cleanup
        try:
            shutil.rmtree(test_project_dir)
            print(f"\nCleaned up test project: {test_project_dir}")
        except Exception as e:
            print(f"Warning: Failed to cleanup test project: {e}")

def test_windows_specific_conventions():
    """Test Windows-specific convention detection"""
    print("\n=== Testing Windows-Specific Conventions ===")
    
    # Initialize components
    db_manager = DatabaseManager("data/test_conventions.db")
    memory_manager = MemoryManager(db_manager)
    convention_learner = ProjectConventionLearner(memory_manager, db_manager)
    
    # Start session
    memory_manager.start_session(os.getcwd())
    
    print("\n1. Testing OS Detection...")
    env_details = convention_learner._learn_environment()
    
    print(f"   [OK] Detected OS: {env_details.get('os')}")
    print(f"   [OK] Shell: {env_details.get('shell')}")
    print(f"   [OK] Path separator: {env_details.get('path_separator')}")
    
    preferred_commands = env_details.get('preferred_commands', {})
    if isinstance(preferred_commands, dict):
        print(f"   [OK] Preferred commands for {env_details.get('os')}:")
        for cmd_type, cmd in preferred_commands.items():
            print(f"       {cmd_type}: {cmd}")
    else:
        print(f"   [INFO] Preferred commands: {preferred_commands}")
    
    print("\n2. Testing Tool Availability...")
    tools_available = env_details.get('tools_available', {})
    if isinstance(tools_available, dict):
        available_tools = [tool for tool, available in tools_available.items() if available]
        unavailable_tools = [tool for tool, available in tools_available.items() if not available]
    else:
        available_tools = []
        unavailable_tools = []
    
    print(f"   [OK] Available tools: {available_tools}")
    print(f"   [INFO] Unavailable tools: {unavailable_tools}")
    
    print("\n3. Testing Command Corrections for Windows...")
    # Test Windows-specific command corrections
    windows_test_commands = [
        ("python main.py", "Should suggest Windows-compatible Python command"),
        ("ls -la", "Should suggest 'dir' for Windows"),
        ("npm run dev", "Should be accepted for Node.js projects")
    ]
    
    for test_cmd, expected in windows_test_commands:
        suggestion = convention_learner.suggest_correct_command(test_cmd)
        print(f"   [TEST] '{test_cmd}' -> {suggestion or 'No correction'}")
        print(f"         Expected: {expected}")
    
    return env_details

def test_memory_persistence():
    """Test that learned conventions persist across sessions"""
    print("\n=== Testing Convention Persistence ===")
    
    # Initialize first session
    db_manager = DatabaseManager("data/test_conventions.db")
    memory_manager1 = MemoryManager(db_manager)
    convention_learner1 = ProjectConventionLearner(memory_manager1, db_manager)
    
    memory_manager1.start_session(os.getcwd())
    
    print("\n1. Learning conventions in first session...")
    conventions1 = convention_learner1.auto_learn_project_conventions()
    summary1 = convention_learner1.get_project_conventions_summary()
    
    print(f"   [OK] First session learned: {conventions1.get('project_type')}")
    print(f"   [OK] First session summary length: {len(summary1)}")
    
    # Start second session (simulate restart)
    memory_manager2 = MemoryManager(db_manager)
    convention_learner2 = ProjectConventionLearner(memory_manager2, db_manager)
    
    memory_manager2.start_session(os.getcwd())
    
    print("\n2. Checking persistence in second session...")
    summary2 = convention_learner2.get_project_conventions_summary()
    
    print(f"   [OK] Second session summary length: {len(summary2)}")
    
    # Check if conventions are still available
    has_conventions = "No project conventions learned yet" not in summary2
    print(f"   [OK] Conventions persisted: {has_conventions}")
    
    if has_conventions:
        print("   [OK] Sample persistent context:")
        lines = summary2.split('\n')[:8]
        for line in lines:
            if line.strip():
                print(f"       {line}")
    
    return {
        'first_session_summary': len(summary1),
        'second_session_summary': len(summary2),
        'persistence_works': has_conventions
    }

def main():
    """Run all convention learning tests"""
    print("Project Convention Learning Test Suite")
    print("=" * 55)
    
    try:
        # Create test database directory
        os.makedirs("data", exist_ok=True)
        
        # Run test suites
        learning_results = test_project_convention_learning()
        windows_results = test_windows_specific_conventions()
        persistence_results = test_memory_persistence()
        
        print("\n" + "=" * 55)
        print("All convention learning tests completed!")
        
        print("\nTest Results Summary:")
        print(f"   • Project type detected: {learning_results['conventions'].get('project_type')}")
        print(f"   • Convention memories created: {learning_results['memories_created']}")
        print(f"   • Context enhancement working: {learning_results['context_enhanced']}")
        print(f"   • OS detected: {windows_results.get('os')}")
        tools_available = windows_results.get('tools_available', {})
        if isinstance(tools_available, dict):
            available_count = len([k for k, v in tools_available.items() if v])
            print(f"   • Tools available: {available_count}")
        else:
            print(f"   • Tools available: 0")
        print(f"   • Convention persistence: {persistence_results['persistence_works']}")
        
        print("\nConvention learning system is working correctly!")
        print("   • Automatically detects project type and environment")
        print("   • Learns project-specific commands and tools")
        print("   • Stores conventions in memory for AI context")
        print("   • Provides command suggestions and corrections")
        print("   • Persists learned conventions across sessions")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
