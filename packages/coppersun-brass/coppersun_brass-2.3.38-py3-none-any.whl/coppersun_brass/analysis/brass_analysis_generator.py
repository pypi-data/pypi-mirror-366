"""
Brass Analysis Generator

Executive analysis report generator that creates .brass/brass_analysis.md
with high-level project intelligence following the PrivacyReportGenerator pattern.

Key Features:
- Executive dashboard format (concise, actionable)
- Smart data sampling (performance-optimized queries)
- Cross-referenced intelligence (links to detailed files)
- Professional markdown output
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


@dataclass
class SecurityOverview:
    """Security analysis overview data."""
    total_issues: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    top_categories: List[Tuple[str, int]]
    files_with_issues: int


@dataclass
class QualityOverview:
    """Code quality overview data."""
    total_todos: int
    critical_todos: int
    high_priority_todos: int
    complexity_average: float
    high_complexity_functions: int
    largest_functions: List[Tuple[str, str, int]]


@dataclass
class ArchitectureOverview:
    """Architecture analysis overview data."""
    functions_analyzed: int
    classes_analyzed: int
    avg_function_length: float
    external_imports: int
    internal_modules: int
    circular_dependencies: int


class BrassAnalysisGenerator:
    """
    Executive analysis report generator.
    
    Creates .brass/brass_analysis.md with project health dashboard,
    security summary, code quality overview, and architecture insights.
    
    Follows PrivacyReportGenerator pattern for clean integration.
    """
    
    def __init__(self, project_path: str, storage):
        """
        Initialize brass analysis generator.
        
        Args:
            project_path: Root path of project to analyze
            storage: BrassStorage instance for data access
            
        Raises:
            ValueError: If storage doesn't implement required methods
        """
        # Validate storage interface
        required_methods = ['get_observations_by_type', 'get_all_observations']
        for method in required_methods:
            if not hasattr(storage, method):
                raise ValueError(f"Storage must implement {method} method")
        
        self.project_path = Path(project_path)
        self.storage = storage
        self.brass_dir = self.project_path / '.brass'
        self.output_path = self.brass_dir / 'brass_analysis.md'
        
        logger.info(f"Brass analysis generator initialized for project: {self.project_path}")
    
    def generate_report(self) -> str:
        """
        Generate executive analysis report.
        
        Returns:
            Path to generated .brass/brass_analysis.md file
        """
        start_time = datetime.now()
        
        logger.info("Starting brass analysis report generation")
        
        # Ensure .brass directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        # Phase 1: Gather overview data with smart sampling
        logger.info("Phase 1: Gathering security overview")
        security_overview = self._get_security_overview()
        
        logger.info("Phase 2: Gathering quality overview")
        quality_overview = self._get_quality_overview()
        
        logger.info("Phase 3: Gathering architecture overview")
        architecture_overview = self._get_architecture_overview()
        
        # Phase 4: Compute health scores
        logger.info("Phase 4: Computing health scores")
        health_scores = self._compute_health_scores(security_overview, quality_overview)
        
        # Phase 5: Generate markdown report
        logger.info("Phase 5: Generating markdown report")
        report_content = self._generate_markdown_report(
            security_overview, quality_overview, architecture_overview, health_scores, start_time
        )
        
        # Phase 6: Write report
        self.output_path.write_text(report_content, encoding='utf-8')
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        logger.info(f"Brass analysis report generated successfully in {generation_time:.2f}s: {self.output_path}")
        return str(self.output_path)
    
    def _get_security_overview(self) -> SecurityOverview:
        """Get security analysis overview with smart sampling."""
        try:
            # Get total count efficiently
            total_issues = self._count_observations_by_type('security_issue')
            
            # Get representative sample of security issues for analysis
            security_issues = self.storage.get_observations_by_type('security_issue', limit=1000)
            
            # Analyze severity distribution
            severity_counts = defaultdict(int)
            categories = defaultdict(int)
            files_with_issues = set()
            
            for issue in security_issues:
                try:
                    data = json.loads(issue['data']) if isinstance(issue['data'], str) else issue['data']
                    severity = data.get('severity', 'unknown').lower()
                    severity_counts[severity] += 1
                    
                    # Extract category from pattern_name or description
                    pattern_name = data.get('pattern_name', '')
                    categories[pattern_name] += 1
                    
                    # Track files with issues
                    file_path = data.get('file_path', '')
                    if file_path:
                        files_with_issues.add(file_path)
                        
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse security issue data: {e}")
                    continue
            
            # Scale counts to represent full dataset
            scale_factor = total_issues / len(security_issues) if security_issues and len(security_issues) > 0 else 1
            
            return SecurityOverview(
                total_issues=total_issues,
                critical_count=int(severity_counts['critical'] * scale_factor),
                high_count=int(severity_counts['high'] * scale_factor), 
                medium_count=int(severity_counts['medium'] * scale_factor),
                low_count=int(severity_counts['low'] * scale_factor),
                top_categories=sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5],
                files_with_issues=len(files_with_issues)
            )
            
        except Exception as e:
            logger.error(f"Failed to get security overview: {e}")
            return SecurityOverview(0, 0, 0, 0, 0, [], 0)
    
    def _get_quality_overview(self) -> QualityOverview:
        """Get code quality overview with smart sampling."""
        try:
            # Get TODO data
            total_todos = self._count_observations_by_type('todo')
            todo_issues = self.storage.get_observations_by_type('todo', limit=500)
            
            # Analyze TODO priorities
            critical_todos = 0
            high_priority_todos = 0
            
            for todo in todo_issues:
                try:
                    priority = todo.get('priority', 0)
                    if priority >= 80:
                        critical_todos += 1
                    elif priority >= 60:
                        high_priority_todos += 1
                except (KeyError, TypeError):
                    continue
            
            # Get code entity data for complexity analysis
            code_entities = self.storage.get_observations_by_type('code_entity', limit=500)
            
            function_lengths = []
            largest_functions = []
            functions_analyzed = 0
            classes_analyzed = 0
            
            for entity in code_entities:
                try:
                    data = json.loads(entity['data']) if isinstance(entity['data'], str) else entity['data']
                    entity_type = data.get('entity_type', '')
                    
                    if entity_type == 'function':
                        functions_analyzed += 1
                        length = data.get('line_count', 0)
                        if length > 0:
                            function_lengths.append(length)
                            if length > 50:  # Consider large functions
                                largest_functions.append((
                                    data.get('entity_name', 'unknown'),
                                    data.get('file_path', '').split('/')[-1],
                                    length
                                ))
                    elif entity_type == 'class':
                        classes_analyzed += 1
                        
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse code entity data: {e}")
                    continue
            
            # Sort largest functions
            largest_functions.sort(key=lambda x: x[2], reverse=True)
            
            return QualityOverview(
                total_todos=total_todos,
                critical_todos=critical_todos,
                high_priority_todos=high_priority_todos,
                complexity_average=sum(function_lengths) / len(function_lengths) if function_lengths else 0,
                high_complexity_functions=len([l for l in function_lengths if l > 50]),
                largest_functions=largest_functions[:3]
            )
            
        except Exception as e:
            logger.error(f"Failed to get quality overview: {e}")
            return QualityOverview(0, 0, 0, 0.0, 0, [])
    
    def _get_architecture_overview(self) -> ArchitectureOverview:
        """Get architecture overview with smart sampling."""
        try:
            # Get code entity counts
            code_entities = self.storage.get_observations_by_type('code_entity', limit=500)
            
            functions_analyzed = 0
            classes_analyzed = 0
            function_lengths = []
            
            for entity in code_entities:
                try:
                    data = json.loads(entity['data']) if isinstance(entity['data'], str) else entity['data']
                    entity_type = data.get('entity_type', '')
                    
                    if entity_type == 'function':
                        functions_analyzed += 1
                        length = data.get('line_count', 0)
                        if length > 0:
                            function_lengths.append(length)
                    elif entity_type == 'class':
                        classes_analyzed += 1
                        
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse architecture entity data: {e}")
                    continue
            
            # Placeholder values for dependency analysis (would need separate implementation)
            # In a full implementation, this would analyze import statements
            external_imports = 0
            internal_modules = 0
            circular_dependencies = 0
            
            return ArchitectureOverview(
                functions_analyzed=functions_analyzed,
                classes_analyzed=classes_analyzed,
                avg_function_length=sum(function_lengths) / len(function_lengths) if function_lengths else 0,
                external_imports=external_imports,
                internal_modules=internal_modules,
                circular_dependencies=circular_dependencies
            )
            
        except Exception as e:
            logger.error(f"Failed to get architecture overview: {e}")
            return ArchitectureOverview(0, 0, 0.0, 0, 0, 0)
    
    def _compute_health_scores(self, security: SecurityOverview, quality: QualityOverview) -> Dict[str, Any]:
        """Compute project health scores based on analysis data."""
        try:
            # Security score (0-10, lower is better for issues)
            security_score = 10.0
            if security.total_issues > 0:
                # Penalize based on severity
                penalty = (security.critical_count * 3 + security.high_count * 2 + security.medium_count * 1) / security.total_issues
                security_score = max(0, 10 - penalty * 2)
            
            # Quality score based on technical debt
            quality_score = 10.0
            if quality.total_todos > 0:
                critical_ratio = quality.critical_todos / quality.total_todos
                quality_score = max(0, 10 - critical_ratio * 5)
            
            # Overall score (weighted average)
            overall_score = (security_score * 0.6 + quality_score * 0.4)
            
            # Risk level
            if overall_score >= 8:
                risk_level = "low"
            elif overall_score >= 6:
                risk_level = "medium"
            else:
                risk_level = "high"
            
            return {
                'overall_score': round(overall_score, 1),
                'security_score': round(security_score, 1),
                'quality_score': round(quality_score, 1),
                'risk_level': risk_level
            }
            
        except Exception as e:
            logger.error(f"Failed to compute health scores: {e}")
            return {'overall_score': 0.0, 'security_score': 0.0, 'quality_score': 0.0, 'risk_level': 'unknown'}
    
    def _count_observations_by_type(self, obs_type: str) -> int:
        """Count observations of a specific type efficiently."""
        try:
            # Use storage method if available, otherwise estimate
            if hasattr(self.storage, 'count_observations_by_type'):
                return self.storage.count_observations_by_type(obs_type)
            else:
                # Fallback: get sample and estimate
                sample = self.storage.get_observations_by_type(obs_type, limit=100)
                all_obs = self.storage.get_all_observations(limit=5000)
                total_count = len([obs for obs in all_obs if obs.get('type') == obs_type])
                return total_count
        except Exception as e:
            logger.error(f"Failed to count observations of type {obs_type}: {e}")
            return 0
    
    def _generate_markdown_report(
        self,
        security: SecurityOverview,
        quality: QualityOverview, 
        architecture: ArchitectureOverview,
        health_scores: Dict[str, Any],
        start_time: datetime
    ) -> str:
        """Generate the markdown report content."""
        
        lines = []
        
        # Header
        lines.append("# Project Analysis Dashboard")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("")
        
        # Health Overview
        lines.append("## 📊 Project Health Overview")
        lines.append(f"- **Overall Score**: {health_scores['overall_score']}/10 ({self._score_label(health_scores['overall_score'])})")
        lines.append(f"- **Security Score**: {health_scores['security_score']}/10 ({self._score_label(health_scores['security_score'])})")
        lines.append(f"- **Quality Score**: {health_scores['quality_score']}/10 ({self._score_label(health_scores['quality_score'])})")
        lines.append(f"- **Risk Level**: {health_scores['risk_level'].title()}")
        lines.append("")
        
        # Security Summary
        lines.append("## 🔒 Security Summary")
        lines.append(f"**Total Issues**: {security.total_issues:,}")
        lines.append("")
        
        if security.total_issues > 0:
            lines.append("### By Severity")
            if security.critical_count > 0:
                lines.append(f"- **Critical**: {security.critical_count} (immediate attention required)")
            if security.high_count > 0:
                lines.append(f"- **High**: {security.high_count} (address in next sprint)")
            if security.medium_count > 0:
                lines.append(f"- **Medium**: {security.medium_count} (planned remediation)")
            if security.low_count > 0:
                lines.append(f"- **Low**: {security.low_count} (backlog)")
            lines.append("")
            
            if security.top_categories:
                lines.append("### Top Issue Categories")
                for category, count in security.top_categories:
                    if category and count > 0:
                        lines.append(f"- **{category}**: {count} issues")
                lines.append("")
            
            lines.append(f"**Files Affected**: {security.files_with_issues} files")
        else:
            lines.append("✅ No security issues detected")
        
        lines.append("")
        lines.append("**📄 Details**: See `CODE_SECURITY_AND_QUALITY_ANALYSIS.md`")
        lines.append("")
        
        # Code Quality
        lines.append("## ⚙️ Code Quality")
        if quality.total_todos > 0:
            lines.append(f"**Total TODOs**: {quality.total_todos:,}")
            if quality.critical_todos > 0:
                lines.append(f"- **Critical**: {quality.critical_todos} (urgent fixes needed)")
            if quality.high_priority_todos > 0:
                lines.append(f"- **High Priority**: {quality.high_priority_todos} (important improvements)")
            lines.append("")
        
        if quality.complexity_average > 0:
            lines.append("### Complexity Analysis")
            lines.append(f"- **Average Function Length**: {quality.complexity_average:.1f} lines")
            if quality.high_complexity_functions > 0:
                lines.append(f"- **High Complexity Functions**: {quality.high_complexity_functions}")
            
            if quality.largest_functions:
                lines.append("- **Largest Functions**:")
                for name, file, length in quality.largest_functions:
                    lines.append(f"  - `{name}` in {file}: {length} lines")
            lines.append("")
        
        lines.append("**📄 Details**: See `todos.yaml`")
        lines.append("")
        
        # Architecture Overview
        lines.append("## 🏗️ Architecture Overview")
        if architecture.functions_analyzed > 0 or architecture.classes_analyzed > 0:
            lines.append("### Code Structure")
            if architecture.functions_analyzed > 0:
                lines.append(f"- **Functions Analyzed**: {architecture.functions_analyzed}")
            if architecture.classes_analyzed > 0:
                lines.append(f"- **Classes Analyzed**: {architecture.classes_analyzed}")
            if architecture.avg_function_length > 0:
                lines.append(f"- **Average Function Length**: {architecture.avg_function_length:.1f} lines")
            lines.append("")
        
        # Cross-references
        lines.append("## 🔗 Detailed Reports")
        lines.append("- **Security & Quality**: `CODE_SECURITY_AND_QUALITY_ANALYSIS.md`")
        lines.append("- **Privacy Analysis**: `privacy_analysis.yaml`")
        lines.append("- **TODO List**: `todos.yaml`")
        lines.append("- **Project Context**: `project_context.json`")
        lines.append("- **Enterprise Readiness**: `enterprise_readiness.json`")
        lines.append("")
        
        # Recommendations
        lines.append("## 📈 Key Recommendations")
        recommendations = self._generate_recommendations(security, quality, architecture)
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. **{rec}**")
        lines.append("")
        
        # Footer
        lines.append(f"*Report generated by Copper Sun Brass in {(datetime.now() - start_time).total_seconds():.1f}s*")
        
        return "\n".join(lines)
    
    def _score_label(self, score: float) -> str:
        """Convert numeric score to descriptive label."""
        if score >= 8:
            return "Excellent"
        elif score >= 6:
            return "Good"
        elif score >= 4:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _generate_recommendations(
        self, 
        security: SecurityOverview, 
        quality: QualityOverview, 
        architecture: ArchitectureOverview
    ) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Security recommendations
        if security.critical_count > 0:
            recommendations.append(f"Address {security.critical_count} critical security issues immediately")
        elif security.high_count > 0:
            recommendations.append(f"Prioritize {security.high_count} high-severity security issues")
        
        # Quality recommendations  
        if quality.critical_todos > 0:
            recommendations.append(f"Fix {quality.critical_todos} critical TODOs (estimated 2-8 hours)")
        elif quality.high_priority_todos > 0:
            recommendations.append(f"Address {quality.high_priority_todos} high-priority TODOs")
        
        # Complexity recommendations
        if quality.high_complexity_functions > 0:
            recommendations.append(f"Refactor {quality.high_complexity_functions} high-complexity functions")
        
        # Category-specific recommendations
        if security.top_categories:
            top_category, count = security.top_categories[0]
            if count > 50:  # Significant category
                recommendations.append(f"Focus on {top_category.lower()} ({count} issues)")
        
        # Default recommendation if none generated
        if not recommendations:
            recommendations.append("Continue monitoring and maintain current quality standards")
        
        return recommendations[:4]  # Limit to top 4 recommendations