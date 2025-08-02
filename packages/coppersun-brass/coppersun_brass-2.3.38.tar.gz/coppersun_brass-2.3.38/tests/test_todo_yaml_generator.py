#!/usr/bin/env python3
"""
Test suite for TodoYamlGenerator functionality.

Tests the TODO JSON to YAML conversion implementation to ensure
it generates valid YAML with proper structure and content.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock

from coppersun_brass.analysis.todo_yaml_generator import TodoYamlGenerator


class TestTodoYamlGenerator:
    """Test cases for TodoYamlGenerator."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_path = self.temp_dir / "test_project"
        self.project_path.mkdir()
        
        # Mock storage
        self.mock_storage = Mock()
        self.mock_storage.get_observations_by_type.return_value = []
        
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_todo_yaml_generator_initialization(self):
        """Test that TodoYamlGenerator initializes correctly."""
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        
        assert generator.project_path == self.project_path
        assert generator.storage == self.mock_storage
        assert generator.yaml_output_path == self.project_path / '.brass' / 'todos.yaml'
    
    def test_generate_yaml_report_creates_file(self):
        """Test that generate_yaml_report creates a valid YAML file."""
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        
        # Generate YAML report
        output_path = generator.generate_yaml_report()
        
        # Verify file was created
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.yaml'
        
        # Verify it's valid YAML
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert isinstance(data, dict)
        assert 'metadata' in data
        assert 'todo_summary' in data
        assert 'todos_by_priority' in data
        assert 'ai_consumption_metadata' in data
    
    def test_yaml_structure_with_mock_todos(self):
        """Test YAML structure with mock TODO data."""
        # Mock some TODO data
        from datetime import datetime, timezone
        
        # Use current time to avoid timezone comparison issues
        current_time = datetime.now(timezone.utc).isoformat()
        
        mock_todos = [
            {
                'id': 1,
                'created_at': current_time,
                'priority': 80,
                'data': {
                    'file_path': 'src/main.py',
                    'line_number': 42,
                    'content': 'TODO: Fix critical security bug',
                    'category': 'bug_fixes'
                }
            },
            {
                'id': 2,
                'created_at': current_time,
                'priority': 30,
                'data': {
                    'file_path': 'src/utils.py', 
                    'line_number': 15,
                    'content': 'TODO: Add documentation',
                    'category': 'documentation'
                }
            }
        ]
        
        self.mock_storage.get_observations_by_type.return_value = mock_todos
        
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        output_path = generator.generate_yaml_report()
        
        # Load and verify YAML content
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Verify summary data
        assert data['todo_summary']['total_todos'] == 2
        assert data['todo_summary']['priority_breakdown']['critical'] == 1  # priority >= 80
        assert data['todo_summary']['priority_breakdown']['low'] == 1      # priority < 40
        
        # Verify priority grouping
        assert len(data['todos_by_priority']['critical']) == 1
        assert len(data['todos_by_priority']['low']) == 1
        assert len(data['todos_by_priority']['high']) == 0
        assert len(data['todos_by_priority']['medium']) == 0
        
        # Verify location grouping
        assert 'src/main.py:42' in data['todos_by_location']
        assert 'src/utils.py:15' in data['todos_by_location']
        
        # Verify category grouping
        assert 'bug_fixes' in data['todos_by_category']
        assert 'documentation' in data['todos_by_category']
    
    def test_yaml_metadata_structure(self):
        """Test that YAML metadata follows expected structure."""
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        output_path = generator.generate_yaml_report()
        
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        metadata = data['metadata']
        assert 'generated' in metadata
        assert metadata['generator_version'] == '2.3.30'
        assert metadata['format_version'] == '1.0'
        assert metadata['schema_description'] == 'TODO analysis data optimized for AI consumption'
        assert metadata['window_hours'] == 24
        assert metadata['deduplication_applied'] is True
    
    def test_ai_consumption_metadata(self):
        """Test AI consumption metadata structure."""
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        output_path = generator.generate_yaml_report()
        
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        ai_meta = data['ai_consumption_metadata']
        assert ai_meta['parsing_instruction'] == 'Use yaml.safe_load() for secure parsing'
        assert 'data_access_examples' in ai_meta
        assert ai_meta['recommended_libraries'] == ['PyYAML', 'ruamel.yaml']
        assert ai_meta['schema_stability'] == 'format_version tracks breaking changes'
        
        # Verify access examples
        examples = ai_meta['data_access_examples']
        assert examples['total_todos'] == "data['todo_summary']['total_todos']"
        assert examples['critical_count'] == "len(data['todos_by_priority']['critical'])"
    
    def test_empty_project_handling(self):
        """Test handling of project with no TODOs."""
        generator = TodoYamlGenerator(str(self.project_path), self.mock_storage)
        output_path = generator.generate_yaml_report()
        
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Verify empty state
        assert data['todo_summary']['total_todos'] == 0
        assert data['todo_summary']['active_todos'] == 0
        assert all(count == 0 for count in data['todo_summary']['priority_breakdown'].values())
        assert data['todos_by_location'] == {}
        assert data['todos_by_category'] == {}
        
        # Verify all priority arrays are empty
        for priority in ['critical', 'high', 'medium', 'low']:
            assert data['todos_by_priority'][priority] == []


if __name__ == "__main__":
    pytest.main([__file__])