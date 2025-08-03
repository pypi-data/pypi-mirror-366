"""
Project Convention Learning System
Automatically captures and remembers project-specific patterns, commands, and environment details

Copyright 2025 Chris Bunting.
"""

import os
import json
import logging
import re
import platform
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime

class ProjectConventionLearner:
    """
    Learns and remembers project-specific conventions automatically
    """
    
    def __init__(self, memory_manager, db_manager):
        self.memory_manager = memory_manager
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Convention categories
        self.convention_types = {
            'commands': 'Project-specific commands and scripts',
            'environment': 'Operating system and runtime environment details',
            'tools': 'Development tools and workflows used',
            'patterns': 'Code patterns and architectural decisions',
            'deployment': 'Build and deployment procedures',
            'dependencies': 'Package managers and dependency handling',
            'testing': 'Testing frameworks and procedures'
        }
        
        # Command pattern mapping for different project types
        self.command_patterns = {
            'node_js': {
                'dev': ['npm run dev', 'npm start', 'yarn dev'],
                'build': ['npm run build', 'yarn build'],
                'test': ['npm test', 'yarn test'],
                'install': ['npm install', 'yarn install']
            },
            'python': {
                'run': ['python main.py', 'python app.py', 'uvicorn main:app'],
                'test': ['pytest', 'python -m pytest', 'python test.py'],
                'install': ['pip install -r requirements.txt', 'poetry install']
            },
            'rust': {
                'run': ['cargo run', 'cargo run --release'],
                'build': ['cargo build', 'cargo build --release'],
                'test': ['cargo test']
            },
            'go': {
                'run': ['go run main.go', 'go run .'],
                'build': ['go build', 'go build .'],
                'test': ['go test', 'go test ./...']
            }
        }
    
    def auto_learn_project_conventions(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """Automatically learn project conventions from files and environment"""
        if not project_path:
            project_path = os.getcwd()
        
        conventions = {}
        
        # Learn environment details
        conventions['environment'] = self._learn_environment()
        
        # Learn project type and commands
        conventions['project_type'] = self._detect_project_type(project_path)
        conventions['commands'] = self._learn_commands(project_path, conventions['project_type'])
        
        # Learn tools and dependencies
        conventions['tools'] = self._learn_tools(project_path)
        conventions['dependencies'] = self._learn_dependencies(project_path)
        
        # Learn deployment patterns
        conventions['deployment'] = self._learn_deployment_patterns(project_path)
        
        # Learn testing patterns
        conventions['testing'] = self._learn_testing_patterns(project_path)
        
        # Store learned conventions as memories
        self._store_conventions_as_memories(conventions)
        
        return conventions
    
    def _learn_environment(self) -> Dict[str, str]:
        """Learn operating system and environment details"""
        env_details = {
            'os': platform.system(),
            'os_version': platform.version(),
            'architecture': platform.machine(),
            'python_version': platform.python_version(),
            'shell': 'cmd.exe' if platform.system() == 'Windows' else 'bash',
            'path_separator': '\\' if platform.system() == 'Windows' else '/',
            'preferred_commands': self._get_os_preferred_commands()
        }
        
        # Check for specific tools
        tools_available = {}
        common_tools = ['node', 'npm', 'yarn', 'python', 'pip', 'cargo', 'go', 'git', 'docker']
        
        for tool in common_tools:
            try:
                import subprocess
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                tools_available[tool] = result.returncode == 0
            except:
                tools_available[tool] = False
        
        env_details['tools_available'] = tools_available
        return env_details
    
    def _get_os_preferred_commands(self) -> Dict[str, str]:
        """Get OS-specific preferred commands"""
        if platform.system() == 'Windows':
            return {
                'shell': 'cmd.exe',
                'python': 'python',
                'list_files': 'dir',
                'copy': 'copy',
                'move': 'move',
                'remove': 'del',
                'path_separator': '\\'
            }
        else:
            return {
                'shell': 'bash',
                'python': 'python3',
                'list_files': 'ls',
                'copy': 'cp',
                'move': 'mv',
                'remove': 'rm',
                'path_separator': '/'
            }
    
    def _detect_project_type(self, project_path: str) -> str:
        """Detect project type from files"""
        project_indicators = {
            'node_js': ['package.json', 'yarn.lock', 'npm-shrinkwrap.json'],
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
            'rust': ['Cargo.toml', 'Cargo.lock'],
            'go': ['go.mod', 'go.sum'],
            'java': ['pom.xml', 'build.gradle'],
            'csharp': ['.csproj', '.sln'],
            'mcp_server': ['mcp_server.py', 'mcp_server_enhanced.py'],
            'fastapi': ['main.py', 'app.py'],
            'django': ['manage.py', 'settings.py'],
            'flask': ['app.py', 'wsgi.py']
        }
        
        detected_types = []
        for project_type, indicators in project_indicators.items():
            for indicator in indicators:
                if os.path.exists(os.path.join(project_path, indicator)):
                    detected_types.append(project_type)
                    break
        
        # Return most specific type
        if 'mcp_server' in detected_types:
            return 'mcp_server'
        elif 'fastapi' in detected_types:
            return 'fastapi'
        elif 'django' in detected_types:
            return 'django'
        elif 'flask' in detected_types:
            return 'flask'
        elif detected_types:
            return detected_types[0]
        else:
            return 'unknown'
    
    def _learn_commands(self, project_path: str, project_type: str) -> Dict[str, List[str]]:
        """Learn project-specific commands"""
        commands = {}
        
        # Check package.json scripts for Node.js projects
        if project_type == 'node_js':
            package_json = os.path.join(project_path, 'package.json')
            if os.path.exists(package_json):
                try:
                    with open(package_json, 'r') as f:
                        data = json.load(f)
                        scripts = data.get('scripts', {})
                        for script_name, script_command in scripts.items():
                            commands[script_name] = [f'npm run {script_name}']
                except:
                    pass
        
        # Check for common command files
        command_files = {
            'Makefile': self._parse_makefile,
            'package.json': self._parse_package_json,
            'pyproject.toml': self._parse_pyproject_toml,
            'Cargo.toml': self._parse_cargo_toml
        }
        
        for filename, parser in command_files.items():
            filepath = os.path.join(project_path, filename)
            if os.path.exists(filepath):
                try:
                    file_commands = parser(filepath)
                    commands.update(file_commands)
                except Exception as e:
                    self.logger.warning(f"Failed to parse {filename}: {e}")
        
        # Add default commands based on project type
        if project_type in self.command_patterns:
            default_commands = self.command_patterns[project_type]
            for cmd_type, cmd_list in default_commands.items():
                if cmd_type not in commands:
                    commands[cmd_type] = cmd_list
        
        return commands
    
    def _parse_package_json(self, filepath: str) -> Dict[str, List[str]]:
        """Parse package.json for npm scripts"""
        commands = {}
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                scripts = data.get('scripts', {})
                for script_name, _ in scripts.items():
                    commands[script_name] = [f'npm run {script_name}']
        except:
            pass
        return commands
    
    def _parse_makefile(self, filepath: str) -> Dict[str, List[str]]:
        """Parse Makefile for make targets"""
        commands = {}
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                # Find make targets (lines that start with word followed by :)
                targets = re.findall(r'^([a-zA-Z][a-zA-Z0-9_-]*):(?!.*=)', content, re.MULTILINE)
                for target in targets:
                    commands[target] = [f'make {target}']
        except:
            pass
        return commands
    
    def _parse_pyproject_toml(self, filepath: str) -> Dict[str, List[str]]:
        """Parse pyproject.toml for Python project commands"""
        commands = {}
        try:
            # Basic parsing without external dependencies
            with open(filepath, 'r') as f:
                content = f.read()
                # Look for tool.poetry.scripts or similar sections
                if 'poetry' in content:
                    commands['install'] = ['poetry install']
                    commands['run'] = ['poetry run python main.py']
        except:
            pass
        return commands
    
    def _parse_cargo_toml(self, filepath: str) -> Dict[str, List[str]]:
        """Parse Cargo.toml for Rust project commands"""
        commands = {
            'run': ['cargo run'],
            'build': ['cargo build'],
            'test': ['cargo test']
        }
        return commands
    
    def _learn_tools(self, project_path: str) -> Dict[str, Any]:
        """Learn development tools used in the project"""
        tools = {}
        
        # Check for IDE/editor config files
        ide_configs = {
            '.vscode': 'Visual Studio Code',
            '.idea': 'IntelliJ IDEA',
            '.vim': 'Vim',
            '.emacs': 'Emacs'
        }
        
        for config_dir, tool_name in ide_configs.items():
            if os.path.exists(os.path.join(project_path, config_dir)):
                tools['editor'] = tool_name
                break
        
        # Check for linting/formatting tools
        linting_files = {
            '.eslintrc.*': 'ESLint',
            '.prettierrc.*': 'Prettier',
            'pyproject.toml': 'Black/isort (if Python)',
            '.flake8': 'Flake8',
            'rustfmt.toml': 'rustfmt'
        }
        
        for pattern, tool in linting_files.items():
            files = list(Path(project_path).glob(pattern))
            if files:
                tools['linting'] = tools.get('linting', []) + [tool]
        
        # Check for CI/CD
        ci_indicators = {
            '.github/workflows': 'GitHub Actions',
            '.gitlab-ci.yml': 'GitLab CI',
            'Jenkinsfile': 'Jenkins',
            '.circleci': 'CircleCI'
        }
        
        for indicator, ci_tool in ci_indicators.items():
            if os.path.exists(os.path.join(project_path, indicator)):
                tools['ci_cd'] = ci_tool
                break
        
        return tools
    
    def _learn_dependencies(self, project_path: str) -> Dict[str, Any]:
        """Learn dependency management patterns"""
        deps = {}
        
        # Check for dependency files
        dep_files = {
            'package.json': 'npm/yarn',
            'requirements.txt': 'pip',
            'Pipfile': 'pipenv',
            'pyproject.toml': 'poetry/pip',
            'Cargo.toml': 'cargo',
            'go.mod': 'go modules',
            'pom.xml': 'maven',
            'build.gradle': 'gradle'
        }
        
        for filename, manager in dep_files.items():
            if os.path.exists(os.path.join(project_path, filename)):
                deps['package_manager'] = manager
                deps['dependency_file'] = filename
                break
        
        # Check for lock files
        lock_files = {
            'package-lock.json': 'npm',
            'yarn.lock': 'yarn',
            'Pipfile.lock': 'pipenv',
            'Cargo.lock': 'cargo',
            'go.sum': 'go'
        }
        
        for lockfile, manager in lock_files.items():
            if os.path.exists(os.path.join(project_path, lockfile)):
                deps['lock_file'] = lockfile
                deps['lock_manager'] = manager
                break
        
        return deps
    
    def _learn_deployment_patterns(self, project_path: str) -> Dict[str, Any]:
        """Learn deployment and build patterns"""
        deployment = {}
        
        # Check for containerization
        if os.path.exists(os.path.join(project_path, 'Dockerfile')):
            deployment['containerization'] = 'Docker'
        
        if os.path.exists(os.path.join(project_path, 'docker-compose.yml')):
            deployment['orchestration'] = 'Docker Compose'
        
        # Check for build tools
        build_files = {
            'webpack.config.js': 'Webpack',
            'vite.config.js': 'Vite',
            'rollup.config.js': 'Rollup',
            'build.sh': 'Shell script',
            'build.bat': 'Batch script'
        }
        
        for build_file, build_tool in build_files.items():
            if os.path.exists(os.path.join(project_path, build_file)):
                deployment['build_tool'] = build_tool
                break
        
        # Check for deployment configs
        deploy_configs = {
            'vercel.json': 'Vercel',
            'netlify.toml': 'Netlify',
            'Procfile': 'Heroku',
            'app.yaml': 'Google App Engine'
        }
        
        for config_file, platform in deploy_configs.items():
            if os.path.exists(os.path.join(project_path, config_file)):
                deployment['platform'] = platform
                break
        
        return deployment
    
    def _learn_testing_patterns(self, project_path: str) -> Dict[str, Any]:
        """Learn testing frameworks and patterns"""
        testing = {}
        
        # Check for test frameworks
        test_indicators = {
            'jest.config.js': 'Jest',
            'vitest.config.js': 'Vitest',
            'pytest.ini': 'pytest',
            'test_*.py': 'pytest',
            '*_test.py': 'pytest',
            'tests/': 'Generic test directory',
            '__tests__/': 'Jest tests',
            'spec/': 'Spec tests'
        }
        
        for indicator, framework in test_indicators.items():
            if '*' in indicator:
                # Glob pattern
                files = list(Path(project_path).glob(indicator))
                if files:
                    testing['framework'] = framework
                    break
            else:
                # Direct file/directory check
                if os.path.exists(os.path.join(project_path, indicator)):
                    testing['framework'] = framework
                    break
        
        # Check for test commands in package.json
        package_json = os.path.join(project_path, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    scripts = data.get('scripts', {})
                    if 'test' in scripts:
                        testing['test_command'] = 'npm test'
            except:
                pass
        
        return testing
    
    def _store_conventions_as_memories(self, conventions: Dict[str, Any]):
        """Store learned conventions as project memories"""
        if not self.memory_manager.current_project_id:
            return
        
        # Store environment details
        env_details = conventions.get('environment', {})
        if env_details:
            env_content = f"""Project Environment Configuration:
            
Operating System: {env_details.get('os')} {env_details.get('os_version')}
Architecture: {env_details.get('architecture')}
Shell: {env_details.get('shell')}
Python Version: {env_details.get('python_version')}

Preferred Commands for {env_details.get('os')}:
{json.dumps(env_details.get('preferred_commands', {}), indent=2)}

Available Tools:
{json.dumps(env_details.get('tools_available', {}), indent=2)}
"""
            
            self.memory_manager.add_context_memory(
                content=env_content,
                memory_type="environment",
                importance=0.9,
                tags=["environment", "os", "tools", "commands"]
            )
        
        # Store project type and commands
        project_type = conventions.get('project_type')
        commands = conventions.get('commands', {})
        if project_type and commands:
            cmd_content = f"""Project Type: {project_type}

Recommended Commands:
{json.dumps(commands, indent=2)}

IMPORTANT: Always use these project-specific commands instead of generic alternatives.
For example, use 'npm run dev' instead of 'node server.js' for this project.
"""
            
            self.memory_manager.add_context_memory(
                content=cmd_content,
                memory_type="commands",
                importance=0.95,
                tags=["commands", "project-type", project_type, "scripts"]
            )
        
        # Store tools and dependencies
        tools = conventions.get('tools', {})
        deps = conventions.get('dependencies', {})
        if tools or deps:
            tools_content = f"""Development Tools & Dependencies:

Tools:
{json.dumps(tools, indent=2)}

Dependencies:
{json.dumps(deps, indent=2)}

Use the specified package manager and follow established patterns for this project.
"""
            
            self.memory_manager.add_context_memory(
                content=tools_content,
                memory_type="tools",
                importance=0.8,
                tags=["tools", "dependencies", "setup"]
            )
        
        # Store deployment patterns
        deployment = conventions.get('deployment', {})
        if deployment:
            deploy_content = f"""Deployment Configuration:

{json.dumps(deployment, indent=2)}

Follow these deployment patterns for consistency with project setup.
"""
            
            self.memory_manager.add_context_memory(
                content=deploy_content,
                memory_type="deployment",
                importance=0.7,
                tags=["deployment", "build", "setup"]
            )
        
        # Store testing patterns
        testing = conventions.get('testing', {})
        if testing:
            test_content = f"""Testing Configuration:

{json.dumps(testing, indent=2)}

Use the specified testing framework and commands for this project.
"""
            
            self.memory_manager.add_context_memory(
                content=test_content,
                memory_type="testing",
                importance=0.7,
                tags=["testing", "qa", "commands"]
            )
    
    def get_project_conventions_summary(self) -> str:
        """Get a formatted summary of project conventions for AI context"""
        if not self.memory_manager.current_project_id:
            return "No active project for convention lookup."
        
        # Search for convention memories
        convention_memories = []
        for conv_type in self.convention_types.keys():
            memories = self.db.search_memories(conv_type, self.memory_manager.current_project_id, limit=2)
            convention_memories.extend(memories)
        
        if not convention_memories:
            return "No project conventions learned yet. Use auto_learn_project_conventions() to analyze the project."
        
        # Format convention summary
        summary_parts = ["## 🏗️ Project Conventions & Environment"]
        
        for memory in convention_memories:
            memory_type = memory['type']
            title = memory['title']
            content_preview = memory['content'][:200] + "..." if len(memory['content']) > 200 else memory['content']
            
            summary_parts.append(f"\n### {memory_type.title()}: {title}")
            summary_parts.append(content_preview)
        
        summary_parts.append("\n⚠️ IMPORTANT: Always follow these project-specific conventions and commands!")
        
        return "\n".join(summary_parts)
    
    def suggest_correct_command(self, user_command: str) -> Optional[str]:
        """Suggest correct project-specific command based on user input"""
        if not self.memory_manager.current_project_id:
            return None
        
        # Search for command memories
        command_memories = self.db.search_memories("commands", self.memory_manager.current_project_id, limit=5)
        
        if not command_memories:
            return None
        
        # Extract command patterns from memories
        all_commands = {}
        for memory in command_memories:
            try:
                # Look for JSON command structures in memory content
                content = memory['content']
                if '{' in content and '}' in content:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    json_part = content[start:end]
                    commands_data = json.loads(json_part)
                    all_commands.update(commands_data)
            except:
                continue
        
        # Suggest corrections based on common patterns
        suggestions = {}
        
        # Common command mappings
        command_mappings = {
            'node': ['npm run dev', 'npm start'],
            'python app.py': ['python main.py', 'uvicorn main:app'],
            'python server.py': ['python main.py', 'npm run dev'],
            'start': ['npm run dev', 'npm start'],
            'dev': ['npm run dev'],
            'build': ['npm run build', 'cargo build'],
            'test': ['npm test', 'pytest', 'cargo test']
        }
        
        # Check if user command matches any patterns
        user_lower = user_command.lower()
        for pattern, suggestions_list in command_mappings.items():
            if pattern in user_lower:
                # Find matching commands from project
                for cmd_type, cmd_list in all_commands.items():
                    if any(suggestion in cmd_list for suggestion in suggestions_list):
                        return f"Use '{cmd_list[0]}' instead of '{user_command}' for this project"
        
        return None
