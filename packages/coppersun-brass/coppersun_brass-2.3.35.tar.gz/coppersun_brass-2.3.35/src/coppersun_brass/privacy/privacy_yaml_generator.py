"""
Privacy YAML Generator

YAML variant of PrivacyReportGenerator that creates .brass/privacy_analysis.yaml
with structured data optimized for AI consumption while preserving all privacy intelligence.

Key Features:
- Structured YAML format for direct programmatic access
- Location-based consolidation to prevent duplicate entries
- Type-safe data (native integers, floats, booleans, arrays)  
- AI-optimized schema with consistent data access patterns
- Inherits data collection logic from PrivacyReportGenerator

Follows the exact same proven pattern as BrassYamlGenerator inheriting from BrassAnalysisGenerator.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

from .privacy_report_generator import (
    PrivacyReportGenerator, 
    FileAnalysis,
    SecurityFinding
)

logger = logging.getLogger(__name__)


class PrivacyYamlGenerator(PrivacyReportGenerator):
    """
    YAML variant of privacy report generator for AI consumption.
    
    Inherits data collection logic from PrivacyReportGenerator but outputs
    structured YAML format optimized for programmatic access by AI agents.
    
    Follows evidence-based consolidation patterns from OutputGenerator
    to prevent duplicate entries and group similar issues by location.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize YAML privacy report generator.
        
        Args:
            project_path: Root path of project to analyze
        """
        super().__init__(project_path)
        self.yaml_output_path = self.brass_dir / 'privacy_analysis.yaml'
        
        logger.info(f"YAML privacy report generator initialized for project: {self.project_path}")
    
    def generate_yaml_report(self) -> str:
        """
        Generate structured YAML privacy report for AI consumption.
        
        Returns:
            Path to generated .brass/privacy_analysis.yaml file
        """
        start_time = datetime.now()
        
        logger.info("Starting YAML privacy analysis report generation")
        
        # Ensure .brass directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        # Phase 1-3: Reuse parent class data collection logic
        logger.info("Phase 1: Scanning project files")
        file_analyses = self._scan_project_files()
        
        logger.info("Phase 2: Collecting and deduplicating findings")
        all_findings = []
        for analysis in file_analyses:
            all_findings.extend(analysis.findings)
        
        deduplicated_findings = self._deduplicate_findings(all_findings)
        
        logger.info("Phase 3: Categorizing findings")
        categorized_findings = self._categorize_findings(deduplicated_findings)
        
        # Phase 4: Generate YAML structure (new implementation)
        logger.info("Phase 4: Generating YAML structure")
        yaml_data = self._build_yaml_structure(
            file_analyses, categorized_findings, start_time
        )
        
        # Phase 5: Write YAML file
        logger.info("Phase 5: Writing YAML file")
        with open(self.yaml_output_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        generation_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Privacy YAML report generated successfully in {generation_time:.2f}s: {self.yaml_output_path}")
        
        return str(self.yaml_output_path)
    
    def _build_yaml_structure(
        self, 
        file_analyses: List[FileAnalysis], 
        categorized_findings: Dict[str, List[SecurityFinding]],
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Build structured YAML data optimized for AI consumption.
        
        Args:
            file_analyses: File analysis results
            categorized_findings: Categorized and sorted findings
            start_time: Report generation start time
            
        Returns:
            Complete YAML data structure
        """
        total_findings = sum(len(findings) for findings in categorized_findings.values())
        files_with_issues = len([f for f in file_analyses if f.findings])
        
        # Calculate risk level and recommendation
        risk_level, recommendation = self._calculate_risk_assessment(categorized_findings)
        
        return {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'generator_version': '2.3.30',
                'format_version': '1.0',
                'schema_description': 'Privacy analysis data optimized for AI consumption',
                'analysis_engine': 'DualPurposeContentSafety v2.3.15+',
                'project_name': self.project_path.name
            },
            
            'privacy_summary': {
                'files_scanned': len(file_analyses),
                'files_with_issues': files_with_issues,
                'total_privacy_issues': total_findings,
                'risk_level': risk_level,
                'recommendation': recommendation,
                'analysis_scope': {
                    'target_extensions': sorted(list(self.target_extensions)),
                    'excluded_patterns': sorted(list(self.exclude_patterns))
                }
            },
            
            'findings_by_category': {
                'critical_pii': self._format_findings_for_yaml(categorized_findings['critical_pii']),
                'credentials': self._format_findings_for_yaml(categorized_findings['credentials']),
                'international_pii': self._format_findings_for_yaml(categorized_findings['international_pii']),
                'personal_info': self._format_findings_for_yaml(categorized_findings['personal_info']),
                'professional_content': self._format_findings_for_yaml(categorized_findings['professional_content'])
            },
            
            'findings_by_severity': self._group_findings_by_severity(categorized_findings),
            
            'findings_by_location': self._group_findings_by_location(categorized_findings),
            
            'compliance_guidance': self._build_compliance_guidance_yaml(categorized_findings),
            
            'performance_metrics': {
                'generation_time_seconds': (datetime.now() - start_time).total_seconds(),
                'average_file_analysis_ms': sum(f.analysis_time_ms for f in file_analyses) / len(file_analyses) if file_analyses else 0.0,
                'total_files_processed': len(file_analyses),
                'detection_coverage_regions': ['US', 'EU', 'UK', 'India', 'Singapore', 'Australia']
            },
            
            'ai_consumption_metadata': {
                'parsing_instruction': 'Use yaml.safe_load() for secure parsing',
                'data_access_examples': {
                    'total_issues': "data['privacy_summary']['total_privacy_issues']",
                    'risk_level': "data['privacy_summary']['risk_level']",
                    'critical_pii_count': "len(data['findings_by_category']['critical_pii'])",
                    'findings_at_location': "data['findings_by_location']['file.py:line']"
                },
                'recommended_libraries': ['PyYAML', 'ruamel.yaml'],
                'schema_stability': 'format_version tracks breaking changes'
            }
        }
    
    def _format_findings_for_yaml(self, findings: List[SecurityFinding]) -> List[Dict[str, Any]]:
        """
        Format findings list for YAML output with type-safe data.
        
        Args:
            findings: Security findings to format
            
        Returns:
            List of finding dictionaries optimized for YAML
        """
        yaml_findings = []
        
        for finding in findings:
            yaml_finding = {
                'type': finding.type,
                'location': finding.location,
                'severity': finding.severity,
                'confidence': float(finding.confidence),  # Ensure numeric type
                'risk_explanation': finding.risk_explanation,
                'remediation': finding.remediation
            }
            
            # Add additional metadata if available
            if hasattr(finding, 'metadata') and finding.metadata:
                yaml_finding['metadata'] = finding.metadata
            
            yaml_findings.append(yaml_finding)
        
        return yaml_findings
    
    def _group_findings_by_severity(self, categorized_findings: Dict[str, List[SecurityFinding]]) -> Dict[str, Any]:
        """
        Group all findings by severity level for easy filtering.
        
        Args:
            categorized_findings: Categorized findings
            
        Returns:
            Severity-based grouping with counts and examples
        """
        severity_groups = defaultdict(list)
        
        for category_findings in categorized_findings.values():
            for finding in category_findings:
                severity_groups[finding.severity].append({
                    'type': finding.type,
                    'location': finding.location,
                    'category': self._classify_finding(finding)
                })
        
        # Add counts and statistics
        severity_data = {}
        for severity, findings in severity_groups.items():
            severity_data[severity] = {
                'count': len(findings),
                'findings': findings
            }
        
        return severity_data
    
    def _group_findings_by_location(self, categorized_findings: Dict[str, List[SecurityFinding]]) -> Dict[str, Any]:
        """
        Group findings by file location for location-based analysis.
        
        Args:
            categorized_findings: Categorized findings
            
        Returns:
            Location-based grouping with consolidated issues
        """
        location_groups = defaultdict(list)
        
        for category_findings in categorized_findings.values():
            for finding in category_findings:
                location_groups[finding.location].append({
                    'type': finding.type,
                    'severity': finding.severity,
                    'category': self._classify_finding(finding),
                    'confidence': float(finding.confidence)
                })
        
        # Process location groups with statistics
        location_data = {}
        for location, findings in location_groups.items():
            severities = [f['severity'] for f in findings]
            location_data[location] = {
                'issue_count': len(findings),
                'primary_severity': max(severities, key=['critical', 'high', 'medium', 'low'].index) if severities else 'unknown',
                'findings': findings,
                'categories_present': list(set(f['category'] for f in findings))
            }
        
        return location_data
    
    def _build_compliance_guidance_yaml(self, categorized_findings: Dict[str, List[SecurityFinding]]) -> Dict[str, Any]:
        """
        Build compliance guidance section optimized for YAML structure.
        
        Args:
            categorized_findings: Categorized findings
            
        Returns:
            Structured compliance guidance data
        """
        pii_count = len(categorized_findings['personal_info']) + len(categorized_findings['international_pii'])
        critical_pii_count = len(categorized_findings['critical_pii'])
        credentials_count = len(categorized_findings['credentials'])
        
        return {
            'gdpr': {
                'applicable': pii_count > 0,
                'pii_items_detected': pii_count,
                'risk_level': 'high' if pii_count >= 10 else 'medium' if pii_count > 0 else 'low',
                'recommendations': [
                    'Ensure lawful basis for processing personal data',
                    'Implement data minimization and purpose limitation', 
                    'Consider data protection impact assessment (DPIA)',
                    'Update privacy notices for data collection'
                ] if pii_count > 0 else ['No personal data detected - maintain privacy-by-design']
            },
            
            'ccpa': {
                'applicable': critical_pii_count > 0,
                'personal_identifiers_detected': critical_pii_count,
                'risk_level': 'high' if critical_pii_count >= 5 else 'medium' if critical_pii_count > 0 else 'low', 
                'recommendations': [
                    'Ensure consumer privacy rights are respected',
                    'Implement data deletion and portability mechanisms',
                    'Update privacy notices for data collection',
                    'Establish consumer request handling procedures'
                ] if critical_pii_count > 0 else ['No critical personal identifiers detected']
            },
            
            'security': {
                'applicable': credentials_count > 0,
                'credential_exposures_detected': credentials_count,
                'risk_level': 'critical' if credentials_count >= 5 else 'high' if credentials_count > 0 else 'low',
                'recommendations': [
                    'Rotate all exposed credentials immediately',
                    'Implement environment variable management',
                    'Consider secrets management solution',
                    'Add pre-commit hooks for credential scanning'
                ] if credentials_count > 0 else ['No credential exposures detected']
            },
            
            'general': {
                'recommendations': [
                    'Implement pre-commit hooks for privacy scanning',
                    'Train development team on privacy-by-design principles', 
                    'Regular privacy audits and assessments',
                    'Document data processing activities',
                    'Establish incident response procedures'
                ]
            }
        }
    
    def _calculate_risk_assessment(self, categorized_findings: Dict[str, List[SecurityFinding]]) -> tuple[str, str]:
        """
        Calculate overall risk level and recommendation based on findings.
        
        Args:
            categorized_findings: Categorized findings
            
        Returns:
            Tuple of (risk_level, recommendation)
        """
        critical_count = len(categorized_findings['critical_pii'])
        credentials_count = len(categorized_findings['credentials'])
        total_findings = sum(len(findings) for findings in categorized_findings.values())
        
        high_severity_count = sum(
            len([f for f in findings if f.severity in ['critical', 'high']])
            for findings in categorized_findings.values()
        )
        
        if critical_count > 0 or credentials_count >= 3 or high_severity_count >= 10:
            return "HIGH", "Immediate attention required - critical privacy issues detected"
        elif high_severity_count > 0 or total_findings >= 5:
            return "MEDIUM", "Review and remediate identified privacy issues"
        elif total_findings > 0:
            return "LOW", "Monitor identified issues and maintain privacy practices"
        else:
            return "MINIMAL", "No significant privacy issues detected"


# Standalone execution capability (matching parent class pattern)
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python privacy_yaml_generator.py <project_path>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    generator = PrivacyYamlGenerator(project_path)
    report_path = generator.generate_yaml_report()
    print(f"Privacy YAML report generated: {report_path}")