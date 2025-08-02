#!/usr/bin/env python3
"""
Scout Agent - Enhanced with Deep Analysis Capabilities

General Staff Role: G2 Intelligence Officer
Provides comprehensive code intelligence through multiple analyzers,
integrating TODO detection, AST analysis, pattern recognition, and
evolution tracking for strategic AI decision-making.

Persistent Value: Creates multi-layered intelligence that helps AI
understand code health, risks, and opportunities across time.
"""

import os
import json
import logging
import math
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
from dataclasses import dataclass, field
import concurrent.futures
import threading

# Core Scout components
from .todo_detector import TODODetector, TODOFinding
from .dcp_integrator import ScoutDCPIntegrator
from .research_generator import ResearchQueryGenerator

# Enhanced analyzers
from .analyzers import (
    BaseAnalyzer, AnalysisResult, CodeEntity, CodeIssue, CodeMetrics,
    PythonAnalyzer, JavaScriptAnalyzer, TypeScriptAnalyzer,
    PatternAnalyzer, PatternDefinition
)
from .analyzers.evolution_tracker import EvolutionTracker, IssueEvolution

# DCP integration
try:
    from ...core.dcp_adapter import DCPAdapter
    DCPManager = DCPAdapter
except ImportError:
    DCPManager = None

from ..base_agent import DCPAwareAgent
from ...core.constants import AgentNames, TimeWindows, ObservationTypes, PerformanceSettings

logger = logging.getLogger(__name__)


@dataclass
class ScoutAnalysisResult:
    """Combined result from all Scout analyzers.
    
    Structured for optimal AI consumption with clear relationships
    between different types of intelligence.
    """
    
    # Basic TODO findings
    todo_findings: List[TODOFinding] = field(default_factory=list)
    
    # Deep analysis results
    ast_results: List[AnalysisResult] = field(default_factory=list)
    pattern_results: List[AnalysisResult] = field(default_factory=list)
    
    # Evolution tracking
    persistent_issues: List[IssueEvolution] = field(default_factory=list)
    evolution_report: Optional[Dict[str, Any]] = None
    
    # Research opportunities
    research_queries: List[Any] = field(default_factory=list)
    
    # Aggregate metrics
    total_files_analyzed: int = 0
    total_issues_found: int = 0
    critical_issues: int = 0
    security_issues: int = 0
    
    # Analysis metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    analysis_duration: float = 0.0
    analyzers_used: List[str] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)
    
    # Database persistence tracking
    observations_committed: int = 0
    
    def to_dcp_observations(self) -> List[Dict[str, Any]]:
        """Convert all results to DCP observations for AI coordination."""
        observations = []
        
        # Add summary observation
        observations.append({
            "type": "scout_analysis_summary",
            "timestamp": self.analysis_timestamp.isoformat(),
            "summary": f"Analyzed {self.total_files_analyzed} files, found {self.total_issues_found} issues ({self.critical_issues} critical)",
            "priority": 80 if self.critical_issues > 0 else 50,
            "data": {
                "files_analyzed": self.total_files_analyzed,
                "total_issues": self.total_issues_found,
                "critical_issues": self.critical_issues,
                "security_issues": self.security_issues,
                "persistent_issues": len(self.persistent_issues),
                "research_opportunities": len(self.research_queries)
            },
            "analyzers": self.analyzers_used,
            "duration_seconds": self.analysis_duration
        })
        
        # Add significant findings from each analyzer
        # (Individual analyzers already have to_dcp_observation methods)
        
        return observations


class ScoutAgent(DCPAwareAgent):
    """Enhanced Scout Agent with deep analysis capabilities.
    
    General Staff Role: Chief Intelligence Officer coordinating multiple
    intelligence gathering operations for comprehensive code understanding.
    """
    
    def __init__(self, dcp_manager: Optional[Any] = None, config: Optional[Dict] = None, 
                 dcp_path: Optional[str] = None, project_root: Optional[Path] = None):
        """Initialize Scout Agent with all analyzers.
        
        Args:
            dcp_manager: DCP manager for coordination (shared DCPAdapter)
            config: Configuration options
            dcp_path: Path to DCP file for startup loading
            project_root: Project root path for analysis
        """
        # Initialize DCP-aware base class with shared DCPAdapter
        project_path = str(project_root) if project_root else str(Path.cwd())
        super().__init__(
            project_path=project_path,
            dcp_path=dcp_path,
            dcp_adapter=dcp_manager,  # Pass shared DCPAdapter to prevent database conflicts
            context_window_hours=config.get('context_window_hours', TimeWindows.SCOUT_CONTEXT) if config else TimeWindows.SCOUT_CONTEXT
        )
        
        self.config = config or {}
        self.project_root = Path(project_root) if project_root else Path.cwd()
        
        # Initialize core components
        self.todo_detector = TODODetector()
        self.dcp_integrator = ScoutDCPIntegrator(dcp_manager=self.dcp_manager)
        self.research_generator = ResearchQueryGenerator()
        
        # Initialize enhanced analyzers
        self.python_analyzer = PythonAnalyzer(dcp_path=self._get_dcp_path())
        self.javascript_analyzer = JavaScriptAnalyzer(dcp_path=self._get_dcp_path())
        self.typescript_analyzer = TypeScriptAnalyzer(dcp_path=self._get_dcp_path())
        self.pattern_analyzer = PatternAnalyzer(dcp_path=self._get_dcp_path())
        self.evolution_tracker = EvolutionTracker(dcp_path=self._get_dcp_path())
        
        # Thread safety for concurrent analysis - protects shared result collections
        # from concurrent modification during parallel AST and pattern analysis
        self._analysis_lock = threading.Lock()
        
        # Analysis options (no validation needed for boolean flags)
        self.enable_ast = self.config.get('enable_ast', True)
        self.enable_patterns = self.config.get('enable_patterns', True)
        self.enable_evolution = self.config.get('enable_evolution', True)
        
        # Timeout bounds for dynamic calculation
        self.min_timeout = 5   # Minimum timeout for safety
        self.max_timeout = 300  # Maximum timeout (5 minutes)
        
        # Validate and apply configuration parameters
        self._validate_and_apply_config()
        
        # Context already loaded by base class
    
    def _validate_and_apply_config(self) -> None:
        """Validate and apply configuration parameters with bounds checking."""
        # Validate max_workers (1-16 workers)
        raw_max_workers = self.config.get('max_workers', PerformanceSettings.MAX_WORKERS)
        if not isinstance(raw_max_workers, int) or raw_max_workers < 1:
            logger.warning(f"Invalid max_workers value: {raw_max_workers}, using default: {PerformanceSettings.MAX_WORKERS}")
            self.max_workers = PerformanceSettings.MAX_WORKERS
        elif raw_max_workers > 16:
            logger.warning(f"max_workers too high: {raw_max_workers}, limiting to 16")
            self.max_workers = 16
        else:
            self.max_workers = raw_max_workers
        
        # Validate analysis_timeout (5-300 seconds)
        raw_timeout = self.config.get('analysis_timeout', 30)
        if not isinstance(raw_timeout, (int, float)) or raw_timeout < 5:
            logger.warning(f"Invalid analysis_timeout value: {raw_timeout}, using default: 30")
            self.analysis_timeout = 30
        elif raw_timeout > 300:
            logger.warning(f"analysis_timeout too high: {raw_timeout}, limiting to 300")
            self.analysis_timeout = 300
        else:
            self.analysis_timeout = int(raw_timeout)
        
        # Validate collection limits (must be positive integers)
        collection_limits = {
            'max_todo_findings': 1000,
            'max_ast_results': 500,
            'max_pattern_results': 500,
            'max_observations': 1000,
            'max_files_analyzed': 2000
        }
        
        for param_name, default_value in collection_limits.items():
            raw_value = self.config.get(param_name, default_value)
            if not isinstance(raw_value, int) or raw_value < 1:
                logger.warning(f"Invalid {param_name} value: {raw_value}, using default: {default_value}")
                setattr(self, param_name, default_value)
            elif raw_value > 10000:  # Reasonable upper bound
                logger.warning(f"{param_name} too high: {raw_value}, limiting to 10000")
                setattr(self, param_name, 10000)
            else:
                setattr(self, param_name, raw_value)
    
    @property
    def agent_name(self) -> str:
        """Return the agent's identifier."""
        return AgentNames.SCOUT
    
    @property
    def relevant_observation_types(self) -> List[str]:
        """Define which observation types this agent needs on startup."""
        return [
            'todo', 'code_smell', 'security_issue', 'pattern_match',
            'evolution_report', 'scout_analysis_summary'
        ]
        
    def analyze(self, path: str, deep_analysis: bool = False, 
                analysis_types: Optional[Set[str]] = None) -> ScoutAnalysisResult:
        """Perform comprehensive analysis on a file or directory.
        
        Args:
            path: File or directory to analyze
            deep_analysis: Enable all analyzers (not just TODO detection)
            analysis_types: Specific analysis types to run
            
        Returns:
            ScoutAnalysisResult with comprehensive intelligence
        """
        start_time = datetime.now()
        result = ScoutAnalysisResult()
        
        # Determine which analyzers to use
        if analysis_types:
            use_todo = 'todo' in analysis_types
            use_ast = 'ast' in analysis_types and self.enable_ast
            use_patterns = 'patterns' in analysis_types or 'security' in analysis_types
            use_evolution = 'evolution' in analysis_types and self.enable_evolution
        else:
            use_todo = True
            use_ast = deep_analysis and self.enable_ast
            use_patterns = deep_analysis and self.enable_patterns
            use_evolution = deep_analysis and self.enable_evolution
        
        # Get files to analyze with limits
        files_found = self._get_files_to_analyze(path)
        
        # Limit number of files to prevent memory exhaustion
        if len(files_found) > self.max_files_analyzed:
            logger.warning(f"Found {len(files_found)} files, limiting to {self.max_files_analyzed} for analysis")
            files_to_analyze = files_found[:self.max_files_analyzed]
        else:
            files_to_analyze = files_found
            
        result.total_files_analyzed = len(files_to_analyze)
        
        if not files_to_analyze:
            logger.warning(f"No files found to analyze in {path}")
            return result
        
        # Run analyzers
        if use_todo:
            self._run_todo_analysis(files_to_analyze, result)
            result.analyzers_used.append('todo_detector')
        
        if use_ast or use_patterns:
            self._run_deep_analysis(files_to_analyze, result, use_ast, use_patterns)
            if use_ast:
                result.analyzers_used.append('ast_analyzer')
            if use_patterns:
                result.analyzers_used.append('pattern_analyzer')
        
        if use_evolution:
            self._run_evolution_analysis(result)
            result.analyzers_used.append('evolution_tracker')
        
        # Generate research queries if applicable
        if result.todo_findings:
            researchable = [f for f in result.todo_findings if f.is_researchable]
            if researchable:
                result.research_queries = self.research_generator.generate_queries(researchable)
        
        # Calculate aggregate metrics
        self._calculate_aggregate_metrics(result)
        
        # Record analysis duration
        result.analysis_duration = (datetime.now() - start_time).total_seconds()
        
        # CRITICAL FIX: Direct database storage bypassing staging system
        if result.todo_findings:
            logger.info(f"Storing {len(result.todo_findings)} TODO findings directly to database...")
            try:
                observations = []
                for finding in result.todo_findings:
                    # Convert TODO finding directly to observation format
                    obs = {
                        "type": "todo",
                        "priority": finding.priority_score,
                        "summary": f"{finding.todo_type}: {finding.content}",
                        "confidence": finding.confidence,
                        "data": {
                            "file_path": finding.file_path,
                            "line_number": finding.line_number,
                            "content": finding.content,
                            "todo_type": finding.todo_type,
                            "context_lines": finding.context_lines
                        }
                    }
                    observations.append(obs)
                
                # Store directly through DCP manager
                if self.dcp_manager:
                    with self.dcp_manager.lock():
                        result_data = self.dcp_manager.add_observations(observations, source_agent="scout")
                        committed = result_data.get('succeeded', 0)
                        failed = result_data.get('failed', 0)
                        logger.info(f"Direct storage: {committed} observations stored, {failed} failed")
                        result.observations_committed = committed
                        
                        if failed > 0:
                            for error in result_data.get('errors', []):
                                logger.error(f"Storage error: {error}")
                else:
                    logger.warning("No DCP manager available for direct storage")
                    result.observations_committed = 0
                    
            except Exception as e:
                logger.error(f"Failed direct storage to database: {e}")
                result.observations_committed = 0
        
        return result
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze entire project (compatibility method).
        
        Args:
            project_path: Path to project to analyze
            
        Returns:
            Analysis results dictionary for compatibility
        """
        try:
            # Use the main analyze method with deep analysis
            result = self.analyze(project_path, deep_analysis=True)
            
            # Check if analysis found any files or had errors
            if result.total_files_analyzed == 0 and result.errors:
                # If no files found and there were errors, return error status
                return {
                    "status": "error",
                    "error": "No files found to analyze",
                    "total_files_analyzed": 0,
                    "total_issues_found": 0,
                    "errors": result.errors
                }
            elif result.total_files_analyzed == 0:
                # If no files found but no explicit errors, still indicate issue
                return {
                    "status": "error", 
                    "error": "No accessible files found in specified path",
                    "total_files_analyzed": 0,
                    "total_issues_found": 0
                }
            
            # Convert to dictionary format for compatibility
            return {
                "status": "success",
                "total_files_analyzed": result.total_files_analyzed,
                "total_issues_found": result.total_issues_found,
                "critical_issues": result.critical_issues,
                "security_issues": result.security_issues,
                "todo_findings": len(result.todo_findings),
                "ast_results": len(result.ast_results),
                "pattern_results": len(result.pattern_results),
                "analysis_duration": result.analysis_duration,
                "analyzers_used": result.analyzers_used,
                "errors": result.errors
            }
        except Exception as e:
            logger.error(f"Project analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "total_files_analyzed": 0,
                "total_issues_found": 0
            }
    
    def _run_todo_analysis(self, files: List[Path], result: ScoutAnalysisResult):
        """Run TODO detection on files."""
        logger.info(f"Running TODO analysis on {len(files)} files")
        
        for file_path in files:
            try:
                findings = self.todo_detector.scan_file(str(file_path))
                # Enforce limit on TODO findings to prevent memory exhaustion
                self._enforce_collection_limit(
                    result.todo_findings, findings, self.max_todo_findings, "todo_findings"
                )
            except Exception as e:
                result.errors.append({
                    'analyzer': 'todo_detector',
                    'file': str(file_path),
                    'error': str(e)
                })
    
    def _run_deep_analysis(self, files: List[Path], result: ScoutAnalysisResult,
                          use_ast: bool, use_patterns: bool):
        """Run AST and pattern analysis on files."""
        logger.info(f"Running deep analysis on {len(files)} files")
        
        # Use thread pool for parallel analysis
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit analysis tasks
            futures = []
            
            for file_path in files:
                if use_ast and self._can_analyze_with_ast(file_path):
                    future = executor.submit(self._analyze_with_ast, file_path)
                    futures.append(('ast', file_path, future))
                
                if use_patterns and self.pattern_analyzer.can_analyze(file_path):
                    future = executor.submit(self._analyze_with_patterns, file_path)
                    futures.append(('pattern', file_path, future))
            
            # Collect results with thread safety
            for analyzer_type, file_path, future in futures:
                try:
                    # Use dynamic timeout based on file characteristics
                    timeout = self._calculate_analysis_timeout(file_path)
                    analysis_result = future.result(timeout=timeout)
                    # Use lock to protect shared result collections from concurrent modification
                    with self._analysis_lock:
                        if analyzer_type == 'ast':
                            # Enforce limit on AST results
                            if len(result.ast_results) < self.max_ast_results:
                                result.ast_results.append(analysis_result)
                            else:
                                logger.warning(f"AST results at capacity ({self.max_ast_results}), dropping result for {file_path}")
                        else:
                            # Enforce limit on pattern results
                            if len(result.pattern_results) < self.max_pattern_results:
                                result.pattern_results.append(analysis_result)  
                            else:
                                logger.warning(f"Pattern results at capacity ({self.max_pattern_results}), dropping result for {file_path}")
                except Exception as e:
                    # Protect error collection as well
                    with self._analysis_lock:
                        result.errors.append({
                            'analyzer': analyzer_type,
                            'file': str(file_path),
                            'error': str(e)
                        })
    
    def _can_analyze_with_ast(self, file_path: Path) -> bool:
        """Check if file can be analyzed with AST analyzer."""
        return (self.python_analyzer.can_analyze(file_path) or
                self.javascript_analyzer.can_analyze(file_path) or
                self.typescript_analyzer.can_analyze(file_path))
    
    def _analyze_with_ast(self, file_path: Path) -> AnalysisResult:
        """Analyze file with appropriate AST analyzer based on language."""
        # Determine which analyzer to use based on file extension
        ext = file_path.suffix.lower()
        
        if ext == '.py':
            return self.python_analyzer.analyze(file_path)
        elif ext in ['.js', '.jsx', '.mjs', '.cjs']:
            return self.javascript_analyzer.analyze(file_path)
        elif ext in ['.ts', '.tsx']:
            return self.typescript_analyzer.analyze(file_path)
        else:
            # Fallback to Python analyzer (shouldn't happen due to can_analyze check)
            logger.warning(f"No AST analyzer for {ext}, using Python analyzer")
            return self.python_analyzer.analyze(file_path)
    
    def _analyze_with_patterns(self, file_path: Path) -> AnalysisResult:
        """Analyze file with pattern analyzer."""
        return self.pattern_analyzer.analyze(file_path)
    
    def _run_evolution_analysis(self, result: ScoutAnalysisResult):
        """Track issue evolution over time."""
        logger.info("Running evolution analysis")
        
        try:
            # Collect all issues from different sources
            all_issues = []
            
            # Convert TODO findings to issues
            for finding in result.todo_findings:
                issue = CodeIssue(
                    issue_type='todo_comment' if finding.todo_type == 'TODO' else 'fixme_comment',
                    severity='low' if finding.priority_score < 50 else 'medium',
                    file_path=finding.file_path,
                    line_number=finding.line_number,
                    entity_name=f"line_{finding.line_number}",
                    description=finding.content,
                    ai_recommendation="Address or remove if obsolete",
                    fix_complexity='varies'
                )
                all_issues.append(issue)
            
            # Add AST-detected issues
            for ast_result in result.ast_results:
                all_issues.extend(ast_result.issues)
            
            # Add pattern-detected issues
            for pattern_result in result.pattern_results:
                all_issues.extend(pattern_result.issues)
            
            # Track all issues
            if all_issues:
                self.evolution_tracker.track_issues(all_issues)
            
            # Get persistent issues
            result.persistent_issues = self.evolution_tracker.get_persistent_issues(
                min_days=14, min_sprints=2
            )
            
            # Get evolution report
            result.evolution_report = self.evolution_tracker.get_evolution_report()
            
        except Exception as e:
            result.errors.append({
                'analyzer': 'evolution_tracker',
                'error': str(e)
            })
    
    def _calculate_aggregate_metrics(self, result: ScoutAnalysisResult):
        """Calculate aggregate metrics across all analyzers."""
        # Count total issues
        result.total_issues_found = len(result.todo_findings)
        
        # Add issues from AST analysis
        for ast_result in result.ast_results:
            result.total_issues_found += len(ast_result.issues)
            result.critical_issues += sum(1 for i in ast_result.issues if i.severity == 'critical')
        
        # Add issues from pattern analysis
        for pattern_result in result.pattern_results:
            result.total_issues_found += len(pattern_result.issues)
            result.critical_issues += sum(1 for i in pattern_result.issues if i.severity == 'critical')
            # Count security issues
            result.security_issues += sum(
                1 for i in pattern_result.issues 
                if i.metadata.get('pattern_type') == 'security'
            )
    
    def _get_files_to_analyze(self, path: str) -> List[Path]:
        """Get list of files to analyze."""
        path_obj = Path(path).resolve()
        
        # Security: Ensure path is within project root (use configured project_root, not cwd)
        try:
            project_root = self.project_root.resolve()
            path_obj.relative_to(project_root)
        except ValueError:
            logger.warning(f"Path {path} is outside project root {self.project_root}")
            return []
        
        if path_obj.is_file():
            return [path_obj]
        elif path_obj.is_dir():
            # Get all supported files
            files = []
            for ext in self.todo_detector.supported_extensions:
                files.extend(path_obj.rglob(f"*{ext}"))
            
            # Filter out excluded directories
            excluded_dirs = {
                'node_modules', '.git', '__pycache__', '.pytest_cache',
                'build', 'dist', '.venv', 'venv', 'htmlcov'
            }
            
            filtered_files = []
            for f in files:
                if not any(excluded in f.parts for excluded in excluded_dirs):
                    filtered_files.append(f)
            
            return filtered_files
        else:
            return []
    
    def _create_dcp_manager(self, dcp_path: Optional[str] = None):
        """Create DCP manager if available."""
        if DCPManager:
            try:
                return DCPAdapter(dcp_path=dcp_path)
            except Exception as e:
                logger.warning(f"Failed to create DCP manager: {e}")
        return None
    
    def _get_dcp_path(self) -> Optional[str]:
        """Get DCP path from manager."""
        if self.dcp_manager and hasattr(self.dcp_manager, 'dcp_path'):
            return self.dcp_manager.dcp_path
        return None
    
    def _enforce_collection_limit(self, collection: List, new_items: List, max_size: int, collection_name: str) -> int:
        """Enforce size limits on result collections with graceful truncation.
        
        Args:
            collection: The list to add items to
            new_items: Items to add
            max_size: Maximum allowed size
            collection_name: Name for logging
            
        Returns:
            Number of items actually added
        """
        if not new_items:
            return 0
            
        current_size = len(collection)
        available_space = max_size - current_size
        
        if available_space <= 0:
            logger.warning(f"Collection {collection_name} at capacity ({max_size}), dropping {len(new_items)} new items")
            return 0
        
        if len(new_items) > available_space:
            items_to_add = new_items[:available_space]
            dropped_count = len(new_items) - available_space
            logger.warning(f"Collection {collection_name} near capacity, adding {len(items_to_add)} items, dropping {dropped_count}")
            collection.extend(items_to_add)
            return len(items_to_add)
        else:
            collection.extend(new_items)
            return len(new_items)
    
    def _calculate_analysis_timeout(self, file_path: Path) -> int:
        """Calculate dynamic timeout based on file characteristics.
        
        Args:
            file_path: Path to file being analyzed
            
        Returns:
            Timeout in seconds, bounded by min/max limits
        """
        try:
            # Base timeout from configuration
            timeout = self.analysis_timeout
            
            # Adjust based on file size (rough heuristic)
            file_size = file_path.stat().st_size
            if file_size > 100000:  # > 100KB
                # Use ceiling division to ensure minimum 1 second increment for large files
                # This ensures files between 100-149KB get at least 1 additional second
                extra_bytes = file_size - 100000
                extra_seconds = math.ceil(extra_bytes / 50000)
                timeout += extra_seconds
            
            # Enforce bounds
            timeout = max(self.min_timeout, min(timeout, self.max_timeout))
            
            return timeout
        except Exception:
            # If we can't get file stats, use default timeout
            return self.analysis_timeout
    
    def _process_startup_context(self, context: Dict[str, List[Dict[str, Any]]]) -> None:
        """Process loaded context from base class.
        
        Args:
            context: Dict mapping observation types to lists of observations
        """
        # Extract TODO history
        todo_history = context.get('todo', [])
        if todo_history:
            logger.info(f"Scout loaded {len(todo_history)} previous TODO observations")
            # Could use this to track TODO resolution patterns
        
        # Extract security issues
        security_history = context.get('security_issue', [])
        if security_history:
            logger.info(f"Scout loaded {len(security_history)} security observations")
            # Feed to pattern analyzer for known vulnerabilities
        
        # Extract previous analysis summaries
        summaries = context.get('scout_analysis_summary', [])
        if summaries:
            logger.info(f"Scout loaded {len(summaries)} previous analysis summaries")
            # Use for tracking trends
        
        self._previous_boot = 'hot'  # Mark as hot boot since we loaded context
        
        # Initialize timing and cold start detection for startup metrics
        startup_start_time = time.time()
        is_cold_start = not hasattr(self, '_previous_boot') or self._previous_boot is None
        
        try:
            if not self.dcp_manager:
                logger.debug("DCP manager not available, using cold boot")
                self._cold_boot_initialization()
                return
            
            # Read TODO analysis observations
            todo_observations = self.dcp_manager.get_observations_by_type(
                "todo_analysis", limit=50
            )
            
            # Read code pattern observations
            pattern_observations = self.dcp_manager.get_observations_by_type(
                "code_pattern", limit=100
            )
            
            # Read security observations
            security_observations = self.dcp_manager.get_observations_by_type(
                "security", limit=30
            )
            
            # Read AST analysis observations
            ast_observations = self.dcp_manager.get_observations_by_type(
                "ast_analysis", limit=50
            )
            
            # Rebuild pattern cache from DCP
            self._rebuild_pattern_cache(pattern_observations)
            
            # Initialize analyzers with known patterns
            self._initialize_analyzers_from_context(todo_observations, security_observations, ast_observations)
            
            # Record startup metrics
            total_observations = (len(todo_observations) + len(pattern_observations) + 
                                len(security_observations) + len(ast_observations))
            
            if self.dcp_manager:
                self.dcp_manager.add_observation({
                    'type': 'startup_time',
                    'agent': 'scout',
                    'duration_ms': (time.time() - startup_start_time) * 1000,
                    'is_cold_start': is_cold_start,
                    'observations_loaded': total_observations,
                    'context_categories': ['todo_analysis', 'code_pattern', 'security', 'ast_analysis'],
                    'analyzers_initialized': len(self._get_active_analyzers())
                }, source_agent='scout')
                
            logger.info(f"Scout agent loaded context: {len(todo_observations)} TODO observations, "
                       f"{len(pattern_observations)} patterns, {len(security_observations)} security observations")
            
        except Exception as e:
            # Fallback to cold boot mode
            logger.warning(f"DCP context load failed, using cold boot: {e}")
            if self.dcp_manager:
                self.dcp_manager.add_observation({
                    'type': 'dcp_failure',
                    'agent': 'scout',
                    'reason': str(e),
                    'recovery_action': 'cold_boot'
                }, source_agent='scout')
            self._cold_boot_initialization()
    
    def _rebuild_pattern_cache(self, pattern_observations: List[Dict]):
        """Rebuild pattern cache from DCP observations."""
        if not pattern_observations:
            return
            
        # Extract patterns from observations
        known_patterns = []
        for obs in pattern_observations:
            if 'details' in obs and 'pattern_type' in obs['details']:
                pattern_data = obs['details']
                # Convert to PatternDefinition if we have enough data
                if 'severity' in pattern_data and 'description' in pattern_data:
                    pattern = PatternDefinition(
                        name=pattern_data.get('pattern_name', 'unknown'),
                        description=pattern_data['description'],
                        severity=pattern_data['severity'],
                        pattern_type=pattern_data['pattern_type'],
                        file_types=pattern_data.get('file_types', []),
                        regex_pattern=pattern_data.get('regex_pattern', ''),
                        ast_checks=pattern_data.get('ast_checks', [])
                    )
                    known_patterns.append(pattern)
        
        # Update pattern analyzer with known patterns
        if known_patterns and hasattr(self.pattern_analyzer, 'add_known_patterns'):
            self.pattern_analyzer.add_known_patterns(known_patterns)
            logger.debug(f"Rebuilt pattern cache with {len(known_patterns)} patterns")
    
    def _initialize_analyzers_from_context(self, todo_obs: List[Dict], 
                                         security_obs: List[Dict], ast_obs: List[Dict]):
        """Initialize analyzers with context from previous analyses."""
        # Update TODO detector with known TODO patterns
        if todo_obs:
            # Extract TODO types and priorities from previous analyses
            todo_types = set()
            for obs in todo_obs[-10:]:  # Last 10 TODO analyses
                if 'details' in obs and 'todo_type' in obs['details']:
                    todo_types.add(obs['details']['todo_type'])
            
            # Update TODO detector patterns if possible
            if hasattr(self.todo_detector, 'update_patterns'):
                self.todo_detector.update_patterns(list(todo_types))
        
        # Configure analyzers based on previous security findings
        if security_obs:
            # Enable security-focused analysis
            self.enable_patterns = True
            if hasattr(self.pattern_analyzer, 'enable_security_patterns'):
                self.pattern_analyzer.enable_security_patterns()
        
        # Configure AST analyzers based on previous findings
        if ast_obs:
            # Adjust analysis depth based on previous complexity
            complexity_scores = []
            for obs in ast_obs[-5:]:  # Last 5 AST analyses
                if 'details' in obs and 'complexity_score' in obs['details']:
                    complexity_scores.append(obs['details']['complexity_score'])
            
            if complexity_scores:
                avg_complexity = sum(complexity_scores) / len(complexity_scores)
                # Adjust max_workers based on complexity
                if avg_complexity > 80:  # High complexity
                    self.max_workers = min(self.max_workers, 2)  # Reduce parallelism
        
        # Track previous boot for hot start detection
        self._previous_boot = time.time()
    
    def _cold_boot_initialization(self):
        """Initialize agent without DCP context (fallback mode)."""
        logger.info("Scout agent starting in cold boot mode")
        # Set conservative defaults
        self.max_workers = min(self.max_workers, 2)  # Conservative parallelism
        self._previous_boot = None
        # Enable all analysis types for comprehensive first scan
        self.enable_ast = True
        self.enable_patterns = True
        self.enable_evolution = True
    
    def _get_active_analyzers(self) -> List[str]:
        """Get list of active analyzer names."""
        analyzers = ['todo_detector']
        if self.enable_ast:
            analyzers.extend(['python_analyzer', 'javascript_analyzer', 'typescript_analyzer'])
        if self.enable_patterns:
            analyzers.append('pattern_analyzer')
        if self.enable_evolution:
            analyzers.append('evolution_tracker')
        return analyzers
    
    def stage_findings(self, analysis_result: ScoutAnalysisResult) -> Dict[str, int]:
        """Stage findings from analysis for review and commit.
        
        Args:
            analysis_result: Results from analyze()
            
        Returns:
            Staging statistics
        """
        # Stage TODO findings
        todo_stats = self.dcp_integrator.stage_findings(analysis_result.todo_findings)
        
        # TODO: Also stage significant issues from other analyzers
        # This would require extending the staging system to handle CodeIssue objects
        
        return todo_stats
    
    def get_cli_flags(self) -> List[Tuple[str, str]]:
        """Get CLI flags for enhanced Scout functionality.
        
        Returns:
            List of (flag, description) tuples
        """
        return [
            ('--deep-analysis', 'Enable all analyzers (AST, patterns, evolution)'),
            ('--ast', 'Enable AST analysis for code structure'),
            ('--patterns', 'Enable pattern analysis for code smells'),
            ('--security', 'Enable security pattern detection'),
            ('--evolution', 'Track issue evolution over time'),
            ('--analysis-types', 'Comma-separated list of analysis types'),
            ('--max-workers', 'Maximum parallel analysis workers (default: 4)')
        ]
    
    def _cleanup(self) -> None:
        """Clean up Scout agent resources."""
        # Clean up analyzers - call cleanup on each individual analyzer
        analyzers_to_cleanup = [
            self.todo_detector,
            self.dcp_integrator,
            self.research_generator,
            self.python_analyzer,
            self.javascript_analyzer,
            self.typescript_analyzer,
            self.pattern_analyzer,
            self.evolution_tracker
        ]
        
        for analyzer in analyzers_to_cleanup:
            if hasattr(analyzer, 'cleanup'):
                try:
                    analyzer.cleanup()
                except Exception as e:
                    logger.warning(f"Failed to cleanup {analyzer.__class__.__name__}: {e}")
        
        # Clean up any temporary files
        logger.debug("Scout agent cleanup completed")


# Backward compatibility functions
def create_scout_agent(dcp_manager=None, **kwargs) -> ScoutAgent:
    """Factory function to create Scout Agent.
    
    Args:
        dcp_manager: Optional DCP manager
        **kwargs: Additional configuration
        
    Returns:
        Configured ScoutAgent instance
    """
    config = kwargs
    return ScoutAgent(dcp_manager=dcp_manager, config=config)


def run_scout_analysis(path: str, deep: bool = False) -> ScoutAnalysisResult:
    """Quick function to run Scout analysis.
    
    Args:
        path: Path to analyze  
        deep: Enable deep analysis
        
    Returns:
        Analysis results
    """
    agent = ScoutAgent()
    return agent.analyze(path, deep_analysis=deep)