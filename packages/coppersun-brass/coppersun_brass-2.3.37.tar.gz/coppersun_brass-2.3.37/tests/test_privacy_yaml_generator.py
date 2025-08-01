#!/usr/bin/env python3
"""
Test suite for PrivacyYamlGenerator functionality.

Tests the Privacy YAML generator that creates .brass/privacy_analysis.yaml
with structured privacy and PII analysis data optimized for AI consumption.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock

from coppersun_brass.privacy.privacy_yaml_generator import PrivacyYamlGenerator


class TestPrivacyYamlGenerator:
    """Test cases for PrivacyYamlGenerator."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_path = self.temp_dir / "test_project"
        self.project_path.mkdir()
        
        # Create test files directory
        self.src_dir = self.project_path / "src"
        self.src_dir.mkdir()
        
        # Create sample files for analysis
        (self.src_dir / "main.py").write_text("""
# Sample Python file with PII
email = "user@example.com"
ssn = "123-45-6789"
# TODO: Remove hardcoded credentials
api_key = "sk-1234567890abcdef"
""")
        
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_privacy_yaml_generator_initialization(self):
        """Test that PrivacyYamlGenerator initializes correctly."""
        generator = PrivacyYamlGenerator(str(self.project_path))
        
        # Use resolve() to handle macOS symlink path differences
        assert generator.project_path.resolve() == self.project_path.resolve()
        assert generator.yaml_output_path.resolve() == (self.project_path / '.brass' / 'privacy_analysis.yaml').resolve()
    
    def test_generate_yaml_report_creates_file(self):
        """Test that generate_yaml_report creates a valid YAML file."""
        generator = PrivacyYamlGenerator(str(self.project_path))
        
        # Generate YAML report
        output_path = generator.generate_yaml_report()
        
        # Verify file was created
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.yaml'
        assert Path(output_path).name == 'privacy_analysis.yaml'
        
        # Verify it's valid YAML
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert isinstance(data, dict)
        assert 'metadata' in data
        assert 'privacy_summary' in data
        assert 'findings_by_category' in data
        assert 'compliance_guidance' in data
        assert 'ai_consumption_metadata' in data
    
    def test_privacy_yaml_metadata_structure(self):
        """Test that YAML metadata follows expected structure."""
        generator = PrivacyYamlGenerator(str(self.project_path))
        output_path = generator.generate_yaml_report()
        
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        metadata = data['metadata']
        assert 'generated' in metadata
        assert metadata['generator_version'] == '2.3.30'
        assert metadata['format_version'] == '1.0'
        assert metadata['schema_description'] == 'Privacy analysis data optimized for AI consumption'
        assert metadata['analysis_engine'] == 'DualPurposeContentSafety v2.3.15+'
        assert metadata['project_name'] == 'test_project'
    
    def test_privacy_summary_structure(self):
        """Test privacy summary structure and content."""
        generator = PrivacyYamlGenerator(str(self.project_path))
        output_path = generator.generate_yaml_report()
        
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        summary = data['privacy_summary']
        assert 'files_scanned' in summary
        assert 'files_with_issues' in summary
        assert 'total_privacy_issues' in summary
        assert 'risk_level' in summary
        assert 'recommendation' in summary
        assert 'analysis_scope' in summary
        
        # Verify numeric types
        assert isinstance(summary['files_scanned'], int)
        assert isinstance(summary['files_with_issues'], int)
        assert isinstance(summary['total_privacy_issues'], int)
        assert isinstance(summary['risk_level'], str)
    
    def test_findings_by_category_structure(self):
        """Test findings categorization structure."""
        generator = PrivacyYamlGenerator(str(self.project_path))
        output_path = generator.generate_yaml_report()
        
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        categories = data['findings_by_category']
        expected_categories = [
            'critical_pii',
            'credentials', 
            'international_pii',
            'personal_info',
            'professional_content'
        ]
        
        for category in expected_categories:
            assert category in categories
            assert isinstance(categories[category], list)
            
            # Check finding structure if any findings exist
            for finding in categories[category]:
                if finding:  # If not empty
                    assert 'type' in finding
                    assert 'location' in finding
                    assert 'severity' in finding
                    assert 'confidence' in finding
                    assert isinstance(finding['confidence'], float)
    
    def test_compliance_guidance_structure(self):
        """Test compliance guidance structure."""
        generator = PrivacyYamlGenerator(str(self.project_path))
        output_path = generator.generate_yaml_report()
        
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        compliance = data['compliance_guidance']
        
        # Check main compliance frameworks
        assert 'gdpr' in compliance
        assert 'ccpa' in compliance
        assert 'security' in compliance
        assert 'general' in compliance
        
        # Check GDPR structure
        gdpr = compliance['gdpr']
        assert 'applicable' in gdpr
        assert 'pii_items_detected' in gdpr
        assert 'risk_level' in gdpr
        assert 'recommendations' in gdpr
        assert isinstance(gdpr['applicable'], bool)
        assert isinstance(gdpr['pii_items_detected'], int)
        assert isinstance(gdpr['recommendations'], list)
    
    def test_ai_consumption_metadata(self):
        """Test AI consumption metadata structure."""
        generator = PrivacyYamlGenerator(str(self.project_path))
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
        assert examples['total_issues'] == "data['privacy_summary']['total_privacy_issues']"
        assert examples['risk_level'] == "data['privacy_summary']['risk_level']"
        assert examples['critical_pii_count'] == "len(data['findings_by_category']['critical_pii'])"
    
    def test_multi_dimensional_organization(self):
        """Test multi-dimensional data organization."""
        generator = PrivacyYamlGenerator(str(self.project_path))
        output_path = generator.generate_yaml_report()
        
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Verify all organizational dimensions exist
        assert 'findings_by_category' in data
        assert 'findings_by_severity' in data
        assert 'findings_by_location' in data
        
        # Test severity grouping structure
        severity_data = data['findings_by_severity']
        for severity_level, findings in severity_data.items():
            if isinstance(findings, dict):
                assert 'count' in findings
                assert 'findings' in findings
                assert isinstance(findings['count'], int)
                assert isinstance(findings['findings'], list)
    
    def test_performance_metrics_structure(self):
        """Test performance metrics structure."""
        generator = PrivacyYamlGenerator(str(self.project_path))
        output_path = generator.generate_yaml_report()
        
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        metrics = data['performance_metrics']
        assert 'generation_time_seconds' in metrics
        assert 'average_file_analysis_ms' in metrics
        assert 'total_files_processed' in metrics
        assert 'detection_coverage_regions' in metrics
        
        # Verify types
        assert isinstance(metrics['generation_time_seconds'], (int, float))
        assert isinstance(metrics['average_file_analysis_ms'], (int, float))
        assert isinstance(metrics['total_files_processed'], int)
        assert isinstance(metrics['detection_coverage_regions'], list)
        assert 'US' in metrics['detection_coverage_regions']
    
    def test_empty_project_handling(self):
        """Test handling of project with no privacy issues."""
        # Create empty project
        empty_project = self.temp_dir / "empty_project"
        empty_project.mkdir()
        
        generator = PrivacyYamlGenerator(str(empty_project))
        output_path = generator.generate_yaml_report()
        
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Verify empty state handling
        summary = data['privacy_summary']
        assert summary['total_privacy_issues'] == 0
        assert summary['files_with_issues'] == 0
        
        # Verify all categories are empty but present
        for category in data['findings_by_category'].values():
            assert isinstance(category, list)
            assert len(category) == 0


if __name__ == "__main__":
    pytest.main([__file__])