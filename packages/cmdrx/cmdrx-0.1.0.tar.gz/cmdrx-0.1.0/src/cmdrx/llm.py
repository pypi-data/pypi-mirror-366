"""
CmdRx LLM Provider Module

Handles communication with various LLM services including OpenAI, Anthropic, Grok, and custom providers.
"""

import json
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, TYPE_CHECKING
import requests
from openai import OpenAI

from .exceptions import LLMError, ConfigurationError

if TYPE_CHECKING:
    from .config import ConfigManager


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    response_time: float = 0.0
    provider: str = ""


class LLMProvider:
    """
    Handles communication with LLM providers.
    """
    
    def __init__(self, config_manager: 'ConfigManager'):
        """
        Initialize LLM provider.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.credentials = config_manager.get_llm_credentials()
        
        # Validate configuration
        self._validate_config()
        
        # Initialize client based on provider
        self.provider = self.config.get('llm_provider', 'openai')
        self.client = self._create_client()
    
    def analyze(self, prompt: str) -> LLMResponse:
        """
        Send analysis request to LLM.
        
        Args:
            prompt: The analysis prompt
            
        Returns:
            LLM response
        """
        start_time = time.time()
        
        try:
            if self.provider in ['openai', 'grok', 'custom']:
                response = self._analyze_openai_compatible(prompt)
            elif self.provider == 'anthropic':
                response = self._analyze_anthropic(prompt)
            else:
                raise LLMError(f"Unsupported provider: {self.provider}")
            
            response.response_time = time.time() - start_time
            response.provider = self.provider
            
            return response
        
        except Exception as e:
            raise LLMError(f"LLM analysis failed: {e}")
    
    def _validate_config(self) -> None:
        """Validate LLM configuration."""
        provider = self.config.get('llm_provider')
        if not provider:
            raise ConfigurationError("No LLM provider configured")
        
        model = self.config.get('llm_model')
        if not model:
            raise ConfigurationError("No LLM model configured")
        
        # Check for required credentials
        if provider in ['openai', 'anthropic', 'grok']:
            if 'api_key' not in self.credentials:
                raise ConfigurationError(f"API key required for {provider}")
        elif provider == 'custom':
            auth_type = self.config.get('llm_auth_type', 'none')
            if auth_type == 'api_key' and 'api_key' not in self.credentials:
                raise ConfigurationError("API key required for custom provider")
            elif auth_type == 'bearer_token' and 'bearer_token' not in self.credentials:
                raise ConfigurationError("Bearer token required for custom provider")
        
        # Validate base URL for custom providers
        if provider == 'custom':
            base_url = self.config.get('llm_base_url')
            if not base_url:
                raise ConfigurationError("Base URL required for custom provider")
    
    def _create_client(self) -> OpenAI:
        """Create OpenAI-compatible client."""
        base_url = self.config.get('llm_base_url')
        api_key = self.credentials.get('api_key', 'not-needed')
        timeout = self.config.get('llm_timeout', 30)
        
        # Provider-specific base URLs
        if self.provider == 'openai':
            base_url = 'https://api.openai.com/v1'
        elif self.provider == 'grok':
            base_url = 'https://api.x.ai/v1'
        elif self.provider == 'custom' and not base_url:
            raise ConfigurationError("Base URL required for custom provider")
        
        return OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout
        )
    
    def _analyze_openai_compatible(self, prompt: str) -> LLMResponse:
        """Analyze using OpenAI-compatible API."""
        model = self.config.get('llm_model', 'gpt-4')
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are CmdRx, an expert system administrator AI assistant. Provide detailed, accurate troubleshooting information."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent, focused responses
                max_tokens=2000,
            )
            
            content = response.choices[0].message.content
            usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            } if response.usage else None
            
            return LLMResponse(
                content=content,
                model=model,
                usage=usage
            )
        
        except Exception as e:
            raise LLMError(f"OpenAI-compatible API error: {e}")
    
    def _analyze_anthropic(self, prompt: str) -> LLMResponse:
        """Analyze using Anthropic Claude API."""
        import anthropic
        
        api_key = self.credentials.get('api_key')
        if not api_key:
            raise ConfigurationError("Anthropic API key not configured")
        
        model = self.config.get('llm_model', 'claude-3-sonnet-20240229')
        timeout = self.config.get('llm_timeout', 30)
        
        try:
            client = anthropic.Anthropic(
                api_key=api_key,
                timeout=timeout
            )
            
            message = client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.1,
                system="You are CmdRx, an expert system administrator AI assistant. Provide detailed, accurate troubleshooting information.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = message.content[0].text if message.content else ""
            usage = {
                'input_tokens': message.usage.input_tokens,
                'output_tokens': message.usage.output_tokens,
            } if message.usage else None
            
            return LLMResponse(
                content=content,
                model=model,
                usage=usage
            )
        
        except ImportError:
            raise LLMError("Anthropic library not installed. Install with: pip install anthropic")
        except Exception as e:
            raise LLMError(f"Anthropic API error: {e}")
    
    def test_connection(self) -> bool:
        """
        Test connection to LLM provider.
        
        Returns:
            True if connection successful
        """
        try:
            test_prompt = "Respond with 'OK' if you can read this test message."
            response = self.analyze(test_prompt)
            return bool(response and response.content)
        except Exception:
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the current provider.
        
        Returns:
            Provider information
        """
        return {
            'provider': self.provider,
            'model': self.config.get('llm_model'),
            'base_url': self.config.get('llm_base_url'),
            'auth_type': self.config.get('llm_auth_type'),
            'timeout': self.config.get('llm_timeout'),
            'has_credentials': bool(self.credentials)
        }