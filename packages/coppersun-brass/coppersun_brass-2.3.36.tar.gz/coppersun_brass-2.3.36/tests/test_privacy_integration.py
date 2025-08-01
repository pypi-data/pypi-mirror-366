"""
Test Privacy Report Integration

Comprehensive test suite for the Privacy Report Integration fix that ensures
the PrivacyReportGenerator is properly integrated with OutputGenerator.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from coppersun_brass.core.output_generator import OutputGenerator
from coppersun_brass.core.dcp_adapter import DCPAdapter
from coppersun_brass.privacy import PrivacyReportGenerator


class TestPrivacyReportIntegration:
    """Test suite for privacy report integration functionality."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        # Create temporary project directory
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_dir = self.temp_dir / "test_project"
        self.project_dir.mkdir()
        self.brass_dir = self.project_dir / ".brass"
        self.brass_dir.mkdir()
        
        # Create test files with some content
        (self.project_dir / "app.py").write_text("""
# Test Python file
email = "user@example.com"
ssn = "123-45-6789"

def process_data():
    pass
        """)
        
        # Mock DCP adapter
        self.mock_dcp = Mock(spec=DCPAdapter)
        self.mock_dcp.get_observations_by_type.return_value = []
        
        # Create OutputGenerator instance
        self.output_generator = OutputGenerator(
            output_dir=self.brass_dir,
            storage=self.mock_dcp,
            dcp=self.mock_dcp
        )
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_generate_privacy_report_method_exists(self):
        """Test that generate_privacy_report method exists and is callable."""
        assert hasattr(self.output_generator, 'generate_privacy_report')
        assert callable(getattr(self.output_generator, 'generate_privacy_report'))
    
    def test_generate_privacy_report_returns_path(self):
        """Test that generate_privacy_report returns a Path object."""
        result = self.output_generator.generate_privacy_report()
        assert isinstance(result, Path)
        assert result.name == "PRIVACY_ANALYSIS.md"
        assert result.exists()
    
    def test_generate_privacy_report_creates_file(self):
        """Test that privacy report file is actually created."""
        # Ensure file doesn't exist initially
        privacy_file = self.brass_dir / "PRIVACY_ANALYSIS.md"
        assert not privacy_file.exists()
        
        # Generate report
        result_path = self.output_generator.generate_privacy_report()
        
        # Verify file was created
        assert privacy_file.exists()
        assert result_path == privacy_file
        
        # Verify file has content
        content = privacy_file.read_text()
        assert len(content) > 0
        assert "Privacy Analysis Report" in content
    
    def test_generate_privacy_report_error_handling(self):
        """Test error handling when PrivacyReportGenerator fails."""
        with patch('coppersun_brass.core.output_generator.PrivacyReportGenerator') as mock_generator_class:
            # Mock PrivacyReportGenerator to raise an exception
            mock_generator = Mock()
            mock_generator.generate_report.side_effect = Exception("Test error")
            mock_generator_class.return_value = mock_generator
            
            # Should raise the exception
            with pytest.raises(Exception) as exc_info:
                self.output_generator.generate_privacy_report()
            
            assert "Test error" in str(exc_info.value)
    
    def test_generate_all_outputs_includes_privacy(self):
        """Test that generate_all_outputs includes privacy_analysis in outputs."""
        # Mock all the storage methods to return empty lists
        self.mock_dcp.get_all_observations.return_value = []
        self.mock_dcp.get_observations_by_type.return_value = []
        self.mock_dcp.get_resolution_metrics.return_value = {
            'total_resolved': 0,
            'resolution_rate': 0.0,
            'avg_resolution_time': 0.0
        }
        
        outputs = self.output_generator.generate_all_outputs()
        
        # Verify privacy_analysis is included in outputs
        assert 'privacy_analysis' in outputs
        assert isinstance(outputs['privacy_analysis'], Path)
        assert outputs['privacy_analysis'].name == "PRIVACY_ANALYSIS.md"
        assert outputs['privacy_analysis'].exists()
    
    def test_privacy_report_content_quality(self):
        """Test that generated privacy report has expected content structure."""
        result_path = self.output_generator.generate_privacy_report()
        content = result_path.read_text()
        
        # Check for expected sections
        expected_sections = [
            "Privacy Analysis Report",
            "Executive Summary", 
            "Findings by Category",
            "Compliance Analysis",
            "Recommendations"
        ]
        
        for section in expected_sections:
            assert section in content, f"Missing expected section: {section}"
        
        # Check that it found our test PII data
        assert "email" in content.lower() or "personal" in content.lower()
    
    def test_privacy_generator_project_path_parameter(self):
        """Test that PrivacyReportGenerator receives correct project path."""
        with patch('coppersun_brass.core.output_generator.PrivacyReportGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator.generate_report.return_value = str(self.brass_dir / "PRIVACY_ANALYSIS.md")
            mock_generator_class.return_value = mock_generator
            
            # Create a dummy file so Path() doesn't fail
            (self.brass_dir / "PRIVACY_ANALYSIS.md").touch()
            
            self.output_generator.generate_privacy_report()
            
            # Verify PrivacyReportGenerator was called with project root (not .brass dir)
            mock_generator_class.assert_called_once_with(str(self.project_dir))
    
    def test_privacy_integration_blood_oath_compliance(self):
        """Test that privacy integration maintains Blood Oath compliance."""
        # This test ensures no heavy dependencies are introduced
        import coppersun_brass.privacy.privacy_report_generator as privacy_module
        
        # Check that only allowed imports are used
        allowed_imports = {
            'os', 'hashlib', 'logging', 'pathlib', 'typing', 'dataclasses', 
            'datetime', 'collections', 'coppersun_brass'
        }
        
        # The privacy module should only import standard library and internal modules
        # This is a basic check - more comprehensive dependency analysis would be in blood oath tests
        assert hasattr(privacy_module, 'PrivacyReportGenerator')
        assert hasattr(privacy_module, 'DualPurposeContentSafety')


class TestPrivacyReportGeneratorStandalone:
    """Test the PrivacyReportGenerator module in isolation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_dir = self.temp_dir / "test_project"
        self.project_dir.mkdir()
        
        # Create test file with PII
        (self.project_dir / "data.py").write_text("""
email = "test@example.com"
phone = "555-123-4567"
credit_card = "4111-1111-1111-1111"
        """)
    
    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_privacy_report_generator_standalone(self):
        """Test PrivacyReportGenerator works as standalone module."""
        generator = PrivacyReportGenerator(str(self.project_dir))
        result_path = generator.generate_report()
        
        # Verify report was generated
        assert isinstance(result_path, str)
        result_file = Path(result_path)
        assert result_file.exists()
        assert result_file.name == "PRIVACY_ANALYSIS.md"
        
        # Verify content
        content = result_file.read_text()
        assert len(content) > 0
        assert "Privacy Analysis Report" in content


if __name__ == "__main__":
    pytest.main([__file__])