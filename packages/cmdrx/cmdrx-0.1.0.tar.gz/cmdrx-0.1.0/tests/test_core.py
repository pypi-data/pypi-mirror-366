"""
Tests for CmdRx core functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import json

from cmdrx.core import CmdRxCore
from cmdrx.config import ConfigManager
from cmdrx.llm import LLMResponse
from cmdrx.exceptions import ConfigurationError, LLMError


class TestCmdRxCore:
    """Test CmdRx core functionality."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock configuration manager."""
        config_manager = Mock(spec=ConfigManager)
        config_manager.get_config.return_value = {
            'llm_provider': 'openai',
            'llm_model': 'gpt-4',
            'llm_base_url': 'https://api.openai.com/v1',
            'llm_auth_type': 'api_key',
            'llm_timeout': 30,
            'log_directory': '~/cmdrx_logs',
            'verbose': False,
            'auto_fix_scripts': True,
            'command_timeout': 30
        }
        config_manager.get_llm_credentials.return_value = {
            'api_key': 'test-api-key'
        }
        return config_manager
    
    @pytest.fixture
    def mock_llm_provider(self):
        """Create a mock LLM provider."""
        llm_provider = Mock()
        response = LLMResponse(
            content=json.dumps({
                "analysis": "Test analysis",
                "status": "info",
                "issues": ["Test issue"],
                "troubleshooting_steps": [
                    {
                        "step": 1,
                        "description": "Test step",
                        "command": "test command",
                        "explanation": "Test explanation"
                    }
                ],
                "suggested_fixes": [
                    {
                        "description": "Test fix",
                        "commands": ["fix command"],
                        "risk_level": "low",
                        "explanation": "Test fix explanation"
                    }
                ],
                "additional_info": "Test additional info"
            }),
            model="gpt-4",
            response_time=1.5,
            provider="openai"
        )
        llm_provider.analyze.return_value = response
        return llm_provider
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary log directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @patch('cmdrx.core.ConfigManager')
    @patch('cmdrx.core.LLMProvider')
    @patch('cmdrx.core.OutputGenerator')
    def test_core_initialization(
        self, 
        mock_output_gen, 
        mock_llm_provider_class, 
        mock_config_manager_class,
        mock_config_manager,
        temp_log_dir
    ):
        """Test CmdRx core initialization."""
        mock_config_manager_class.return_value = mock_config_manager
        mock_llm_provider_class.return_value = Mock()
        mock_output_gen.return_value = Mock()
        
        core = CmdRxCore(verbose=True, log_dir=str(temp_log_dir))
        
        assert core.verbose is True
        assert core.log_dir == temp_log_dir
        mock_config_manager_class.assert_called_once()
        mock_llm_provider_class.assert_called_once_with(mock_config_manager)
    
    @patch('cmdrx.core.ConfigManager')
    @patch('cmdrx.core.LLMProvider')
    @patch('cmdrx.core.OutputGenerator')
    def test_analyze_output_success(
        self, 
        mock_output_gen_class, 
        mock_llm_provider_class, 
        mock_config_manager_class,
        mock_config_manager,
        mock_llm_provider,
        temp_log_dir
    ):
        """Test successful output analysis."""
        mock_config_manager_class.return_value = mock_config_manager
        mock_llm_provider_class.return_value = mock_llm_provider
        
        mock_output_gen = Mock()
        mock_output_gen.generate_outputs.return_value = True
        mock_output_gen_class.return_value = mock_output_gen
        
        core = CmdRxCore(log_dir=str(temp_log_dir))
        
        result = core.analyze_output(
            command="systemctl status httpd",
            output="● httpd.service - The Apache HTTP Server\n   Loaded: loaded",
            return_code=0
        )
        
        assert result is True
        mock_llm_provider.analyze.assert_called_once()
        mock_output_gen.generate_outputs.assert_called_once()
    
    @patch('cmdrx.core.ConfigManager')
    @patch('cmdrx.core.LLMProvider')
    @patch('cmdrx.core.OutputGenerator')
    def test_analyze_output_llm_error(
        self, 
        mock_output_gen_class, 
        mock_llm_provider_class, 
        mock_config_manager_class,
        mock_config_manager,
        temp_log_dir
    ):
        """Test LLM error handling during analysis."""
        mock_config_manager_class.return_value = mock_config_manager
        
        mock_llm_provider = Mock()
        mock_llm_provider.analyze.side_effect = Exception("API Error")
        mock_llm_provider_class.return_value = mock_llm_provider
        
        mock_output_gen_class.return_value = Mock()
        
        core = CmdRxCore(log_dir=str(temp_log_dir))
        
        with pytest.raises(LLMError):
            core.analyze_output(
                command="systemctl status httpd",
                output="test output",
                return_code=1
            )
    
    def test_generate_prompt(self, mock_config_manager, temp_log_dir):
        """Test prompt generation."""
        with patch('cmdrx.core.ConfigManager') as mock_config_manager_class, \
             patch('cmdrx.core.LLMProvider') as mock_llm_provider_class, \
             patch('cmdrx.core.OutputGenerator') as mock_output_gen_class:
            
            mock_config_manager_class.return_value = mock_config_manager
            mock_llm_provider_class.return_value = Mock()
            mock_output_gen_class.return_value = Mock()
            
            core = CmdRxCore(log_dir=str(temp_log_dir))
            
            context = {
                'command': 'systemctl status httpd',
                'output': 'test output',
                'return_code': 1,
                'timestamp': '2024-01-01T12:00:00',
                'system_info': {'os': 'Linux'}
            }
            
            prompt = core._generate_prompt(context)
            
            assert 'systemctl status httpd' in prompt
            assert 'test output' in prompt
            assert 'Exit code: 1' in prompt
            assert 'JSON format' in prompt
    
    def test_system_info_generation(self, mock_config_manager, temp_log_dir):
        """Test system information gathering."""
        with patch('cmdrx.core.ConfigManager') as mock_config_manager_class, \
             patch('cmdrx.core.LLMProvider') as mock_llm_provider_class, \
             patch('cmdrx.core.OutputGenerator') as mock_output_gen_class:
            
            mock_config_manager_class.return_value = mock_config_manager
            mock_llm_provider_class.return_value = Mock()
            mock_output_gen_class.return_value = Mock()
            
            core = CmdRxCore(log_dir=str(temp_log_dir))
            
            system_info = core._get_system_info()
            
            assert isinstance(system_info, dict)
            # Should have some basic system information
            assert len(system_info) > 0