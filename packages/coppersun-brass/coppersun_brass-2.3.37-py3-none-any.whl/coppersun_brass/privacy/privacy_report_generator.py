"""
Privacy Report Generator

Self-contained privacy and PII analysis system that generates independent
.brass/PRIVACY_ANALYSIS.md reports using the proven DualPurposeContentSafety
technology without modifying existing systems.

Key Features:
- Uses DualPurposeContentSafety directly for accurate detection
- Smart deduplication to prevent over-reporting 
- Clear categorization by PII type, severity, and compliance region
- Professional markdown report generation
- Completely self-contained with no external dependencies
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

# Import the proven privacy technology from Phase 2
from ..integrations.content_safety import DualPurposeContentSafety, SecurityFinding

logger = logging.getLogger(__name__)


@dataclass
class FileAnalysis:
    """Results of analyzing a single file for privacy issues."""
    file_path: str
    findings: List[SecurityFinding]
    analysis_time_ms: float
    file_size_bytes: int


class PrivacyReportGenerator:
    """
    Self-contained privacy report generator.
    
    Creates independent .brass/PRIVACY_ANALYSIS.md reports by:
    1. Scanning project files for privacy/PII content
    2. Using DualPurposeContentSafety for accurate detection
    3. Applying smart deduplication to prevent over-reporting
    4. Categorizing findings by type, severity, and compliance region
    5. Generating professional, actionable markdown reports
    """
    
    def __init__(self, project_path: str):
        """
        Initialize privacy report generator.
        
        Args:
            project_path: Root path of project to analyze
        """
        self.project_path = Path(project_path).resolve()
        self.brass_dir = self.project_path / '.brass'
        
        # Initialize the proven content safety system
        self.content_safety = DualPurposeContentSafety()
        
        # File extensions to analyze
        self.target_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.sql', '.yaml', '.yml', '.json', '.xml', '.env', '.config',
            '.properties', '.ini', '.toml', '.md', '.txt'
        }
        
        # Files/directories to exclude
        self.exclude_patterns = {
            '.git', '.svn', '.hg', '__pycache__', '.pytest_cache',
            'node_modules', '.venv', 'venv', '.env', 'build', 'dist',
            '.brass', '.idea', '.vscode', '.DS_Store'
        }
        
        logger.info(f"Privacy report generator initialized for project: {self.project_path}")
    
    def generate_report(self) -> str:
        """
        Generate complete privacy analysis report.
        
        Returns:
            Path to generated .brass/PRIVACY_ANALYSIS.md file
        """
        start_time = datetime.now()
        
        logger.info("Starting privacy analysis report generation")
        
        # Ensure .brass directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        # Phase 1: Scan project files
        logger.info("Phase 1: Scanning project files")
        file_analyses = self._scan_project_files()
        
        # Phase 2: Collect and deduplicate findings
        logger.info("Phase 2: Collecting and deduplicating findings")
        all_findings = []
        for analysis in file_analyses:
            all_findings.extend(analysis.findings)
        
        deduplicated_findings = self._deduplicate_findings(all_findings)
        
        # Phase 3: Categorize findings
        logger.info("Phase 3: Categorizing findings")
        categorized_findings = self._categorize_findings(deduplicated_findings)
        
        # Phase 4: Generate markdown report
        logger.info("Phase 4: Generating markdown report")
        report_content = self._generate_markdown_report(
            file_analyses, categorized_findings, start_time
        )
        
        # Phase 5: Write report file
        report_path = self.brass_dir / 'PRIVACY_ANALYSIS.md'
        report_path.write_text(report_content, encoding='utf-8')
        
        generation_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Privacy report generated successfully in {generation_time:.2f}s: {report_path}")
        
        return str(report_path)
    
    def _scan_project_files(self) -> List[FileAnalysis]:
        """
        Scan all relevant project files for privacy issues.
        
        Returns:
            List of FileAnalysis results for each scanned file
        """
        file_analyses = []
        scanned_count = 0
        skipped_count = 0
        
        for file_path in self._discover_files():
            try:
                analysis = self._analyze_single_file(file_path)
                if analysis:
                    file_analyses.append(analysis)
                    scanned_count += 1
                else:
                    skipped_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to analyze file {file_path}: {e}")
                skipped_count += 1
                continue
        
        logger.info(f"File scanning complete: {scanned_count} analyzed, {skipped_count} skipped")
        return file_analyses
    
    def _discover_files(self) -> List[Path]:
        """
        Discover all relevant files to analyze in the project.
        
        Returns:
            List of file paths to analyze
        """
        discovered_files = []
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_patterns]
            
            root_path = Path(root)
            
            for file_name in files:
                file_path = root_path / file_name
                
                # Check if file extension is in our target list
                if file_path.suffix.lower() in self.target_extensions:
                    # Skip if file is too large (>1MB)
                    try:
                        if file_path.stat().st_size > 1024 * 1024:
                            continue
                    except OSError:
                        continue
                    
                    discovered_files.append(file_path)
        
        logger.info(f"Discovered {len(discovered_files)} files for analysis")
        return discovered_files
    
    def _analyze_single_file(self, file_path: Path) -> Optional[FileAnalysis]:
        """
        Analyze a single file for privacy issues.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            FileAnalysis result or None if file couldn't be analyzed
        """
        try:
            start_time = datetime.now()
            
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            file_size = len(content.encode('utf-8'))
            
            # Skip empty files
            if len(content.strip()) == 0:
                return None
            
            # Analyze content using DualPurposeContentSafety
            relative_path = str(file_path.relative_to(self.project_path))
            safety_result = self.content_safety.analyze_content_comprehensive(
                content=content,
                file_path=relative_path,
                line_number=1
            )
            
            analysis_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return FileAnalysis(
                file_path=relative_path,
                findings=safety_result.customer_findings,
                analysis_time_ms=analysis_time,
                file_size_bytes=file_size
            )
            
        except Exception as e:
            logger.debug(f"Could not analyze file {file_path}: {e}")
            return None
    
    def _deduplicate_findings(self, findings: List[SecurityFinding]) -> List[SecurityFinding]:
        """
        Apply smart deduplication to prevent over-reporting.
        
        Addresses the Phase 2 issue where same API key was reported 3 times.
        
        Args:
            findings: Raw findings list (may contain duplicates)
            
        Returns:
            Deduplicated findings list
        """
        seen_signatures = set()
        deduplicated = []
        
        for finding in findings:
            # Create unique signature for this finding
            signature = self._create_finding_signature(finding)
            
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                deduplicated.append(finding)
                
        reduction_count = len(findings) - len(deduplicated)
        if reduction_count > 0:
            logger.info(f"Deduplication removed {reduction_count} duplicate findings")
            
        return deduplicated
    
    def _create_finding_signature(self, finding: SecurityFinding) -> str:
        """
        Create unique signature for a finding to enable deduplication.
        
        Args:
            finding: SecurityFinding to create signature for
            
        Returns:
            Unique string signature
        """
        # Combine key identifying information
        signature_data = f"{finding.location}|{finding.type}|{finding.description[:100]}"
        return hashlib.md5(signature_data.encode()).hexdigest()
    
    def _categorize_findings(self, findings: List[SecurityFinding]) -> Dict[str, List[SecurityFinding]]:
        """
        Categorize findings by type, severity, and compliance requirements.
        
        Args:
            findings: Deduplicated findings to categorize
            
        Returns:
            Dictionary of categorized findings
        """
        categories = {
            'critical_pii': [],      # SSN, credit cards, etc.
            'personal_info': [],     # Email, phone, addresses
            'credentials': [],       # API keys, passwords, tokens
            'international_pii': [], # Non-US PII (NHS, Aadhaar, etc.)
            'professional_content': [] # Profanity, inappropriate language
        }
        
        for finding in findings:
            category = self._classify_finding(finding)
            if category in categories:
                categories[category].append(finding)
        
        # Sort each category by severity
        for category_name, category_findings in categories.items():
            categories[category_name] = self._sort_by_severity(category_findings)
        
        return categories
    
    def _classify_finding(self, finding: SecurityFinding) -> str:
        """
        Classify a finding into appropriate category.
        
        Args:
            finding: SecurityFinding to classify
            
        Returns:
            Category name
        """
        finding_type = finding.type.lower()
        risk_text = finding.risk_explanation.lower()
        
        # Critical PII (high-risk identifiers)
        if any(term in finding_type for term in ['ssn', 'social security', 'credit card', 'tax file']):
            return 'critical_pii'
        
        # International PII
        if any(term in finding_type for term in ['nhs', 'aadhaar', 'nino', 'nric', 'medicare']):
            return 'international_pii'
        
        # Credentials and secrets
        if any(term in finding_type for term in ['api key', 'token', 'password', 'secret', 'credential']):
            return 'credentials'
        
        # Professional content issues
        if any(term in finding_type for term in ['profanity', 'inappropriate', 'language']):
            return 'professional_content'
        
        # Default to personal info
        return 'personal_info'
    
    def _sort_by_severity(self, findings: List[SecurityFinding]) -> List[SecurityFinding]:
        """
        Sort findings by severity level.
        
        Args:
            findings: Findings to sort
            
        Returns:
            Sorted findings (critical first)
        """
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        return sorted(findings, key=lambda f: severity_order.get(f.severity, 4))
    
    def _generate_markdown_report(
        self, 
        file_analyses: List[FileAnalysis], 
        categorized_findings: Dict[str, List[SecurityFinding]],
        start_time: datetime
    ) -> str:
        """
        Generate professional markdown privacy report.
        
        Args:
            file_analyses: File analysis results
            categorized_findings: Categorized and sorted findings
            start_time: Report generation start time
            
        Returns:
            Complete markdown report content
        """
        sections = []
        
        # Header
        sections.append("# Privacy & PII Analysis Report\n")
        sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        sections.append(f"*Project: {self.project_path.name}*\n\n")
        
        # Executive Summary
        total_findings = sum(len(findings) for findings in categorized_findings.values())
        total_files = len(file_analyses)
        files_with_issues = len([f for f in file_analyses if f.findings])
        
        sections.append("## 📊 Executive Summary\n")
        sections.append(f"- **Files Scanned**: {total_files}\n")
        sections.append(f"- **Files with Issues**: {files_with_issues}\n")
        sections.append(f"- **Total Privacy Issues**: {total_findings}\n")
        
        # Risk level
        critical_count = len(categorized_findings['critical_pii'])
        high_severity_count = sum(
            len([f for f in findings if f.severity in ['critical', 'high']])
            for findings in categorized_findings.values()
        )
        
        if critical_count > 0 or high_severity_count >= 5:
            risk_level = "🚨 HIGH"
            recommendations = "Immediate attention required"
        elif high_severity_count > 0 or total_findings >= 3:
            risk_level = "⚠️ MEDIUM" 
            recommendations = "Review and remediate identified issues"
        else:
            risk_level = "✅ LOW"
            recommendations = "Monitor and maintain current practices"
            
        sections.append(f"- **Risk Level**: {risk_level}\n")
        sections.append(f"- **Recommendation**: {recommendations}\n\n")
        
        # Detailed findings by category
        if total_findings > 0:
            sections.append("## 🔍 Detailed Findings\n")
            
            # Critical PII
            if categorized_findings['critical_pii']:
                sections.append("### 🚨 Critical PII (Immediate Action Required)\n")
                sections.extend(self._format_findings_section(categorized_findings['critical_pii']))
            
            # Credentials
            if categorized_findings['credentials']:
                sections.append("### 🔑 Credentials & Secrets\n")
                sections.extend(self._format_findings_section(categorized_findings['credentials']))
            
            # International PII
            if categorized_findings['international_pii']:
                sections.append("### 🌍 International PII\n")
                sections.extend(self._format_findings_section(categorized_findings['international_pii']))
            
            # Personal Information
            if categorized_findings['personal_info']:
                sections.append("### 📧 Personal Information\n")
                sections.extend(self._format_findings_section(categorized_findings['personal_info']))
            
            # Professional Content
            if categorized_findings['professional_content']:
                sections.append("### 💼 Professional Content Issues\n")
                sections.extend(self._format_findings_section(categorized_findings['professional_content']))
        
        else:
            sections.append("## ✅ No Privacy Issues Detected\n")
            sections.append("No privacy or PII concerns were identified in the scanned files.\n\n")
        
        # Compliance guidance
        sections.append("## 📋 Compliance Guidance\n")
        sections.extend(self._generate_compliance_guidance(categorized_findings))
        
        # Performance metrics
        generation_time = (datetime.now() - start_time).total_seconds()
        avg_file_time = sum(f.analysis_time_ms for f in file_analyses) / len(file_analyses) if file_analyses else 0
        
        sections.append("## ⚡ Analysis Performance\n")
        sections.append(f"- **Total Generation Time**: {generation_time:.2f} seconds\n")
        sections.append(f"- **Average File Analysis**: {avg_file_time:.2f}ms\n")
        sections.append(f"- **Analysis Engine**: DualPurposeContentSafety v2.3.15+\n")
        sections.append(f"- **Detection Coverage**: US, EU, UK, India, Singapore, Australia\n\n")
        
        # Footer
        sections.append("---\n")
        sections.append("*This report was generated by Copper Sun Brass Privacy Analysis System.*\n")
        sections.append("*For questions or compliance guidance, consult your security team.*\n")
        
        return "".join(sections)
    
    def _format_findings_section(self, findings: List[SecurityFinding]) -> List[str]:
        """
        Format a list of findings for markdown display.
        
        Args:
            findings: Findings to format
            
        Returns:
            List of markdown lines
        """
        lines = []
        
        for i, finding in enumerate(findings, 1):
            lines.append(f"#### {i}. {finding.type}\n")
            lines.append(f"**Location**: `{finding.location}`\n")
            lines.append(f"**Severity**: {finding.severity.title()}\n")
            lines.append(f"**Risk**: {finding.risk_explanation}\n")
            lines.append(f"**Remediation**: {finding.remediation}\n")
            lines.append(f"**Confidence**: {finding.confidence:.0%}\n\n")
        
        return lines
    
    def _generate_compliance_guidance(self, categorized_findings: Dict[str, List[SecurityFinding]]) -> List[str]:
        """
        Generate compliance guidance based on findings.
        
        Args:
            categorized_findings: Categorized findings
            
        Returns:
            List of compliance guidance lines
        """
        lines = []
        
        # GDPR guidance
        pii_count = len(categorized_findings['personal_info']) + len(categorized_findings['international_pii'])
        if pii_count > 0:
            lines.append("### 🇪🇺 GDPR Compliance\n")
            lines.append(f"- **{pii_count} personal data items** detected\n")
            lines.append("- Ensure lawful basis for processing personal data\n")
            lines.append("- Implement data minimization and purpose limitation\n")
            lines.append("- Consider data protection impact assessment (DPIA)\n\n")
        
        # CCPA guidance
        us_pii_count = len(categorized_findings['critical_pii'])
        if us_pii_count > 0:
            lines.append("### 🇺🇸 CCPA Compliance\n")
            lines.append(f"- **{us_pii_count} personal identifiers** detected\n")
            lines.append("- Ensure consumer privacy rights are respected\n")
            lines.append("- Implement data deletion and portability mechanisms\n")
            lines.append("- Update privacy notices for data collection\n\n")
        
        # Security recommendations
        cred_count = len(categorized_findings['credentials'])
        if cred_count > 0:
            lines.append("### 🔒 Security Recommendations\n")
            lines.append(f"- **{cred_count} credential exposures** detected\n")
            lines.append("- Rotate all exposed credentials immediately\n")
            lines.append("- Implement environment variable management\n")
            lines.append("- Consider secrets management solution\n\n")
        
        # General recommendations
        lines.append("### 📋 General Recommendations\n")
        lines.append("- Implement pre-commit hooks for privacy scanning\n")
        lines.append("- Train development team on privacy-by-design principles\n")
        lines.append("- Regular privacy audits and assessments\n")
        lines.append("- Document data processing activities\n\n")
        
        return lines


# Standalone execution capability
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python privacy_report_generator.py <project_path>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    generator = PrivacyReportGenerator(project_path)
    report_path = generator.generate_report()
    print(f"Privacy report generated: {report_path}")