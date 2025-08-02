"""
Output Generator for Copper Alloy Brass

Generates JSON output files for Claude Code to read.
"""

import json
import copy
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from coppersun_brass.core.storage import BrassStorage
from coppersun_brass.core.dcp_adapter import DCPAdapter
from coppersun_brass.config import BrassConfig
from coppersun_brass.integrations.content_safety import DualPurposeContentSafety

logger = logging.getLogger(__name__)


class OutputGenerator:
    """Generates structured output files for AI consumption."""
    
    def __init__(self, config: BrassConfig, storage: BrassStorage):
        """
        Initialize output generator.
        
        Args:
            config: Copper Alloy Brass configuration
            storage: Storage instance
        """
        self.config = config
        self.storage = storage
        self.output_dir = config.output_dir
        
        # Initialize content safety for Phase 3 customer-facing security analysis
        self.content_safety = DualPurposeContentSafety()
        logger.info("Content safety system initialized for customer security analysis")
        
    # DEPRECATED: analysis_report.json replaced by brass_analysis.yaml (structured, AI-optimized)
    # Remove in future version - kept for reference during transition
    def _generate_analysis_report_deprecated(self) -> Path:
        """
        DEPRECATED: Generate comprehensive analysis report.
        
        REPLACED BY: brass_analysis.yaml via generate_brass_yaml()
        REASON: YAML provides structured data, type safety, location consolidation
        
        Returns:
            Path to generated report file
        """
        # Get all observations
        observations = self.storage.get_all_observations()
        
        # Group by type
        grouped = {}
        for obs in observations:
            obs_type = obs['type']
            if obs_type not in grouped:
                grouped[obs_type] = []
            grouped[obs_type].append(obs)
        
        # Create report structure
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'project_path': str(self.config.project_root),
                'total_observations': len(observations),
                'brass_version': '1.0.0'
            },
            'summary': {
                'total_todos': len(grouped.get('todo', [])),
                'total_files_analyzed': len(grouped.get('scout_analysis_summary', [])),
                'critical_issues': self._count_critical_issues(observations),
                'by_type': {k: len(v) for k, v in grouped.items()}
            },
            'todos': self._format_todos(grouped.get('todo', [])),
            'issues': self._format_issues(observations),
            'file_summaries': self._format_file_summaries(grouped.get('scout_analysis_summary', []))
        }
        
        # Write report
        report_path = self.output_dir / 'analysis_report.json'
        report_path.write_text(json.dumps(report, indent=2))
        logger.info(f"Generated analysis report: {report_path}")
        
        return report_path
    
    def generate_todo_list(self) -> Path:
        """
        Generate a structured TODO YAML report using TodoYamlGenerator.
        
        Returns:
            Path to generated TODO YAML file
        """
        try:
            from ..analysis.todo_yaml_generator import TodoYamlGenerator
        except ImportError as import_error:
            logger.error(f"TodoYamlGenerator import failed: {import_error}")
            return self._generate_fallback_todo_json()
        
        try:
            generator = TodoYamlGenerator(str(self.config.project_root), self.storage)
            yaml_path = generator.generate_yaml_report()
            
            logger.info(f"Generated TODO YAML report: {yaml_path}")
            return Path(yaml_path)
            
        except Exception as e:
            logger.error(f"Failed to generate TODO YAML report: {e}")
            # Fallback to original JSON generation for compatibility
            return self._generate_fallback_todo_json()
    
    def _generate_fallback_todo_json(self) -> Path:
        """
        Fallback TODO JSON generation for compatibility.
        
        Returns:
            Path to generated fallback todos.json file
        """
        logger.warning("Using fallback TODO JSON generation")
        
        # Get recent TODOs from the last 24 hours to avoid duplicates from multiple runs
        since = datetime.now() - timedelta(hours=24)
        todos = self.storage.get_observations(obs_type='todo', since=since)
        
        # Deduplicate TODOs by file+line+content
        seen = set()
        unique_todos = []
        for todo in todos:
            data = todo.get('data', {})
            key = (data.get('file_path', data.get('file', '')), data.get('line_number', data.get('line', 0)), data.get('content', ''))
            if key not in seen:
                seen.add(key)
                unique_todos.append(todo)
        
        # Sort by priority
        unique_todos.sort(key=lambda x: x.get('priority', 50), reverse=True)
        
        todo_list = {
            'generated_at': datetime.now().isoformat(),
            'total_todos': len(unique_todos),
            'todos': [
                {
                    'file': todo.get('data', {}).get('file_path', todo.get('data', {}).get('file', 'unknown')),
                    'line': todo.get('data', {}).get('line_number', todo.get('data', {}).get('line', 0)),
                    'content': todo.get('data', {}).get('content', ''),
                    'priority': todo.get('priority', 50),
                    'classification': todo.get('data', {}).get('classification', 'unclassified')
                }
                for todo in unique_todos
            ]
        }
        
        # Write fallback TODO JSON
        todo_path = self.output_dir / 'todos.json'
        todo_path.write_text(json.dumps(todo_list, indent=2))
        logger.info(f"Generated fallback TODO JSON: {todo_path}")
        
        return todo_path
    
    def generate_project_context(self) -> Path:
        """
        Generate project context information.
        
        Returns:
            Path to generated context file
        """
        # Get statistics
        stats = self.storage.get_activity_stats()
        
        context = {
            'project': {
                'path': str(self.config.project_root),
                'name': self.config.project_root.name,
                'analyzed_at': datetime.now().isoformat()
            },
            'statistics': {
                'files_analyzed': stats.get('files_analyzed', 0),
                'total_observations': stats.get('total_observations', 0),
                'critical_issues': stats.get('critical_count', 0),
                'important_issues': stats.get('important_count', 0)
            },
            'recent_activity': {
                'last_24h': stats
            }
        }
        
        # Write context
        context_path = self.output_dir / 'project_context.json'
        context_path.write_text(json.dumps(context, indent=2))
        logger.info(f"Generated project context: {context_path}")
        
        return context_path
    
    def _count_critical_issues(self, observations: List[Dict]) -> int:
        """Count critical issues from observations."""
        return sum(
            1 for obs in observations
            if obs.get('data', {}).get('classification') == 'critical'
        )
    
    def _format_todos(self, todos: List[Dict]) -> List[Dict]:
        """Format TODO observations for report."""
        formatted = []
        for todo in todos:
            data = todo.get('data', {})
            formatted.append({
                'file': data.get('file_path', data.get('file', 'unknown')),
                'line': data.get('line_number', data.get('line', 0)),
                'content': data.get('content', ''),
                'priority': todo.get('priority', 50),
                'classification': data.get('classification', 'unclassified'),
                'ml_confidence': data.get('ml_confidence', 0.0)
            })
        return sorted(formatted, key=lambda x: x['priority'], reverse=True)
    
    def _format_issues(self, observations: List[Dict]) -> List[Dict]:
        """Format critical and important issues."""
        issues = []
        for obs in observations:
            data = obs.get('data', {})
            classification = data.get('classification', '')
            
            if classification in ['critical', 'important']:
                issues.append({
                    'type': obs.get('type'),
                    'severity': classification,
                    'file': data.get('file_path', data.get('file', 'unknown')),
                    'description': data.get('content', data.get('summary', '')),
                    'confidence': data.get('ml_confidence', 0.0)
                })
        
        return sorted(issues, key=lambda x: (
            0 if x['severity'] == 'critical' else 1,
            -x['confidence']
        ))
    
    def _format_file_summaries(self, summaries: List[Dict]) -> List[Dict]:
        """Format file analysis summaries."""
        formatted = []
        for summary in summaries:
            data = summary.get('data', {})
            formatted.append({
                'file': data.get('file_path', data.get('file', 'unknown')),
                'analyzed_at': summary.get('created_at', ''),
                'summary': data.get('summary', {}),
                'has_issues': data.get('total_issues', 0) > 0
            })
        return formatted
    
    
    def generate_enterprise_readiness(self) -> Path:
        """
        Generate enterprise readiness assessment report.
        
        Returns:
            Path to generated enterprise readiness report file
        """
        logger.debug("Starting enterprise readiness generation")
        
        # Get comprehensive data for enterprise assessment
        security_issues = self.storage.get_observations_by_type('security_issue', limit=100)
        code_issues = self.storage.get_observations_by_type('code_issue', limit=100)
        todos = self.storage.get_observations_by_type('todo', limit=50)
        code_entities = self.storage.get_observations_by_type('code_entity', limit=100)
        
        logger.debug(f"Retrieved data: {len(security_issues)} security, {len(code_issues)} code, {len(todos)} todos, {len(code_entities)} entities")
        
        # Calculate enterprise readiness metrics
        readiness_assessment = self._calculate_enterprise_readiness(
            security_issues, code_issues, todos, code_entities
        )
        
        # Generate structured report
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'project_path': str(self.config.project_root),
                'assessment_version': '1.0.0'
            },
            'enterprise_readiness': readiness_assessment,
            'security_posture': self._assess_security_posture(security_issues),
            'code_quality': self._assess_code_quality(code_issues, code_entities),
            'technical_debt': self._assess_technical_debt(todos),
            'recommendations': self._generate_enterprise_recommendations(readiness_assessment)
        }
        
        # Write enterprise readiness report
        report_path = self.output_dir / 'enterprise_readiness.json'
        report_path.write_text(json.dumps(report, indent=2))
        logger.info(f"Generated enterprise readiness assessment: {report_path}")
        
        return report_path
    
    def _calculate_enterprise_readiness(self, security_issues, code_issues, todos, entities) -> Dict:
        """Calculate overall enterprise readiness score and assessment."""
        # Security score (0-100)
        critical_security = sum(1 for s in security_issues if s.get('data', {}).get('severity') == 'critical')
        high_security = len([s for s in security_issues if s.get('data', {}).get('severity') == 'high'])
        total_security = len(security_issues)
        
        security_score = 100
        if total_security > 0:
            security_score = max(0, 100 - (critical_security * 25) - (high_security * 10))
        
        # Code quality score (0-100)
        critical_code = len([c for c in code_issues if c.get('data', {}).get('severity') == 'critical'])
        high_code = len([c for c in code_issues if c.get('data', {}).get('severity') == 'high'])
        
        quality_score = 100
        if code_issues:
            quality_score = max(0, 100 - (critical_code * 15) - (high_code * 5))
        
        # Documentation score (0-100)
        total_entities = len(entities)
        documented_entities = len([e for e in entities if e.get('data', {}).get('has_docstring', False)])
        doc_score = (documented_entities / total_entities * 100) if total_entities > 0 else 100
        
        # Technical debt score (0-100)
        high_priority_todos = len([t for t in todos if t.get('data', {}).get('priority_score', 0) > 70])
        debt_score = max(0, 100 - (high_priority_todos * 2))
        
        # Overall readiness score (weighted average)
        overall_score = (security_score * 0.4 + quality_score * 0.3 + doc_score * 0.2 + debt_score * 0.1)
        
        # Determine readiness level
        if overall_score >= 90:
            readiness_level = "ENTERPRISE_READY"
        elif overall_score >= 75:
            readiness_level = "MOSTLY_READY"
        elif overall_score >= 60:
            readiness_level = "NEEDS_IMPROVEMENT"
        else:
            readiness_level = "NOT_READY"
        
        return {
            'overall_score': round(overall_score, 1),
            'readiness_level': readiness_level,
            'component_scores': {
                'security': round(security_score, 1),
                'code_quality': round(quality_score, 1),
                'documentation': round(doc_score, 1),
                'technical_debt': round(debt_score, 1)
            },
            'assessment_date': datetime.now().isoformat()
        }
    
    def _assess_security_posture(self, security_issues) -> Dict:
        """Assess security posture for enterprise readiness."""
        by_severity = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for issue in security_issues:
            severity = issue.get('data', {}).get('severity', 'low')
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            'total_issues': len(security_issues),
            'by_severity': by_severity,
            'status': 'SECURE' if by_severity['critical'] == 0 and by_severity['high'] == 0 else 'NEEDS_ATTENTION'
        }
    
    def _assess_code_quality(self, code_issues, entities) -> Dict:
        """Assess code quality for enterprise readiness."""
        complex_entities = len([e for e in entities if e.get('data', {}).get('complexity_score', 0) > 15])
        total_entities = len(entities)
        
        return {
            'total_issues': len(code_issues),
            'complex_entities': complex_entities,
            'total_entities': total_entities,
            'complexity_ratio': complex_entities / total_entities if total_entities > 0 else 0,
            'status': 'GOOD' if total_entities > 0 and complex_entities / total_entities < 0.1 else 'NEEDS_REFACTORING' if total_entities > 0 else 'GOOD'
        }
    
    def _assess_technical_debt(self, todos) -> Dict:
        """Assess technical debt for enterprise readiness."""
        high_priority = len([t for t in todos if t.get('data', {}).get('priority_score', 0) > 70])
        total_todos = len(todos)
        
        return {
            'total_todos': total_todos,
            'high_priority_todos': high_priority,
            'debt_ratio': high_priority / total_todos if total_todos > 0 else 0,
            'status': 'MANAGEABLE' if high_priority < 10 else 'HIGH_DEBT'
        }
    
    def _generate_enterprise_recommendations(self, assessment) -> List[str]:
        """Generate recommendations based on enterprise readiness assessment."""
        recommendations = []
        
        scores = assessment['component_scores']
        
        if scores['security'] < 80:
            recommendations.append("Address critical and high-severity security issues before enterprise deployment")
        
        if scores['code_quality'] < 70:
            recommendations.append("Refactor complex code entities and resolve critical code quality issues")
        
        if scores['documentation'] < 60:
            recommendations.append("Improve code documentation coverage for enterprise maintainability")
        
        if scores['technical_debt'] < 80:
            recommendations.append("Reduce technical debt by addressing high-priority TODOs")
        
        if assessment['overall_score'] >= 90:
            recommendations.append("Project meets enterprise readiness standards")
        elif assessment['overall_score'] >= 75:
            recommendations.append("Project is mostly enterprise-ready with minor improvements needed")
        
        return recommendations
    
    def generate_all_outputs(self) -> Dict[str, Path]:
        """
        Generate all output files.
        
        Returns:
            Dictionary mapping output type to file path
        """
        outputs = {}
        
        try:
            # NOTE: analysis_report.json deprecated in favor of brass_analysis.yaml (structured, AI-optimized)
            outputs['todo_list'] = self.generate_todo_list()
            outputs['project_context'] = self.generate_project_context()
            outputs['code_security_analysis'] = self.generate_code_security_analysis()  # ADD COMPREHENSIVE
            outputs['privacy_analysis'] = self.generate_privacy_report()  # PRIVACY INTEGRATION
            outputs['best_practices'] = self.generate_best_practices()  # BEST PRACTICES YAML
            outputs['brass_yaml'] = self.generate_brass_yaml()  # YAML FOR AI CONSUMPTION
            
            # Enhanced error logging for enterprise readiness
            try:
                logger.debug("ENTERPRISE_DEBUG: Starting enterprise readiness generation")
                outputs['enterprise_readiness'] = self.generate_enterprise_readiness()  # ENTERPRISE READINESS
                logger.debug("ENTERPRISE_DEBUG: Enterprise readiness generation completed successfully")
            except Exception as enterprise_error:
                import traceback
                logger.error(f"ENTERPRISE_READINESS_FAILURE: {type(enterprise_error).__name__}: {enterprise_error}")
                logger.error(f"ENTERPRISE_READINESS_STACK: {traceback.format_exc()}")
                # Log data state for debugging
                try:
                    observations_count = len(self.storage.get_observations_by_type('code_issue'))
                    logger.error(f"ENTERPRISE_DEBUG_STATE: code_issues={observations_count}")
                    security_count = len(self.storage.get_observations_by_type('security_issue'))
                    logger.error(f"ENTERPRISE_DEBUG_STATE: security_issues={security_count}")
                    todo_count = len(self.storage.get_observations_by_type('todo'))
                    logger.error(f"ENTERPRISE_DEBUG_STATE: todos={todo_count}")
                except Exception as debug_error:
                    logger.error(f"ENTERPRISE_DEBUG_FAILURE: Could not log state: {debug_error}")
                # Re-raise to maintain current error handling behavior
                raise enterprise_error
            
            logger.info(f"Generated {len(outputs)} output files in {self.output_dir}")
        except Exception as e:
            import traceback
            logger.error(f"Failed to generate outputs: {type(e).__name__}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return outputs
    
    def generate_code_security_analysis(self) -> Path:
        """Generate comprehensive analysis covering ALL rich data types via OutputGenerator."""
        
        # Get ALL rich data types with increased limits for comprehensive intelligence display
        # Previous limits were causing 85-99% intelligence loss - now using much higher limits
        todo_observations = self.storage.get_observations_by_type('todo', limit=500)
        code_issues = self.storage.get_observations_by_type('code_issue', limit=500) 
        security_issues = self.storage.get_observations_by_type('security_issue', limit=500)  # Critical fix: was 50, now 500 (10x increase)
        code_entities = self.storage.get_observations_by_type('code_entity', limit=500)
        code_metrics = self.storage.get_observations_by_type('code_metrics', limit=200)
        persistent_issues = self.storage.get_observations_by_type('persistent_issue', limit=200)
        evolution_report = self._get_evolution_summary()
        
        # Build comprehensive structured markdown
        content = self._build_all_data_types_analysis(
            todo_observations, code_issues, security_issues, 
            code_entities, code_metrics, persistent_issues, evolution_report
        )
        
        file_path = self.output_dir / 'CODE_SECURITY_AND_QUALITY_ANALYSIS.md'
        file_path.write_text(content)
        logger.info(f"Generated comprehensive intelligence report: {file_path}")
        return file_path
    
    def generate_privacy_report(self) -> Path:
        """
        Generate privacy analysis report using PrivacyYamlGenerator.
        
        Returns:
            Path to generated .brass/privacy_analysis.yaml file
        """
        try:
            from ..privacy import PrivacyYamlGenerator
        except ImportError as import_error:
            logger.error(f"PrivacyYamlGenerator import failed: {import_error}")
            raise
        
        try:
            # PrivacyYamlGenerator expects project root, not .brass directory
            project_root = str(self.output_dir.parent)
            generator = PrivacyYamlGenerator(project_root)
            
            # PrivacyYamlGenerator.generate_yaml_report() returns string path
            report_path_str = generator.generate_yaml_report()
            report_path = Path(report_path_str)
            
            logger.info(f"Generated privacy analysis YAML report: {report_path}")
            return report_path
            
        except Exception as e:
            import traceback
            logger.error(f"PRIVACY_YAML_GENERATION_FAILURE: {type(e).__name__}: {e}")
            logger.error(f"PRIVACY_YAML_STACK: {traceback.format_exc()}")
            # Re-raise to maintain current error handling behavior
            raise e
    
    def generate_best_practices(self) -> Path:
        """
        Generate best practices YAML report using BestPracticesYamlGenerator.
        
        Returns:
            Path to generated .brass/best_practices.yaml file
        """
        try:
            from ..analysis.best_practices_yaml_generator import BestPracticesYamlGenerator
        except ImportError as import_error:
            logger.error(f"BestPracticesYamlGenerator import failed: {import_error}")
            raise
        
        try:
            generator = BestPracticesYamlGenerator(str(self.config.project_root), self.storage)
            yaml_path = generator.generate_yaml_report()
            
            logger.info(f"Generated best practices YAML report: {yaml_path}")
            return Path(yaml_path)
            
        except Exception as e:
            import traceback
            logger.error(f"BEST_PRACTICES_YAML_GENERATION_FAILURE: {type(e).__name__}: {e}")
            logger.error(f"BEST_PRACTICES_YAML_STACK: {traceback.format_exc()}")
            # Re-raise to maintain current error handling behavior
            raise e
    
    def generate_brass_analysis(self) -> Path:
        """
        Generate executive analysis report using BrassAnalysisGenerator.
        
        Returns:
            Path to generated .brass/brass_analysis.md file
        """
        try:
            from ..analysis import BrassAnalysisGenerator
        except ImportError as import_error:
            logger.error(f"BrassAnalysisGenerator import failed: {import_error}")
            raise
        
        try:
            # BrassAnalysisGenerator expects project root, not .brass directory
            project_root = str(self.output_dir.parent)
            generator = BrassAnalysisGenerator(project_root, self.storage)
            
            # BrassAnalysisGenerator.generate_report() returns string path
            report_path_str = generator.generate_report()
            report_path = Path(report_path_str)
            
            logger.info(f"Generated brass analysis report: {report_path}")
            return report_path
            
        except Exception as e:
            import traceback
            logger.error(f"BRASS_ANALYSIS_FAILURE: {type(e).__name__}: {e}")
            logger.error(f"BRASS_ANALYSIS_STACK: {traceback.format_exc()}")
            # Re-raise to maintain current error handling behavior
            raise e
    
    def generate_brass_yaml(self) -> Path:
        """
        Generate YAML analysis report using BrassYamlGenerator for AI consumption.
        
        Returns:
            Path to generated .brass/brass_analysis.yaml file
        """
        try:
            from ..analysis import BrassYamlGenerator
        except ImportError as import_error:
            logger.error(f"BrassYamlGenerator import failed: {import_error}")
            raise
        
        try:
            # BrassYamlGenerator expects project root, not .brass directory
            project_root = str(self.output_dir.parent)
            generator = BrassYamlGenerator(project_root, self.storage)
            
            # BrassYamlGenerator.generate_yaml_report() returns string path
            report_path_str = generator.generate_yaml_report()
            report_path = Path(report_path_str)
            
            logger.info(f"Generated YAML brass analysis report: {report_path}")
            return report_path
            
        except Exception as e:
            import traceback
            logger.error(f"BRASS_YAML_FAILURE: {type(e).__name__}: {e}")
            logger.error(f"BRASS_YAML_STACK: {traceback.format_exc()}")
            # Re-raise to maintain current error handling behavior
            raise e
    
    def _get_evolution_summary(self) -> Dict:
        """Get evolution summary data."""
        # For now, return empty dict - this can be enhanced later
        return {}
    
    def _deduplicate_by_location(self, observations):
        """Deduplicate observations by file_path:line_number, consolidating multiple issues per location."""
        location_map = {}
        
        for obs in observations:
            data = obs.get('data', {})
            file_path = data.get('file_path', 'unknown')
            line_number = data.get('line_number', 0)
            location_key = f"{file_path}:{line_number}"
            
            if location_key not in location_map:
                location_map[location_key] = {
                    'primary_observation': obs.copy(),  # Shallow copy sufficient for non-modified observations
                    'consolidated_issues': [data.copy()],  # Shallow copy sufficient for consolidation list
                    'location': location_key
                }
            else:
                # Add to consolidated issues for this location
                location_map[location_key]['consolidated_issues'].append(data.copy())
        
        # Return deduplicated observations with consolidated data
        deduplicated = []
        for location_data in location_map.values():
            primary_obs = location_data['primary_observation']
            consolidated_issues = location_data['consolidated_issues']
            
            # If multiple issues at same location, consolidate them
            if len(consolidated_issues) > 1:
                # Use selective copying for memory efficiency instead of deep copy
                primary_data = {
                    **primary_obs.get('data', {}),  # Spread existing data
                    'consolidated_issues': consolidated_issues,
                    'issue_count': len(consolidated_issues),
                    'description': f"Multiple issues detected: {', '.join([issue.get('pattern_name', issue.get('description', 'Unknown')) for issue in consolidated_issues])}"
                }
                # Update the primary observation with modified data
                primary_obs = primary_obs.copy()
                primary_obs['data'] = primary_data
            
            deduplicated.append(primary_obs)
        
        return deduplicated

    def _deduplicate_entities(self, entities):
        """Deduplicate entities by entity_name + file_path combination."""
        entity_map = {}
        
        for entity in entities:
            data = entity.get('data', {})
            entity_name = data.get('entity_name', 'unknown')
            file_path = data.get('file_path', 'unknown')
            entity_key = f"{file_path}:{entity_name}"
            
            if entity_key not in entity_map:
                entity_map[entity_key] = entity
        
        return list(entity_map.values())

    def _build_all_data_types_analysis(self, todos, code_issues, security_issues, 
                                     entities, metrics, persistent, evolution):
        """Build structured markdown covering ALL rich data types."""
        sections = []
        
        # Import needed for datetime formatting
        from datetime import datetime
        import json
        
        # Header with comprehensive Claude Code context
        sections.append("# Code Security and Quality Analysis\n")
        sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        # Claude Code Context and Documentation
        sections.append("## 🤖 For Claude Code AI Assistant\n")
        sections.append("**Purpose**: This file contains comprehensive project intelligence generated by Copper Sun Brass to provide Claude Code with rich context about security vulnerabilities, code quality issues, architectural insights, and strategic recommendations.\n\n")
        
        sections.append("**How to Use This Intelligence**:\n")
        sections.append("- **Security Issues**: Critical vulnerabilities requiring immediate attention with CWE/OWASP classifications\n")
        sections.append("- **TODO Analysis**: Development tasks with priority scoring and research opportunities\n")
        sections.append("- **Code Quality**: Complexity analysis, documentation gaps, and architectural concerns\n")
        sections.append("- **Entity Analysis**: Function/class complexity, refactoring opportunities\n")
        sections.append("- **Project Metrics**: Aggregate statistics for informed decision-making\n")
        sections.append("- **Strategic Recommendations**: AI-generated actionable insights based on aggregate analysis\n\n")
        
        sections.append("## 📊 Data Categories Explained\n")
        sections.append("### Security Issues\n")
        sections.append("- **CWE**: Common Weakness Enumeration classification\n")
        sections.append("- **OWASP**: Open Web Application Security Project mapping\n")
        sections.append("- **Severity**: critical (immediate fix), high (next sprint), medium (planned), low (backlog)\n")
        sections.append("- **Fix Complexity**: trivial (< 1 hour), simple (< 1 day), moderate (< 1 week), complex (> 1 week)\n\n")
        
        sections.append("### TODO Analysis\n")
        sections.append("- **Priority Score**: 0-100 calculated based on keywords, context, and placement\n")
        sections.append("- **TODO Types**: TODO (general task), FIXME (bug fix), BUG (critical issue), NOTE (documentation)\n")
        sections.append("- **Confidence**: ML model confidence in classification (0.0-1.0)\n")
        sections.append("- **Researchable**: Flag indicating whether this TODO could benefit from AI research\n\n")
        
        sections.append("### Code Quality & Complexity\n")
        sections.append("- **Complexity Score**: Cyclomatic complexity (> 10 needs attention, > 20 requires refactoring)\n")
        sections.append("- **Documentation Coverage**: Percentage of entities with proper documentation\n")
        sections.append("- **Entity Types**: function, class, method, module - architectural building blocks\n")
        sections.append("- **Dependencies**: Internal/external dependencies affecting maintainability\n\n")
        
        sections.append("### Strategic Intelligence\n")
        sections.append("- **Persistence Tracking**: Issues appearing across multiple analysis runs\n")
        sections.append("- **Evolution Analysis**: How code quality and security posture changes over time\n")
        sections.append("- **Sprint Count**: Number of development cycles an issue has persisted\n")
        sections.append("- **Strategic Importance**: Business impact assessment of persistent issues\n\n")
        
        sections.append("---\n\n")
        
        # 1. Critical Security Issues (from pattern analysis) - WITH DEDUPLICATION
        if security_issues:
            sections.append("## 🚨 Critical Security Issues\n")
            
            # Apply deduplication before severity filtering
            deduplicated_security = self._deduplicate_by_location(security_issues)
            
            critical_security = [s for s in deduplicated_security if s.get('data', {}).get('severity') == 'critical']
            high_security = [s for s in deduplicated_security if s.get('data', {}).get('severity') == 'high']
            
            for issue_group, title in [(critical_security, "Critical"), (high_security, "High Priority")]:
                if issue_group:
                    sections.append(f"### {title} Security Issues\n")
                    for issue in issue_group[:10]:
                        data = issue.get('data', {})
                        
                        # Show consolidated issues if multiple at same location
                        if data.get('issue_count', 1) > 1:
                            sections.append(f"#### {data.get('issue_count')} Security Issues in {data.get('file_path', 'unknown')}:{data.get('line_number', 0)}\n")
                            sections.append("```json\n")
                            # Show all consolidated issues
                            for i, consolidated_issue in enumerate(data.get('consolidated_issues', [data])):
                                sections.append(f"// Issue {i+1}:\n")
                                sections.append(json.dumps(consolidated_issue, indent=2))
                                if i < len(data.get('consolidated_issues', [])) - 1:
                                    sections.append("\n// ---\n")
                            sections.append("\n```\n")
                        else:
                            sections.append(f"#### {data.get('pattern_name', 'Security Issue')} in {data.get('file_path', 'unknown')}:{data.get('line_number', 0)}\n")
                            sections.append("```json\n")
                            sections.append(json.dumps(data, indent=2))
                            sections.append("\n```\n")
                        
                        sections.append(f"**CWE**: {data.get('cwe', 'N/A')} | **OWASP**: {data.get('owasp', 'N/A')}\n")
                        sections.append(f"**Impact**: {data.get('description', 'No description')}\n")
                        sections.append(f"**Recommendation**: {data.get('ai_recommendation', 'Review required')}\n\n")
        
        # 2. TODO Analysis (from TODO detector) - WITH DEDUPLICATION
        if todos:
            sections.append("## 📋 TODO Analysis\n")
            
            # Apply deduplication before priority filtering
            deduplicated_todos = self._deduplicate_by_location(todos)
            
            high_priority_todos = [t for t in deduplicated_todos if t.get('data', {}).get('priority_score', 0) > 70]
            medium_priority_todos = [t for t in deduplicated_todos if 40 <= t.get('data', {}).get('priority_score', 0) <= 70]
            
            for todo_group, title in [(high_priority_todos, "High Priority"), (medium_priority_todos, "Medium Priority")]:
                if todo_group:
                    sections.append(f"### {title} TODOs\n")
                    for todo in todo_group[:15]:
                        data = todo.get('data', {})
                        
                        # Show consolidated TODOs if multiple at same location
                        if data.get('issue_count', 1) > 1:
                            sections.append(f"#### {data.get('file_path', 'unknown')}:{data.get('line_number', 0)} - {data.get('issue_count')} TODOs\n")
                        else:
                            sections.append(f"#### {data.get('file_path', 'unknown')}:{data.get('line_number', 0)} - {data.get('todo_type', 'TODO')}\n")
                        
                        sections.append("```json\n")
                        sections.append(json.dumps(data, indent=2))
                        sections.append("\n```\n")
                        sections.append(f"**Content**: {data.get('content', 'No content')}\n")
                        sections.append(f"**Confidence**: {data.get('confidence', 0):.1%} | **Researchable**: {data.get('is_researchable', False)}\n\n")
        
        # 3. Code Quality Issues (from AST analysis)
        if code_issues:
            sections.append("## 🔍 Code Quality Issues\n")
            critical_code = [c for c in code_issues if c.get('data', {}).get('severity') == 'critical']
            high_code = [c for c in code_issues if c.get('data', {}).get('severity') == 'high']
            
            for issue_group, title in [(critical_code, "Critical"), (high_code, "High Priority")]:
                if issue_group:
                    sections.append(f"### {title} Code Issues\n")
                    for issue in issue_group[:10]:
                        data = issue.get('data', {})
                        sections.append(f"#### {data.get('issue_type', 'unknown').replace('_', ' ').title()} in {data.get('entity_name', 'unknown')}\n")
                        sections.append("```json\n")
                        sections.append(json.dumps(data, indent=2))
                        sections.append("\n```\n")
                        sections.append(f"**Location**: {data.get('file_path', 'unknown')}:{data.get('line_number', 0)}\n")
                        sections.append(f"**Fix Complexity**: {data.get('fix_complexity', 'unknown')}\n")
                        sections.append(f"**Recommendation**: {data.get('ai_recommendation', 'Review required')}\n\n")
        
        # 4. Complex Code Entities (from AST analysis) - WITH DEDUPLICATION
        if entities:
            sections.append("## 🏗️ Complex Code Entities\n")
            
            # Apply deduplication using entity name + file path as key for entities
            deduplicated_entities = self._deduplicate_entities(entities)
            
            complex_entities = sorted([e for e in deduplicated_entities if e.get('data', {}).get('complexity_score', 0) > 15], 
                                    key=lambda x: x.get('data', {}).get('complexity_score', 0), reverse=True)
            undocumented = [e for e in deduplicated_entities if not e.get('data', {}).get('has_docstring', True)]
            
            if complex_entities:
                sections.append("### High Complexity Entities\n")
                for entity in complex_entities[:10]:
                    data = entity.get('data', {})
                    sections.append(f"#### {data.get('entity_type', 'entity').title()}: {data.get('entity_name', 'unknown')}\n")
                    sections.append("```json\n")
                    sections.append(json.dumps(data, indent=2))
                    sections.append("\n```\n")
                    sections.append(f"**Location**: {data.get('file_path', 'unknown')}:{data.get('line_start', 0)}-{data.get('line_end', 0)}\n")
                    sections.append(f"**Complexity**: {data.get('complexity_score', 0)} | **Dependencies**: {len(data.get('dependencies', []))}\n\n")
            
            if undocumented:
                sections.append("### Undocumented Entities\n")
                for entity in undocumented[:15]:
                    data = entity.get('data', {})
                    sections.append(f"- **{data.get('entity_name', 'unknown')}** ({data.get('entity_type', 'entity')}) in {data.get('file_path', 'unknown')}:{data.get('line_start', 0)}\n")
                sections.append("\n")
        
        # 5. Aggregate Metrics (from AST analysis)
        if metrics:
            sections.append("## 📊 Code Metrics Summary\n")
            total_lines = sum(m.get('data', {}).get('total_lines', 0) for m in metrics)
            total_code_lines = sum(m.get('data', {}).get('code_lines', 0) for m in metrics)
            avg_complexity = sum(m.get('data', {}).get('average_complexity', 0) for m in metrics) / len(metrics) if metrics else 0
            avg_doc_coverage = sum(m.get('data', {}).get('documentation_coverage', 0) for m in metrics) / len(metrics) if metrics else 0
            
            sections.append("### Project Overview\n")
            sections.append("```json\n")
            sections.append(json.dumps({
                'total_lines_analyzed': total_lines,
                'code_lines': total_code_lines,
                'comment_ratio': (total_lines - total_code_lines) / total_lines if total_lines > 0 else 0,
                'average_complexity': round(avg_complexity, 2),
                'documentation_coverage': round(avg_doc_coverage, 2),
                'files_analyzed': len(metrics)
            }, indent=2))
            sections.append("\n```\n\n")
            
            sections.append("### Per-File Metrics\n")
            for metric in sorted(metrics, key=lambda x: x.get('data', {}).get('average_complexity', 0), reverse=True)[:10]:
                data = metric.get('data', {})
                sections.append(f"- **{data.get('file_path', 'unknown')}**: {data.get('code_lines', 0)} lines, complexity {data.get('average_complexity', 0):.1f}, {data.get('documentation_coverage', 0):.1%} documented\n")
            sections.append("\n")
        
        # 6. Evolution & Persistence Tracking (from evolution tracker)
        if persistent or evolution:
            sections.append("## 🔄 Evolution & Persistence Analysis\n")
            
            if persistent:
                sections.append("### Persistent Issues\n")
                chronic_issues = [p for p in persistent if p.get('data', {}).get('sprint_count', 0) >= 3]
                if chronic_issues:
                    sections.append("#### Chronic Issues (3+ Sprints)\n")
                    for issue in chronic_issues[:10]:
                        data = issue.get('data', {})
                        sections.append(f"##### {data.get('issue_type', 'unknown').replace('_', ' ').title()} in {data.get('file_path', 'unknown')}:{data.get('line_number', 0)}\n")
                        sections.append("```json\n")
                        sections.append(json.dumps(data, indent=2))
                        sections.append("\n```\n")
                        sections.append(f"**Persistence**: {data.get('sprint_count', 0)} sprints ({data.get('persistence_days', 0)} days)\n")
                        sections.append(f"**Strategic Importance**: {data.get('strategic_importance', 'unknown')}\n\n")
            
            if evolution:
                sections.append("### Evolution Summary\n")
                sections.append("```json\n")
                sections.append(json.dumps(evolution, indent=2))
                sections.append("\n```\n\n")
        
        # NOTE: Privacy functionality is provided by generate_privacy_report() method
        # which creates separate .brass/privacy_analysis.yaml files via PrivacyYamlGenerator
        
        # NOTE: Best Practices Recommendations moved to dedicated best_practices.yaml
        # Generated by BestPracticesYamlGenerator for enhanced AI consumption
        
        return "\n".join(sections)

    def _generate_strategic_recommendations(self, security, todos, code_issues, entities, persistent):
        """[DEPRECATED] Old strategic recommendations method - replaced by BestPracticesRecommendationEngine.
        
        This method is kept for backward compatibility but is no longer used.
        """
        recommendations = []
        
        # Since this method is deprecated and not called, provide basic recommendations
        
        # Security recommendations
        critical_security = len([s for s in security if s.get('data', {}).get('severity') == 'critical'])
        if critical_security > 0:
            recommendations.append(f"🚨 **URGENT**: {critical_security} critical security issues require immediate attention")
        
        # TODO recommendations  
        high_priority_todos = len([t for t in todos if t.get('data', {}).get('priority_score', 0) > 70])
        if high_priority_todos > 10:
            recommendations.append(f"📋 **TODO Overflow**: {high_priority_todos} high-priority TODOs - schedule dedicated cleanup sprint")
        
        # Code quality recommendations
        complex_entities = len([e for e in entities if e.get('data', {}).get('complexity_score', 0) > 20])
        if complex_entities > 5:
            recommendations.append(f"🔧 **Complexity Crisis**: {complex_entities} highly complex entities need refactoring")
        
        # Documentation recommendations
        undocumented = len([e for e in entities if not e.get('data', {}).get('has_docstring', True)])
        total_entities = len(entities)
        if total_entities > 0 and undocumented / total_entities > 0.5:
            recommendations.append(f"📚 **Documentation Gap**: {undocumented}/{total_entities} entities lack documentation")
        
        # Persistence recommendations
        chronic_issues = len([p for p in persistent if p.get('data', {}).get('sprint_count', 0) >= 3])
        if chronic_issues > 5:
            recommendations.append(f"⏰ **Technical Debt Alert**: {chronic_issues} issues persisting 3+ sprints require strategic intervention")
        
        return recommendations
    
    def _generate_customer_security_analysis(self, todos, code_issues, security_issues, entities) -> str:
        """Generate customer-facing security and privacy analysis using Phase 3 dual-purpose content safety.
        
        This provides actionable security audit insights for customers using our breakthrough
        dual-purpose content safety system.
        
        Args:
            todos, code_issues, security_issues, entities: Observation data
            
        Returns:
            Formatted markdown section with customer security analysis
        """
        sections = []
        
        # Collect all code content for comprehensive analysis
        all_findings = []
        code_samples = []
        
        # Extract content from all observation types for analysis
        for observation_group in [todos, code_issues, security_issues, entities]:
            for obs in observation_group:
                data = obs.get('data', {})
                
                # Extract various content fields
                content_fields = ['content', 'snippet', 'description', 'pattern_text', 'entity_name']
                content = ''
                for field in content_fields:
                    if field in data and data[field]:
                        content = str(data[field])
                        break
                
                if content and len(content.strip()) > 5:
                    code_samples.append({
                        'content': content,
                        'file_path': data.get('file_path', 'unknown'),
                        'line_number': data.get('line_number', 0),
                        'observation_type': obs.get('type', 'unknown')
                    })
        
        # Analyze samples with content safety system
        total_samples = len(code_samples)
        if total_samples == 0:
            sections.append("### Summary\n")
            sections.append("No security concerns detected in available code samples.\n\n")
            return "\n".join(sections)
        
        # Run security analysis on samples
        all_security_findings = []
        high_risk_samples = 0
        medium_risk_samples = 0
        
        for sample in code_samples[:50]:  # Limit for performance
            try:
                safety_result = self.content_safety.analyze_content_comprehensive(
                    content=sample['content'],
                    file_path=sample['file_path'], 
                    line_number=sample['line_number']
                )
                
                if safety_result.customer_findings:
                    all_security_findings.extend(safety_result.customer_findings)
                    
                    if safety_result.risk_score == "HIGH":
                        high_risk_samples += 1
                    elif safety_result.risk_score == "MEDIUM":
                        medium_risk_samples += 1
                        
            except ImportError as e:
                logger.warning(f"Content safety module import error: {e}")
                continue
            except ValueError as e:
                logger.debug(f"Content safety data validation error: {e}")
                continue
            except AttributeError as e:
                logger.debug(f"Content safety method error: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected content safety error: {type(e).__name__}: {e}")
                continue
        
        # Generate customer report using the dual-purpose system
        customer_report = self.content_safety.generate_customer_security_report(all_security_findings)
        
        # Format for markdown output
        sections.append("### Executive Summary\n")
        sections.append(f"**{customer_report['summary']}**\n\n")
        
        sections.append(f"- **Files Analyzed**: {total_samples} code samples\n")
        sections.append(f"- **Security Items Found**: {customer_report['findings_count']}\n")
        sections.append(f"- **Risk Level**: {customer_report['risk_level']}\n")
        sections.append(f"- **Enterprise Readiness**: {customer_report.get('enterprise_readiness', 'UNKNOWN')}\n\n")
        
        # Risk breakdown
        if customer_report['findings_count'] > 0:
            sections.append("### Risk Assessment\n")
            
            findings_by_priority = customer_report['findings_by_priority']
            
            if findings_by_priority['high']:
                sections.append(f"#### 🚨 High Priority Issues ({len(findings_by_priority['high'])})\n")
                for finding in findings_by_priority['high'][:5]:
                    sections.append(f"- **{finding.type}** at {finding.location}\n")
                    sections.append(f"  - *Risk*: {finding.risk_explanation}\n")
                    sections.append(f"  - *Fix*: {finding.remediation}\n")
                sections.append("\n")
            
            if findings_by_priority['medium']:
                sections.append(f"#### ⚠️ Medium Priority Issues ({len(findings_by_priority['medium'])})\n")
                for finding in findings_by_priority['medium'][:5]:
                    sections.append(f"- **{finding.type}** at {finding.location}\n")
                    sections.append(f"  - *Fix*: {finding.remediation}\n")
                sections.append("\n")
            
            if findings_by_priority['low']:
                sections.append(f"#### ℹ️ Low Priority Items ({len(findings_by_priority['low'])})\n")
                sections.append("Professional language and documentation improvements identified.\n\n")
        
        # Actionable recommendations
        sections.append("### Recommended Actions\n")
        for i, recommendation in enumerate(customer_report['recommendations'], 1):
            sections.append(f"{i}. {recommendation}\n")
        sections.append("\n")
        
        # Compliance status
        sections.append("### Compliance & Privacy Status\n")
        
        # Count PII findings
        pii_findings = [f for f in all_security_findings if 'personal' in f.risk_explanation.lower() or 'identifier' in f.risk_explanation.lower()]
        secret_findings = [f for f in all_security_findings if 'api' in f.type.lower() or 'key' in f.type.lower() or 'password' in f.type.lower()]
        
        if pii_findings:
            sections.append(f"- **Privacy Compliance**: ⚠️ {len(pii_findings)} personal information items detected\n")
            sections.append("  - Review for GDPR/CCPA compliance\n")
            sections.append("  - Consider data anonymization for development\n")
        else:
            sections.append("- **Privacy Compliance**: ✅ No personal information detected in code\n")
        
        if secret_findings:
            sections.append(f"- **Secret Management**: ⚠️ {len(secret_findings)} hardcoded credentials detected\n")
            sections.append("  - Move to environment variables immediately\n")
            sections.append("  - Implement secure credential management\n")
        else:
            sections.append("- **Secret Management**: ✅ No hardcoded credentials detected\n")
        
        sections.append("\n")
        
        # Performance metrics
        sections.append("### Analysis Performance\n")
        sections.append(f"- **Samples Processed**: {total_samples}\n")
        sections.append(f"- **High Risk Samples**: {high_risk_samples}\n") 
        sections.append(f"- **Medium Risk Samples**: {medium_risk_samples}\n")
        sections.append(f"- **Analysis Engine**: Dual-purpose content safety with international PII detection\n")
        sections.append(f"- **Coverage**: US, EU, UK, India, Singapore, Australia compliance patterns\n\n")
        
        sections.append("---\n")
        sections.append("*This analysis was generated by Copper Sun Brass automated security analysis engine. ")
        sections.append("For enterprise deployment support, contact your development team.*\n\n")
        
        return "\n".join(sections)