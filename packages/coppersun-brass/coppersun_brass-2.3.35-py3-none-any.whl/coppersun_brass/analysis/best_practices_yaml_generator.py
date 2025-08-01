"""
Best Practices YAML Generator

YAML generator for best practices recommendations that creates .brass/best_practices.yaml
with structured data optimized for AI consumption while preserving all evidence-based intelligence.

Key Features:
- Structured YAML format for direct programmatic access
- Evidence-based recommendations with detailed tracking
- Type-safe data (native integers, floats, booleans, arrays)  
- AI-optimized schema with consistent data access patterns
- Cross-references to related security, quality, and privacy analysis

Follows the proven pattern established by TodoYamlGenerator and PrivacyYamlGenerator.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

from coppersun_brass.core.best_practices_recommendations import BestPracticesRecommendationEngine

logger = logging.getLogger(__name__)


class BestPracticesYamlGenerator:
    """
    YAML generator for best practices recommendations for AI consumption.
    
    Creates structured YAML format optimized for programmatic access by AI agents.
    
    Integrates with BestPracticesRecommendationEngine for evidence-based analysis
    and enhances output with rich metadata for AI consumption.
    """
    
    def __init__(self, project_path: str, storage):
        """
        Initialize YAML best practices generator.
        
        Args:
            project_path: Root path of project to analyze
            storage: BrassStorage instance for data access
            
        Raises:
            ValueError: If project_path is not a valid directory
        """
        self.project_path = Path(project_path)
        self.storage = storage
        self.brass_dir = self.project_path / '.brass'
        self.yaml_output_path = self.brass_dir / 'best_practices.yaml'
        
        # Initialize best practices engine with graceful path validation
        try:
            self.best_practices_engine = BestPracticesRecommendationEngine(project_path=self.project_path)
        except ValueError as e:
            logger.warning(f"Invalid project path, using minimal recommendations: {e}")
            self.best_practices_engine = None  # Will generate fallback recommendations
        
        logger.info(f"YAML best practices generator initialized for project: {self.project_path}")
    
    def generate_yaml_report(self) -> str:
        """
        Generate structured YAML best practices report for AI consumption.
        
        Returns:
            Path to generated .brass/best_practices.yaml file
        """
        start_time = datetime.now()
        
        logger.info("Starting YAML best practices report generation")
        
        # Ensure .brass directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        # Phase 1: Gather project evidence
        logger.info("Phase 1: Gathering project evidence")
        evidence = self._gather_project_evidence()
        
        # Phase 2: Generate recommendations using existing engine
        logger.info("Phase 2: Generating evidence-based recommendations")
        raw_recommendations = self._generate_recommendations(evidence)
        
        # Phase 3: Enhance recommendations with metadata
        logger.info("Phase 3: Enhancing recommendations with AI metadata")
        enhanced_recommendations = self._enhance_recommendations(raw_recommendations, evidence)
        
        # Phase 4: Create comprehensive YAML structure
        logger.info("Phase 4: Creating comprehensive YAML structure")
        yaml_data = self._create_yaml_structure(enhanced_recommendations, evidence, start_time)
        
        # Phase 5: Write YAML file
        logger.info("Phase 5: Writing YAML file")
        yaml_content = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        self.yaml_output_path.write_text(yaml_content, encoding='utf-8')
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        logger.info(f"YAML best practices report generated successfully in {generation_time:.2f}s: {self.yaml_output_path}")
        return str(self.yaml_output_path)
    
    def _gather_project_evidence(self) -> Dict[str, Any]:
        """
        Gather evidence from project storage for recommendation analysis.
        
        Returns:
            Dictionary containing security issues, TODOs, code entities, and metrics
        """
        try:
            # Get observations from storage
            security_issues = self.storage.get_observations_by_type('security_issue', limit=1000)
            todos = self.storage.get_observations_by_type('todo', limit=500)
            code_entities = self.storage.get_observations_by_type('code_entity', limit=200)
            
            # Get code metrics (latest)
            metrics = self.storage.get_observations_by_type('code_metrics', limit=1)
            
            evidence = {
                'security_issues': security_issues,
                'todos': todos,
                'code_entities': code_entities,
                'code_metrics': metrics[0] if metrics else None,
                'project_stats': {
                    'security_issue_count': len(security_issues),
                    'todo_count': len(todos),
                    'code_entity_count': len(code_entities),
                    'has_metrics': bool(metrics)
                }
            }
            
            logger.info(f"Gathered evidence: {evidence['project_stats']}")
            return evidence
            
        except Exception as e:
            logger.warning(f"Failed to gather complete project evidence: {e}")
            # Return minimal evidence structure
            return {
                'security_issues': [],
                'todos': [],
                'code_entities': [],
                'code_metrics': None,
                'project_stats': {
                    'security_issue_count': 0,
                    'todo_count': 0,
                    'code_entity_count': 0,
                    'has_metrics': False
                }
            }
    
    def _generate_recommendations(self, evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations using BestPracticesRecommendationEngine.
        
        Args:
            evidence: Project evidence gathered from storage
            
        Returns:
            List of raw recommendation dictionaries
        """
        try:
            # Handle case where best practices engine failed to initialize
            if self.best_practices_engine is None:
                logger.info("Using fallback recommendations due to invalid project path")
                return self._get_fallback_recommendations()
            
            # Analyze project using existing engine
            analysis = self.best_practices_engine.analyze_project(
                security_issues=evidence['security_issues'],
                todos=evidence['todos'],
                code_entities=evidence['code_entities'],
                code_metrics=evidence['code_metrics']
            )
            
            # Generate recommendations (get more for YAML vs markdown)
            recommendations = self.best_practices_engine.generate_recommendations(analysis, limit=10)
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return self._get_fallback_recommendations()
    
    def _enhance_recommendations(self, raw_recommendations: List[Dict], evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Enhance recommendations with additional metadata for AI consumption.
        
        Args:
            raw_recommendations: Raw recommendations from engine
            evidence: Project evidence for cross-referencing
            
        Returns:
            Enhanced recommendations with AI metadata
        """
        enhanced = []
        
        for i, rec in enumerate(raw_recommendations):
            # Create enhanced recommendation structure
            enhanced_rec = {
                'id': self._generate_recommendation_id(rec.get('title', f'recommendation-{i}')),
                'priority': rec.get('priority', 50),
                'priority_level': self._get_priority_level(rec.get('priority', 50)),
                'category': rec.get('category', 'general'),
                'title': rec.get('title', 'Unnamed Recommendation'),
                'description': rec.get('description', ''),
                'implementation_guidance': rec.get('implementation', ''),
                'why_recommended': rec.get('rationale', ''),
                'references': rec.get('references', []),
                'evidence_detected': self._determine_evidence_types(rec, evidence),
                'implementation_time_estimate': self._estimate_implementation_time(rec),
                'success_metrics': self._generate_success_metrics(rec),
                'related_issues': {
                    'security_issue_count': evidence['project_stats']['security_issue_count'],
                    'todo_count': evidence['project_stats']['todo_count']
                },
                'status': 'recommended',
                'applicability_score': self._calculate_applicability_score(rec, evidence)
            }
            
            enhanced.append(enhanced_rec)
        
        # Sort by priority (highest first)
        enhanced.sort(key=lambda x: x['priority'], reverse=True)
        
        return enhanced
    
    def _create_yaml_structure(self, recommendations: List[Dict], evidence: Dict[str, Any], start_time: datetime) -> Dict[str, Any]:
        """
        Create comprehensive YAML structure for AI consumption.
        
        Args:
            recommendations: Enhanced recommendations
            evidence: Project evidence
            start_time: Generation start time
            
        Returns:
            Complete YAML data structure
        """
        # Calculate summary statistics
        priority_counts = defaultdict(int)
        category_counts = defaultdict(int)
        evidence_types = set()
        
        for rec in recommendations:
            priority_level = rec['priority_level']
            priority_counts[priority_level] += 1
            category_counts[rec['category']] += 1
            evidence_types.update(rec['evidence_detected'])
        
        yaml_structure = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'generator_version': '2.3.30',
                'format_version': '1.0',
                'schema_description': 'Evidence-based best practices recommendations optimized for AI consumption',
                'project_path': str(self.project_path),
                'generation_time_seconds': (datetime.now() - start_time).total_seconds(),
                'evidence_based_analysis': True
            },
            
            'recommendation_summary': {
                'total_recommendations': len(recommendations),
                'by_priority': dict(priority_counts),
                'by_category': dict(category_counts),
                'evidence_detected': sorted(list(evidence_types)),
                'project_stats': evidence['project_stats']
            },
            
            'recommendations': recommendations,
            
            'cross_references': {
                'security_analysis': 'CODE_SECURITY_AND_QUALITY_ANALYSIS.md',
                'quality_analysis': 'todos.yaml',
                'project_health': 'brass_analysis.yaml',
                'privacy_analysis': 'privacy_analysis.yaml',
                'enterprise_readiness': 'enterprise_readiness.json'
            },
            
            'ai_consumption_metadata': {
                'format_version': '1.0',
                'recommended_parsers': ['PyYAML', 'ruamel.yaml'],
                'parsing_instruction': 'Use yaml.safe_load() for secure parsing',
                'data_access_examples': {
                    'total_recommendations': "data['recommendation_summary']['total_recommendations']",
                    'high_priority_recs': "data['recommendation_summary']['by_priority']['high']",
                    'methodology_recs': "[r for r in data['recommendations'] if r['category'] == 'methodology']",
                    'top_priority_rec': "max(data['recommendations'], key=lambda x: x['priority'])",
                    'implementation_time': "data['recommendations'][0]['implementation_time_estimate']",
                    'success_metrics': "data['recommendations'][0]['success_metrics']",
                    'evidence_detected': "data['recommendations'][0]['evidence_detected']",
                    'related_security_issues': "data['recommendations'][0]['related_issues']['security_issue_count']"
                },
                'schema_stability': 'format_version tracks breaking changes',
                'integration_note': 'Standalone best practices analysis with cross-references to other .brass files'
            }
        }
        
        return yaml_structure
    
    def _generate_recommendation_id(self, title: str) -> str:
        """Generate a clean ID from recommendation title."""
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        clean_id = title.lower().replace(' ', '-').replace('/', '-')
        # Remove special characters except hyphens
        clean_id = ''.join(c for c in clean_id if c.isalnum() or c == '-')
        # Remove multiple consecutive hyphens
        while '--' in clean_id:
            clean_id = clean_id.replace('--', '-')
        return clean_id.strip('-')
    
    def _get_priority_level(self, priority: int) -> str:
        """Convert numeric priority to level."""
        if priority >= 90:
            return 'critical'
        elif priority >= 80:
            return 'high'
        elif priority >= 70:
            return 'medium'
        else:
            return 'low'
    
    def _determine_evidence_types(self, recommendation: Dict, evidence: Dict[str, Any]) -> List[str]:
        """Determine what evidence triggered this recommendation."""
        evidence_types = []
        
        # Check for security-related evidence
        if evidence['project_stats']['security_issue_count'] > 0:
            if 'security' in recommendation.get('category', ''):
                evidence_types.append('security_vulnerabilities')
        
        # Check for quality-related evidence
        if evidence['project_stats']['todo_count'] > 0:
            if any(keyword in recommendation.get('title', '').lower() for keyword in ['test', 'quality', 'coverage']):
                evidence_types.append('quality_issues')
        
        # Check for complexity evidence
        if evidence['project_stats']['code_entity_count'] > 0:
            if any(keyword in recommendation.get('title', '').lower() for keyword in ['complex', 'refactor', 'architecture']):
                evidence_types.append('complex_code_patterns')
        
        # Check for documentation evidence
        if any(keyword in recommendation.get('title', '').lower() for keyword in ['document', 'api', 'guide']):
            evidence_types.append('documentation_gaps')
        
        # Default evidence type
        if not evidence_types:
            evidence_types.append('general_best_practices')
        
        return evidence_types
    
    def _estimate_implementation_time(self, recommendation: Dict) -> str:
        """Estimate implementation time based on recommendation characteristics."""
        title = recommendation.get('title', '').lower()
        priority = recommendation.get('priority', 50)
        
        # High-effort items
        if any(keyword in title for keyword in ['comprehensive', 'system', 'architecture', 'migration']):
            return '1-2 weeks'
        elif any(keyword in title for keyword in ['monitoring', 'testing', 'security']):
            return '2-5 days'
        elif priority >= 90:
            return '2-4 hours initial setup'
        elif priority >= 80:
            return '1-2 days'
        else:
            return '4-8 hours'
    
    def _generate_success_metrics(self, recommendation: Dict) -> List[str]:
        """Generate success metrics based on recommendation type."""
        title = recommendation.get('title', '').lower()
        category = recommendation.get('category', '')
        
        metrics = []
        
        if 'test' in title or 'coverage' in title:
            metrics.extend(['increased_test_coverage', 'reduced_bug_count'])
        if 'security' in title or category == 'security':
            metrics.extend(['reduced_security_vulnerabilities', 'improved_security_score'])
        if 'documentation' in title:
            metrics.extend(['improved_documentation_coverage', 'faster_onboarding'])
        if 'monitoring' in title:
            metrics.extend(['faster_incident_response', 'improved_uptime'])
        if 'process' in title or 'methodology' in title:
            metrics.extend(['reduced_defect_rate', 'faster_delivery_cycles'])
        
        # Default metrics
        if not metrics:
            metrics.extend(['improved_code_quality', 'enhanced_maintainability'])
        
        return metrics
    
    def _calculate_applicability_score(self, recommendation: Dict, evidence: Dict[str, Any]) -> float:
        """Calculate how applicable this recommendation is to the current project."""
        score = 0.5  # Base score
        
        # Increase score based on evidence
        if evidence['project_stats']['security_issue_count'] > 0 and 'security' in recommendation.get('category', ''):
            score += 0.3
        if evidence['project_stats']['todo_count'] > 0 and 'quality' in recommendation.get('title', '').lower():
            score += 0.2
        if evidence['project_stats']['code_entity_count'] > 10:
            score += 0.1
        
        # Adjust based on priority
        priority = recommendation.get('priority', 50)
        if priority >= 90:
            score += 0.2
        elif priority >= 80:
            score += 0.1
        
        return min(1.0, score)  # Cap at 1.0
    
    def _get_fallback_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate minimal fallback recommendations when project path is invalid.
        
        Returns basic development best practices that apply to any project.
        """
        return [
            {
                'title': 'Secure Secrets Management',
                'description': 'Never commit secrets; use secure secret management solutions',
                'implementation': 'Use HashiCorp Vault, AWS Secrets Manager, or environment variables',
                'rationale': 'Prevents credential exposure and security breaches',
                'references': ['OWASP A07:2021', 'NIST 800-57'],
                'priority': 95,
                'category': 'security'
            },
            {
                'title': 'Input Validation and Sanitization',
                'description': 'Validate and sanitize all user inputs to prevent injection attacks',
                'implementation': 'Use parameterized queries, input validation libraries, and output encoding',
                'rationale': 'Prevents SQL injection, XSS, and other injection vulnerabilities',
                'references': ['OWASP Top 10', 'CWE-20'],
                'priority': 90,
                'category': 'security'
            },
            {
                'title': 'Regular Security Updates',
                'description': 'Keep dependencies and frameworks updated with security patches',
                'implementation': 'Use automated dependency scanning and update tools',
                'rationale': 'Prevents exploitation of known vulnerabilities',
                'references': ['OWASP A06:2021', 'NIST CVE'],
                'priority': 85,
                'category': 'security'
            },
            {
                'title': 'Code Review Process',
                'description': 'Implement peer code reviews for all code changes',
                'implementation': 'Use pull request workflows with required reviews',
                'rationale': 'Catches bugs, improves code quality, and shares knowledge',
                'references': ['Google Code Review Guidelines', 'GitHub Flow'],
                'priority': 80,
                'category': 'quality'
            },
            {
                'title': 'Automated Testing Strategy',
                'description': 'Implement comprehensive testing including unit, integration, and security tests',
                'implementation': 'Set up CI/CD pipelines with automated test execution',
                'rationale': 'Prevents regressions and ensures code reliability',
                'references': ['Test Pyramid', 'DevOps Best Practices'],
                'priority': 75,
                'category': 'reliability'
            }
        ]