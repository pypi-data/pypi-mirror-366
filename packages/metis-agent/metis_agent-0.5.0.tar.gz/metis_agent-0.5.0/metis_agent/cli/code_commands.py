"""
CLI commands for code intelligence features.

This module provides CLI commands for code analysis, generation, and context-aware
development assistance.
"""
import click
from pathlib import Path
from ..tools.code_analysis import CodeAnalysisTool
from ..tools.context_aware_generator import ContextAwareCodeGenerator
from ..tools.filesystem import FileSystemTool
from ..core.agent import SingleAgent


@click.group()
def code():
    """Code intelligence and generation commands."""
    pass


@code.command()
@click.argument('file_path', required=False)
@click.option('--project', '-p', is_flag=True, help='Analyze entire project')
@click.option('--overview', '-o', is_flag=True, help='Show code overview')
@click.option('--dependencies', '-d', is_flag=True, help='Show dependencies')
def analyze(file_path, project, overview, dependencies):
    """Analyze code structure and patterns."""
    tool = CodeAnalysisTool()
    
    try:
        if dependencies:
            result = tool.analyze_dependencies(".")
            if result.get("success"):
                click.echo("Dependency Analysis")
                click.echo("=" * 50)
                
                internal = result.get("internal_imports", [])
                external = result.get("external_imports", [])
                
                if external:
                    click.echo(f"\nExternal Dependencies ({len(external)}):")
                    for dep in external[:10]:  # Show top 10
                        click.echo(f"  - {dep}")
                    if len(external) > 10:
                        click.echo(f"  ... and {len(external) - 10} more")
                
                if internal:
                    click.echo(f"\nInternal Imports ({len(internal)}):")
                    for dep in internal[:10]:  # Show top 10
                        click.echo(f"  - {dep}")
                    if len(internal) > 10:
                        click.echo(f"  ... and {len(internal) - 10} more")
                        
            else:
                click.echo(f"Error: {result.get('error', 'Unknown error')}")
        
        elif overview:
            result = tool.get_code_overview(".")
            if result.get("success"):
                summary = result.get("summary", {})
                click.echo("Code Overview")
                click.echo("=" * 50)
                
                click.echo(f"Primary Language: {summary.get('primary_language', 'Unknown')}")
                click.echo(f"Total Files: {summary.get('total_files', 0)}")
                click.echo(f"Total Lines: {summary.get('total_lines', 0)}")
                
                languages = summary.get('languages_used', [])
                if languages:
                    click.echo(f"Languages: {', '.join(languages)}")
                
                complexity = summary.get('complexity_distribution', {})
                if complexity:
                    click.echo(f"Complexity: {complexity.get('low', 0)} low, {complexity.get('medium', 0)} medium, {complexity.get('high', 0)} high")
                
                patterns = summary.get('patterns', [])
                if patterns:
                    click.echo("\nProject Patterns:")
                    for pattern in patterns[:5]:
                        click.echo(f"  - {pattern}")
                        
            else:
                click.echo(f"Error: {result.get('error', 'Unknown error')}")
        
        elif project:
            result = tool.analyze_project(".")
            if result.get("success"):
                click.echo(" Project Analysis")
                click.echo("=" * 50)
                
                click.echo(f" Directory: {result.get('directory', '.')}")
                click.echo(f" Total Files: {result.get('total_files', 0)}")
                click.echo(f" Total Lines: {result.get('total_lines', 0)}")
                
                languages = result.get('languages', {})
                if languages:
                    click.echo(f"\n Languages:")
                    for lang, count in languages.items():
                        click.echo(f"   {lang}: {count} files")
                
                complexity = result.get('complexity_summary', {})
                if complexity:
                    click.echo(f"\n Complexity Distribution:")
                    for level, count in complexity.items():
                        if count > 0:
                            click.echo(f"   {level}: {count} files")
                
                common_imports = result.get('common_imports', {})
                if common_imports:
                    click.echo(f"\n Most Common Imports:")
                    for imp, count in sorted(common_imports.items(), key=lambda x: x[1], reverse=True)[:5]:
                        click.echo(f"   {imp}: {count} files")
                        
            else:
                click.echo(f"Error: {result.get('error', 'Unknown error')}")
        
        elif file_path:
            result = tool.analyze_file(file_path)
            if result.get("success"):
                click.echo(f" Analysis: {result.get('file_path')}")
                click.echo("=" * 50)
                
                click.echo(f" Language: {result.get('language', 'Unknown')}")
                click.echo(f" Lines: {result.get('lines_count', 0)}")
                click.echo(f" Size: {result.get('size_bytes', 0)} bytes")
                click.echo(f" Complexity: {result.get('complexity_estimate', 'Unknown')}")
                
                functions = result.get('functions', [])
                if functions:
                    click.echo(f"\n Functions ({len(functions)}):")
                    for func in functions:
                        name = func.get('name', 'Unknown')
                        line = func.get('line_number', '?')
                        args = func.get('args_count', 0)
                        click.echo(f"   {name}() - Line {line} ({args} args)")
                
                classes = result.get('classes', [])
                if classes:
                    click.echo(f"\n Classes ({len(classes)}):")
                    for cls in classes:
                        name = cls.get('name', 'Unknown')
                        line = cls.get('line_number', '?')
                        methods = len(cls.get('methods', []))
                        click.echo(f"   {name} - Line {line} ({methods} methods)")
                
                imports = result.get('imports', [])
                if imports:
                    click.echo(f"\n Imports ({len(imports)}):")
                    for imp in imports[:10]:  # Show first 10
                        if imp.get('type') == 'import':
                            click.echo(f"   import {imp.get('module', '')}")
                        else:
                            click.echo(f"   from {imp.get('module', '')} import {imp.get('name', '')}")
                    if len(imports) > 10:
                        click.echo(f"  ... and {len(imports) - 10} more")
                        
            else:
                click.echo(f"Error: {result.get('error', 'Unknown error')}")
        
        else:
            # Default to project overview
            result = tool.get_code_overview(".")
            if result.get("success"):
                summary = result.get("summary", {})
                click.echo(" Quick Code Overview")
                click.echo("=" * 30)
                click.echo(f" Language: {summary.get('primary_language', 'Unknown')}")
                click.echo(f" Files: {summary.get('total_files', 0)}")
                click.echo(f" Lines: {summary.get('total_lines', 0)}")
                
                click.echo(f"\n Use 'metis code analyze --project' for detailed analysis")
            else:
                click.echo(f"Error: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        click.echo(f" Error analyzing code: {str(e)}")


@code.command()
@click.argument('description')
@click.option('--type', '-t', type=click.Choice(['function', 'class', 'test', 'docs']), 
              help='Type of code to generate')
@click.option('--language', '-l', type=str, help='Target language (auto-detected if not specified)')
@click.option('--file', '-f', type=str, help='Output file path')
@click.option('--show-context', is_flag=True, help='Show project context used for generation')
@click.option('--interactive', '-i', is_flag=True, help='Enable interactive planning and chat with agent')
@click.option('--skip-chat', is_flag=True, help='Skip interactive chat phase (used with --interactive)')
@click.option('--branch', '-b', type=str, help='Create specific named feature branch for code generation work')
@click.option('--no-branch', is_flag=True, help='Skip automatic branch creation and work on current branch')
def generate(description, type, language, file, show_context, interactive, skip_chat, branch, no_branch):
    """Generate code based on description and project context."""
    
    # Handle branch creation before code generation (default behavior unless --no-branch)
    if not no_branch:
        # Auto-branch by default, or use specific branch name if provided
        auto_branch = branch is None  # Auto-generate if no specific branch name
        branch_created = _create_feature_branch(branch, auto_branch, description)
        if not branch_created:
            return  # Branch creation failed
    
    # Interactive mode - use original interactive behavior if explicitly requested
    if interactive:
        return _interactive_generate(description, type, language, file, skip_chat)
    
    # DEFAULT: Natural language generation (no flags needed)
    return _natural_language_generate(description, type, language, file)


def _interactive_generate(description, type, language, file, skip_chat):
    """Interactive code generation with agent planning."""
    click.echo(click.style("[INTERACTIVE CODE GENERATION]", fg="cyan", bold=True))
    click.echo("=" * 50)
    
    # Step 1: Agent Analysis
    click.echo(click.style("[ANALYZING] Agent analyzing your request...", fg="yellow"))
    
    agent = get_agent()
    
    # Let the agent create the initial plan
    planning_prompt = f"""I need to generate code with the following requirements:
    - Description: {description}
    - Type: {type or 'Auto-detect'}
    - Target file: {file or 'To be determined'}
    - Language: {language or 'Auto-detect'}
    
    Please analyze the current project context and create a detailed plan for this code generation task.
    Include analysis, steps, files that will be affected, and potential risks.
    """
    
    agent_plan_response = agent.process_query(planning_prompt)
    click.echo(click.style("[AGENT PLAN]", fg="blue", bold=True))
    click.echo(agent_plan_response)
    
    # Create structured plan data for further processing
    initial_plan = {
        "objective": description,
        "agent_analysis": agent_plan_response,
        "target_file": file,
        "language": language,
        "type": type,
        "skip_chat": skip_chat
    }
    
    # Step 2: Interactive Chat (optional)
    if not skip_chat:
        refined_plan = chat_with_agent(description, initial_plan)
        if refined_plan is None:
            return
    else:
        refined_plan = initial_plan
    
    # Step 3: Confirmation
    if not confirm_execution():
        click.echo(click.style("[CANCELLED] Operation cancelled.", fg="red"))
        return
    
    # Step 4: Agent Execution
    click.echo(click.style("\n[EXECUTING] Agent executing the plan...", fg="green", bold=True))
    
    try:
        # Let the agent execute the code generation with context from planning
        execution_prompt = f"""Based on our planning discussion, please generate the code for:
        
        Objective: {description}
        Type: {type or 'Auto-detect'}
        Target file: {file or 'To be determined'}
        Language: {language or 'Auto-detect'}
        
        Context from planning: {refined_plan.get('agent_analysis', '')}
        
        Please generate the actual code and write it to the appropriate file.
        Make sure to use the FileSystemTool to create/modify files as needed.
        """
        
        execution_result = agent.process_query(execution_prompt)
        click.echo(click.style("[AGENT EXECUTION]", fg="blue", bold=True))
        click.echo(execution_result)
        
        # Also offer to save code manually if the agent provided code content
        if "```" in execution_result or "def " in execution_result or "class " in execution_result:
            save_manually = click.confirm("\nWould you like to manually save the generated code to a file?")
            if save_manually:
                if not file:
                    file = interactive_prompt("Enter filename:")
                
                # Extract code from agent response (simple heuristic)
                code_content = execution_result
                if "```" in execution_result:
                    # Try to extract code block
                    parts = execution_result.split("```")
                    if len(parts) >= 3:
                        # Get the code block (skip language identifier)
                        code_content = parts[1]
                        if "\n" in code_content:
                            lines = code_content.split("\n")
                            if lines[0].strip() in ['python', 'py', 'javascript', 'js', 'java', 'cpp', 'c']:
                                code_content = "\n".join(lines[1:])
                
                fs_tool = FileSystemTool()
                write_result = fs_tool.write_file(file, code_content)
                
                if write_result.get("success"):
                    click.echo(click.style(f"[SUCCESS] Code saved to {file}", fg="green"))
                else:
                    click.echo(click.style(f"[ERROR] Error saving file: {write_result.get('error')}", fg="red"))
        
        click.echo(click.style("\n[COMPLETE] Code generation session completed!", fg="green", bold=True))
            
    except Exception as e:
        click.echo(click.style(f"[ERROR] Error during agent execution: {str(e)}", fg="red"))


def _natural_language_generate(description, type, language, file):
    """Natural language code generation - the new default behavior."""
    click.echo(click.style("[NATURAL LANGUAGE CODE GENERATION]", fg="cyan", bold=True))
    click.echo("=" * 50)
    
    try:
        from ..core.agent import SingleAgent
        from ..tools.filesystem import FileSystemTool
        import os
        import glob
        
        agent = SingleAgent()
        fs_tool = FileSystemTool()
        
        # Step 1: Analyze project context
        click.echo(click.style("[ANALYZING] Understanding your request and project context...", fg="yellow"))
        
        # Get current working directory files for context
        python_files = glob.glob("*.py") + glob.glob("**/*.py", recursive=True)
        project_context = []
        
        # Read existing files for context (limit to first 5 files)
        for py_file in python_files[:5]:
            try:
                result = fs_tool.read_file(py_file)
                if result.get("success"):
                    content = result.get('content', '')
                    # Extract key information: classes, functions, imports
                    project_context.append(f"File: {py_file}\n{content[:800]}...")
            except:
                pass
        
        context_info = "\n\n".join(project_context) if project_context else "No existing Python files found in current directory."
        
        # Step 2: Natural language processing and code generation
        natural_prompt = f"""You are an expert developer assistant. I need you to understand my request and generate appropriate code.
        
        USER REQUEST: "{description}"
        
        CURRENT PROJECT CONTEXT:
        {context_info}
        
        INSTRUCTIONS:
        1. Analyze my request in natural language - understand what I really want
        2. Look at the existing code and determine if I want to:
           - Extend/modify existing classes or functions
           - Create new code that works with existing code  
           - Create completely new standalone code
        3. Generate contextually appropriate code that:
           - Uses proper imports and follows existing patterns
           - Integrates seamlessly with the current codebase
           - Follows Python best practices
        4. Be conversational - explain what you're doing
        5. Provide the code in a clear code block
        
        Please respond naturally, explain your understanding, and then provide the code."""
        
        click.echo(click.style("[AGENT] Processing your request naturally...", fg="blue"))
        agent_response = agent.process_query(natural_prompt)
        
        # Display agent's response
        click.echo("\n" + "=" * 50)
        click.echo(click.style("[AGENT RESPONSE]", fg="green", bold=True))
        click.echo(agent_response)
        
        # Extract and save generated code automatically
        if '```' in agent_response:
            # Try to extract code from response
            code_content = _extract_code_from_response(agent_response)
            if code_content:
                # Auto-suggest filename if not provided
                if not file:
                    suggested_file = _suggest_filename(description, {'language': language or 'python'}, language)
                    click.echo(f"\n[AUTO-SAVE] Saving to: {suggested_file}")
                    file = suggested_file
                
                # Save the code
                with open(file, 'w') as f:
                    f.write(code_content)
                
                click.echo(click.style(f"[SUCCESS] Code saved to {file}", fg="green"))
                
                # Auto-commit to git
                _auto_git_commit(file, description)
            else:
                click.echo(click.style("[INFO] Agent provided guidance but no code to save", fg="yellow"))
        
    except Exception as e:
        click.echo(click.style(f"[ERROR] Natural language generation failed: {str(e)}", fg="red"))
        # Fallback to basic generation
        click.echo("[FALLBACK] Using basic code generation...")
        return _basic_generate(description, type, language, file)


def _extract_code_from_response(response):
    """Extract code content from agent response."""
    # Look for code blocks
    if '```' in response:
        parts = response.split('```')
        for i, part in enumerate(parts):
            if i % 2 == 1:  # Odd indices are code blocks
                # Remove language identifier if present
                lines = part.strip().split('\n')
                if lines and lines[0].strip() in ['python', 'py', 'javascript', 'js', 'java', 'cpp', 'c']:
                    return '\n'.join(lines[1:])
                return part.strip()
    return None


def _basic_generate(description, type, language, file):
    """Fallback basic generation when natural language fails."""
    try:
        from ..tools.code_generator import ContextAwareCodeGenerator
        
        generator = ContextAwareCodeGenerator()
        result = generator.generate_code({
            'description': description,
            'type': type,
            'language': language or 'python'
        })
        
        if result.get('success') and result.get('code'):
            if not file:
                file = _suggest_filename(description, result, language or 'python')
            
            with open(file, 'w') as f:
                f.write(result['code'])
            
            click.echo(click.style(f"[SUCCESS] Code generated and saved to {file}", fg="green"))
            _auto_git_commit(file, description)
        else:
            click.echo(click.style(f"[ERROR] {result.get('error', 'Code generation failed')}", fg="red"))
            
    except Exception as e:
        click.echo(click.style(f"[ERROR] Basic generation failed: {str(e)}", fg="red"))


def _auto_git_commit(filename, description):
    """Auto-commit generated code to git."""
    try:
        import subprocess
        subprocess.run(["git", "add", filename], capture_output=True, timeout=10)
        subprocess.run(["git", "commit", "-m", f"Add generated code: {description}"], capture_output=True, timeout=10)
        click.echo(click.style(f"[COMMIT] Code committed to current branch", fg="cyan"))
    except:
        pass  # Silent fail for git operations


@code.command()
@click.argument('target', required=False)
@click.option('--project', '-p', is_flag=True, help='Generate documentation for entire project')
@click.option('--format', '-f', type=click.Choice(['markdown', 'rst', 'txt']), 
              default='markdown', help='Documentation format')
@click.option('--output', '-o', type=str, help='Output file path')
def docs(target, project, format, output):
    """Generate documentation for code or project."""
    tool = ContextAwareCodeGenerator()
    
    try:
        if project:
            task = "generate project documentation"
        elif target:
            task = f"generate documentation for {target}"
        else:
            task = "generate project documentation"
        
        result = tool.execute(task)
        
        if result.get("success"):
            click.echo(" Generated Documentation")
            click.echo("=" * 50)
            
            doc_content = result.get("documentation", "")
            if doc_content:
                click.echo(doc_content)
                
                # Save to file if requested or suggested
                output_file = output or result.get("filename", "documentation.md")
                if output_file:
                    try:
                        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(doc_content)
                        click.echo(f"\n Documentation saved to: {output_file}")
                    except Exception as e:
                        click.echo(f" Error saving documentation: {str(e)}")
            else:
                click.echo(" No documentation content generated")
                
        else:
            click.echo(f" Error: {result.get('error', 'Documentation generation failed')}")
            
    except Exception as e:
        click.echo(f" Error generating documentation: {str(e)}")


@code.command()
@click.argument('file_or_code', required=False)
@click.option('--suggestions', '-s', is_flag=True, help='Show refactoring suggestions')
def refactor(file_or_code, suggestions):
    """Get refactoring suggestions for code."""
    tool = ContextAwareCodeGenerator()
    
    try:
        if file_or_code:
            task = f"suggest refactoring for {file_or_code}"
        else:
            task = "suggest refactoring for current project"
        
        result = tool.execute(task)
        
        if result.get("success"):
            click.echo(" Refactoring Suggestions")
            click.echo("=" * 50)
            
            suggestions_list = result.get("suggestions", [])
            if suggestions_list:
                for i, suggestion in enumerate(suggestions_list, 1):
                    click.echo(f"{i}. {suggestion}")
            
            priority = result.get("priority", "medium")
            effort = result.get("estimated_effort", "unknown")
            
            click.echo(f"\n Priority: {priority.title()}")
            click.echo(f" Estimated Effort: {effort}")
            
        else:
            click.echo(f" Error: {result.get('error', 'Refactoring analysis failed')}")
            
    except Exception as e:
        click.echo(f" Error analyzing refactoring: {str(e)}")


@code.command()
@click.option('--interactive', '-i', is_flag=True, help='Start interactive code exploration')
def explore(interactive):
    """Explore codebase with context-aware assistance."""
    if interactive:
        click.echo(" Interactive Code Explorer")
        click.echo("=" * 50)
        click.echo("Type commands or questions about your code:")
        click.echo("   'analyze <file>' - Analyze specific file")
        click.echo("   'generate <description>' - Generate code")
        click.echo("   'help' - Show help")
        click.echo("   'exit' - Exit explorer")
        click.echo()
        
        # Simple interactive loop
        analysis_tool = CodeAnalysisTool()
        generator_tool = ContextAwareCodeGenerator()
        
        while True:
            try:
                user_input = click.prompt("code> ", type=str, show_default=False)
                
                if user_input.lower() in ['exit', 'quit']:
                    break
                elif user_input.lower() == 'help':
                    click.echo("Available commands:")
                    click.echo("  analyze <file> - Analyze file")
                    click.echo("  generate <desc> - Generate code")
                    click.echo("  overview - Project overview")
                    click.echo("  exit - Exit explorer")
                elif user_input.lower().startswith('analyze '):
                    file_path = user_input[8:].strip()
                    result = analysis_tool.analyze_file(file_path)
                    if result.get("success"):
                        click.echo(f" {file_path}: {result.get('lines_count', 0)} lines, {len(result.get('functions', []))} functions")
                    else:
                        click.echo(f" {result.get('error', 'Analysis failed')}")
                elif user_input.lower().startswith('generate '):
                    description = user_input[9:].strip()
                    result = generator_tool.execute(f"generate: {description}")
                    if result.get("success"):
                        click.echo(f" Generated {result.get('language', 'code')}:")
                        click.echo(result.get('code', ''))
                    else:
                        click.echo(f" {result.get('error', 'Generation failed')}")
                elif user_input.lower() == 'overview':
                    result = analysis_tool.get_code_overview(".")
                    if result.get("success"):
                        summary = result.get("summary", {})
                        click.echo(f" {summary.get('total_files', 0)} files, {summary.get('total_lines', 0)} lines")
                        click.echo(f" Primary: {summary.get('primary_language', 'Unknown')}")
                    else:
                        click.echo(f" {result.get('error', 'Overview failed')}")
                else:
                    click.echo(" Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        click.echo("\n Goodbye!")
    else:
        # Non-interactive exploration - show project overview
        tool = CodeAnalysisTool()
        result = tool.get_code_overview(".")
        
        if result.get("success"):
            summary = result.get("summary", {})
            click.echo(" Code Exploration")
            click.echo("=" * 30)
            click.echo(f" Primary Language: {summary.get('primary_language', 'Unknown')}")
            click.echo(f" Total Files: {summary.get('total_files', 0)}")
            click.echo(f" Total Lines: {summary.get('total_lines', 0)}")
            
            click.echo(f"\n Use 'metis code explore --interactive' for interactive exploration")
        else:
            click.echo(f" Error: {result.get('error', 'Unknown error')}")


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f}{size_names[i]}"


@code.command()
@click.argument('filepath')
@click.option('-c', '--content', help='Content to write to file')
@click.option('-i', '--input', 'input_file', help='Read content from another file')
@click.option('-e', '--encoding', default='utf-8', help='File encoding')
@click.option('--no-backup', is_flag=True, help="Don't create backup of existing file")
def write(filepath, content, input_file, encoding, no_backup):
    """Write content to a file."""
    tool = FileSystemTool()
    
    # Handle different content sources
    if content:
        write_content = content
    elif input_file:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                write_content = f.read()
        except Exception as e:
            click.echo(click.style(f"Error reading input file: {e}", fg="red"))
            return
    else:
        click.echo(click.style("Error: No content specified. Use -c or -i option.", fg="red"))
        return
    
    try:
        result = tool.write_file(filepath, write_content)
        
        if result.get("success"):
            file_path = Path(result["file_path"])
            size = file_path.stat().st_size
            lines = len(write_content.splitlines())
            
            click.echo(click.style("✓", fg="green") + f" File written: {file_path}")
            click.echo(f"Size: {format_file_size(size)}")
            click.echo(f"Lines: {lines}")
        else:
            click.echo(click.style(f"Error: {result.get('error', 'Unknown error')}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"Error writing file: {e}", fg="red"))


@code.command()
@click.argument('filepath')
@click.option('-e', '--encoding', default='utf-8', help='File encoding')
@click.option('-l', '--lines', help='Line range (e.g., 1-10)')
def read(filepath, encoding, lines):
    """Read and display file contents."""
    tool = FileSystemTool()
    
    try:
        result = tool.read_file(filepath)
        
        if result.get("success"):
            content = result["content"]
            
            # Handle line range
            if lines:
                try:
                    if '-' in lines:
                        start, end = map(int, lines.split('-'))
                        content_lines = content.splitlines()
                        content = '\n'.join(content_lines[start-1:end])
                    else:
                        line_num = int(lines)
                        content_lines = content.splitlines()
                        if 1 <= line_num <= len(content_lines):
                            content = content_lines[line_num-1]
                        else:
                            click.echo(click.style(f"Line {line_num} not found in file", fg="red"))
                            return
                except ValueError:
                    click.echo(click.style("Invalid line range format", fg="red"))
                    return
            
            click.echo(f"File: {filepath}")
            click.echo("─" * 50)
            click.echo(content)
        else:
            click.echo(click.style(f"Error: {result.get('error', 'Unknown error')}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"Error reading file: {e}", fg="red"))


@code.command()
@click.argument('directory', default='.')
@click.option('-a', '--all', is_flag=True, help='Show hidden files')
@click.option('-r', '--recursive', is_flag=True, help='List recursively')
@click.option('-p', '--pattern', help='Filter by pattern (glob style)')
def list(directory, all, recursive, pattern):
    """List files and directories."""
    tool = FileSystemTool()
    
    try:
        result = tool.list_files(directory, show_hidden=all, recursive=recursive, pattern=pattern)
        
        if result.get("success"):
            click.echo(f"Directory: {result['directory']}")
            click.echo()
            
            # Display directories first
            if result["directories"]:
                click.echo(click.style("Directories:", fg="blue", bold=True))
                for dir_info in result["directories"]:
                    contents = f"({dir_info['contents_count']} items)" if isinstance(dir_info['contents_count'], int) else ""
                    click.echo(f"  📁 {dir_info['name']} {contents}")
                click.echo()
            
            # Display files
            if result["files"]:
                click.echo(click.style("Files:", fg="yellow", bold=True))
                for file_info in result["files"]:
                    size = format_file_size(file_info['size'])
                    modified = file_info.get('modified', '')
                    click.echo(f"  📄 {file_info['name']} ({size})")
        else:
            click.echo(click.style(f"Error: {result.get('error', 'Unknown error')}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"Error listing files: {e}", fg="red"))


@code.command()
@click.argument('pattern')
@click.option('-d', '--directory', default='.', help='Directory to search in')
@click.option('-c', '--content', is_flag=True, help='Search in file contents')
@click.option('-i', '--case-insensitive', is_flag=True, help='Case insensitive search')
@click.option('-t', '--file-types', help='File types to search (comma-separated)')
def search(pattern, directory, content, case_insensitive, file_types):
    """Search for files by name or content."""
    tool = FileSystemTool()
    
    file_types_list = file_types.split(',') if file_types else None
    
    try:
        if content:
            result = tool.search_files(directory, pattern=pattern, 
                                     search_content=True, 
                                     case_sensitive=not case_insensitive,
                                     file_types=file_types_list)
        else:
            result = tool.search_files(directory, pattern=pattern,
                                     case_sensitive=not case_insensitive,
                                     file_types=file_types_list)
        
        if result.get("success"):
            matches = result.get("matches", [])
            
            if not matches:
                click.echo("No matches found.")
                return
            
            click.echo(f"Found {len(matches)} match(es):")
            click.echo()
            
            for match in matches:
                if content and "line" in match:
                    click.echo(f"📄 {match['file']}:{match['line']} - {match['content']}")
                else:
                    click.echo(f"📄 {match['file']}")
        else:
            click.echo(click.style(f"Error: {result.get('error', 'Unknown error')}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"Error searching: {e}", fg="red"))


@code.command()
@click.argument('directory', default='.')
@click.option('-d', '--depth', type=int, help='Maximum depth to display')
@click.option('-a', '--all', is_flag=True, help='Show hidden files')
def tree(directory, depth, all):
    """Display directory tree structure."""
    tool = FileSystemTool()
    
    # Set default depth if not specified
    if depth is None:
        depth = 3
    
    try:
        result = tool.get_tree(directory, max_depth=depth, show_hidden=all)
        
        if result.get("success"):
            tree_data = result["tree"]
            
            def format_tree_display(tree_dict, prefix="", is_last=True):
                """Recursively display directory tree."""
                if not isinstance(tree_dict, dict):
                    return
                
                name = tree_dict.get("name", "")
                is_dir = tree_dict.get("type") == "directory"
                
                if name:
                    connector = "└── " if is_last else "├── "
                    icon = "[DIR]" if is_dir else "[FILE]"
                    click.echo(f"{prefix}{connector}{icon} {name}")
                
                children = tree_dict.get("children", [])
                if children and is_dir:
                    extension = "    " if is_last else "│   "
                    new_prefix = prefix + extension
                    
                    for i, child in enumerate(children):
                        is_last_child = i == len(children) - 1
                        format_tree_display(child, new_prefix, is_last_child)
            
            click.echo(f"Directory tree: {directory}")
            click.echo("─" * 50)
            format_tree_display(tree_data)
        else:
            click.echo(click.style(f"Error: {result.get('error', 'Unknown error')}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"Error generating tree: {e}", fg="red"))


# Interactive helper functions
def get_agent():
    """Get a configured Metis agent instance."""
    return SingleAgent()

def interactive_prompt(question):
    """Get user input with a styled prompt."""
    return click.prompt(click.style(f"[INPUT] {question}", fg="cyan"))

def confirm_execution():
    """Confirm if user wants to proceed with execution."""
    return click.confirm(click.style("[CONFIRM] Proceed with execution?", fg="yellow"))

def _suggest_filename(description, result, language):
    """Suggest a filename based on the code generation context."""
    import re
    
    # Try to extract meaningful name from description
    desc_lower = description.lower()
    
    # Look for specific indicators
    if "test" in desc_lower or "unit test" in desc_lower:
        base = "test_"
        if "calculator" in desc_lower:
            base += "calculator"
        elif result.get("class_name"):
            base += result["class_name"].lower()
        else:
            # Extract key words from description
            words = re.findall(r'\b\w+\b', desc_lower)
            meaningful_words = [w for w in words if w not in ['add', 'create', 'generate', 'for', 'the', 'a', 'an', 'to', 'of', 'in', 'with']]
            if meaningful_words:
                base += "_".join(meaningful_words[:2])
            else:
                base += "code"
    elif result.get("class_name"):
        base = result["class_name"].lower()
    elif result.get("function_name"):
        base = result["function_name"].lower()
    else:
        # Generate from description
        words = re.findall(r'\b\w+\b', desc_lower)
        meaningful_words = [w for w in words if w not in ['add', 'create', 'generate', 'for', 'the', 'a', 'an', 'to', 'of', 'in', 'with']]
        if meaningful_words:
            base = "_".join(meaningful_words[:2])
        else:
            base = "generated_code"
    
    # Determine extension
    lang = (language or "").lower()
    if lang in ["python", "py"] or not lang:
        ext = ".py"
    elif lang in ["javascript", "js"]:
        ext = ".js"
    elif lang in ["java"]:
        ext = ".java"
    elif lang in ["cpp", "c++"]:
        ext = ".cpp"
    elif lang in ["c"]:
        ext = ".c"
    else:
        ext = ".py"  # Default to Python
    
    return base + ext


def _create_feature_branch(branch_name, auto_branch, description):
    """Create a feature branch for code generation work."""
    from ..tools.git_integration import GitIntegrationTool
    import subprocess
    import re
    from datetime import datetime
    
    # Check if we're in a git repository
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            click.echo(click.style("[INFO] Not in a git repository, skipping branch creation.", fg="yellow"))
            return True  # Continue with code generation
    except:
        click.echo(click.style("[INFO] Git not available, skipping branch creation.", fg="yellow"))
        return True  # Continue with code generation
    
    # Generate branch name
    if branch_name:
        new_branch = branch_name
    elif auto_branch:
        # Generate branch name from description
        safe_desc = re.sub(r'[^\w\s-]', '', description.lower())
        safe_desc = re.sub(r'\s+', '-', safe_desc.strip())
        if len(safe_desc) > 30:
            safe_desc = safe_desc[:30]
        timestamp = datetime.now().strftime("%m%d-%H%M")
        new_branch = f"feature/{safe_desc}-{timestamp}"
    else:
        return True  # No branch requested
    
    # Create the branch using direct git commands for reliability
    try:
        # Create and switch to the new branch
        result = subprocess.run(
            ["git", "checkout", "-b", new_branch],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            click.echo(click.style(f"[BRANCH] Created and switched to branch '{new_branch}'", fg="green"))
            return True
        else:
            # If branch already exists, try to switch to it
            switch_result = subprocess.run(
                ["git", "checkout", new_branch],
                capture_output=True,
                text=True,
                timeout=10
            )
            if switch_result.returncode == 0:
                click.echo(click.style(f"[BRANCH] Switched to existing branch '{new_branch}'", fg="green"))
                return True
            else:
                click.echo(click.style(f"[ERROR] Branch creation failed: {result.stderr.strip()}", fg="red"))
                return click.confirm("Continue with code generation without creating branch?")
                
    except Exception as e:
        click.echo(click.style(f"[ERROR] Branch creation failed: {str(e)}", fg="red"))
        return click.confirm("Continue with code generation without creating branch?")

def chat_with_agent(initial_request, context):
    """Interactive chat loop with the Metis agent."""
    click.echo(click.style("\n[CHAT MODE] Starting conversation with Metis agent...", fg="magenta", bold=True))
    click.echo("Type 'done', 'ready', or 'proceed' to finish planning.")
    click.echo("Type 'quit', 'exit', or 'cancel' to cancel the operation.")
    click.echo("=" * 50)
    
    agent = get_agent()
    
    # Start conversation with context
    conversation_context = f"""Hello! I'm planning to {initial_request}.
    
Current plan context: {context}
    
I want to discuss and refine this plan with you. Please help me think through the approach."""
    
    # Initialize conversation with the agent
    agent_response = agent.process_query(conversation_context)
    click.echo(click.style("[Metis Agent]: ", fg="blue", bold=True) + agent_response)
    
    refined_plan = context.copy()
    
    while True:
        user_input = interactive_prompt("What would you like to discuss or modify?")
        
        if user_input.lower() in ['done', 'ready', 'proceed']:
            break
        elif user_input.lower() in ['quit', 'exit', 'cancel']:
            click.echo(click.style("[CANCELLED] Operation cancelled by user.", fg="red"))
            return None
        else:
            # Get intelligent response from agent
            chat_prompt = f"""The user said: "{user_input}"
            
Context: We are planning {initial_request}
Current plan: {refined_plan}
            
Please respond helpfully and suggest any plan modifications if needed."""
            
            agent_response = agent.process_query(chat_prompt)
            click.echo(click.style("[Metis Agent]: ", fg="blue", bold=True) + agent_response)
            
            # Ask if they want to modify the plan based on the discussion
            modify = click.confirm("Would you like to update the plan based on this discussion?")
            if modify:
                refined_plan['agent_discussion'] = refined_plan.get('agent_discussion', []) + [user_input, agent_response]
    
    return refined_plan


# Export the command group
__all__ = ['code']
