#!/usr/bin/env python3
"""
Comprehensive test suite for TodoYamlGenerator fallback mechanisms.

Tests all fallback scenarios to ensure robust error handling and graceful degradation.
"""

import pytest
import tempfile
import json
import yaml
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys
sys.path.insert(0, 'src')

from coppersun_brass.analysis.todo_yaml_generator import TodoYamlGenerator


class TestTodoYamlFallbackMechanisms:
    """Test suite for TodoYamlGenerator fallback mechanisms."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_path = self.temp_dir / "test_project"
        self.project_path.mkdir()
        
        # Mock storage with test data
        self.mock_storage = Mock()
        self.test_todo_data = [
            {
                'id': 1,
                'content': 'Fix authentication bug',
                'file_path': '/test/auth.py',
                'line_number': 45,
                'priority': 80,
                'category': 'security',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 2,
                'content': 'Optimize database queries',
                'file_path': '/test/db.py',
                'line_number': 123,
                'priority': 60,
                'category': 'performance',
                'created_at': datetime.now().isoformat()
            }
        ]
        
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_primary_yaml_generation_success(self):
        """Test successful primary YAML generation."""
        # Setup mock storage to return test data
        self.mock_storage.get_observations_by_type.return_value = [
            {
                'id': 1,
                'created_at': datetime.now().isoformat(),
                'data': {
                    'content': 'Test TODO',
                    'file_path': '/test/file.py',
                    'line_number': 10,
                    'category': 'general'
                },
                'priority': 50
            }
        ]
        
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        
        # Should generate primary YAML successfully
        result_path = generator.generate_yaml_report()
        
        assert result_path == str(generator.yaml_output_path)
        assert Path(result_path).exists()
        
        # Verify YAML content is valid
        with open(result_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        assert 'metadata' in yaml_data
        assert 'todo_summary' in yaml_data
        assert yaml_data['metadata']['format_version'] == '1.0'
    
    def test_data_collection_failure_triggers_emergency_fallback(self):
        """Test that data collection failure triggers emergency fallback."""
        # Setup mock storage to raise exception
        self.mock_storage.get_observations_by_type.side_effect = Exception("Database connection failed")
        
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        
        # Should trigger emergency fallback
        result_path = generator.generate_yaml_report()
        
        assert 'todos_emergency.txt' in result_path
        emergency_file = Path(result_path)
        assert emergency_file.exists()
        
        # Verify emergency file content
        content = emergency_file.read_text()
        assert "EMERGENCY TODO REPORT" in content
        assert "WARNING: Normal TODO generation failed" in content
    
    def test_yaml_structure_failure_triggers_simplified_yaml(self):
        """Test that YAML structure failure triggers simplified YAML fallback."""
        # Setup mock storage with valid data
        self.mock_storage.get_observations_by_type.return_value = [
            {
                'id': 1,
                'created_at': datetime.now().isoformat(),
                'data': '{"content": "Test TODO", "file_path": "/test/file.py", "line_number": 10}',
                'priority': 50
            }
        ]
        
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        
        # Mock _build_yaml_structure to fail
        with patch.object(generator, '_build_yaml_structure_impl', side_effect=Exception("YAML structure error")):
            result_path = generator.generate_yaml_report()
        
        assert result_path == str(generator.yaml_output_path)
        assert Path(result_path).exists()
        
        # Verify simplified YAML was generated
        with open(result_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        assert yaml_data['metadata']['format_version'] == '1.0-simplified'
        assert yaml_data['metadata']['fallback_reason'] == 'Primary generation failed - using simplified structure'
        assert 'todos' in yaml_data
    
    def test_simplified_yaml_failure_triggers_json_fallback(self):
        """Test that simplified YAML failure triggers JSON fallback."""
        # Setup mock storage with valid data
        self.mock_storage.get_observations_by_type.return_value = [
            {
                'id': 1,
                'created_at': datetime.now().isoformat(),
                'data': '{"content": "Test TODO", "file_path": "/test/file.py", "line_number": 10}',
                'priority': 50
            }
        ]
        
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        
        # Mock both primary and simplified YAML to fail
        with patch.object(generator, '_build_yaml_structure_impl', side_effect=Exception("YAML structure error")):
            with patch('yaml.dump', side_effect=Exception("YAML dump error")):
                result_path = generator.generate_yaml_report()
        
        assert result_path == str(generator.json_fallback_path)
        assert Path(result_path).exists()
        
        # Verify JSON fallback was generated
        with open(result_path, 'r') as f:
            json_data = json.load(f)
        
        assert json_data['generator'] == 'TodoYamlGenerator-JSONFallback'
        assert json_data['fallback_reason'] == 'YAML generation failed - using JSON compatibility mode'
        assert 'todos' in json_data
    
    def test_json_fallback_failure_triggers_emergency_fallback(self):
        """Test that JSON fallback failure triggers emergency fallback."""
        # Setup mock storage with valid data
        self.mock_storage.get_observations_by_type.return_value = [
            {
                'id': 1,
                'created_at': datetime.now().isoformat(),
                'data': '{"content": "Test TODO", "file_path": "/test/file.py", "line_number": 10}',
                'priority': 50
            }
        ]
        
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        
        # Mock all generation methods to fail
        with patch.object(generator, '_build_yaml_structure_impl', side_effect=Exception("YAML structure error")):
            with patch('yaml.dump', side_effect=Exception("YAML dump error")):
                with patch('json.dump', side_effect=Exception("JSON dump error")):
                    result_path = generator.generate_yaml_report()
        
        assert 'todos_emergency.txt' in result_path
        emergency_file = Path(result_path)
        assert emergency_file.exists()
        
        # Verify emergency file content includes the TODO data
        content = emergency_file.read_text()
        assert "EMERGENCY TODO REPORT" in content
        assert "Found 1 TODOs" in content
        assert "Test TODO" in content
    
    def test_directory_creation_failure(self):
        """Test behavior when .brass directory cannot be created."""
        # Setup mock storage
        self.mock_storage.get_observations_by_type.return_value = []
        
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        
        # Use a read-only path to simulate permission error
        import stat
        readonly_path = self.temp_dir / "readonly_project"
        readonly_path.mkdir()
        readonly_path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)  # Read-only
        
        generator_readonly = TodoYamlGenerator(str(readonly_path), self.mock_storage)
        
        try:
            result_path = generator_readonly.generate_yaml_report()
            
            # Should return error message since .brass directory can't be created
            assert "CRITICAL_ERROR" in result_path or "emergency" in result_path
        finally:
            # Restore permissions for cleanup
            readonly_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    
    def test_absolute_emergency_fallback_failure(self):
        """Test behavior when even emergency fallback fails."""
        # Setup mock storage with test data
        self.mock_storage.get_observations_by_type.return_value = [
            {
                'id': 1,
                'created_at': datetime.now().isoformat(),
                'data': '{"content": "Test TODO", "file_path": "/test/file.py", "line_number": 10}',
                'priority': 50
            }
        ]
        
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        
        # Mock all file operations to fail
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result_path = generator.generate_yaml_report()
        
        # Should return critical error message
        assert "CRITICAL_ERROR" in result_path
        assert "All TODO generation methods failed" in result_path
    
    def test_malformed_data_handling(self):
        """Test handling of malformed TODO data."""
        # Setup mock storage with malformed data
        self.mock_storage.get_observations_by_type.return_value = [
            {
                'id': 1,
                'created_at': 'invalid_date',
                'data': 'invalid_json',
                'priority': 'not_a_number'
            },
            {
                'id': 2,
                # Missing required fields
                'random_field': 'value'
            }
        ]
        
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        
        # Should handle malformed data gracefully
        result_path = generator.generate_yaml_report()
        
        # Should succeed with some form of output (simplified or fallback)
        assert Path(result_path).exists()
    
    def test_large_data_handling(self):
        """Test handling of very large TODO datasets."""
        # Generate large dataset
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                'id': i,
                'created_at': datetime.now().isoformat(),
                'data': json.dumps({
                    'content': f'TODO item {i}' * 100,  # Very long content
                    'file_path': f'/test/file_{i}.py',
                    'line_number': i,
                    'category': 'general'
                }),
                'priority': 50
            })
        
        self.mock_storage.get_observations_by_type.return_value = large_dataset
        
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        
        # Should handle large dataset without crashing
        result_path = generator.generate_yaml_report()
        
        assert Path(result_path).exists()
        # File should exist and be reasonably sized
        file_size = Path(result_path).stat().st_size
        assert file_size > 0  # Should have content
        assert file_size < 50 * 1024 * 1024  # But not excessively large (< 50MB)
    
    def test_unicode_content_handling(self):
        """Test handling of Unicode content in TODOs."""
        # Setup mock storage with Unicode content
        self.mock_storage.get_observations_by_type.return_value = [
            {
                'id': 1,
                'created_at': datetime.now().isoformat(),
                'data': json.dumps({
                    'content': 'TODO: Fix encoding issue with émojis 🐛 and unicode characters like café',
                    'file_path': '/test/unicode_file.py',
                    'line_number': 42,
                    'category': 'bug_fixes'
                }),
                'priority': 75
            }
        ]
        
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        
        # Should handle Unicode content properly
        result_path = generator.generate_yaml_report()
        
        assert Path(result_path).exists()
        
        # Verify Unicode content is preserved
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'émojis 🐛' in content
        assert 'café' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])