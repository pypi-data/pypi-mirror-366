"""
CmdRx Output Generator

Handles generation of log files, fix scripts, and other output artifacts.
"""

import os
import json
import stat
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console

from .exceptions import OutputError
from .llm import LLMResponse

console = Console()


class OutputGenerator:
    """
    Generates output files including logs and fix scripts.
    """
    
    def __init__(self, log_dir: Path, dry_run: bool = False, verbose: bool = False):
        """
        Initialize output generator.
        
        Args:
            log_dir: Directory for output files
            dry_run: Don't create fix scripts if True
            verbose: Enable verbose output
        """
        self.log_dir = log_dir
        self.dry_run = dry_run
        self.verbose = verbose
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_outputs(
        self, 
        context: Dict[str, Any], 
        analysis_data: Dict[str, Any],
        llm_response: LLMResponse
    ) -> bool:
        """
        Generate all output files.
        
        Args:
            context: Analysis context (command, output, etc.)
            analysis_data: Parsed analysis data
            llm_response: Raw LLM response
            
        Returns:
            True if outputs generated successfully
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Generate log file
            log_file = self._generate_log_file(context, analysis_data, llm_response, timestamp)
            
            # Generate fix script if there are suggested fixes
            fix_script = None
            suggested_fixes = analysis_data.get('suggested_fixes', [])
            if suggested_fixes and not self.dry_run:
                fix_script = self._generate_fix_script(suggested_fixes, timestamp, context)
            
            # Show generated files
            self._show_generated_files(log_file, fix_script)
            
            return True
        
        except Exception as e:
            raise OutputError(f"Failed to generate outputs: {e}")
    
    def _generate_log_file(
        self, 
        context: Dict[str, Any], 
        analysis_data: Dict[str, Any],
        llm_response: LLMResponse,
        timestamp: str
    ) -> Path:
        """Generate detailed log file."""
        
        log_filename = f"cmdrx_analysis_{timestamp}.log"
        log_file = self.log_dir / log_filename
        
        # Prepare log content
        log_content = self._create_log_content(context, analysis_data, llm_response)
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            if self.verbose:
                console.print(f"[blue]Log file created: {log_file}[/blue]")
            
            return log_file
        
        except Exception as e:
            raise OutputError(f"Failed to create log file: {e}")
    
    def _generate_fix_script(
        self, 
        suggested_fixes: List[Dict[str, Any]], 
        timestamp: str,
        context: Dict[str, Any]
    ) -> Path:
        """Generate executable fix script."""
        
        script_filename = f"cmdrx_fix_{timestamp}.sh"
        script_file = self.log_dir / script_filename
        
        # Prepare script content
        script_content = self._create_fix_script_content(suggested_fixes, context)
        
        try:
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Make script executable
            script_file.chmod(script_file.stat().st_mode | stat.S_IEXEC)
            
            if self.verbose:
                console.print(f"[blue]Fix script created: {script_file}[/blue]")
            
            return script_file
        
        except Exception as e:
            raise OutputError(f"Failed to create fix script: {e}")
    
    def _create_log_content(
        self, 
        context: Dict[str, Any], 
        analysis_data: Dict[str, Any],
        llm_response: LLMResponse
    ) -> str:
        """Create comprehensive log file content."""
        
        timestamp = context.get('timestamp', datetime.now().isoformat())
        
        log_parts = [
            "=" * 80,
            "CmdRx Analysis Log",
            "=" * 80,
            f"Timestamp: {timestamp}",
            f"Command: {context.get('command', 'N/A')}",
            f"Return Code: {context.get('return_code', 'N/A')}",
            f"LLM Provider: {llm_response.provider}",
            f"LLM Model: {llm_response.model}",
            f"Response Time: {llm_response.response_time:.2f}s",
            "",
            "SYSTEM INFORMATION",
            "-" * 40,
        ]
        
        # Add system info
        system_info = context.get('system_info', {})
        for key, value in system_info.items():
            log_parts.append(f"{key.title()}: {value}")
        
        log_parts.extend([
            "",
            "COMMAND OUTPUT", 
            "-" * 40,
            context.get('output', 'No output'),
            "",
            "ANALYSIS RESULTS",
            "-" * 40,
        ])
        
        # Add analysis sections
        analysis = analysis_data.get('analysis', 'No analysis provided')
        log_parts.extend([
            f"Status: {analysis_data.get('status', 'unknown').upper()}",
            f"Analysis: {analysis}",
            ""
        ])
        
        # Issues
        issues = analysis_data.get('issues', [])
        if issues:
            log_parts.extend([
                "ISSUES IDENTIFIED",
                "-" * 20,
            ])
            for i, issue in enumerate(issues, 1):
                log_parts.append(f"{i}. {issue}")
            log_parts.append("")
        
        # Troubleshooting steps
        steps = analysis_data.get('troubleshooting_steps', [])
        if steps:
            log_parts.extend([
                "TROUBLESHOOTING STEPS",
                "-" * 25,
            ])
            for step in steps:
                step_num = step.get('step', '?')
                description = step.get('description', 'No description')
                command = step.get('command', '')
                explanation = step.get('explanation', '')
                
                log_parts.append(f"Step {step_num}: {description}")
                if command:
                    log_parts.append(f"  Command: {command}")
                if explanation:
                    log_parts.append(f"  Explanation: {explanation}")
                log_parts.append("")
        
        # Suggested fixes
        fixes = analysis_data.get('suggested_fixes', [])
        if fixes:
            log_parts.extend([
                "SUGGESTED FIXES",
                "-" * 15,
            ])
            for i, fix in enumerate(fixes, 1):
                description = fix.get('description', 'No description')
                commands = fix.get('commands', [])
                risk_level = fix.get('risk_level', 'unknown')
                explanation = fix.get('explanation', '')
                
                log_parts.append(f"Fix {i}: {description}")
                log_parts.append(f"  Risk Level: {risk_level.upper()}")
                if commands:
                    log_parts.append("  Commands:")
                    for cmd in commands:
                        log_parts.append(f"    {cmd}")
                if explanation:
                    log_parts.append(f"  Explanation: {explanation}")
                log_parts.append("")
        
        # Additional info
        additional_info = analysis_data.get('additional_info', '')
        if additional_info:
            log_parts.extend([
                "ADDITIONAL INFORMATION",
                "-" * 25,
                additional_info,
                ""
            ])
        
        # Raw LLM response
        if llm_response.usage:
            log_parts.extend([
                "LLM USAGE INFORMATION",
                "-" * 22,
                json.dumps(llm_response.usage, indent=2),
                ""
            ])
        
        log_parts.extend([
            "RAW LLM RESPONSE",
            "-" * 17,
            llm_response.content,
            "",
            "=" * 80,
            f"End of CmdRx Analysis Log - {timestamp}",
            "=" * 80
        ])
        
        return "\n".join(log_parts)
    
    def _create_fix_script_content(
        self, 
        suggested_fixes: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> str:
        """Create fix script content."""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        command = context.get('command', 'unknown')
        
        script_parts = [
            "#!/bin/bash",
            "#",
            "# CmdRx Generated Fix Script",
            f"# Generated: {timestamp}",
            f"# Original Command: {command}",
            "#",
            "# WARNING: This script contains suggested fixes generated by AI.",
            "# Review all commands carefully before execution.",
            "# Some commands may:",
            "#   - Modify system configuration",
            "#   - Restart services",
            "#   - Delete or modify files",
            "#   - Require administrative privileges",
            "#",
            "# Usage: bash cmdrx_fix_<timestamp>.sh",
            "#",
            "",
            "set -e  # Exit on any error",
            "set -u  # Exit on undefined variables",
            "",
            "# Colors for output",
            'RED="\\033[31m"',
            'GREEN="\\033[32m"',
            'YELLOW="\\033[33m"',
            'BLUE="\\033[34m"',
            'NC="\\033[0m"  # No Color',
            "",
            "# Function to ask for confirmation",
            "confirm() {",
            '    echo -e "${YELLOW}$1${NC}"',
            '    read -p "Do you want to continue? (y/N): " -n 1 -r',
            '    echo',
            '    if [[ ! $REPLY =~ ^[Yy]$ ]]; then',
            '        echo -e "${RED}Aborted.${NC}"',
            '        exit 1',
            '    fi',
            "}",
            "",
            "# Function to run command with confirmation",
            "run_command() {",
            '    echo -e "${BLUE}About to run: $1${NC}"',
            '    confirm "This will execute the above command."',
            '    echo -e "${GREEN}Executing: $1${NC}"',
            '    eval "$1"',
            '    echo -e "${GREEN}Command completed.${NC}"',
            '    echo',
            "}",
            "",
            'echo -e "${BLUE}CmdRx Fix Script${NC}"',
            'echo -e "${YELLOW}Generated fixes for command: ' + command + '${NC}"',
            'echo',
        ]
        
        # Add each fix as a section
        for i, fix in enumerate(suggested_fixes, 1):
            description = fix.get('description', 'No description')
            commands = fix.get('commands', [])
            risk_level = fix.get('risk_level', 'unknown')
            explanation = fix.get('explanation', '')
            
            risk_colors = {
                'low': '${GREEN}',
                'medium': '${YELLOW}',
                'high': '${RED}'
            }
            risk_color = risk_colors.get(risk_level.lower(), '${YELLOW}')
            
            script_parts.extend([
                f"# Fix {i}: {description}",
                f"echo -e \"{risk_color}Fix {i}: {description}${{NC}}\"",
                f"echo -e \"Risk Level: {risk_color}{risk_level.upper()}${{NC}}\"",
            ])
            
            if explanation:
                script_parts.append(f"echo \"Explanation: {explanation}\"")
            
            script_parts.append("echo")
            
            if commands:
                for j, cmd in enumerate(commands, 1):
                    # Escape quotes and special characters for bash
                    escaped_cmd = cmd.replace('"', '\\"').replace('$', '\\$')
                    script_parts.append(f'run_command "{escaped_cmd}"')
            else:
                script_parts.append('echo -e "${YELLOW}No commands provided for this fix.${NC}"')
            
            script_parts.append("echo")
        
        script_parts.extend([
            'echo -e "${GREEN}All fixes completed successfully!${NC}"',
            'echo -e "${BLUE}Check the system status to verify the fixes worked as expected.${NC}"',
        ])
        
        return "\n".join(script_parts)
    
    def _show_generated_files(self, log_file: Optional[Path], fix_script: Optional[Path]) -> None:
        """Show information about generated files."""
        
        console.print("\n[bold]Generated Files:[/bold]")
        
        if log_file:
            file_size = log_file.stat().st_size
            console.print(f"📄 Log file: [cyan]{log_file}[/cyan] ({file_size} bytes)")
        
        if fix_script:
            console.print(f"🔧 Fix script: [green]{fix_script}[/green] (executable)")
            console.print(f"   Run with: [yellow]bash {fix_script}[/yellow]")
        elif self.dry_run:
            console.print("[yellow]Fix script generation skipped (dry run mode)[/yellow]")
        
        console.print(f"📁 All files saved to: [blue]{self.log_dir}[/blue]")