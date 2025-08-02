"""
Brass YAML Generator

YAML variant of brass analysis generator that creates .brass/brass_analysis.yaml
with structured data optimized for AI consumption while preserving all intelligence.

Key Features:
- Structured YAML format for direct programmatic access
- Location-based consolidation to prevent duplicate entries  
- Type-safe data (native integers, floats, booleans, arrays)
- AI-optimized schema with consistent data access patterns
- Inherits data collection logic from BrassAnalysisGenerator
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict

from .brass_analysis_generator import (
    BrassAnalysisGenerator, 
    SecurityOverview, 
    QualityOverview, 
    ArchitectureOverview
)

logger = logging.getLogger(__name__)


class BrassYamlGenerator(BrassAnalysisGenerator):
    """
    YAML variant of brass analysis generator for AI consumption.
    
    Inherits data collection logic from BrassAnalysisGenerator but outputs
    structured YAML format optimized for programmatic access by AI agents.
    
    Follows evidence-based consolidation patterns from OutputGenerator
    to prevent duplicate entries and group similar issues by location.
    """
    
    def __init__(self, project_path: str, storage):
        """
        Initialize YAML brass analysis generator.
        
        Args:
            project_path: Root path of project to analyze
            storage: BrassStorage instance for data access
            
        Raises:
            ValueError: If storage doesn't implement required methods
        """
        super().__init__(project_path, storage)
        self.yaml_output_path = self.brass_dir / 'brass_analysis.yaml'
        
        logger.info(f"YAML brass analysis generator initialized for project: {self.project_path}")
    
    def generate_yaml_report(self) -> str:
        """
        Generate structured YAML analysis report for AI consumption.
        
        Returns:
            Path to generated .brass/brass_analysis.yaml file
        """
        start_time = datetime.now()
        
        logger.info("Starting YAML brass analysis report generation")
        
        # Ensure .brass directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        # Phase 1: Gather overview data (reuse parent logic)
        logger.info("Phase 1: Gathering security overview")
        security_overview = self._get_security_overview()
        
        logger.info("Phase 2: Gathering quality overview")
        quality_overview = self._get_quality_overview()
        
        logger.info("Phase 3: Gathering architecture overview")
        architecture_overview = self._get_architecture_overview()
        
        # Phase 4: Compute health scores (reuse parent logic)
        logger.info("Phase 4: Computing health scores")
        health_scores = self._compute_health_scores(security_overview, quality_overview)
        
        # Phase 5: Generate YAML structure with consolidation
        logger.info("Phase 5: Generating YAML structure with consolidation")
        yaml_data = self._generate_yaml_structure(
            security_overview, quality_overview, architecture_overview, health_scores, start_time
        )
        
        # Phase 6: Write YAML file
        logger.info("Phase 6: Writing YAML file")
        yaml_content = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        self.yaml_output_path.write_text(yaml_content, encoding='utf-8')
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        logger.info(f"YAML brass analysis report generated successfully in {generation_time:.2f}s: {self.yaml_output_path}")
        return str(self.yaml_output_path)
    
    def _generate_yaml_structure(
        self,
        security: SecurityOverview,
        quality: QualityOverview, 
        architecture: ArchitectureOverview,
        health_scores: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Generate structured YAML data with location-based consolidation.
        
        Applies consolidation patterns from OutputGenerator to prevent
        duplicate entries and group similar issues by file:line location.
        """
        
        # Get consolidated security issues by location
        consolidated_security = self._consolidate_security_issues()
        consolidated_quality = self._consolidate_quality_issues()
        
        yaml_structure = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'generator_version': '2.3.30',
                'project_path': str(self.project_path),
                'generation_time_seconds': (datetime.now() - start_time).total_seconds(),
                'format_version': '1.2',
                'schema_description': 'Enhanced YAML format with sophisticated agent intelligence and intelligent deduplication - AI recommendations, security classifications, ML confidence scores with consolidated identical issues',
                'deduplication_enabled': True
            },
            
            'project_health': {
                'overall_score': health_scores['overall_score'],
                'security_score': health_scores['security_score'],
                'quality_score': health_scores['quality_score'],
                'risk_level': health_scores['risk_level'],
                'score_explanation': {
                    'overall': self._score_label(health_scores['overall_score']),
                    'security': self._score_label(health_scores['security_score']),
                    'quality': self._score_label(health_scores['quality_score'])
                }
            },
            
            'security_summary': {
                'total_issues': security.total_issues,
                'files_with_issues': security.files_with_issues,
                'severity_distribution': {
                    'critical': security.critical_count,
                    'high': security.high_count,
                    'medium': security.medium_count,
                    'low': security.low_count
                },
                'top_categories': [
                    {
                        'category': category,
                        'count': count,
                        'percentage': round((count / security.total_issues * 100), 1) if security.total_issues > 0 else 0
                    }
                    for category, count in security.top_categories[:5]
                ],
                'issues_by_location': consolidated_security
            },
            
            'code_quality': {
                'todos': {
                    'total': quality.total_todos,
                    'critical': quality.critical_todos,
                    'high_priority': quality.high_priority_todos,
                    'completion_percentage': round(
                        ((quality.total_todos - quality.critical_todos - quality.high_priority_todos) / quality.total_todos * 100), 1
                    ) if quality.total_todos > 0 else 100
                },
                'complexity': {
                    'average_function_length': quality.complexity_average,
                    'high_complexity_functions': quality.high_complexity_functions,
                    'complexity_threshold': 50,
                    'largest_functions': [
                        {
                            'name': name,
                            'file': file,
                            'lines': lines,
                            'complexity_ratio': round(lines / quality.complexity_average, 1) if quality.complexity_average > 0 else 0
                        }
                        for name, file, lines in quality.largest_functions
                    ]
                },
                'quality_issues_by_location': consolidated_quality
            },
            
            'architecture': {
                'code_structure': {
                    'functions_analyzed': architecture.functions_analyzed,
                    'classes_analyzed': architecture.classes_analyzed,
                    'avg_function_length': architecture.avg_function_length,
                    'external_imports': architecture.external_imports,
                    'internal_modules': architecture.internal_modules,
                    'circular_dependencies': architecture.circular_dependencies
                },
                'structure_ratios': {
                    'class_to_function_ratio': round(
                        architecture.classes_analyzed / architecture.functions_analyzed, 2
                    ) if architecture.functions_analyzed > 0 else 0,
                    'external_to_internal_ratio': round(
                        architecture.external_imports / architecture.internal_modules, 2
                    ) if architecture.internal_modules > 0 else 0
                }
            },
            
            'recommendations': self._generate_structured_recommendations(security, quality, architecture),
            
            'cross_references': {
                'detailed_security': 'CODE_SECURITY_AND_QUALITY_ANALYSIS.md',
                'privacy_analysis': 'privacy_analysis.yaml',
                'todo_list': 'todos.yaml',
                'best_practices': 'best_practices.yaml',
                'project_context': 'project_context.json',
                'enterprise_readiness': 'enterprise_readiness.json',
                'markdown_version': 'brass_analysis.md'
            },
            
            'ai_consumption_metadata': {
                'format_version': '1.2',  # Enhanced with sophisticated fields and deduplication
                'enhanced_intelligence': True,
                'deduplication_applied': True,
                'sophisticated_fields_available': ['ai_recommendation', 'cwe', 'owasp', 'fix_complexity', 'ml_confidence', 'metadata', 'duplicate_count'],
                'recommended_parsers': ['PyYAML', 'ruamel.yaml'],
                'parsing_instruction': 'Use yaml.safe_load() for secure parsing',
                'data_access_examples': {
                    'overall_score': "data['project_health']['overall_score']",
                    'critical_security_count': "data['security_summary']['severity_distribution']['critical']",
                    'issues_at_location': "data['security_summary']['issues_by_location']['src/main.py:15']",
                    'ai_recommendation': "data['security_summary']['issues_by_location']['file.py:line']['consolidated_issues'][0]['ai_recommendation']",
                    'security_classification': "data['security_summary']['issues_by_location']['file.py:line']['consolidated_issues'][0]['cwe']",
                    'implementation_complexity': "data['security_summary']['issues_by_location']['file.py:line']['consolidated_issues'][0]['fix_complexity']",
                    'ml_confidence_score': "data['security_summary']['issues_by_location']['file.py:line']['consolidated_issues'][0]['ml_confidence']",
                    'rich_metadata': "data['security_summary']['issues_by_location']['file.py:line']['consolidated_issues'][0]['metadata']",
                    'duplicate_instances': "data['security_summary']['issues_by_location']['file.py:line']['consolidated_issues'][0]['duplicate_count']"
                },
                'deduplication_notes': 'Identical issues within same location are consolidated with duplicate_count metadata',
                'migration_notes': 'Enhanced from v1.0 with sophisticated agent intelligence and intelligent deduplication - backward compatible'
            }
        }
        
        return yaml_structure
    
    def _consolidate_security_issues(self) -> Dict[str, Any]:
        """
        Consolidate security issues by location using OutputGenerator pattern.
        
        Groups multiple security issues at the same file:line location into
        consolidated entries to prevent duplicates and provide clean AI access.
        """
        try:
            # Get raw security issues from storage
            security_issues = self.storage.get_observations_by_type('security_issue', limit=1000)
            
            # Apply location-based consolidation (same logic as OutputGenerator)
            consolidated = self._apply_location_consolidation(security_issues, 'security')
            
            return consolidated
            
        except Exception as e:
            logger.warning(f"Failed to consolidate security issues: {e}")
            return {}
    
    def _consolidate_quality_issues(self) -> Dict[str, Any]:
        """
        Consolidate quality issues (TODOs, complexity) by location.
        """
        try:
            # Get TODOs and code entities for quality analysis
            todos = self.storage.get_observations_by_type('todo', limit=500)
            
            # Apply location-based consolidation
            consolidated = self._apply_location_consolidation(todos, 'quality')
            
            return consolidated
            
        except Exception as e:
            logger.warning(f"Failed to consolidate quality issues: {e}")
            return {}
    
    def _apply_location_consolidation(self, observations: List[Dict], issue_type: str) -> Dict[str, Any]:
        """
        Apply location-based consolidation following OutputGenerator._deduplicate_by_location pattern.
        
        Groups observations by file_path:line_number, consolidating multiple issues
        per location into structured entries for clean AI consumption.
        """
        location_map = {}
        
        for obs in observations:
            try:
                data = obs.get('data', {})
                if isinstance(data, str):
                    import json
                    data = json.loads(data)
                
                file_path = data.get('file_path', 'unknown')
                line_number = data.get('line_number', 0)
                location_key = f"{file_path}:{line_number}"
                
                if location_key not in location_map:
                    location_map[location_key] = {
                        'location': location_key,
                        'file_path': file_path,
                        'line_number': line_number,
                        'issue_count': 0,
                        'consolidated_issues': [],
                        'severity_distribution': defaultdict(int),
                        'primary_severity': 'unknown'
                    }
                
                # Extract issue details - Enhanced with sophisticated fields
                issue_data = {
                    # Core fields (preserved for compatibility)
                    'pattern_name': data.get('pattern_name', data.get('description', 'Unknown')),
                    'severity': data.get('severity', 'unknown'),
                    'description': data.get('description', ''),
                    'confidence': data.get('confidence', 0.0),
                    'issue_type': issue_type
                }
                
                # Extract sophisticated agent intelligence fields
                sophisticated_fields = self._extract_sophisticated_fields(data)
                issue_data.update(sophisticated_fields)
                
                location_entry = location_map[location_key]
                location_entry['consolidated_issues'].append(issue_data)
                location_entry['issue_count'] += 1
                location_entry['severity_distribution'][issue_data['severity']] += 1
                
                # Determine primary severity (highest severity becomes primary)
                severity_priority = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'unknown': 0}
                current_priority = severity_priority.get(location_entry['primary_severity'], 0)
                new_priority = severity_priority.get(issue_data['severity'], 0)
                
                if new_priority > current_priority:
                    location_entry['primary_severity'] = issue_data['severity']
                
            except Exception as e:
                logger.warning(f"Failed to process observation for consolidation: {e}")
                continue
        
        # Apply deduplication within each location
        for location_key, entry in location_map.items():
            entry['consolidated_issues'] = self._deduplicate_issues_within_location(entry['consolidated_issues'])
            entry['issue_count'] = len(entry['consolidated_issues'])
            
            # Recalculate severity distribution after deduplication
            entry['severity_distribution'] = defaultdict(int)
            for issue in entry['consolidated_issues']:
                entry['severity_distribution'][issue['severity']] += issue.get('duplicate_count', 1)
            
            # Convert defaultdict to regular dict for YAML serialization
            entry['severity_distribution'] = dict(entry['severity_distribution'])
        
        return location_map
    
    def _deduplicate_issues_within_location(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate identical issues within a single location.
        
        Groups issues by pattern_name + description, keeping one representative
        per group with enhanced metadata about duplicates.
        
        Args:
            issues: List of issue dictionaries from same file:line location
            
        Returns:
            Deduplicated list with duplicate_count metadata
        """
        if len(issues) <= 1:
            # No deduplication needed for single issues
            for issue in issues:
                issue['duplicate_count'] = 1
            return issues
        
        # Group issues by unique signature (pattern + description)
        signature_groups = {}
        
        for issue in issues:
            # Create unique signature for this issue type
            pattern_name = issue.get('pattern_name', 'Unknown')
            description = issue.get('description', '')
            severity = issue.get('severity', 'unknown')
            
            # Use pattern+description+severity as signature for exact matches
            signature = f"{pattern_name}::{description}::{severity}"
            
            if signature not in signature_groups:
                signature_groups[signature] = []
            signature_groups[signature].append(issue)
        
        # Create deduplicated list with enhanced metadata
        deduplicated = []
        
        for signature, group in signature_groups.items():
            if len(group) == 1:
                # Single instance - just add duplicate_count
                representative = group[0]
                representative['duplicate_count'] = 1
                deduplicated.append(representative)
            else:
                # Multiple instances - merge intelligence and add metadata
                representative = self._merge_duplicate_issues(group)
                deduplicated.append(representative)
        
        # Sort by severity priority then by duplicate count for consistent output
        severity_priority = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'unknown': 0}
        deduplicated.sort(
            key=lambda x: (
                -severity_priority.get(x.get('severity', 'unknown'), 0),  # Higher severity first
                -x.get('duplicate_count', 1),  # More duplicates first
                x.get('pattern_name', '')  # Alphabetical for consistency
            )
        )
        
        return deduplicated
    
    def _merge_duplicate_issues(self, duplicate_group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple identical issues into single representative with enhanced metadata.
        
        Preserves highest confidence scores and merges sophisticated fields.
        
        Args:
            duplicate_group: List of identical issue instances
            
        Returns:
            Single representative issue with duplicate metadata
        """
        if not duplicate_group:
            return {}
        
        # Use first issue as base (they should be identical)
        representative = duplicate_group[0].copy()
        representative['duplicate_count'] = len(duplicate_group)
        
        # Merge sophisticated fields from all instances
        all_ai_recommendations = []
        all_cwe_codes = set()
        all_owasp_refs = set()
        max_ml_confidence = 0.0
        max_confidence = 0.0
        merged_metadata = {}
        
        for issue in duplicate_group:
            # Collect AI recommendations
            ai_rec = issue.get('ai_recommendation', '').strip()
            if ai_rec and ai_rec not in all_ai_recommendations:
                all_ai_recommendations.append(ai_rec)
            
            # Collect security classifications
            cwe = issue.get('cwe', '').strip()
            if cwe:
                all_cwe_codes.add(cwe)
            
            owasp = issue.get('owasp', '').strip()
            if owasp:
                all_owasp_refs.add(owasp)
            
            # Find highest confidence scores
            ml_conf = float(issue.get('ml_confidence', 0.0))
            if ml_conf > max_ml_confidence:
                max_ml_confidence = ml_conf
            
            conf = float(issue.get('confidence', 0.0))
            if conf > max_confidence:
                max_confidence = conf
            
            # Merge metadata
            metadata = issue.get('metadata', {})
            if isinstance(metadata, dict):
                merged_metadata.update(metadata)
        
        # Update representative with merged intelligence
        if all_ai_recommendations:
            # Use the first unique recommendation, or merge if multiple unique ones
            representative['ai_recommendation'] = all_ai_recommendations[0]
            if len(all_ai_recommendations) > 1:
                representative['alternative_ai_recommendations'] = all_ai_recommendations[1:]
        
        if all_cwe_codes:
            representative['cwe'] = ', '.join(sorted(all_cwe_codes))
        
        if all_owasp_refs:
            representative['owasp'] = ', '.join(sorted(all_owasp_refs))
        
        # Use highest confidence scores
        representative['ml_confidence'] = max_ml_confidence
        representative['confidence'] = max_confidence
        
        # Update metadata with duplicate tracking
        if merged_metadata:
            representative['metadata'] = merged_metadata
        
        representative['metadata'] = representative.get('metadata', {})
        representative['metadata']['deduplication_applied'] = True
        representative['metadata']['original_instances'] = len(duplicate_group)
        
        return representative
    
    def _generate_structured_recommendations(
        self, 
        security: SecurityOverview, 
        quality: QualityOverview, 
        architecture: ArchitectureOverview
    ) -> List[Dict[str, Any]]:
        """
        Generate structured recommendations with priority, category, and effort estimates.
        """
        recommendations = []
        
        # Security recommendations
        if security.critical_count > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'security',
                'action': f'Address {security.critical_count} critical security issues immediately',
                'impact': 'high',
                'estimated_effort_hours': min(security.critical_count * 0.5, 8),  # Cap at 8 hours
                'urgency': 'immediate',
                'affected_files': security.files_with_issues
            })
        elif security.high_count > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'security',
                'action': f'Prioritize {security.high_count} high-severity security issues',
                'impact': 'medium',
                'estimated_effort_hours': min(security.high_count * 0.3, 6),
                'urgency': 'next_sprint',
                'affected_files': security.files_with_issues
            })
        
        # Quality recommendations  
        if quality.critical_todos > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'maintenance',
                'action': f'Fix {quality.critical_todos} critical TODOs',
                'impact': 'medium',
                'estimated_effort_hours': quality.critical_todos * 0.25,
                'urgency': 'this_week',
                'completion_benefit': 'Reduced technical debt'
            })
        
        # Complexity recommendations
        if quality.high_complexity_functions > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'quality',
                'action': f'Refactor {quality.high_complexity_functions} high-complexity functions',
                'impact': 'medium',
                'estimated_effort_hours': quality.high_complexity_functions * 0.5,
                'urgency': 'planned',
                'completion_benefit': 'Improved maintainability'
            })
        
        # Category-specific recommendations
        if security.top_categories:
            top_category, count = security.top_categories[0]
            if count > 5:  # Only if significant category
                recommendations.append({
                    'priority': 'medium',
                    'category': 'security_pattern',
                    'action': f'Focus on {top_category.lower()} pattern ({count} issues)',
                    'impact': 'medium',
                    'estimated_effort_hours': count * 0.2,
                    'urgency': 'planned',
                    'pattern_focus': top_category
                })
        
        # Default recommendation if none generated
        if not recommendations:
            recommendations.append({
                'priority': 'low',
                'category': 'maintenance',
                'action': 'Continue monitoring and maintain current quality standards',
                'impact': 'low',
                'estimated_effort_hours': 0.5,
                'urgency': 'ongoing',
                'completion_benefit': 'Sustained code quality'
            })
        
        # Sort by priority and limit to top 4
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return recommendations[:4]
    
    def _extract_sophisticated_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract sophisticated agent intelligence fields with graceful degradation.
        
        Handles AI recommendations, security classifications, ML confidence scores,
        and rich metadata while ensuring backward compatibility.
        
        Args:
            data: Raw observation data from storage
            
        Returns:
            Dictionary of sophisticated fields with safe defaults
        """
        sophisticated = {}
        
        # AI Recommendation - Critical field for actionable intelligence
        ai_rec = data.get('ai_recommendation', '')
        sophisticated['ai_recommendation'] = ai_rec if isinstance(ai_rec, str) else ''
        
        # Security Classifications - Professional analysis
        cwe = data.get('cwe', '')
        sophisticated['cwe'] = cwe if isinstance(cwe, str) else ''
        
        owasp = data.get('owasp', '')
        sophisticated['owasp'] = owasp if isinstance(owasp, str) else ''
        
        # Implementation Guidance
        fix_complexity = data.get('fix_complexity', 'unknown')
        sophisticated['fix_complexity'] = fix_complexity if isinstance(fix_complexity, str) else 'unknown'
        
        # Quality Metrics - Handle numeric conversion safely
        try:
            ml_conf = data.get('ml_confidence', 0.0)
            sophisticated['ml_confidence'] = float(ml_conf) if ml_conf is not None else 0.0
        except (ValueError, TypeError):
            sophisticated['ml_confidence'] = 0.0
        
        # Rich Context - Handle dict structure safely
        metadata = data.get('metadata', {})
        if isinstance(metadata, dict):
            sophisticated['metadata'] = metadata
        elif isinstance(metadata, str):
            # Handle case where metadata might be JSON string
            try:
                import json
                sophisticated['metadata'] = json.loads(metadata)
            except (json.JSONDecodeError, TypeError):
                sophisticated['metadata'] = {}
        else:
            sophisticated['metadata'] = {}
        
        return sophisticated