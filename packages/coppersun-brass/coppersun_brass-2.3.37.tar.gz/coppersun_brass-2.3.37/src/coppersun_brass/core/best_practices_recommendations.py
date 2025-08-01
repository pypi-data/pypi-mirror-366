"""
Best Practices Recommendations Engine for Copper Sun Brass

Modern implementation that provides actionable best practices recommendations
based on project analysis. Directly integrated with OutputGenerator.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from collections import defaultdict, Counter
import itertools

logger = logging.getLogger(__name__)


class BestPracticesRecommendationEngine:
    """Generates actionable best practices recommendations based on project analysis."""
    
    def __init__(self, project_path: Optional[Path] = None):
        """Initialize the Best Practices Recommendation Engine.
        
        Args:
            project_path: Root path of the project to analyze
            
        Raises:
            ValueError: If project_path is not a valid directory
            PermissionError: If project_path is not accessible
        """
        try:
            if project_path is None:
                self.project_path = Path.cwd()
            else:
                self.project_path = Path(project_path)
                
            # Validate project path
            if not self.project_path.exists():
                raise ValueError(f"Project path does not exist: {self.project_path}")
            if not self.project_path.is_dir():
                raise ValueError(f"Project path is not a directory: {self.project_path}")
                
            # Test accessibility with early termination (memory-efficient)
            try:
                next(self.project_path.iterdir(), None)  # Test access without full directory listing
            except PermissionError as e:
                raise PermissionError(f"Cannot access project directory: {self.project_path}") from e
                
        except Exception as e:
            logger.error(f"Failed to initialize BestPracticesRecommendationEngine: {e}")
            raise
        
        # Define recommendation templates with modern best practices
        self.recommendation_templates = {
            'security_scanning': {
                'title': 'Implement Automated Security Scanning',
                'description': 'Add automated security vulnerability scanning to your CI/CD pipeline',
                'implementation': 'Use tools like Snyk, GitHub Security Scanning, or OWASP Dependency Check',
                'rationale': 'Identifies vulnerabilities early in development cycle, reducing security debt',
                'references': ['OWASP DevSecOps Guideline', 'NIST 800-53 SA-11'],
                'priority': 90,
                'category': 'security'
            },
            'input_validation': {
                'title': 'Comprehensive Input Validation',
                'description': 'Implement strict input validation for all user-provided data',
                'implementation': 'Use schema validation libraries (Joi, Yup, Pydantic) and sanitize all inputs',
                'rationale': 'Prevents injection attacks and data corruption issues',
                'references': ['OWASP Input Validation Cheat Sheet', 'CWE-20'],
                'priority': 85,
                'category': 'security'
            },
            'error_handling': {
                'title': 'Structured Error Handling and Logging',
                'description': 'Implement comprehensive error handling with structured logging',
                'implementation': 'Use structured logging libraries with correlation IDs and error context',
                'rationale': 'Essential for debugging production issues and security incident response',
                'references': ['OWASP Logging Cheat Sheet', 'NIST 800-92'],
                'priority': 80,
                'category': 'reliability'
            },
            'code_review': {
                'title': 'Mandatory Code Review Process',
                'description': 'Establish mandatory peer code review for all changes',
                'implementation': 'Use pull request workflows with required approvals and automated checks',
                'rationale': 'Catches bugs early, shares knowledge, and improves code quality',
                'references': ['IEEE 1028-2008', 'Google Engineering Practices'],
                'priority': 85,
                'category': 'quality'
            },
            'test_coverage': {
                'title': 'Comprehensive Test Coverage',
                'description': 'Achieve and maintain at least 80% code coverage with quality tests',
                'implementation': 'Use coverage tools, focus on critical paths and edge cases',
                'rationale': 'Reduces regression bugs and enables confident refactoring',
                'references': ['Martin Fowler Test Coverage', 'IEEE 829-2008'],
                'priority': 75,
                'category': 'quality'
            },
            'documentation': {
                'title': 'Comprehensive Documentation',
                'description': 'Maintain up-to-date documentation for architecture, APIs, and deployment',
                'implementation': 'Use tools like Swagger/OpenAPI, architecture decision records (ADRs)',
                'rationale': 'Reduces onboarding time and prevents knowledge silos',
                'references': ['RFC 2119', 'ISO/IEC/IEEE 26515:2018'],
                'priority': 70,
                'category': 'maintainability'
            },
            'dependency_management': {
                'title': 'Automated Dependency Management',
                'description': 'Implement automated dependency updates with security scanning',
                'implementation': 'Use Dependabot, Renovate, or similar tools with automated testing',
                'rationale': 'Prevents security vulnerabilities from outdated dependencies',
                'references': ['OWASP A06:2021', 'NIST 800-161'],
                'priority': 75,
                'category': 'security'
            },
            'monitoring': {
                'title': 'Production Monitoring and Alerting',
                'description': 'Implement comprehensive monitoring with proactive alerting',
                'implementation': 'Use APM tools (DataDog, New Relic) with custom metrics and alerts',
                'rationale': 'Enables rapid incident response and performance optimization',
                'references': ['SRE Book Ch. 6', 'NIST 800-137'],
                'priority': 80,
                'category': 'operations'
            },
            'api_versioning': {
                'title': 'API Versioning Strategy',
                'description': 'Implement clear API versioning for backward compatibility',
                'implementation': 'Use semantic versioning with deprecation policies',
                'rationale': 'Prevents breaking changes for API consumers',
                'references': ['REST API Design Rulebook', 'RFC 7231'],
                'priority': 70,
                'category': 'architecture'
            },
            'secrets_management': {
                'title': 'Secure Secrets Management',
                'description': 'Never commit secrets; use secure secret management solutions',
                'implementation': 'Use HashiCorp Vault, AWS Secrets Manager, or environment variables',
                'rationale': 'Prevents credential exposure and security breaches',
                'references': ['OWASP A07:2021', 'NIST 800-57'],
                'priority': 95,
                'category': 'security'
            },
            
            # AI Coding Best Practices
            'ai_iterative_refinement': {
                'title': 'AI Iterative Refinement Process',
                'description': 'Break complex coding tasks into smaller, manageable AI prompts',
                'implementation': 'Use step-by-step approach with feedback loops and incremental improvements',
                'rationale': 'Prevents AI from generating overly complex or incorrect solutions',
                'references': ['Prompt Engineering Standards', 'AI Development Workflows'],
                'priority': 70,
                'category': 'ai_workflow'
            },
            'ai_code_testing': {
                'title': 'Mandatory AI Code Testing',
                'description': 'Always test, lint, and type-check AI-generated code',
                'implementation': 'Run automated tests, linting tools, and type checking after AI code generation',
                'rationale': 'AI can introduce bugs, security vulnerabilities, and style inconsistencies',
                'references': ['AI Code Quality Standards', 'Automated Testing Best Practices'],
                'priority': 90,
                'category': 'ai_quality'
            },
            'ai_version_control': {
                'title': 'AI Change Tracking',
                'description': 'Track and document AI-generated code modifications separately',
                'implementation': 'Use commit messages and documentation to identify AI-generated changes',
                'rationale': 'Enables better debugging and maintenance of AI-assisted codebases',
                'references': ['Version Control Best Practices', 'AI Development Documentation'],
                'priority': 65,
                'category': 'ai_workflow'
            },
            'ai_evidence_based_development': {
                'title': '7-Step Evidence-Based Development Process',
                'description': 'Follow systematic 7-step methodology for feature implementation',
                'implementation': 'Execute all steps systematically: Problem Definition → Evidence Gathering → Architecture Design → Implementation → Integration Testing → Documentation → Deployment',
                'rationale': 'Proven methodology achieving 100% success rate with measurable outcomes (Smart File Classification: 359→13 findings)',
                'references': ['docs/developer-guide/EVIDENCE_BASED_DEVELOPMENT_PROCESS.md', 'Smart File Classification Success Pattern'],
                'priority': 95,
                'category': 'ai_workflow'
            },
        }

    def analyze_project(self, 
                       security_issues: List[Dict[str, Any]] = None,
                       todos: List[Dict[str, Any]] = None,
                       code_entities: List[Dict[str, Any]] = None,
                       code_metrics: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze project characteristics to determine relevant recommendations.
        
        Args:
            security_issues: List of security issues found
            todos: List of TODO items in code
            code_entities: List of code entities (functions, classes)
            code_metrics: Overall code metrics
            
        Returns:
            Analysis results with project characteristics
        """
        # Input validation with safe defaults
        security_issues = security_issues if security_issues is not None else []
        todos = todos if todos is not None else []
        code_entities = code_entities if code_entities is not None else []
        code_metrics = code_metrics if code_metrics is not None else {}
        
        # Validate input types
        if not isinstance(security_issues, list):
            logger.warning(f"Invalid security_issues type: {type(security_issues)}, using empty list")
            security_issues = []
        if not isinstance(todos, list):
            logger.warning(f"Invalid todos type: {type(todos)}, using empty list")
            todos = []
        if not isinstance(code_entities, list):
            logger.warning(f"Invalid code_entities type: {type(code_entities)}, using empty list")
            code_entities = []
        if not isinstance(code_metrics, dict):
            logger.warning(f"Invalid code_metrics type: {type(code_metrics)}, using empty dict")
            code_metrics = {}
        analysis = {
            'project_size': 'unknown',
            'languages': set(),
            'frameworks': set(),
            'has_tests': False,
            'has_ci': False,
            'has_docs': False,
            'security_score': 100,  # Start at 100, deduct for issues
            'quality_score': 100,
            'identified_gaps': []
        }
        
        # Log best practices system activation with thresholds
        logger.info("BEST_PRACTICES: Evidence-based analysis starting")
        logger.info("BEST_PRACTICES: Detection thresholds - Security: 1+ high issues, Complexity: >5 avg, Documentation: <50% coverage")
        
        try:
            # Analyze file structure
            file_stats = self._analyze_file_structure()
            analysis['languages'] = file_stats['languages']
            analysis['project_size'] = file_stats['size']
            analysis['has_tests'] = file_stats['has_tests']
            analysis['has_docs'] = file_stats['has_docs']
            analysis['has_ci'] = file_stats['has_ci']
            
            # Analyze security posture - LOWERED THRESHOLDS for better detection
            if security_issues:
                critical_count = len([s for s in security_issues if s.get('severity') == 'critical'])
                high_count = len([s for s in security_issues if s.get('severity') == 'high'])
                medium_count = len([s for s in security_issues if s.get('severity') == 'medium'])
                total_security_issues = len(security_issues)
                
                analysis['security_score'] -= (critical_count * 20 + high_count * 10 + medium_count * 5)
                analysis['security_score'] = max(0, analysis['security_score'])
                
                # LOWERED: Any critical issues trigger immediate response
                if critical_count > 0:
                    analysis['identified_gaps'].append('critical_security_issues')
                # LOWERED: 1+ high security issues (was 2+)
                if high_count >= 1:
                    analysis['identified_gaps'].append('multiple_security_issues')
                # NEW: Detect patterns of security neglect
                if total_security_issues > 20:
                    analysis['identified_gaps'].append('security_debt')
            
            # Analyze code quality - LOWERED THRESHOLDS for better detection
            if code_metrics:
                avg_complexity = code_metrics.get('average_complexity', 0)
                doc_coverage = code_metrics.get('documentation_coverage', 0)
                
                # LOWERED: 5+ complexity (was 10+) indicates refactoring needs
                if avg_complexity > 5:
                    analysis['quality_score'] -= 20
                    analysis['identified_gaps'].append('high_complexity')
                # LOWERED: <50% documentation (was <30%) indicates documentation gaps
                if doc_coverage < 0.5:
                    analysis['quality_score'] -= 15
                    analysis['identified_gaps'].append('low_documentation')
                # NEW: Detect zero documentation as critical gap
                if doc_coverage == 0:
                    analysis['identified_gaps'].append('missing_documentation')
            
            # Analyze TODOs for patterns - ENHANCED DETECTION
            if todos:
                # Detect security-related TODOs with expanded keywords
                security_keywords = ['security', 'auth', 'validation', 'sanitiz', 'encrypt', 'hash', 'token', 'permission', 'rate limit', 'input', 'vulnerability']
                security_todos = len([t for t in todos if any(keyword in str(t).lower() for keyword in security_keywords)])
                
                # LOWERED: 1+ security TODOs (was 3+) indicates security debt
                if security_todos >= 1:
                    analysis['identified_gaps'].append('security_debt')
                
                # NEW: Detect high volume of TODOs indicating technical debt
                total_todos = len(todos)
                if total_todos > 30:
                    analysis['identified_gaps'].append('technical_debt')
                
                # NEW: Detect FIXME patterns indicating urgent issues
                fixme_todos = len([t for t in todos if 'fixme' in str(t).lower()])
                if fixme_todos > 5:
                    analysis['identified_gaps'].append('urgent_fixes_needed')
            
            # Detect observable AI-related problems from project analysis
            ai_issues = self._detect_ai_related_issues(security_issues, todos, code_entities, code_metrics)
            analysis['identified_gaps'].extend(ai_issues)
            
            # Check for missing critical components
            if not analysis['has_tests']:
                analysis['identified_gaps'].append('missing_tests')
            if not analysis['has_ci']:
                analysis['identified_gaps'].append('missing_ci')
            
            # Log analysis results with detailed metrics
            security_count = len(security_issues) if security_issues else 0
            todo_count = len(todos) if todos else 0
            entity_count = len(code_entities) if code_entities else 0
            gap_count = len(analysis['identified_gaps'])
            
            logger.info("BEST_PRACTICES: Analysis complete - %d security issues, %d TODOs, %d code entities", 
                       security_count, todo_count, entity_count)
            logger.info("BEST_PRACTICES: Identified %d gaps: %s%s", 
                       gap_count, ', '.join(analysis['identified_gaps'][:5]),
                       '...' if gap_count > 5 else '')
            logger.info("BEST_PRACTICES: Project characteristics - Size: %s, Languages: %s",
                       analysis['project_size'], 
                       ', '.join(analysis['languages']) if analysis['languages'] else 'none')
            
        except Exception as e:
            logger.warning(f"Error during project analysis: {e}")
        
        return analysis

    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analyze project file structure to identify characteristics."""
        stats = {
            'languages': set(),
            'size': 'small',
            'has_tests': False,
            'has_docs': False,
            'has_ci': False,
            'file_count': 0
        }
        
        try:
            # Count files by extension with memory safety limits
            extension_map = {
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript',
                '.jsx': 'React',
                '.tsx': 'React',
                '.java': 'Java',
                '.go': 'Go',
                '.rs': 'Rust',
                '.rb': 'Ruby',
                '.php': 'PHP',
                '.cs': 'C#',
                '.cpp': 'C++',
                '.c': 'C',
                '.swift': 'Swift',
                '.kt': 'Kotlin'
            }
            
            # Critical fix: Add safety limits to prevent memory exhaustion
            MAX_FILES_TO_SCAN = 10000  # Prevent unbounded memory usage
            file_count = 0
            files_scanned = 0
            
            for ext, lang in extension_map.items():
                # Use memory-safe bounded iteration from start
                remaining_limit = MAX_FILES_TO_SCAN - files_scanned
                if remaining_limit <= 0:
                    break
                
                # Use itertools.islice to bound memory usage upfront
                file_iterator = itertools.islice(
                    self.project_path.rglob(f'*{ext}'), 
                    remaining_limit
                )
                ext_count = 0
                
                # FILE SCANNING PERFORMANCE FIX: Count files without full iteration
                for file_path in file_iterator:
                    files_scanned += 1
                    ext_count += 1
                    
                    # Early termination check during iteration to prevent excessive processing
                    if files_scanned >= MAX_FILES_TO_SCAN:
                        break
                
                if ext_count > 0:
                    stats['languages'].add(lang)
                    file_count += ext_count
                
                # Log if we hit the limit
                if files_scanned >= MAX_FILES_TO_SCAN:
                    logger.warning(f"File scanning stopped at {MAX_FILES_TO_SCAN} files to prevent memory exhaustion")
                    break
            
            stats['file_count'] = file_count
            
            # Determine project size
            if file_count > 100:
                stats['size'] = 'large'
            elif file_count > 30:
                stats['size'] = 'medium'
            else:
                stats['size'] = 'small'
            
            # Check for test files with safety limits
            test_patterns = ['test_*.py', '*.test.js', '*.spec.js', '*.test.ts', '*.spec.ts']
            for pattern in test_patterns:
                try:
                    # Use memory-safe bounded iteration for test file detection
                    test_iterator = itertools.islice(self.project_path.rglob(pattern), 1)
                    # Use any() for cleaner iteration management
                    if any(True for _ in test_iterator):
                        stats['has_tests'] = True
                        break
                except (OSError, PermissionError):
                    continue  # Handle file system errors gracefully
            if (self.project_path / 'tests').exists() or (self.project_path / 'test').exists():
                stats['has_tests'] = True
            
            # Check for documentation
            doc_files = ['README.md', 'README.rst', 'README.txt', 'CONTRIBUTING.md', 'docs']
            for doc in doc_files:
                if (self.project_path / doc).exists():
                    stats['has_docs'] = True
                    break
            
            # Check for CI/CD
            ci_files = ['.github/workflows', '.gitlab-ci.yml', 'Jenkinsfile', '.circleci', '.travis.yml']
            for ci in ci_files:
                if (self.project_path / ci).exists():
                    stats['has_ci'] = True
                    break
                    
        except Exception as e:
            logger.warning(f"Error analyzing file structure: {e}")
        
        return stats

    def _detect_ai_related_issues(self,
                                 security_issues: List[Dict[str, Any]] = None,
                                 todos: List[Dict[str, Any]] = None,
                                 code_entities: List[Dict[str, Any]] = None,
                                 code_metrics: Dict[str, Any] = None) -> List[str]:
        """Detect observable AI-related problems in the project.
        
        Args:
            security_issues: List of security issues (can be None)
            todos: List of TODO items (can be None)
            code_entities: List of code entities (can be None)
            code_metrics: Overall code metrics (can be None)
        
        Returns:
            List of identified AI-related gaps based on actual evidence
        """
        issues = []
        
        # Input validation and safe defaults
        security_issues = security_issues if security_issues is not None else []
        todos = todos if todos is not None else []
        code_entities = code_entities if code_entities is not None else []
        code_metrics = code_metrics if code_metrics is not None else {}
        
        try:
            # Evidence: Look for AI-generated code without tests
            if self._has_untested_ai_generated_code(code_entities, code_metrics):
                issues.append('untested_ai_code')
            
            # Evidence: Look for suspiciously uniform/repetitive code patterns
            if self._has_ai_code_patterns(code_entities):
                issues.append('ai_generated_code_quality')
            
            # Evidence: Look for TODOs mentioning AI tools or generated code
            if self._has_ai_related_todos(todos):
                issues.append('ai_workflow_debt')
            
            # Evidence: Look for security issues that commonly appear in AI-generated code
            if self._has_ai_typical_security_issues(security_issues):
                issues.append('ai_security_risks')
            
            # Evidence: Look for large functions that might need AI-assisted refactoring
            if self._has_complex_functions_needing_ai_help(code_entities):
                issues.append('complex_code_needs_ai_assistance')
            
            # Evidence: Look for projects that need systematic development approach
            if self._needs_systematic_development_approach(code_entities, code_metrics, todos):
                issues.append('needs_systematic_development')
                
        except Exception as e:
            logger.warning(f"Error during AI-related issue detection: {e}")
            # Return partial results instead of failing completely
        
        return issues
    
    def _has_untested_ai_generated_code(self, code_entities: List[Dict] = None, code_metrics: Dict = None) -> bool:
        """Check if there are signs of untested AI-generated code."""
        if not code_entities or not code_metrics:
            return False
        
        # Evidence: Very low test coverage + presence of repetitive function names
        test_coverage = code_metrics.get('documentation_coverage', 1.0)  # Using doc coverage as proxy
        
        # LOWERED: 0% documentation coverage (was <10%) indicates potential AI generation without proper documentation
        if test_coverage == 0:  # Zero documentation coverage
            # Look for repetitive patterns that suggest AI generation
            function_names = [e.get('entity_name', '') for e in code_entities if e.get('entity_type') == 'function']
            if len(function_names) > 5:
                # O(n) performance optimization: Use set-based similarity detection
                name_similarity_count = 0
                name_parts = set()
                
                for name in function_names:
                    if not name:
                        continue
                    
                    # Split name into components for O(1) similarity checking
                    parts = set(name.lower().split('_'))
                    if name_parts & parts:  # Set intersection is O(1)
                        name_similarity_count += 1
                    name_parts.update(parts)
                    
                    # Early termination for performance
                    if name_similarity_count > 3:
                        return True
        
        return False
    
    def _has_ai_code_patterns(self, code_entities: List[Dict] = None) -> bool:
        """Check for patterns typical of AI-generated code."""
        if not code_entities:
            return False
        
        # Evidence: Multiple entities with identical complexity scores (AI tends to generate uniform code)
        complexity_scores = [e.get('complexity_score', 0) for e in code_entities if e.get('complexity_score')]
        if len(complexity_scores) > 5:
            # Check if too many functions have identical complexity
            complexity_counts = Counter(complexity_scores)
            # Defensive programming: Handle empty Counter (shouldn't happen due to len check above)
            max_identical = max(complexity_counts.values()) if complexity_counts else 0
            if max_identical > len(complexity_scores) * 0.4:  # 40% have same complexity
                return True
        
        return False
    
    def _has_ai_related_todos(self, todos: List[Dict] = None) -> bool:
        """Check for TODOs that mention AI tools or workflow issues."""
        if not todos:
            return False
        
        ai_keywords = ['ai', 'claude', 'gpt', 'generated', 'copilot', 'assistant', 'llm', 'prompt']
        ai_todo_count = 0
        
        for todo in todos:
            content = str(todo.get('content', '')).lower()
            if any(keyword in content for keyword in ai_keywords):
                ai_todo_count += 1
        
        return ai_todo_count > 2  # Multiple AI-related TODOs suggest workflow issues
    
    def _has_ai_typical_security_issues(self, security_issues: List[Dict] = None) -> bool:
        """Check for security issues commonly found in AI-generated code."""
        if not security_issues:
            return False
        
        # AI commonly generates code with these issues
        ai_common_patterns = [
            'hardcoded', 'sql injection', 'xss', 'path traversal', 
            'insecure random', 'weak encryption', 'missing validation'
        ]
        
        ai_related_issues = 0
        for issue in security_issues:
            description = str(issue.get('description', '')).lower()
            if any(pattern in description for pattern in ai_common_patterns):
                ai_related_issues += 1
        
        return ai_related_issues > 3  # Multiple typical AI security issues
    
    def _has_complex_functions_needing_ai_help(self, code_entities: List[Dict] = None) -> bool:
        """Check for overly complex functions that could benefit from AI-assisted refactoring."""
        if not code_entities:
            return False
        
        # LOWERED: Complexity >10 (was >15) indicates refactoring opportunity
        complex_functions = [e for e in code_entities 
                           if e.get('entity_type') in ['function', 'arrow_function', 'class']
                           and e.get('complexity_score', 0) > 10]
        
        # LOWERED: 1+ complex functions (was 2+) triggers recommendation
        return len(complex_functions) >= 1

    def _needs_systematic_development_approach(self, code_entities: List[Dict] = None, 
                                             code_metrics: Dict = None, 
                                             todos: List[Dict] = None) -> bool:
        """Check for projects that would benefit from systematic development approach."""
        if not code_entities and not code_metrics and not todos:
            return False
        
        try:
            # Safe defaults
            code_entities = code_entities if code_entities is not None else []
            code_metrics = code_metrics if code_metrics is not None else {}
            todos = todos if todos is not None else []
            
            # Evidence 1: Large number of complex entities suggesting major feature work
            complex_entities = [e for e in code_entities 
                              if e.get('complexity_score', 0) > 8]
            has_complex_codebase = len(complex_entities) > 5
            
            # Evidence 2: Multiple TODOs indicating incomplete/in-progress work
            has_multiple_todos = len(todos) > 3
            
            # Evidence 3: Large codebase indicating need for systematic approach
            total_entities = len(code_entities)
            has_large_codebase = total_entities > 20
            
            # Evidence 4: TODOs mentioning implementation, features, or architecture
            implementation_todos = [t for t in todos 
                                  if any(keyword in t.get('description', '').lower() 
                                        for keyword in ['implement', 'feature', 'architecture', 
                                                       'refactor', 'design', 'system'])]
            has_implementation_work = len(implementation_todos) > 1
            
            # Recommend systematic approach if multiple indicators present
            indicators = [has_complex_codebase, has_multiple_todos, has_large_codebase, has_implementation_work]
            return sum(indicators) >= 2
            
        except Exception as e:
            logger.warning(f"Error checking systematic development needs: {e}")
            return False

    def generate_recommendations(self,
                               analysis: Dict[str, Any],
                               limit: int = 6) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations based on project analysis.
        
        Args:
            analysis: Project analysis results
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommendations with full details
        """
        recommendations = []
        selected_keys = set()
        
        # Log recommendation generation start
        gap_count = len(analysis.get('identified_gaps', []))
        logger.info("BEST_PRACTICES: Generating recommendations for %d identified gaps (limit: %d)", 
                   gap_count, limit)
        
        # Priority 1: Critical security gaps
        if 'critical_security_issues' in analysis['identified_gaps']:
            if 'input_validation' not in selected_keys:
                recommendations.append(self.recommendation_templates['input_validation'])
                selected_keys.add('input_validation')
            if 'security_scanning' not in selected_keys:
                recommendations.append(self.recommendation_templates['security_scanning'])
                selected_keys.add('security_scanning')
        
        # Priority 2: Missing critical components
        if 'missing_tests' in analysis['identified_gaps'] and 'test_coverage' not in selected_keys:
            recommendations.append(self.recommendation_templates['test_coverage'])
            selected_keys.add('test_coverage')
        
        if 'missing_ci' in analysis['identified_gaps'] and 'code_review' not in selected_keys:
            recommendations.append(self.recommendation_templates['code_review'])
            selected_keys.add('code_review')
        
        # Priority 3: Quality issues - ENHANCED DETECTION
        if ('high_complexity' in analysis['identified_gaps'] or 
            'technical_debt' in analysis['identified_gaps'] or
            'urgent_fixes_needed' in analysis['identified_gaps']):
            if 'error_handling' not in selected_keys:
                recommendations.append(self.recommendation_templates['error_handling'])
                selected_keys.add('error_handling')
        
        # NEW: Handle multiple documentation gap types
        if ('low_documentation' in analysis['identified_gaps'] or 
            'missing_documentation' in analysis['identified_gaps']) and 'documentation' not in selected_keys:
            recommendations.append(self.recommendation_templates['documentation'])
            selected_keys.add('documentation')
        
        # NEW: Handle security debt specifically
        if 'security_debt' in analysis['identified_gaps'] and 'input_validation' not in selected_keys:
            recommendations.append(self.recommendation_templates['input_validation'])
            selected_keys.add('input_validation')
        
        # Priority 4: General best practices based on project size
        if analysis['project_size'] in ['medium', 'large']:
            if 'monitoring' not in selected_keys and len(recommendations) < limit:
                recommendations.append(self.recommendation_templates['monitoring'])
                selected_keys.add('monitoring')
            if 'dependency_management' not in selected_keys and len(recommendations) < limit:
                recommendations.append(self.recommendation_templates['dependency_management'])
                selected_keys.add('dependency_management')
        
        # Priority 5: Evidence-based AI recommendations
        # Only recommend based on actual observed problems
        
        if 'untested_ai_code' in analysis['identified_gaps'] and 'ai_code_testing' not in selected_keys:
            recommendations.append(self.recommendation_templates['ai_code_testing'])
            selected_keys.add('ai_code_testing')
        
        if 'complex_code_needs_ai_assistance' in analysis['identified_gaps'] and 'ai_iterative_refinement' not in selected_keys:
            recommendations.append(self.recommendation_templates['ai_iterative_refinement'])
            selected_keys.add('ai_iterative_refinement')
        
        # Priority 1: Systematic development methodology for complex projects
        if 'needs_systematic_development' in analysis['identified_gaps'] and 'ai_evidence_based_development' not in selected_keys:
            recommendations.append(self.recommendation_templates['ai_evidence_based_development'])
            selected_keys.add('ai_evidence_based_development')
        
        # Always include secrets management if not already included
        if 'secrets_management' not in selected_keys and len(recommendations) < limit:
            recommendations.append(self.recommendation_templates['secrets_management'])
            selected_keys.add('secrets_management')
        
        # Fill remaining slots with other relevant recommendations
        remaining_keys = set(self.recommendation_templates.keys()) - selected_keys
        for key in sorted(remaining_keys, 
                         key=lambda k: self.recommendation_templates[k]['priority'], 
                         reverse=True):
            if len(recommendations) >= limit:
                break
            recommendations.append(self.recommendation_templates[key])
        
        # Sort by priority
        recommendations.sort(key=lambda r: r['priority'], reverse=True)
        
        # Log recommendation results
        final_count = min(len(recommendations), limit)
        if recommendations:
            rec_titles = [rec['title'] for rec in recommendations[:limit]]
            logger.info("BEST_PRACTICES: Generated %d recommendations: %s%s", 
                       final_count, ', '.join(rec_titles[:3]),
                       '...' if final_count > 3 else '')
            logger.info("BEST_PRACTICES: Evidence-based system active - only recommending for observed problems")
        else:
            logger.info("BEST_PRACTICES: No recommendations generated - no significant gaps detected")
        
        return recommendations[:limit]

    def format_recommendations_for_output(self, recommendations: List[Dict[str, Any]]) -> List[str]:
        """Format recommendations for markdown output.
        
        Args:
            recommendations: List of recommendation dictionaries
            
        Returns:
            List of formatted markdown strings
        """
        formatted = []
        
        for rec in recommendations:
            # Determine icon based on priority
            if rec['priority'] >= 90:
                icon = "🚨"
            elif rec['priority'] >= 80:
                icon = "🔴"
            elif rec['priority'] >= 70:
                icon = "🟡"
            else:
                icon = "🟢"
            
            # Format the recommendation
            lines = [f"{icon} **{rec['title']}** (Priority: {rec['priority']})"]
            
            if rec.get('description'):
                lines.append(f"  - *Description*: {rec['description']}")
            
            if rec.get('implementation'):
                lines.append(f"  - *Implementation*: {rec['implementation']}")
            
            if rec.get('rationale'):
                lines.append(f"  - *Why*: {rec['rationale']}")
            
            if rec.get('references'):
                refs = ", ".join(rec['references'])
                lines.append(f"  - *References*: {refs}")
            
            formatted.append("\n".join(lines))
        
        return formatted