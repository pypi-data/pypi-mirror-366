"""
CmdRx Core Module

Main business logic for analyzing command outputs and generating reports.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import ConfigManager
from .llm import LLMProvider, LLMResponse
from .output import OutputGenerator
from .exceptions import CmdRxError, ConfigurationError, LLMError

console = Console()


class CmdRxCore:
    """
    Core CmdRx functionality for analyzing command outputs.
    """
    
    def __init__(
        self, 
        verbose: bool = False, 
        log_dir: Optional[str] = None,
        dry_run: bool = False
    ):
        """
        Initialize CmdRx core.
        
        Args:
            verbose: Enable verbose output
            log_dir: Override default log directory
            dry_run: Don't create fix scripts
        """
        self.verbose = verbose
        self.dry_run = dry_run
        
        # Initialize configuration
        try:
            self.config_manager = ConfigManager()
            self.config = self.config_manager.get_config()
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
        
        # Set up log directory
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = Path(self.config.get('log_directory', '~/cmdrx_logs')).expanduser()
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize LLM provider
        try:
            self.llm_provider = LLMProvider(self.config_manager)
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize LLM provider: {e}")
        
        # Initialize output generator
        self.output_generator = OutputGenerator(
            log_dir=self.log_dir, 
            dry_run=dry_run, 
            verbose=verbose
        )
    
    def analyze_output(
        self, 
        command: str, 
        output: str, 
        return_code: Optional[int] = None
    ) -> bool:
        """
        Analyze command output using configured LLM.
        
        Args:
            command: The original command executed
            output: The command output to analyze
            return_code: The command's exit code (if available)
            
        Returns:
            True if analysis completed successfully
        """
        
        if self.verbose:
            console.print(f"[blue]Starting analysis of command: {command}[/blue]")
        
        # Prepare analysis context
        analysis_context = {
            'command': command,
            'output': output,
            'return_code': return_code,
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_system_info()
        }
        
        # Generate LLM prompt
        prompt = self._generate_prompt(analysis_context)
        
        if self.verbose:
            console.print("[blue]Sending request to LLM...[/blue]")
        
        # Get LLM analysis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Analyzing with AI...", total=None)
            
            try:
                llm_response = self.llm_provider.analyze(prompt)
            except Exception as e:
                raise LLMError(f"LLM analysis failed: {e}")
        
        if self.verbose:
            console.print("[green]✓ LLM analysis complete[/green]")
        
        # Process and display results
        return self._process_llm_response(analysis_context, llm_response)
    
    def _generate_prompt(self, context: Dict[str, Any]) -> str:
        """Generate the prompt for LLM analysis."""
        
        prompt_parts = [
            "You are CmdRx, an expert system administrator AI assistant specialized in Linux/Unix systems.",
            "Analyze the following command output and provide detailed troubleshooting information.",
            "",
            f"Command executed: {context['command']}",
        ]
        
        if context['return_code'] is not None:
            status_desc = "SUCCESS" if context['return_code'] == 0 else "FAILURE"
            prompt_parts.append(f"Exit code: {context['return_code']} ({status_desc})")
        
        # Add system context if available
        system_info = context.get('system_info', {})
        if system_info:
            prompt_parts.extend([
                "",
                "System context:",
                f"- OS: {system_info.get('os', 'Unknown')} {system_info.get('os_version', '')}",
                f"- Architecture: {system_info.get('architecture', 'Unknown')}",
                f"- User: {system_info.get('user', 'Unknown')}",
            ])
        
        prompt_parts.extend([
            "",
            "Command output:",
            "```",
            context['output'],
            "```",
            "",
            "Please provide your analysis in the following JSON format:",
            "{",
            '  "analysis": "Comprehensive analysis of what the output shows and what it means",',
            '  "status": "success|warning|error|info",',
            '  "issues": ["specific", "issues", "identified", "from", "output"],',
            '  "troubleshooting_steps": [',
            '    {',
            '      "step": 1,',
            '      "description": "Clear step description",',
            '      "command": "exact command to run (if applicable)",',
            '      "explanation": "Why this step helps diagnose or resolve the issue"',
            '    }',
            '  ],',
            '  "suggested_fixes": [',
            '    {',
            '      "description": "What this fix accomplishes",',
            '      "commands": ["command1", "command2"],',
            '      "risk_level": "low|medium|high",',
            '      "explanation": "Detailed explanation of the fix and potential impact"',
            '    }',
            '  ],',
            '  "additional_info": "Relevant background information, best practices, or warnings"',
            "}",
            "",
            "Analysis guidelines:",
            "- Provide specific, actionable troubleshooting steps",
            "- Include exact commands when helpful (with proper syntax)",
            "- Clearly categorize risk levels: LOW (safe), MEDIUM (requires caution), HIGH (potential data loss)",
            "- Focus on the most probable root causes based on the error patterns",
            "- Consider common system administration scenarios and solutions",
            "- If successful output, highlight what's working well and any optimization opportunities",
            "- For errors, provide both immediate fixes and preventive measures",
            "- Include relevant log file locations or configuration files to check",
        ])
        
        return "\n".join(prompt_parts)
    
    def _process_llm_response(
        self, 
        context: Dict[str, Any], 
        llm_response: LLMResponse
    ) -> bool:
        """Process LLM response and generate outputs."""
        
        try:
            # Parse JSON response
            analysis_data = json.loads(llm_response.content)
        except json.JSONDecodeError as e:
            if self.verbose:
                console.print(f"[yellow]Failed to parse JSON response: {e}[/yellow]")
                console.print("[yellow]Treating as plain text response[/yellow]")
            
            # Fallback to plain text processing
            analysis_data = {
                "analysis": llm_response.content,
                "status": "info",
                "issues": [],
                "troubleshooting_steps": [],
                "suggested_fixes": [],
                "additional_info": ""
            }
        
        # Display analysis results
        self._display_analysis(analysis_data)
        
        # Generate output files
        return self.output_generator.generate_outputs(context, analysis_data, llm_response)
    
    def _display_analysis(self, analysis_data: Dict[str, Any]) -> None:
        """Display the analysis results to the console."""
        
        # Status indicator
        status = analysis_data.get('status', 'info')
        status_colors = {
            'success': 'green',
            'warning': 'yellow', 
            'error': 'red',
            'info': 'blue'
        }
        status_color = status_colors.get(status, 'blue')
        
        # Main analysis
        console.print(Panel(
            analysis_data.get('analysis', 'No analysis provided'),
            title=f"[{status_color}]Analysis ({status.upper()})[/{status_color}]",
            border_style=status_color
        ))
        
        # Issues identified
        issues = analysis_data.get('issues', [])
        if issues:
            issues_text = "\n".join(f"• {issue}" for issue in issues)
            console.print(Panel(
                issues_text,
                title="[red]Issues Identified[/red]",
                border_style="red"
            ))
        
        # Troubleshooting steps
        steps = analysis_data.get('troubleshooting_steps', [])
        if steps:
            steps_text = []
            for step in steps:
                step_num = step.get('step', '?')
                description = step.get('description', 'No description')
                command = step.get('command', '')
                explanation = step.get('explanation', '')
                
                step_text = f"**{step_num}. {description}**"
                if command:
                    step_text += f"\n   Command: `{command}`"
                if explanation:
                    step_text += f"\n   {explanation}"
                steps_text.append(step_text)
            
            console.print(Panel(
                Markdown("\n\n".join(steps_text)),
                title="[blue]Troubleshooting Steps[/blue]",
                border_style="blue"
            ))
        
        # Suggested fixes
        fixes = analysis_data.get('suggested_fixes', [])
        if fixes:
            fixes_text = []
            for i, fix in enumerate(fixes, 1):
                description = fix.get('description', 'No description')
                commands = fix.get('commands', [])
                risk_level = fix.get('risk_level', 'unknown')
                explanation = fix.get('explanation', '')
                
                risk_colors = {'low': 'green', 'medium': 'yellow', 'high': 'red'}
                risk_color = risk_colors.get(risk_level, 'yellow')
                
                fix_text = f"**Fix {i}: {description}**\n"
                fix_text += f"Risk Level: [{risk_color}]{risk_level.upper()}[/{risk_color}]\n"
                
                if commands:
                    fix_text += "\nCommands:\n"
                    for cmd in commands:
                        fix_text += f"```bash\n{cmd}\n```\n"
                
                if explanation:
                    fix_text += f"\n{explanation}"
                
                fixes_text.append(fix_text)
            
            console.print(Panel(
                Markdown("\n\n---\n\n".join(fixes_text)),
                title="[green]Suggested Fixes[/green]",
                border_style="green"
            ))
        
        # Additional information
        additional_info = analysis_data.get('additional_info', '')
        if additional_info:
            console.print(Panel(
                additional_info,
                title="[cyan]Additional Information[/cyan]",
                border_style="cyan"
            ))
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get basic system information for context."""
        import platform
        import pwd
        
        try:
            return {
                'os': platform.system(),
                'os_version': platform.release(),
                'architecture': platform.machine(),
                'hostname': platform.node(),
                'user': pwd.getpwuid(os.getuid()).pw_name,
                'python_version': platform.python_version(),
            }
        except Exception:
            return {'error': 'Unable to gather system information'}