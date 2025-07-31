from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import os
import re
import time
import json
import shutil
from pathlib import Path
from collections import defaultdict
from ..base import BaseTool

class ProjectScaffoldingTool(BaseTool):
    """Production-ready project scaffolding tool with intelligent template generation.
    
    This tool creates comprehensive project structures, development environments,
    boilerplate code, configuration files, and tooling setup across multiple
    programming languages and frameworks with advanced customization options.
    """
    
    def __init__(self):
        """Initialize project scaffolding tool with required attributes."""
        # Required attributes
        self.name = "ProjectScaffoldingTool"
        self.description = "Creates comprehensive project structures, development environments, and boilerplate code across multiple frameworks"
        
        # Optional metadata
        self.version = "2.0.0"
        self.category = "advanced_tools"
        
        # Supported project types and their configurations
        self.project_types = {
            'python_package': {
                'keywords': ['python', 'package', 'library', 'module', 'pip'],
                'extensions': ['.py'],
                'dependencies': ['pytest', 'black', 'flake8', 'mypy'],
                'structure': ['src', 'tests', 'docs'],
                'config_files': ['setup.py', 'requirements.txt', 'pyproject.toml']
            },
            'fastapi': {
                'keywords': ['fastapi', 'api', 'web api', 'rest api', 'microservice'],
                'extensions': ['.py'],
                'dependencies': ['fastapi', 'uvicorn', 'pydantic', 'pytest'],
                'structure': ['app', 'tests', 'docs', 'alembic'],
                'config_files': ['requirements.txt', 'docker-compose.yml', 'Dockerfile']
            },
            'flask': {
                'keywords': ['flask', 'web app', 'webapp', 'web application'],
                'extensions': ['.py', '.html', '.css'],
                'dependencies': ['flask', 'flask-sqlalchemy', 'pytest'],
                'structure': ['app', 'templates', 'static', 'tests'],
                'config_files': ['requirements.txt', 'config.py']
            },
            'django': {
                'keywords': ['django', 'web framework', 'mvc', 'orm'],
                'extensions': ['.py', '.html', '.css'],
                'dependencies': ['django', 'djangorestframework', 'pytest-django'],
                'structure': ['apps', 'templates', 'static', 'tests'],
                'config_files': ['requirements.txt', 'manage.py', 'settings.py']
            },
            'nodejs': {
                'keywords': ['node', 'nodejs', 'javascript', 'js', 'npm'],
                'extensions': ['.js', '.json'],
                'dependencies': ['express', 'jest', 'nodemon'],
                'structure': ['src', 'test', 'public'],
                'config_files': ['package.json', '.eslintrc.json']
            },
            'react': {
                'keywords': ['react', 'frontend', 'spa', 'web app', 'component'],
                'extensions': ['.js', '.jsx', '.css'],
                'dependencies': ['react', 'react-dom', '@testing-library/react'],
                'structure': ['src', 'public', 'components'],
                'config_files': ['package.json', 'webpack.config.js']
            },
            'nextjs': {
                'keywords': ['next', 'nextjs', 'react framework', 'ssr'],
                'extensions': ['.js', '.jsx', '.ts', '.tsx'],
                'dependencies': ['next', 'react', 'react-dom'],
                'structure': ['pages', 'components', 'styles', 'public'],
                'config_files': ['package.json', 'next.config.js']
            },
            'typescript': {
                'keywords': ['typescript', 'ts', 'typed javascript'],
                'extensions': ['.ts', '.js'],
                'dependencies': ['typescript', '@types/node', 'ts-node'],
                'structure': ['src', 'dist', 'tests'],
                'config_files': ['tsconfig.json', 'package.json']
            },
            'go': {
                'keywords': ['go', 'golang', 'go lang'],
                'extensions': ['.go'],
                'dependencies': [],
                'structure': ['cmd', 'internal', 'pkg'],
                'config_files': ['go.mod', 'main.go']
            },
            'rust': {
                'keywords': ['rust', 'cargo', 'rustlang'],
                'extensions': ['.rs'],
                'dependencies': [],
                'structure': ['src', 'tests'],
                'config_files': ['Cargo.toml', 'main.rs']
            },
            'docker': {
                'keywords': ['docker', 'container', 'containerize'],
                'extensions': [],
                'dependencies': [],
                'structure': [],
                'config_files': ['Dockerfile', 'docker-compose.yml', '.dockerignore']
            }
        }
        
        # Scaffolding operation types
        self.operation_types = {
            'create': ['create', 'new', 'init', 'initialize', 'generate', 'scaffold'],
            'setup': ['setup', 'configure', 'install', 'prepare'],
            'template': ['template', 'boilerplate', 'starter', 'skeleton'],
            'structure': ['structure', 'organize', 'layout', 'framework'],
            'enhance': ['enhance', 'improve', 'upgrade', 'modernize']
        }
        
        # Development environments and tools
        self.dev_tools = {
            'testing': ['pytest', 'jest', 'mocha', 'unittest'],
            'linting': ['eslint', 'flake8', 'pylint', 'tslint'],
            'formatting': ['black', 'prettier', 'autopep8'],
            'typing': ['mypy', 'typescript', 'flow'],
            'documentation': ['sphinx', 'jsdoc', 'typedoc'],
            'ci_cd': ['github-actions', 'gitlab-ci', 'travis'],
            'containerization': ['docker', 'kubernetes']
        }
        
        # Template customization options
        self.customization_options = {
            'license': ['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause'],
            'code_style': ['standard', 'airbnb', 'google', 'pep8'],
            'testing_framework': ['pytest', 'unittest', 'jest', 'mocha'],
            'documentation': ['sphinx', 'mkdocs', 'gitbook'],
            'ci_platform': ['github', 'gitlab', 'bitbucket']
        }
    
    def can_handle(self, task: str) -> bool:
        """Intelligent project scaffolding task detection.
        
        Uses multi-layer analysis to determine if a task requires
        project scaffolding capabilities.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires project scaffolding, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_lower = task.strip().lower()
        
        # Layer 1: Direct Scaffolding Keywords
        scaffolding_keywords = {
            'create', 'init', 'initialize', 'scaffold', 'template', 'boilerplate',
            'setup', 'generate', 'new project', 'project structure', 'starter',
            'skeleton', 'blueprint', 'framework', 'workspace'
        }
        
        if any(keyword in task_lower for keyword in scaffolding_keywords):
            return True
        
        # Layer 2: Project Type Detection
        for project_type, info in self.project_types.items():
            if any(keyword in task_lower for keyword in info['keywords']):
                # Check if combined with creation context
                creation_context = any(word in task_lower for word in [
                    'create', 'new', 'init', 'setup', 'generate', 'build'
                ])
                if creation_context:
                    return True
        
        # Layer 3: Operation Detection
        for operation, keywords in self.operation_types.items():
            if any(keyword in task_lower for keyword in keywords):
                # Check if combined with project context
                project_context = any(word in task_lower for word in [
                    'project', 'application', 'app', 'service', 'package', 'library'
                ])
                if project_context:
                    return True
        
        # Layer 4: Development Environment Patterns
        dev_patterns = [
            r'set\s*up.*development',
            r'create.*environment',
            r'initialize.*workspace',
            r'generate.*project',
            r'build.*from\s*scratch',
            r'start.*new.*(project|app|service)'
        ]
        
        if any(re.search(pattern, task_lower) for pattern in dev_patterns):
            return True
        
        # Layer 5: Framework and Technology Stack
        tech_stack_indicators = {
            'full-stack', 'backend', 'frontend', 'microservice',
            'api', 'web app', 'cli tool', 'library', 'package'
        }
        
        if any(indicator in task_lower for indicator in tech_stack_indicators):
            creation_indicators = {'create', 'build', 'develop', 'setup'}
            if any(indicator in task_lower for indicator in creation_indicators):
                return True
        
        # Layer 6: File and Directory Structure Indicators
        structure_patterns = [
            r'directory\s*structure',
            r'file\s*organization',
            r'project\s*layout',
            r'folder\s*structure',
            r'organize.*files'
        ]
        
        if any(re.search(pattern, task_lower) for pattern in structure_patterns):
            return True
        
        # Layer 7: Exclusion Rules
        non_scaffolding_indicators = {
            'weather', 'temperature', 'calculate', 'analyze data',
            'write content', 'search', 'translate', 'convert'
        }
        
        if any(indicator in task_lower for indicator in non_scaffolding_indicators):
            # Only exclude if it's clearly not scaffolding-related
            scaffolding_indicators = {'project', 'create', 'setup', 'init'}
            if not any(indicator in task_lower for indicator in scaffolding_indicators):
                return False
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute project scaffolding with robust error handling.
        
        Args:
            task: Project scaffolding task to perform
            **kwargs: Additional parameters (project_name, project_type, directory, etc.)
            
        Returns:
            Structured dictionary with scaffolding results
        """
        start_time = time.time()
        
        try:
            # Input validation
            if not task or not isinstance(task, str):
                return self._error_response("Task must be a non-empty string")
            
            if not self.can_handle(task):
                return self._error_response("Task does not appear to be project scaffolding related")
            
            # Extract and validate parameters
            project_name = self._extract_project_name(task, kwargs.get('project_name'))
            project_type = self._detect_project_type(task, kwargs.get('project_type'))
            target_directory = kwargs.get('directory', kwargs.get('cwd', os.getcwd()))
            
            # Validate project name
            if not self._is_valid_project_name(project_name):
                return self._error_response(f"Invalid project name: {project_name}")
            
            # Check if project already exists
            project_path = os.path.join(target_directory, project_name)
            if os.path.exists(project_path):
                if not kwargs.get('force', False):
                    return self._error_response(f"Project directory '{project_name}' already exists")
                else:
                    shutil.rmtree(project_path)
            
            # Extract customization options
            options = self._extract_options(task, kwargs)
            
            # Create project structure
            result = self._create_project(project_name, project_type, target_directory, options)
            
            if not result or not result.get('success'):
                return self._error_response("Failed to create project structure")
            
            execution_time = time.time() - start_time
            
            # Generate project report
            project_report = {
                'project_info': {
                    'name': project_name,
                    'type': project_type,
                    'path': result['project_path'],
                    'structure': result['structure'],
                    'files_created': result['files_created']
                },
                'development_setup': {
                    'dependencies': result['dependencies'],
                    'dev_tools': result['dev_tools'],
                    'scripts': result.get('scripts', {}),
                    'configuration': result.get('configuration', {})
                },
                'getting_started': {
                    'next_steps': result['next_steps'],
                    'commands': result.get('commands', []),
                    'documentation': result.get('documentation', [])
                },
                'customization': options,
                'quality_checks': self._perform_quality_checks(result)
            }
            
            # Success response
            return {
                'success': True,
                'result': project_report,
                'message': f"Project '{project_name}' created successfully",
                'metadata': {
                    'tool_name': self.name,
                    'execution_time': execution_time,
                    'task_type': 'project_scaffolding',
                    'project_type': project_type,
                    'project_name': project_name,
                    'files_count': len(result['files_created']),
                    'directories_count': len(result['structure']),
                    'has_dependencies': len(result['dependencies']) > 0
                }
            }
            
        except Exception as e:
            return self._error_response(f"Project scaffolding failed: {str(e)}", e)
    
    def _detect_project_type(self, task: str, explicit_type: str = None) -> str:
        """Detect the type of project to create."""
        if explicit_type and explicit_type in self.project_types:
            return explicit_type
        
        task_lower = task.lower()
        
        # Score each project type based on keyword matches
        scores = {}
        for project_type, info in self.project_types.items():
            score = 0
            for keyword in info['keywords']:
                if keyword in task_lower:
                    score += 1
            # Bonus for exact matches
            if project_type.replace('_', ' ') in task_lower:
                score += 2
            scores[project_type] = score
        
        # Return highest scoring type
        if scores and max(scores.values()) > 0:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        # Default based on common patterns
        if any(word in task_lower for word in ['api', 'microservice', 'rest']):
            return 'fastapi'
        elif any(word in task_lower for word in ['web', 'website', 'frontend']):
            return 'react'
        elif any(word in task_lower for word in ['package', 'library', 'module']):
            return 'python_package'
        else:
            return 'python_package'  # Default
    
    def _extract_project_name(self, task: str, explicit_name: str = None) -> str:
        """Extract project name from task or use provided name."""
        if explicit_name:
            return explicit_name
        
        # Try to extract project name from task
        patterns = [
            # Handle 'called' patterns first (most specific)
            r'(?:project\s+)?called\s+["\']?([a-zA-Z0-9_-]+)["\']?',
            r'named\s+["\']?([a-zA-Z0-9_-]+)["\']?',
            # Handle initialize patterns
            r'initialize\s+["\']?([a-zA-Z0-9_-]+)["\']?',
            r'init\s+["\']?([a-zA-Z0-9_-]+)["\']?',
            # Handle create patterns (less specific, so later)
            r'create\s+(?:a\s+)?(?:new\s+)?(?:\w+\s+)?(?:project\s+)?["\']?([a-zA-Z0-9_-]+)["\']?',
            r'generate\s+["\']?([a-zA-Z0-9_-]+)["\']?',
            # Handle project type followed by name
            r'(?:fastapi|flask|django|react|nodejs|python)\s+(?:project\s+)?["\']?([a-zA-Z0-9_-]+)["\']?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Default name
        return 'new-project'
    
    def _is_valid_project_name(self, name: str) -> bool:
        """Validate project name format."""
        if not name or len(name) < 2:
            return False
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return False
        
        # Should not start with number or special character
        if name[0].isdigit() or name[0] in '-_':
            return False
        
        return True
    
    def _extract_options(self, task: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract customization options from task and parameters."""
        options = {
            'license': kwargs.get('license', 'MIT'),
            'author': kwargs.get('author', 'Your Name'),
            'email': kwargs.get('email', 'your.email@example.com'),
            'description': kwargs.get('description', ''),
            'version': kwargs.get('version', '0.1.0'),
            'include_tests': kwargs.get('include_tests', True),
            'include_docs': kwargs.get('include_docs', True),
            'include_ci': kwargs.get('include_ci', False),
            'include_docker': kwargs.get('include_docker', False)
        }
        
        # Extract from task text
        task_lower = task.lower()
        
        # License detection
        for license_type in self.customization_options['license']:
            if license_type.lower() in task_lower:
                options['license'] = license_type
                break
        
        # Feature detection
        if any(word in task_lower for word in ['test', 'testing']):
            options['include_tests'] = True
        
        if any(word in task_lower for word in ['docker', 'container']):
            options['include_docker'] = True
        
        if any(word in task_lower for word in ['ci', 'continuous integration', 'github actions']):
            options['include_ci'] = True
        
        return options
    
    def _create_project(self, name: str, project_type: str, target_dir: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create the actual project structure."""
        project_path = os.path.join(target_dir, name)
        
        try:
            # Create base directory
            os.makedirs(project_path, exist_ok=True)
            
            # Get project configuration
            config = self.project_types[project_type]
            
            # Create directory structure
            directories = self._create_directory_structure(project_path, config, options)
            
            # Generate files
            files_created = self._generate_project_files(project_path, name, project_type, config, options)
            
            # Set up development tools
            dev_tools = self._setup_dev_tools(project_path, project_type, options)
            
            # Generate configuration files
            config_files = self._generate_config_files(project_path, name, project_type, options)
            
            # Combine all created files
            all_files = files_created + config_files
            
            return {
                'success': True,
                'project_path': project_path,
                'structure': directories,
                'files_created': all_files,
                'dependencies': config['dependencies'],
                'dev_tools': dev_tools,
                'next_steps': self._generate_next_steps(name, project_type, options),
                'commands': self._generate_useful_commands(project_type),
                'documentation': self._generate_documentation_links(project_type)
            }
            
        except Exception as e:
            # Cleanup on failure
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
            raise e
    
    def _create_directory_structure(self, project_path: str, config: Dict[str, Any], options: Dict[str, Any]) -> List[str]:
        """Create the directory structure for the project."""
        directories = []
        
        # Base directories from configuration
        for directory in config['structure']:
            dir_path = os.path.join(project_path, directory)
            os.makedirs(dir_path, exist_ok=True)
            directories.append(directory)
        
        # Optional directories based on options
        if options.get('include_tests', True) and 'tests' not in directories:
            os.makedirs(os.path.join(project_path, 'tests'), exist_ok=True)
            directories.append('tests')
        
        if options.get('include_docs', True) and 'docs' not in directories:
            os.makedirs(os.path.join(project_path, 'docs'), exist_ok=True)
            directories.append('docs')
        
        if options.get('include_ci', False):
            os.makedirs(os.path.join(project_path, '.github', 'workflows'), exist_ok=True)
            directories.append('.github/workflows')
        
        return directories
    
    def _generate_project_files(self, project_path: str, name: str, project_type: str, 
                               config: Dict[str, Any], options: Dict[str, Any]) -> List[str]:
        """Generate the main project files."""
        files_created = []
        
        if project_type == 'python_package':
            files_created.extend(self._generate_python_package_files(project_path, name, options))
        elif project_type == 'fastapi':
            files_created.extend(self._generate_fastapi_files(project_path, name, options))
        elif project_type == 'flask':
            files_created.extend(self._generate_flask_files(project_path, name, options))
        elif project_type == 'nodejs':
            files_created.extend(self._generate_nodejs_files(project_path, name, options))
        elif project_type == 'react':
            files_created.extend(self._generate_react_files(project_path, name, options))
        elif project_type == 'nextjs':
            files_created.extend(self._generate_nextjs_files(project_path, name, options))
        
        # Common files
        files_created.extend(self._generate_common_files(project_path, name, project_type, options))
        
        return files_created
    
    def _generate_python_package_files(self, project_path: str, name: str, options: Dict[str, Any]) -> List[str]:
        """Generate Python package specific files."""
        files = []
        package_name = name.replace('-', '_')
        
        # Main package directory
        package_dir = os.path.join(project_path, 'src', package_name)
        os.makedirs(package_dir, exist_ok=True)
        
        # __init__.py
        init_content = f'"""{ name } package."""\n\n__version__ = "{options.get("version", "0.1.0")}"\n'
        self._write_file(os.path.join(package_dir, '__init__.py'), init_content)
        files.append(f'src/{package_name}/__init__.py')
        
        # main.py
        main_content = f'''"""Main module for {package_name}."""


def main():
    """Main entry point."""
    print("Hello from {package_name}!")
    return "Hello World"


if __name__ == "__main__":
    main()
'''
        self._write_file(os.path.join(package_dir, 'main.py'), main_content)
        files.append(f'src/{package_name}/main.py')
        
        # requirements.txt
        requirements = [
            '# Production dependencies',
            '# Add your dependencies here',
            ''
        ]
        self._write_file(os.path.join(project_path, 'requirements.txt'), '\n'.join(requirements))
        files.append('requirements.txt')
        
        # requirements-dev.txt
        dev_requirements = [
            'pytest>=7.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=0.991',
            'coverage>=6.0',
            'pre-commit>=2.20.0'
        ]
        self._write_file(os.path.join(project_path, 'requirements-dev.txt'), '\n'.join(dev_requirements))
        files.append('requirements-dev.txt')
        
        # setup.py
        setup_content = f'''"""Setup script for {name}."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="{name}",
    version="{options.get('version', '0.1.0')}",
    author="{options.get('author', 'Your Name')}",
    author_email="{options.get('email', 'your.email@example.com')}",
    description="{options.get('description', f'A Python package: {name}')}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={{"": "src"}},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: {options.get('license', 'MIT')} License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[],
)
'''
        self._write_file(os.path.join(project_path, 'setup.py'), setup_content)
        files.append('setup.py')
        
        # Test file
        if options.get('include_tests', True):
            test_content = f'''"""Tests for {package_name}."""

import pytest
from {package_name}.main import main


def test_main():
    """Test main function."""
    result = main()
    assert result == "Hello World"


def test_package_version():
    """Test package version is defined."""
    from {package_name} import __version__
    assert __version__ is not None
'''
            test_dir = os.path.join(project_path, 'tests')
            os.makedirs(test_dir, exist_ok=True)
            self._write_file(os.path.join(test_dir, f'test_{package_name}.py'), test_content)
            files.append(f'tests/test_{package_name}.py')
        
        return files
    
    def _generate_fastapi_files(self, project_path: str, name: str, options: Dict[str, Any]) -> List[str]:
        """Generate FastAPI specific files."""
        files = []
        
        # Create app directory
        app_dir = os.path.join(project_path, 'app')
        os.makedirs(app_dir, exist_ok=True)
        
        # main.py
        main_content = f'''"""FastAPI application for {name}."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="{name}",
    description="{options.get('description', f'FastAPI application: {name}')}",
    version="{options.get('version', '0.1.0')}"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {{
        "message": "Welcome to {name}!",
        "docs": "/docs",
        "version": "{options.get('version', '0.1.0')}"
    }}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {{"status": "healthy", "service": "{name}"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        self._write_file(os.path.join(app_dir, 'main.py'), main_content)
        files.append('app/main.py')
        
        # __init__.py
        self._write_file(os.path.join(app_dir, '__init__.py'), '"""FastAPI application package."""\n')
        files.append('app/__init__.py')
        
        # requirements.txt
        requirements = [
            'fastapi>=0.100.0',
            'uvicorn[standard]>=0.22.0',
            'pydantic>=2.0.0',
            'python-multipart>=0.0.6'
        ]
        self._write_file(os.path.join(project_path, 'requirements.txt'), '\n'.join(requirements))
        files.append('requirements.txt')
        
        # requirements-dev.txt
        dev_requirements = [
            'pytest>=7.0.0',
            'httpx>=0.24.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=0.991'
        ]
        self._write_file(os.path.join(project_path, 'requirements-dev.txt'), '\n'.join(dev_requirements))
        files.append('requirements-dev.txt')
        
        return files
    
    def _generate_nodejs_files(self, project_path: str, name: str, options: Dict[str, Any]) -> List[str]:
        """Generate Node.js specific files."""
        files = []
        
        # package.json
        package_data = {
            "name": name,
            "version": options.get('version', '1.0.0'),
            "description": options.get('description', f'Node.js application: {name}'),
            "main": "src/index.js",
            "scripts": {
                "start": "node src/index.js",
                "dev": "nodemon src/index.js",
                "test": "jest",
                "lint": "eslint src/",
                "format": "prettier --write src/"
            },
            "keywords": [],
            "author": options.get('author', 'Your Name'),
            "license": options.get('license', 'MIT'),
            "dependencies": {
                "express": "^4.18.0"
            },
            "devDependencies": {
                "jest": "^29.0.0",
                "nodemon": "^3.0.0",
                "eslint": "^8.0.0",
                "prettier": "^3.0.0"
            }
        }
        
        self._write_file(os.path.join(project_path, 'package.json'), json.dumps(package_data, indent=2))
        files.append('package.json')
        
        # src/index.js
        src_dir = os.path.join(project_path, 'src')
        os.makedirs(src_dir, exist_ok=True)
        
        index_content = f'''/**
 * Main application entry point for {name}
 */

const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({{ extended: true }}));

// Routes
app.get('/', (req, res) => {{
    res.json({{
        message: 'Welcome to {name}!',
        version: '{options.get('version', '1.0.0')}',
        timestamp: new Date().toISOString()
    }});
}});

app.get('/health', (req, res) => {{
    res.json({{ status: 'healthy', service: '{name}' }});
}});

// Start server
app.listen(PORT, () => {{
    console.log(`{name} server running on port ${{PORT}}`);
}});

module.exports = app;
'''
        self._write_file(os.path.join(src_dir, 'index.js'), index_content)
        files.append('src/index.js')
        
        return files
    
    def _generate_react_files(self, project_path: str, name: str, options: Dict[str, Any]) -> List[str]:
        """Generate React specific files."""
        files = []
        
        # package.json
        package_data = {
            "name": name,
            "version": options.get('version', '0.1.0'),
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "eslintConfig": {
                "extends": ["react-app", "react-app/jest"]
            },
            "browserslist": {
                "production": [">0.2%", "not dead", "not op_mini all"],
                "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
            }
        }
        
        self._write_file(os.path.join(project_path, 'package.json'), json.dumps(package_data, indent=2))
        files.append('package.json')
        
        # public/index.html
        public_dir = os.path.join(project_path, 'public')
        os.makedirs(public_dir, exist_ok=True)
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="{options.get('description', f'React application: {name}')}" />
    <title>{name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
'''
        self._write_file(os.path.join(public_dir, 'index.html'), html_content)
        files.append('public/index.html')
        
        # src/App.js
        src_dir = os.path.join(project_path, 'src')
        os.makedirs(src_dir, exist_ok=True)
        
        app_content = f'''import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {name}</h1>
        <p>A React application built with Create React App</p>
      </header>
    </div>
  );
}}

export default App;
'''
        self._write_file(os.path.join(src_dir, 'App.js'), app_content)
        files.append('src/App.js')
        
        # src/index.js
        index_content = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
        self._write_file(os.path.join(src_dir, 'index.js'), index_content)
        files.append('src/index.js')
        
        return files
    
    def _generate_common_files(self, project_path: str, name: str, project_type: str, options: Dict[str, Any]) -> List[str]:
        """Generate common files for all project types."""
        files = []
        
        # README.md
        readme_content = self._generate_readme(name, project_type, options)
        self._write_file(os.path.join(project_path, 'README.md'), readme_content)
        files.append('README.md')
        
        # .gitignore
        gitignore_content = self._generate_gitignore(project_type)
        self._write_file(os.path.join(project_path, '.gitignore'), gitignore_content)
        files.append('.gitignore')
        
        # LICENSE
        if options.get('license'):
            license_content = self._generate_license(options['license'], options.get('author', 'Your Name'))
            self._write_file(os.path.join(project_path, 'LICENSE'), license_content)
            files.append('LICENSE')
        
        return files
    
    def _generate_config_files(self, project_path: str, name: str, project_type: str, options: Dict[str, Any]) -> List[str]:
        """Generate configuration files."""
        files = []
        
        # Docker files
        if options.get('include_docker', False):
            dockerfile_content = self._generate_dockerfile(project_type)
            self._write_file(os.path.join(project_path, 'Dockerfile'), dockerfile_content)
            files.append('Dockerfile')
            
            docker_compose_content = self._generate_docker_compose(name, project_type)
            self._write_file(os.path.join(project_path, 'docker-compose.yml'), docker_compose_content)
            files.append('docker-compose.yml')
        
        # CI/CD files
        if options.get('include_ci', False):
            github_workflow = self._generate_github_workflow(project_type)
            workflow_dir = os.path.join(project_path, '.github', 'workflows')
            os.makedirs(workflow_dir, exist_ok=True)
            self._write_file(os.path.join(workflow_dir, 'ci.yml'), github_workflow)
            files.append('.github/workflows/ci.yml')
        
        return files
    
    def _setup_dev_tools(self, project_path: str, project_type: str, options: Dict[str, Any]) -> List[str]:
        """Set up development tools and configurations."""
        dev_tools = []
        
        if project_type.startswith('python') or project_type in ['fastapi', 'flask', 'django']:
            dev_tools.extend(['pytest', 'black', 'flake8', 'mypy'])
            
            # pyproject.toml for Python projects
            pyproject_content = self._generate_pyproject_toml(project_type)
            self._write_file(os.path.join(project_path, 'pyproject.toml'), pyproject_content)
            
        elif project_type in ['nodejs', 'react', 'nextjs', 'typescript']:
            dev_tools.extend(['eslint', 'prettier', 'jest'])
            
            # .eslintrc.json
            eslint_config = {
                "env": {"node": True, "es2021": True},
                "extends": ["eslint:recommended"],
                "parserOptions": {"ecmaVersion": 12, "sourceType": "module"},
                "rules": {}
            }
            self._write_file(os.path.join(project_path, '.eslintrc.json'), json.dumps(eslint_config, indent=2))
        
        return dev_tools
    
    def _perform_quality_checks(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform quality checks on the created project."""
        checks = {
            'structure_complete': len(result['structure']) > 0,
            'files_created': len(result['files_created']) > 0,
            'has_main_file': any('main' in f or 'index' in f for f in result['files_created']),
            'has_readme': 'README.md' in result['files_created'],
            'has_gitignore': '.gitignore' in result['files_created'],
            'has_dependencies': len(result['dependencies']) > 0,
            'has_tests': any('test' in f for f in result['files_created'])
        }
        
        score = sum(checks.values()) / len(checks)
        
        return {
            'checks': checks,
            'score': round(score, 2),
            'grade': 'Excellent' if score >= 0.9 else 'Good' if score >= 0.7 else 'Needs Improvement'
        }
    
    def _generate_next_steps(self, name: str, project_type: str, options: Dict[str, Any]) -> List[str]:
        """Generate next steps for the user."""
        steps = [f"cd {name}"]
        
        if project_type.startswith('python') or project_type in ['fastapi', 'flask']:
            steps.extend([
                "python -m venv venv",
                "source venv/bin/activate  # On Windows: venv\\Scripts\\activate",
                "pip install -r requirements.txt"
            ])
            if options.get('include_tests', True):
                steps.append("pip install -r requirements-dev.txt")
                steps.append("pytest")
        
        elif project_type in ['nodejs', 'react', 'nextjs']:
            steps.extend([
                "npm install",
                "npm start"
            ])
        
        steps.extend([
            "git init",
            "git add .",
            'git commit -m "Initial commit"'
        ])
        
        return steps
    
    def _generate_useful_commands(self, project_type: str) -> List[str]:
        """Generate useful commands for the project type."""
        commands = []
        
        if project_type.startswith('python') or project_type in ['fastapi', 'flask']:
            commands.extend([
                "python -m pytest",
                "black .",
                "flake8 .",
                "mypy ."
            ])
        elif project_type in ['nodejs', 'react', 'nextjs']:
            commands.extend([
                "npm test",
                "npm run build",
                "npm run lint",
                "npm run format"
            ])
        
        return commands
    
    def _generate_documentation_links(self, project_type: str) -> List[str]:
        """Generate relevant documentation links."""
        docs = {
            'python_package': [
                "Python Packaging: https://packaging.python.org/",
                "pytest: https://docs.pytest.org/",
                "Black: https://black.readthedocs.io/"
            ],
            'fastapi': [
                "FastAPI: https://fastapi.tiangolo.com/",
                "Uvicorn: https://www.uvicorn.org/",
                "Pydantic: https://docs.pydantic.dev/"
            ],
            'react': [
                "React: https://react.dev/",
                "Create React App: https://create-react-app.dev/",
                "React Testing Library: https://testing-library.com/docs/react-testing-library/"
            ],
            'nodejs': [
                "Node.js: https://nodejs.org/docs/",
                "Express: https://expressjs.com/",
                "Jest: https://jestjs.io/docs/"
            ]
        }
        
        return docs.get(project_type, ["Project documentation coming soon..."])
    
    def _write_file(self, filepath: str, content: str):
        """Write content to a file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_readme(self, name: str, project_type: str, options: Dict[str, Any]) -> str:
        """Generate README.md content."""
        return f'''# {name}

{options.get('description', f'A {project_type} project')}

## Features

- Modern {project_type} setup
- Development tools included
- Testing framework configured
- CI/CD ready

## Installation

```bash
git clone <repository-url>
cd {name}
```

### For Python projects:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### For Node.js projects:
```bash
npm install
```

## Usage

Describe how to use your project here.

## Development

### Running tests
```bash
# Python
pytest

# Node.js
npm test
```

### Code formatting
```bash
# Python
black .

# Node.js
npm run format
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the {options.get('license', 'MIT')} License.

## Author

{options.get('author', 'Your Name')} - {options.get('email', 'your.email@example.com')}
'''
    
    def _generate_gitignore(self, project_type: str) -> str:
        """Generate .gitignore content based on project type."""
        common = '''# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

'''
        
        if project_type.startswith('python') or project_type in ['fastapi', 'flask', 'django']:
            return common + '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
.venv/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Environment variables
.env
.env.local
'''
        
        elif project_type in ['nodejs', 'react', 'nextjs', 'typescript']:
            return common + '''# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# Build outputs
dist/
build/
.next/
out/

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
'''
        
        return common
    
    def _generate_license(self, license_type: str, author: str) -> str:
        """Generate license content."""
        year = datetime.now().year
        
        if license_type == 'MIT':
            return f'''MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
        
        return f'# {license_type} License\n\nCopyright (c) {year} {author}\n'
    
    def _generate_dockerfile(self, project_type: str) -> str:
        """Generate Dockerfile content."""
        if project_type.startswith('python') or project_type in ['fastapi', 'flask']:
            return '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        
        elif project_type in ['nodejs', 'react', 'nextjs']:
            return '''FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
'''
        
        return '# Dockerfile for custom project type\n'
    
    def _generate_docker_compose(self, name: str, project_type: str) -> str:
        """Generate docker-compose.yml content."""
        return f'''version: '3.8'

services:
  {name}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=development
    volumes:
      - .:/app
      - /app/node_modules
'''
    
    def _generate_github_workflow(self, project_type: str) -> str:
        """Generate GitHub Actions workflow."""
        if project_type.startswith('python') or project_type in ['fastapi', 'flask']:
            return '''name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Type check with mypy
      run: mypy .
    
    - name: Test with pytest
      run: pytest --cov=. --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
'''
        
        elif project_type in ['nodejs', 'react', 'nextjs']:
            return '''name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x]

    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - run: npm ci
    - run: npm run lint
    - run: npm test
    - run: npm run build
'''
        
        return '''name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run tests
      run: echo "Add your test commands here"
'''
    
    def _generate_pyproject_toml(self, project_type: str) -> str:
        """Generate pyproject.toml for Python projects."""
        return '''[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]

[tool.black]
line-length = 88
target-version = ['py38']
include = '\\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]

[tool.coverage.run]
source = ["src"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:"
]
'''
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response."""
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': [
                "Ensure the task contains a clear project creation request",
                "Specify project type and name if not obvious",
                "Check directory permissions for project creation",
                "Examples: 'Create a FastAPI project called my-api', 'Initialize Python package named my-lib'",
                f"Supported project types: {', '.join(self.project_types.keys())}",
                "Use 'force=True' parameter to overwrite existing directories"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_project_types': list(self.project_types.keys()),
                'supported_operations': list(self.operation_types.keys()),
                'customization_options': list(self.customization_options.keys())
            }
        }