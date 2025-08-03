"""Unit tests for Local provider initialization interface."""

import os
import pytest
import tempfile
import platform
from pathlib import Path
from hypothesis import given, strategies as st

from flow.providers.interfaces import ConfigField
from flow.providers.local.init import LocalInit


class TestLocalInit:
    """Test suite for LocalInit class."""
    
    @pytest.fixture
    def local_init(self):
        """Create LocalInit instance."""
        return LocalInit()
    
    def test_get_config_fields(self, local_init):
        """Test configuration field definitions."""
        fields = local_init.get_config_fields()
        
        # Check all required fields are present
        assert 'working_directory' in fields
        assert 'max_parallel_tasks' in fields
        assert 'enable_gpu' in fields
        
        # Verify working_directory field
        work_dir_field = fields['working_directory']
        assert isinstance(work_dir_field, ConfigField)
        assert work_dir_field.description == "Working directory for tasks"
        assert work_dir_field.secret is False
        assert work_dir_field.choices is None
        assert work_dir_field.default == os.path.expanduser("~/.flow/local-tasks")
        
        # Verify max_parallel_tasks field
        max_tasks_field = fields['max_parallel_tasks']
        assert isinstance(max_tasks_field, ConfigField)
        assert max_tasks_field.description == "Maximum parallel tasks"
        assert max_tasks_field.secret is False
        assert max_tasks_field.choices is None
        assert max_tasks_field.default == "4"
        
        # Verify enable_gpu field
        gpu_field = fields['enable_gpu']
        assert isinstance(gpu_field, ConfigField)
        assert gpu_field.description == "Enable GPU passthrough (requires local GPU)"
        assert gpu_field.secret is False
        assert gpu_field.choices == ["true", "false"]
        assert gpu_field.default == "false"
    
    def test_validate_config_valid(self, local_init, tmp_path):
        """Test validation with valid configuration."""
        config = {
            'working_directory': str(tmp_path / "work"),
            'max_parallel_tasks': '8',
            'enable_gpu': 'true'
        }
        
        errors = local_init.validate_config(config)
        assert errors == []
    
    def test_validate_config_missing_working_directory(self, local_init):
        """Test validation with missing working directory."""
        config = {
            'working_directory': '',
            'max_parallel_tasks': '4',
            'enable_gpu': 'false'
        }
        
        errors = local_init.validate_config(config)
        assert "Working directory is required" in errors
    
    def test_validate_config_working_directory_is_file(self, local_init, tmp_path):
        """Test validation when working directory path exists but is a file."""
        # Create a file where directory is expected
        file_path = tmp_path / "not_a_directory"
        file_path.write_text("content")
        
        config = {
            'working_directory': str(file_path),
            'max_parallel_tasks': '4',
            'enable_gpu': 'false'
        }
        
        errors = local_init.validate_config(config)
        assert any("is not a directory" in error for error in errors)
    
    def test_validate_config_nonexistent_working_directory(self, local_init, tmp_path):
        """Test validation with non-existent working directory (should pass)."""
        # Non-existent directory should be OK since we can create it
        config = {
            'working_directory': str(tmp_path / "does_not_exist"),
            'max_parallel_tasks': '4',
            'enable_gpu': 'false'
        }
        
        errors = local_init.validate_config(config)
        assert errors == []
    
    def test_validate_config_invalid_max_parallel_tasks(self, local_init):
        """Test validation with invalid max_parallel_tasks values."""
        # Test non-numeric value
        config = {
            'working_directory': '~/.flow/local-tasks',
            'max_parallel_tasks': 'not_a_number',
            'enable_gpu': 'false'
        }
        errors = local_init.validate_config(config)
        assert any("must be a number" in error for error in errors)
        
        # Test zero value
        config['max_parallel_tasks'] = '0'
        errors = local_init.validate_config(config)
        assert any("must be at least 1" in error for error in errors)
        
        # Test too large value
        config['max_parallel_tasks'] = '200'
        errors = local_init.validate_config(config)
        assert any("should not exceed 100" in error for error in errors)
    
    def test_validate_config_valid_max_parallel_tasks_range(self, local_init):
        """Test validation with edge case values for max_parallel_tasks."""
        # Test minimum valid value
        config = {
            'working_directory': '~/.flow/local-tasks',
            'max_parallel_tasks': '1',
            'enable_gpu': 'false'
        }
        errors = local_init.validate_config(config)
        assert errors == []
        
        # Test maximum valid value
        config['max_parallel_tasks'] = '100'
        errors = local_init.validate_config(config)
        assert errors == []
    
    def test_validate_config_invalid_gpu_setting(self, local_init):
        """Test validation with invalid GPU setting."""
        config = {
            'working_directory': '~/.flow/local-tasks',
            'max_parallel_tasks': '4',
            'enable_gpu': 'yes'  # Should be 'true' or 'false'
        }
        
        errors = local_init.validate_config(config)
        assert any("Enable GPU must be 'true' or 'false'" in error for error in errors)
    
    def test_validate_config_whitespace_handling(self, local_init):
        """Test validation handles whitespace correctly."""
        config = {
            'working_directory': '  ~/.flow/local-tasks  ',
            'max_parallel_tasks': '  4  ',
            'enable_gpu': '  false  '
        }
        
        errors = local_init.validate_config(config)
        assert errors == []
    
    def test_validate_config_case_insensitive_gpu(self, local_init):
        """Test GPU setting is case insensitive."""
        for value in ['TRUE', 'False', 'tRuE', 'FALSE']:
            config = {
                'working_directory': '~/.flow/local-tasks',
                'max_parallel_tasks': '4',
                'enable_gpu': value
            }
            errors = local_init.validate_config(config)
            assert errors == []
    
    def test_list_projects(self, local_init):
        """Test project listing returns empty list."""
        projects = local_init.list_projects()
        assert projects == []
        assert isinstance(projects, list)
    
    def test_list_ssh_keys_without_project(self, local_init):
        """Test SSH key listing without project returns empty list."""
        ssh_keys = local_init.list_ssh_keys()
        assert ssh_keys == []
        assert isinstance(ssh_keys, list)
    
    def test_list_ssh_keys_with_project(self, local_init):
        """Test SSH key listing with project still returns empty list."""
        ssh_keys = local_init.list_ssh_keys(project_id="some-project")
        assert ssh_keys == []
        assert isinstance(ssh_keys, list)
    
    def test_home_directory_expansion(self, local_init):
        """Test that default working directory properly expands home directory."""
        fields = local_init.get_config_fields()
        default_dir = fields['working_directory'].default
        
        # Should not contain ~ after expansion
        assert '~' not in default_dir
        # Should be an absolute path
        assert os.path.isabs(default_dir)
    
    # Property-based tests
    @given(st.integers(min_value=1, max_value=100))
    def test_validate_max_parallel_tasks_valid_range_property(self, num_tasks):
        """Property test: Any integer between 1-100 should be valid for max_parallel_tasks."""
        local_init = LocalInit()
        config = {
            'working_directory': '~/.flow/local-tasks',
            'max_parallel_tasks': str(num_tasks),
            'enable_gpu': 'false'
        }
        errors = local_init.validate_config(config)
        assert not any('parallel tasks' in e.lower() for e in errors)
    
    @given(st.integers().filter(lambda x: x < 1 or x > 100))
    def test_validate_max_parallel_tasks_invalid_range_property(self, num_tasks):
        """Property test: Integers outside 1-100 should fail validation."""
        local_init = LocalInit()
        config = {
            'working_directory': '~/.flow/local-tasks',
            'max_parallel_tasks': str(num_tasks),
            'enable_gpu': 'false'
        }
        errors = local_init.validate_config(config)
        if num_tasks < 1:
            assert any('must be at least 1' in e for e in errors)
        else:
            assert any('should not exceed 100' in e for e in errors)
    
    @given(st.text(min_size=1).filter(lambda x: not x.strip().isdigit()))
    def test_validate_max_parallel_tasks_non_numeric_property(self, non_numeric):
        """Property test: Non-numeric strings should fail validation."""
        local_init = LocalInit()
        config = {
            'working_directory': '~/.flow/local-tasks',
            'max_parallel_tasks': non_numeric,
            'enable_gpu': 'false'
        }
        errors = local_init.validate_config(config)
        assert any('must be a number' in e for e in errors)
    
    def test_config_fields_consistency(self, local_init):
        """Test that config fields are consistent across calls."""
        fields1 = local_init.get_config_fields()
        fields2 = local_init.get_config_fields()
        
        # Should have same keys
        assert set(fields1.keys()) == set(fields2.keys())
        
        # Should have same defaults
        for key in fields1:
            assert fields1[key].default == fields2[key].default
    
    def test_path_validation_edge_cases(self, local_init):
        """Test path validation with various edge cases."""
        test_cases = [
            # Absolute paths
            ('/tmp/flow-tasks', []),
            ('/var/flow/tasks', []),
            # Relative paths (should work after expansion)
            ('./flow-tasks', []),
            ('../flow-tasks', []),
            # Paths with spaces
            ('/tmp/flow tasks', []),
            # Unicode paths
            ('/tmp/フロー', []),
            # Very long paths
            ('/tmp/' + 'a' * 200, [])
        ]
        
        for path, expected_errors in test_cases:
            config = {
                'working_directory': path,
                'max_parallel_tasks': '4',
                'enable_gpu': 'false'
            }
            errors = local_init.validate_config(config)
            if expected_errors:
                assert errors == expected_errors
            else:
                # Should not have working directory errors
                assert not any('directory' in e.lower() for e in errors)
    
    def test_platform_specific_defaults(self, local_init):
        """Test that defaults make sense for the current platform."""
        fields = local_init.get_config_fields()
        work_dir = fields['working_directory'].default
        
        # Should use appropriate path separator
        assert os.sep in work_dir
        
        # Should be under user home
        assert work_dir.startswith(os.path.expanduser('~'))
    
    def test_concurrent_validation(self, local_init):
        """Test that validation is thread-safe."""
        import concurrent.futures
        
        def validate_config():
            config = {
                'working_directory': '~/.flow/local-tasks',
                'max_parallel_tasks': '4',
                'enable_gpu': 'false'
            }
            return local_init.validate_config(config)
        
        # Run validation concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(validate_config) for _ in range(100)]
            results = [f.result() for f in futures]
        
        # All validations should succeed
        assert all(r == [] for r in results)
    
    def test_realistic_configuration_scenarios(self, local_init, tmp_path):
        """Test realistic configuration scenarios users might encounter."""
        scenarios = [
            # Developer laptop configuration
            {
                'config': {
                    'working_directory': str(tmp_path / 'development'),
                    'max_parallel_tasks': '2',
                    'enable_gpu': 'false'
                },
                'description': 'Developer laptop setup'
            },
            # Workstation with GPU
            {
                'config': {
                    'working_directory': '/data/flow-jobs',
                    'max_parallel_tasks': '8',
                    'enable_gpu': 'true'
                },
                'description': 'Workstation with GPU'
            },
            # CI/CD environment
            {
                'config': {
                    'working_directory': str(tmp_path / 'ci-jobs'),
                    'max_parallel_tasks': '1',
                    'enable_gpu': 'false'
                },
                'description': 'CI/CD environment'
            }
        ]
        
        for scenario in scenarios:
            errors = local_init.validate_config(scenario['config'])
            assert errors == [], f"Validation failed for {scenario['description']}: {errors}"
    
    def test_error_message_quality(self, local_init):
        """Test that error messages are helpful and actionable."""
        # Test multiple validation errors
        config = {
            'working_directory': '',
            'max_parallel_tasks': 'many',
            'enable_gpu': 'yes'
        }
        
        errors = local_init.validate_config(config)
        
        # Should have clear, specific error messages
        assert len(errors) == 3
        
        # Each error should be actionable
        assert any('Working directory is required' in e for e in errors)
        assert any('must be a number' in e for e in errors)
        assert any("must be 'true' or 'false'" in e for e in errors)
        
        # Errors should not contain implementation details
        for error in errors:
            assert 'ValueError' not in error
            assert 'Exception' not in error
            assert 'stack trace' not in error.lower()