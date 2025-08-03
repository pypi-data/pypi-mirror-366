"""Unit tests for FCP provider initialization interface."""

import pytest
import json
from unittest.mock import Mock, MagicMock
from typing import Dict, List
import hypothesis
from hypothesis import given, strategies as st

from flow.providers.interfaces import ConfigField
from flow.providers.fcp.init import FCPInit
from flow.providers.fcp.core.constants import DEFAULT_REGION, SUPPORTED_REGIONS


class TestFCPInit:
    """Test suite for FCPInit class."""
    
    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client with realistic behavior."""
        client = Mock()
        # Set up default responses that mimic real API behavior
        client.request.return_value = []
        return client
    
    @pytest.fixture
    def fcp_init(self, mock_http_client):
        """Create FCPInit instance with mocked dependencies."""
        return FCPInit(mock_http_client)
    
    @pytest.fixture
    def realistic_projects(self):
        """Generate realistic project data."""
        return [
            {"id": "proj-abc123", "name": "ml-research", "created_at": "2024-01-01T00:00:00Z"},
            {"id": "proj-def456", "name": "production-models", "display_name": "Production Models"},
            {"id": "proj-ghi789", "name": "test-project", "description": "Testing environment"}
        ]
    
    @pytest.fixture
    def realistic_ssh_keys(self):
        """Generate realistic SSH key data."""
        return [
            {
                "id": "sshkey_rsa_2048_abc",
                "name": "macbook-pro",
                "fingerprint": "SHA256:abcd1234efgh5678ijkl9012mnop3456qrst7890",
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": "sshkey_ed25519_def",
                "display_name": "workstation",
                "fingerprint": "SHA256:1234567890abcdefghijklmnopqrstuvwxyzABCD",
                "type": "ed25519"
            }
        ]
    
    def test_get_config_fields(self, fcp_init):
        """Test configuration field definitions."""
        fields = fcp_init.get_config_fields()
        
        # Check all required fields are present
        assert 'api_key' in fields
        assert 'project' in fields
        assert 'region' in fields
        assert 'default_ssh_key' in fields
        
        # Verify api_key field
        api_key_field = fields['api_key']
        assert isinstance(api_key_field, ConfigField)
        assert api_key_field.description == "MLFoundry API key"
        assert api_key_field.secret is True
        assert api_key_field.choices is None
        assert api_key_field.default is None
        
        # Verify project field
        project_field = fields['project']
        assert isinstance(project_field, ConfigField)
        assert project_field.description == "Project name"
        assert project_field.secret is False
        assert project_field.choices is None
        assert project_field.default is None
        
        # Verify region field
        region_field = fields['region']
        assert isinstance(region_field, ConfigField)
        assert region_field.description == "Region"
        assert region_field.secret is False
        assert region_field.choices == SUPPORTED_REGIONS
        assert region_field.default == DEFAULT_REGION
        
        # Verify default_ssh_key field
        ssh_key_field = fields['default_ssh_key']
        assert isinstance(ssh_key_field, ConfigField)
        assert ssh_key_field.description == "Default SSH key ID (optional)"
        assert ssh_key_field.secret is False
        assert ssh_key_field.choices is None
        assert ssh_key_field.default is None
    
    def test_validate_config_valid(self, fcp_init):
        """Test validation with valid configuration."""
        config = {
            'api_key': 'mlfoundry_test123',
            'project': 'my-project',
            'region': 'us-central1-a',
            'default_ssh_key': 'sshkey_abc123'
        }
        
        errors = fcp_init.validate_config(config)
        assert errors == []
    
    def test_validate_config_missing_api_key(self, fcp_init):
        """Test validation with missing API key."""
        config = {
            'project': 'my-project',
            'region': 'us-central1-a'
        }
        
        errors = fcp_init.validate_config(config)
        assert "API key is required" in errors
    
    def test_validate_config_invalid_api_key_format(self, fcp_init):
        """Test validation with invalid API key format."""
        config = {
            'api_key': 'invalid_key_format',
            'project': 'my-project',
            'region': 'us-central1-a'
        }
        
        errors = fcp_init.validate_config(config)
        assert "API key should start with 'mlfoundry_'" in errors
    
    def test_validate_config_missing_project(self, fcp_init):
        """Test validation with missing project."""
        config = {
            'api_key': 'mlfoundry_test123',
            'region': 'us-central1-a'
        }
        
        errors = fcp_init.validate_config(config)
        assert "Project is required" in errors
    
    def test_validate_config_invalid_region(self, fcp_init):
        """Test validation with invalid region."""
        config = {
            'api_key': 'mlfoundry_test123',
            'project': 'my-project',
            'region': 'invalid-region'
        }
        
        errors = fcp_init.validate_config(config)
        assert any("Invalid region 'invalid-region'" in error for error in errors)
    
    def test_validate_config_invalid_ssh_key_format(self, fcp_init):
        """Test validation with invalid SSH key format."""
        config = {
            'api_key': 'mlfoundry_test123',
            'project': 'my-project',
            'region': 'us-central1-a',
            'default_ssh_key': 'invalid_format'
        }
        
        errors = fcp_init.validate_config(config)
        assert "SSH key ID should start with 'sshkey_'" in errors
    
    def test_validate_config_whitespace_handling(self, fcp_init):
        """Test validation handles whitespace correctly."""
        config = {
            'api_key': '  mlfoundry_test123  ',
            'project': '  my-project  ',
            'region': '  us-central1-a  ',
            'default_ssh_key': '  sshkey_abc123  '
        }
        
        errors = fcp_init.validate_config(config)
        assert errors == []
    
    def test_list_projects_success(self, fcp_init, mock_http_client):
        """Test successful project listing."""
        # Mock API response
        mock_http_client.request.return_value = [
            {"id": "proj1", "name": "Project One"},
            {"id": "proj2", "display_name": "Project Two"},  # Test display_name fallback
            {"id": "proj3", "name": "Project Three", "display_name": "Ignored"}
        ]
        
        projects = fcp_init.list_projects()
        
        # Verify HTTP request
        mock_http_client.request.assert_called_once_with("GET", "/v2/projects")
        
        # Verify response parsing
        assert len(projects) == 3
        assert projects[0] == {"id": "proj1", "name": "Project One"}
        assert projects[1] == {"id": "proj2", "name": "Project Two"}
        assert projects[2] == {"id": "proj3", "name": "Project Three"}
    
    def test_list_projects_empty_response(self, fcp_init, mock_http_client):
        """Test project listing with empty response."""
        mock_http_client.request.return_value = []
        
        projects = fcp_init.list_projects()
        
        assert projects == []
        mock_http_client.request.assert_called_once_with("GET", "/v2/projects")
    
    def test_list_ssh_keys_without_project(self, fcp_init, mock_http_client):
        """Test SSH key listing without project filter."""
        # Mock API response
        mock_http_client.request.return_value = [
            {"id": "sshkey_1", "name": "Key One", "fingerprint": "aa:bb:cc"},
            {"id": "sshkey_2", "display_name": "Key Two"},  # Test display_name fallback
            {"id": "sshkey_3", "name": "Key Three"}
        ]
        
        ssh_keys = fcp_init.list_ssh_keys()
        
        # Verify HTTP request
        mock_http_client.request.assert_called_once_with("GET", "/v2/ssh-keys", params={})
        
        # Verify response parsing
        assert len(ssh_keys) == 3
        assert ssh_keys[0] == {"id": "sshkey_1", "name": "Key One", "fingerprint": "aa:bb:cc"}
        assert ssh_keys[1] == {"id": "sshkey_2", "name": "Key Two", "fingerprint": ""}
        assert ssh_keys[2] == {"id": "sshkey_3", "name": "Key Three", "fingerprint": ""}
    
    def test_list_ssh_keys_with_project(self, fcp_init, mock_http_client):
        """Test SSH key listing with project filter."""
        mock_http_client.request.return_value = [
            {"id": "sshkey_1", "name": "Project Key"}
        ]
        
        ssh_keys = fcp_init.list_ssh_keys(project_id="my-project")
        
        # Verify HTTP request includes project parameter
        mock_http_client.request.assert_called_once_with(
            "GET", 
            "/v2/ssh-keys", 
            params={"project": "my-project"}
        )
        
        assert len(ssh_keys) == 1
        assert ssh_keys[0]["id"] == "sshkey_1"
    
    def test_list_ssh_keys_empty_response(self, fcp_init, mock_http_client):
        """Test SSH key listing with empty response."""
        mock_http_client.request.return_value = []
        
        ssh_keys = fcp_init.list_ssh_keys()
        
        assert ssh_keys == []
        mock_http_client.request.assert_called_once_with("GET", "/v2/ssh-keys", params={})
    
    # Property-based tests
    @given(st.text(min_size=1, max_size=100))
    def test_validate_config_api_key_prefix_property(self, api_key):
        """Property test: Any string not starting with 'mlfoundry_' should fail."""
        # Create FCPInit instance inline to avoid fixture issues with hypothesis
        mock_http = Mock()
        fcp_init = FCPInit(mock_http)
        
        if not api_key.startswith('mlfoundry_'):
            config = {
                'api_key': api_key,
                'project': 'test',
                'region': DEFAULT_REGION
            }
            errors = fcp_init.validate_config(config)
            # Account for validation stripping whitespace
            if api_key.strip():
                assert any("API key should start with 'mlfoundry_'" in e for e in errors)
            else:
                assert any("API key is required" in e for e in errors)
    
    @given(st.text(min_size=1, max_size=50).filter(lambda x: x.strip()))
    def test_validate_config_project_required_property(self, project_name):
        """Property test: Any non-empty project name should pass validation."""
        mock_http = Mock()
        fcp_init = FCPInit(mock_http)
        
        config = {
            'api_key': 'mlfoundry_test123',
            'project': project_name,
            'region': DEFAULT_REGION
        }
        errors = fcp_init.validate_config(config)
        # Should have no project-related errors
        assert not any("Project is required" in e for e in errors)
    
    @given(st.sampled_from(SUPPORTED_REGIONS))
    def test_validate_config_all_supported_regions(self, region):
        """Property test: All supported regions should validate successfully."""
        mock_http = Mock()
        fcp_init = FCPInit(mock_http)
        
        config = {
            'api_key': 'mlfoundry_test123',
            'project': 'test',
            'region': region
        }
        errors = fcp_init.validate_config(config)
        # Should have no region-related errors
        assert not any("Invalid region" in e for e in errors)
    
    def test_config_fields_immutability(self, fcp_init):
        """Test that config fields cannot be modified after retrieval."""
        fields1 = fcp_init.get_config_fields()
        fields2 = fcp_init.get_config_fields()
        
        # Should return new instances each time
        assert fields1 is not fields2
        
        # Modifying one shouldn't affect the other
        fields1['new_field'] = ConfigField(description="test")
        assert 'new_field' not in fields2
    
    def test_list_projects_error_handling(self, fcp_init, mock_http_client):
        """Test that list_projects propagates API errors correctly."""
        mock_http_client.request.side_effect = Exception("API Error: Unauthorized")
        
        with pytest.raises(Exception) as exc_info:
            fcp_init.list_projects()
        
        assert "API Error: Unauthorized" in str(exc_info.value)
    
    def test_list_ssh_keys_error_handling(self, fcp_init, mock_http_client):
        """Test that list_ssh_keys propagates API errors correctly."""
        mock_http_client.request.side_effect = Exception("Network timeout")
        
        with pytest.raises(Exception) as exc_info:
            fcp_init.list_ssh_keys()
        
        assert "Network timeout" in str(exc_info.value)
    
    def test_realistic_api_response_handling(self, fcp_init, mock_http_client, realistic_projects, realistic_ssh_keys):
        """Test handling of realistic API responses with various field formats."""
        # Test projects with different field combinations
        mock_http_client.request.return_value = realistic_projects
        projects = fcp_init.list_projects()
        
        assert len(projects) == 3
        # Should prefer 'name' over 'display_name'
        assert projects[1]['name'] == 'production-models'
        # Should handle missing fields gracefully
        assert all('id' in p and 'name' in p for p in projects)
        
        # Test SSH keys with different field combinations
        mock_http_client.request.return_value = realistic_ssh_keys
        ssh_keys = fcp_init.list_ssh_keys()
        
        assert len(ssh_keys) == 2
        # Should use display_name when name is missing
        assert ssh_keys[1]['name'] == 'workstation'
        # Should include fingerprints
        assert all('fingerprint' in k for k in ssh_keys)
    
    def test_config_validation_comprehensive(self, fcp_init):
        """Test comprehensive validation scenarios."""
        test_cases = [
            # Empty config
            ({}, ["API key is required", "Project is required"]),
            # Only API key
            ({'api_key': 'mlfoundry_123'}, ["Project is required"]),
            # Invalid SSH key with valid others
            ({
                'api_key': 'mlfoundry_123',
                'project': 'test',
                'default_ssh_key': 'invalid-format'
            }, ["SSH key ID should start with 'sshkey_'"]),
            # Multiple errors
            ({
                'api_key': 'wrong_prefix',
                'project': '',
                'region': 'mars-central-1',
                'default_ssh_key': 'also-wrong'
            }, [
                "API key should start with 'mlfoundry_'",
                "Project is required",
                "Invalid region 'mars-central-1'",
                "SSH key ID should start with 'sshkey_'"
            ])
        ]
        
        for config, expected_errors in test_cases:
            errors = fcp_init.validate_config(config)
            for expected_error in expected_errors:
                assert any(expected_error in e for e in errors), \
                    f"Expected error '{expected_error}' not found in {errors}"
    
    def test_edge_cases(self, fcp_init, mock_http_client):
        """Test edge cases and boundary conditions."""
        # Test with None values in API response
        mock_http_client.request.return_value = [
            {"id": None, "name": "test"},
            {"id": "proj-1", "name": None, "display_name": None}
        ]
        
        projects = fcp_init.list_projects()
        assert projects[0]['id'] == ''
        assert projects[0]['name'] == 'test'
        assert projects[1]['id'] == 'proj-1'
        assert projects[1]['name'] == ''
        
        # Test with very long strings
        long_string = 'a' * 1000
        config = {
            'api_key': f'mlfoundry_{long_string}',
            'project': long_string,
            'region': DEFAULT_REGION
        }
        errors = fcp_init.validate_config(config)
        # Should still validate without length restrictions
        assert errors == []