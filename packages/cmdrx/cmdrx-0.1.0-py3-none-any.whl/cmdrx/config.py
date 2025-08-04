"""
CmdRx Configuration Manager

Handles configuration management including TUI interface and secure credential storage.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import keyring
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .exceptions import ConfigurationError, SecurityError

console = Console()


class ConfigManager:
    """
    Manages CmdRx configuration including LLM providers and credentials.
    """
    
    SERVICE_NAME = "cmdrx"
    CONFIG_FILE = "config.json"
    
    # Predefined LLM providers
    PREDEFINED_PROVIDERS = {
        'openai': {
            'name': 'OpenAI',
            'base_url': 'https://api.openai.com/v1',
            'default_model': 'gpt-4',
            'auth_type': 'api_key',
            'description': 'OpenAI GPT models'
        },
        'anthropic': {
            'name': 'Anthropic Claude',
            'base_url': 'https://api.anthropic.com/v1',
            'default_model': 'claude-3-sonnet-20240229',
            'auth_type': 'api_key',
            'description': 'Anthropic Claude models'
        },
        'grok': {
            'name': 'Grok (xAI)',
            'base_url': 'https://api.x.ai/v1',
            'default_model': 'grok-beta',
            'auth_type': 'api_key', 
            'description': 'xAI Grok models'
        }
    }
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path.home() / '.config' / 'cmdrx'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / self.CONFIG_FILE
        
        # Load existing configuration
        self._config = self._load_config()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self._config.copy()
    
    def run_tui(self) -> None:
        """Run the text-based user interface for configuration."""
        console.print(Panel.fit(
            "[bold blue]CmdRx Configuration[/bold blue]\n"
            "Configure your LLM provider and settings",
            border_style="blue"
        ))
        
        while True:
            choice = self._show_main_menu()
            
            if choice == '1':
                self._configure_llm_provider()
            elif choice == '2':
                self._configure_settings()
            elif choice == '3':
                self._test_configuration()
            elif choice == '4':
                self._show_current_config()
            elif choice == 'q':
                break
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")
        
        console.print("[green]Configuration saved successfully![/green]")
    
    def _show_main_menu(self) -> str:
        """Show main configuration menu."""
        console.print("\n[bold]Main Menu:[/bold]")
        console.print("1. Configure LLM Provider")
        console.print("2. Configure Settings")
        console.print("3. Test Configuration")
        console.print("4. Show Current Configuration")
        console.print("q. Quit")
        
        return Prompt.ask(
            "Choose an option",
            choices=['1', '2', '3', '4', 'q'],
            default='1'
        )
    
    def _configure_llm_provider(self) -> None:
        """Configure LLM provider."""
        console.print("\n[bold]LLM Provider Configuration[/bold]")
        
        # Show available providers
        table = Table(title="Available LLM Providers")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Description", style="white")
        
        provider_choices = list(self.PREDEFINED_PROVIDERS.keys()) + ['custom']
        
        for provider_id in self.PREDEFINED_PROVIDERS:
            provider = self.PREDEFINED_PROVIDERS[provider_id]
            table.add_row(provider_id, provider['name'], provider['description'])
        
        table.add_row("custom", "Custom Provider", "Configure a custom LLM endpoint")
        
        console.print(table)
        
        # Get provider choice
        provider_id = Prompt.ask(
            "Select a provider",
            choices=provider_choices,
            default=self._config.get('llm_provider', 'openai')
        )
        
        if provider_id == 'custom':
            self._configure_custom_provider()
        else:
            self._configure_predefined_provider(provider_id)
        
        self._save_config()
    
    def _configure_predefined_provider(self, provider_id: str) -> None:
        """Configure a predefined LLM provider."""
        provider = self.PREDEFINED_PROVIDERS[provider_id]
        
        console.print(f"\n[bold]Configuring {provider['name']}[/bold]")
        
        # Get API key
        current_key = self._get_credential(f"{provider_id}_api_key")
        key_prompt = "API Key"
        if current_key:
            key_prompt += f" (current: {current_key[:8]}...)"
        
        api_key = Prompt.ask(key_prompt, password=True)
        if api_key:
            self._store_credential(f"{provider_id}_api_key", api_key)
        
        # Get model (optional override)
        current_model = self._config.get('llm_model', provider['default_model'])
        model = Prompt.ask(
            f"Model name (default: {provider['default_model']})",
            default=current_model
        )
        
        # Update configuration
        self._config.update({
            'llm_provider': provider_id,
            'llm_model': model,
            'llm_base_url': provider['base_url'],
            'llm_auth_type': provider['auth_type']
        })
        
        console.print(f"[green]✓ {provider['name']} configured successfully[/green]")
    
    def _configure_custom_provider(self) -> None:
        """Configure a custom LLM provider."""
        console.print("\n[bold]Custom LLM Provider Configuration[/bold]")
        
        # Base URL
        base_url = Prompt.ask(
            "Base URL (e.g., http://localhost:11434/v1)",
            default=self._config.get('llm_base_url', 'http://localhost:11434/v1')
        )
        
        # Model name
        model = Prompt.ask(
            "Model name",
            default=self._config.get('llm_model', 'llama2')
        )
        
        # Authentication type
        auth_type = Prompt.ask(
            "Authentication type",
            choices=['none', 'api_key', 'bearer_token'],
            default=self._config.get('llm_auth_type', 'none')
        )
        
        # Authentication credentials
        if auth_type != 'none':
            if auth_type == 'api_key':
                cred_name = "API Key"
                cred_key = "custom_api_key"
            else:
                cred_name = "Bearer Token"
                cred_key = "custom_bearer_token"
            
            current_cred = self._get_credential(cred_key)
            cred_prompt = cred_name
            if current_cred:
                cred_prompt += f" (current: {current_cred[:8]}...)"
            
            credential = Prompt.ask(cred_prompt, password=True)
            if credential:
                self._store_credential(cred_key, credential)
        
        # Request timeout
        timeout = Prompt.ask(
            "Request timeout (seconds)",
            default=str(self._config.get('llm_timeout', 30))
        )
        
        # Update configuration
        self._config.update({
            'llm_provider': 'custom',
            'llm_base_url': base_url,
            'llm_model': model,
            'llm_auth_type': auth_type,
            'llm_timeout': int(timeout)
        })
        
        console.print("[green]✓ Custom provider configured successfully[/green]")
    
    def _configure_settings(self) -> None:
        """Configure general settings."""
        console.print("\n[bold]General Settings[/bold]")
        
        # Log directory
        log_dir = Prompt.ask(
            "Log directory",
            default=self._config.get('log_directory', '~/cmdrx_logs')
        )
        
        # Verbosity
        verbose = Confirm.ask(
            "Enable verbose output by default?",
            default=self._config.get('verbose', False)
        )
        
        # Auto-create fix scripts
        auto_fix_scripts = Confirm.ask(
            "Auto-create fix scripts?",
            default=self._config.get('auto_fix_scripts', True)
        )
        
        # Command timeout
        command_timeout = Prompt.ask(
            "Command execution timeout (seconds)",
            default=str(self._config.get('command_timeout', 30))
        )
        
        # Update configuration
        self._config.update({
            'log_directory': log_dir,
            'verbose': verbose,
            'auto_fix_scripts': auto_fix_scripts,
            'command_timeout': int(command_timeout)
        })
        
        console.print("[green]✓ Settings updated successfully[/green]")
        self._save_config()
    
    def _test_configuration(self) -> None:
        """Test the current configuration."""
        console.print("\n[bold]Testing Configuration[/bold]")
        
        try:
            # Test LLM provider configuration
            from .llm import LLMProvider
            
            console.print("Testing LLM provider connection...")
            llm_provider = LLMProvider(self)
            
            # Simple test prompt
            test_response = llm_provider.analyze("Test prompt: respond with 'OK' if you can read this.")
            
            if test_response and test_response.content:
                console.print("[green]✓ LLM provider test successful[/green]")
                console.print(f"Response: {test_response.content[:100]}...")
            else:
                console.print("[red]✗ LLM provider test failed - no response[/red]")
        
        except Exception as e:
            console.print(f"[red]✗ LLM provider test failed: {e}[/red]")
        
        # Test log directory
        try:
            log_dir = Path(self._config.get('log_directory', '~/cmdrx_logs')).expanduser()
            log_dir.mkdir(parents=True, exist_ok=True)
            
            test_file = log_dir / 'test.txt'
            test_file.write_text('test')
            test_file.unlink()
            
            console.print(f"[green]✓ Log directory accessible: {log_dir}[/green]")
        except Exception as e:
            console.print(f"[red]✗ Log directory test failed: {e}[/red]")
    
    def _show_current_config(self) -> None:
        """Show current configuration."""
        console.print("\n[bold]Current Configuration[/bold]")
        
        # Create configuration table
        table = Table(title="Configuration Settings")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        # Safe config (no sensitive data)
        safe_config = self._config.copy()
        
        for key, value in safe_config.items():
            if 'password' in key.lower() or 'key' in key.lower() or 'token' in key.lower():
                continue  # Skip sensitive data
            table.add_row(key, str(value))
        
        console.print(table)
        
        # Show credential status
        console.print("\n[bold]Credential Status:[/bold]")
        provider = self._config.get('llm_provider', 'none')
        
        if provider in self.PREDEFINED_PROVIDERS:
            key_name = f"{provider}_api_key"
            has_key = bool(self._get_credential(key_name))
            status = "[green]✓ Configured[/green]" if has_key else "[red]✗ Missing[/red]"
            console.print(f"API Key: {status}")
        elif provider == 'custom':
            auth_type = self._config.get('llm_auth_type', 'none')
            if auth_type != 'none':
                cred_key = f"custom_{auth_type}"
                has_cred = bool(self._get_credential(cred_key))
                status = "[green]✓ Configured[/green]" if has_cred else "[red]✗ Missing[/red]"
                console.print(f"{auth_type.replace('_', ' ').title()}: {status}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        default_config = {
            'llm_provider': 'openai',
            'llm_model': 'gpt-4',
            'llm_base_url': '',
            'llm_auth_type': 'api_key',
            'llm_timeout': 30,
            'log_directory': '~/cmdrx_logs',
            'verbose': False,
            'auto_fix_scripts': True,
            'command_timeout': 30
        }
        
        if not self.config_file.exists():
            return default_config
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            merged_config = default_config.copy()
            merged_config.update(config)
            return merged_config
        
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load config file: {e}[/yellow]")
            return default_config
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            # Don't save sensitive data to config file
            safe_config = {k: v for k, v in self._config.items() 
                          if not any(x in k.lower() for x in ['password', 'key', 'token'])}
            
            with open(self.config_file, 'w') as f:
                json.dump(safe_config, f, indent=2)
        
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def _store_credential(self, key: str, value: str) -> None:
        """Store credential securely using keyring."""
        try:
            keyring.set_password(self.SERVICE_NAME, key, value)
        except Exception as e:
            raise SecurityError(f"Failed to store credential '{key}': {e}")
    
    def _get_credential(self, key: str) -> Optional[str]:
        """Retrieve credential securely using keyring."""
        try:
            return keyring.get_password(self.SERVICE_NAME, key)
        except Exception as e:
            if self._config.get('verbose', False):
                console.print(f"[yellow]Warning: Could not retrieve credential '{key}': {e}[/yellow]")
            return None
    
    def get_llm_credentials(self) -> Dict[str, str]:
        """Get LLM credentials for the configured provider."""
        provider = self._config.get('llm_provider', 'openai')
        credentials = {}
        
        if provider in self.PREDEFINED_PROVIDERS:
            api_key = self._get_credential(f"{provider}_api_key")
            if api_key:
                credentials['api_key'] = api_key
        elif provider == 'custom':
            auth_type = self._config.get('llm_auth_type', 'none')
            if auth_type == 'api_key':
                api_key = self._get_credential('custom_api_key')
                if api_key:
                    credentials['api_key'] = api_key
            elif auth_type == 'bearer_token':
                token = self._get_credential('custom_bearer_token')
                if token:
                    credentials['bearer_token'] = token
        
        return credentials