"""
Context Manager for Copper Sun Brass Pro - Handles generation and updates of context files.

This module manages the .brass/ context files that provide persistent memory
and insights across Claude Code sessions.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import re
import logging

# Import best practices engine for testing compatibility
from coppersun_brass.core.best_practices_recommendations import BestPracticesRecommendationEngine

logger = logging.getLogger(__name__)


class ContextManager:
    """Manages Copper Sun Brass context files for persistent memory."""
    
    def __init__(self, project_root: Path = Path.cwd()):
        self.project_root = project_root
        self.brass_dir = project_root / ".brass"
        self.config_file = self.brass_dir / "config.json"
        
        # Context file paths
        self.status_file = self.brass_dir / "STATUS.md"
        self.context_file = self.brass_dir / "CONTEXT.md"
        self.insights_file = self.brass_dir / "INSIGHTS.md"
        self.history_file = self.brass_dir / "HISTORY.md"
        
        # Load configuration
        self.config = self._load_config()
        
        # Best practices now handled directly in OutputGenerator
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Copper Sun Brass configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
                logger.warning(f"Failed to load config from {self.config_file}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error loading config: {e}")
        return {"user_preferences": {}}
    
    def update_status(self, force: bool = False):
        """Update the STATUS.md file with current project status."""
        # Ensure directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        content = ["# Copper Sun Brass Status", ""]
        
        # Active status
        content.append("## 🎺 Copper Sun Brass Active")
        content.append(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        
        # Project information
        content.append("## 📊 Project Overview")
        
        # Count files by type
        file_stats = self._get_file_statistics()
        if file_stats:
            content.append("### File Statistics")
            for ext, count in sorted(file_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                content.append(f"- {ext}: {count} files")
            content.append("")
        
        # Git status if available
        git_info = self._get_git_info()
        if git_info:
            content.append("### Git Status")
            content.append(f"- Branch: {git_info.get('branch', 'unknown')}")
            content.append(f"- Modified files: {git_info.get('modified', 0)}")
            content.append(f"- Untracked files: {git_info.get('untracked', 0)}")
            content.append("")
        
        # Recent activity
        content.append("## 📈 Recent Activity")
        content.append("- Context files are being maintained")
        content.append("- Ready to track development progress")
        content.append("")
        
        # Write status file
        with open(self.status_file, 'w') as f:
            f.write('\n'.join(content))
    
    def update_context(self, current_work: Optional[str] = None):
        """Update the CONTEXT.md file with current work context."""
        # Ensure directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        content = ["# Current Work Context", ""]
        content.append(f"*Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        content.append("")
        
        if current_work:
            content.append("## 🎯 Current Focus")
            content.append(current_work)
            content.append("")
        
        # Add project structure insight
        content.append("## 📁 Key Project Areas")
        key_dirs = self._identify_key_directories()
        for dir_path, description in key_dirs.items():
            content.append(f"- **{dir_path}**: {description}")
        content.append("")
        
        # Add technology stack
        tech_stack = self._identify_tech_stack()
        if tech_stack:
            content.append("## 🛠️ Technology Stack")
            for tech, details in tech_stack.items():
                content.append(f"- **{tech}**: {details}")
            content.append("")
        
        # Configuration reminders
        prefs = self.config.get("user_preferences", {})
        theme = prefs.get("visual_theme", "colorful")
        verbosity = prefs.get("verbosity", "balanced")
        
        content.append("## ⚙️ Copper Sun Brass Configuration")
        content.append(f"- Visual theme: {theme}")
        content.append(f"- Verbosity: {verbosity}")
        content.append("")
        
        # Write context file
        with open(self.context_file, 'w') as f:
            f.write('\n'.join(content))
    
    def generate_insights(self):
        """Generate insights based on project analysis."""
        # Ensure directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        content = ["# Copper Sun Brass Insights", ""]
        content.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        content.append("")
        
        insights = []
        
        # Check for common patterns and issues
        patterns = self._analyze_patterns()
        if patterns:
            content.append("## 💡 Detected Patterns")
            for pattern in patterns:
                content.append(f"- {pattern}")
            content.append("")
        
        # Security insights
        security_issues = self._check_security_patterns()
        if security_issues:
            content.append("## 🔒 Security Considerations")
            for issue in security_issues:
                content.append(f"- ⚠️ {issue}")
            content.append("")
        
        # Performance insights
        perf_suggestions = self._analyze_performance_patterns()
        if perf_suggestions:
            content.append("## ⚡ Performance Suggestions")
            for suggestion in perf_suggestions:
                content.append(f"- {suggestion}")
            content.append("")
        
        # Best practices - now handled directly in OutputGenerator
        try:
            from coppersun_brass.core.best_practices_recommendations import BestPracticesRecommendationEngine
            best_practices_engine = BestPracticesRecommendationEngine(project_path=self.project_root)
            
            # Quick analysis for context generation
            analysis = best_practices_engine.analyze_project()
            recommendations = best_practices_engine.generate_recommendations(analysis, limit=3)
            formatted_recs = best_practices_engine.format_recommendations_for_output(recommendations)
            
            if formatted_recs:
                content.append("## 🎯 Best Practices")
                for rec in formatted_recs:
                    content.append(f"- {rec}")
                content.append("")
        except Exception as e:
            logger.warning(f"Best practices generation failed: {e}")
            # Fallback to simple recommendations
            content.append("## 🎯 Best Practices")
            content.append("- Follow security best practices for your technology stack")
            content.append("- Maintain comprehensive test coverage")
            content.append("- Use consistent code formatting and documentation")
            content.append("")
        
        # Write insights file
        with open(self.insights_file, 'w') as f:
            f.write('\n'.join(content))
    
    # Best practices now handled directly in OutputGenerator - old method removed
    
    # Mock observations method removed - no longer needed with new implementation
    
    def add_to_history(self, event: str, details: Optional[Dict[str, Any]] = None):
        """Add an event to the project history."""
        # Ensure directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        # Read existing history
        history_entries = []
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                content = f.read()
                # Parse existing entries (simple format for now)
                if "## Timeline" in content:
                    history_entries = content.split("## Timeline")[1].strip().split('\n')
                    history_entries = [e for e in history_entries if e.strip()]
        
        # Add new entry
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f"- **{timestamp}**: {event}"
        if details:
            for key, value in details.items():
                new_entry += f"\n  - {key}: {value}"
        
        history_entries.append(new_entry)
        
        # Keep last 50 entries
        if len(history_entries) > 50:
            history_entries = history_entries[-50:]
        
        # Write updated history
        content = ["# Project History", ""]
        content.append("*Copper Sun Brass tracks important events and decisions*")
        content.append("")
        content.append("## Timeline")
        content.extend(history_entries)
        content.append("")
        
        with open(self.history_file, 'w') as f:
            f.write('\n'.join(content))
    
    def _get_file_statistics(self, max_files: int = 10000) -> Dict[str, int]:
        """Get statistics about files in the project with safety limits.
        
        Args:
            max_files: Maximum number of files to process to prevent memory exhaustion
        """
        stats = {}
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.brass', 'venv', '.venv'}
        file_count = 0
        
        try:
            for root, dirs, files in os.walk(self.project_root):
                # Remove ignored directories
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                
                for file in files:
                    if file_count >= max_files:
                        logger.warning(f"File scan limit reached ({max_files}), stopping traversal for safety")
                        return stats
                    
                    ext = Path(file).suffix.lower() or 'no extension'
                    stats[ext] = stats.get(ext, 0) + 1
                    file_count += 1
        except (PermissionError, OSError) as e:
            logger.warning(f"File traversal error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during file statistics: {e}")
        
        return stats
    
    def _get_git_info(self) -> Optional[Dict[str, Any]]:
        """Get git repository information."""
        try:
            # Check if it's a git repo
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return None
            
            info = {}
            
            # Get current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            info['branch'] = result.stdout.strip() if result.returncode == 0 else 'unknown'
            
            # Get status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                info['modified'] = sum(1 for line in lines if line.startswith(' M') or line.startswith('M'))
                info['untracked'] = sum(1 for line in lines if line.startswith('??'))
            
            return info
        except (subprocess.SubprocessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.debug(f"Git operation failed: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error getting git info: {e}")
            return None
    
    def _identify_key_directories(self) -> Dict[str, str]:
        """Identify key directories in the project."""
        key_dirs = {}
        
        # Common directory patterns
        patterns = {
            'src': 'Source code',
            'tests': 'Test files',
            'docs': 'Documentation',
            'scripts': 'Utility scripts',
            'config': 'Configuration files',
            'coppersun_brass': 'Copper Sun Brass core system',
            'examples': 'Example code',
            'templates': 'Template files'
        }
        
        for dir_name, description in patterns.items():
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                key_dirs[dir_name] = description
        
        return key_dirs
    
    def _identify_tech_stack(self) -> Dict[str, str]:
        """Identify the technology stack used in the project."""
        tech_stack = {}
        
        # Check for common config files
        checks = {
            'package.json': ('Node.js', 'JavaScript/TypeScript project'),
            'requirements.txt': ('Python', 'Python dependencies'),
            'pyproject.toml': ('Python', 'Modern Python project'),
            'Cargo.toml': ('Rust', 'Rust project'),
            'go.mod': ('Go', 'Go modules'),
            'pom.xml': ('Java', 'Maven project'),
            'build.gradle': ('Java', 'Gradle project'),
            'Gemfile': ('Ruby', 'Ruby project'),
            'composer.json': ('PHP', 'PHP Composer project')
        }
        
        for filename, (tech, description) in checks.items():
            if (self.project_root / filename).exists():
                tech_stack[tech] = description
        
        return tech_stack
    
    def _safe_is_file(self, path) -> bool:
        """Safely check if path is file, handling permission errors."""
        try:
            return path.is_file()
        except (PermissionError, OSError):
            return False
    
    def _has_test_files(self, max_files_check: int = 1000) -> bool:
        """Check for test files with bounded search."""
        files_checked = 0
        
        # Check for dedicated test directory first (fastest)
        if (self.project_root / 'tests').exists():
            return True
        
        # Bounded search for test files
        try:
            for file_path in self.project_root.rglob('*'):
                if files_checked >= max_files_check:
                    logger.debug(f"Test file search limit reached ({max_files_check})")
                    break
                    
                if (file_path.name.startswith('test_') and file_path.suffix == '.py') or \
                   (file_path.suffix == '.js' and file_path.name.endswith('.test.js')):
                    return True
                    
                files_checked += 1
        except Exception as e:
            logger.debug(f"Error during test file discovery: {e}")
        
        return False
    
    def _analyze_patterns(self) -> List[str]:
        """Analyze project for common patterns."""
        patterns = []
        
        # Check project size (with permission error handling and safety limits)
        file_count = 0
        max_scan_files = 50000  # Limit for safety
        try:
            for i, path in enumerate(self.project_root.rglob('*')):
                if i >= max_scan_files:
                    logger.warning(f"Project scan limit reached ({max_scan_files}), pattern analysis may be incomplete")
                    break
                if self._safe_is_file(path):
                    file_count += 1
        except (PermissionError, OSError):
            file_count = 0  # Fall back to 0 if scanning fails
        except Exception as e:
            logger.warning(f"Error during pattern analysis file counting: {e}")
            file_count = 0
        if file_count > 1000:
            patterns.append("Large project detected - consider modularization")
        elif file_count < 10:
            patterns.append("Small project - good time to establish structure")
        
        # Check for test coverage with bounded search
        has_tests = self._has_test_files()
        
        if not has_tests:
            patterns.append("No test files detected - consider adding tests")
        
        # Check for documentation
        has_docs = (self.project_root / 'README.md').exists() or \
                  (self.project_root / 'docs').exists()
        
        if not has_docs:
            patterns.append("Limited documentation found - consider adding README.md")
        
        return patterns
    
    def _check_security_patterns(self) -> List[str]:
        """Check for security issues from Scout analysis."""
        issues = []
        
        # First, try to read from YAML analysis report (replaces analysis_report.json)
        yaml_report_path = self.brass_dir / 'brass_analysis.yaml'
        if yaml_report_path.exists():
            return self._parse_yaml_security_analysis(yaml_report_path)
        
        # Fallback: Check for common sensitive file patterns
        issues = []
        sensitive_patterns = [
            '*.pem', '*.key', '*.env', '.env.*', 'secrets.*', '*_secret*'
        ]
        
        for pattern in sensitive_patterns:
            # Use iterator with limit to prevent memory exhaustion
            matches = []
            match_count = 0
            max_matches = 100  # Limit matches for safety
            
            try:
                for match in self.project_root.rglob(pattern):
                    if match_count >= max_matches:
                        logger.debug(f"Sensitive file scan limit reached ({max_matches}) for pattern {pattern}")
                        break
                    matches.append(match)
                    match_count += 1
            except Exception as e:
                logger.debug(f"Error scanning for pattern {pattern}: {e}")
                continue
            if matches:
                gitignore_path = self.project_root / '.gitignore'
                if gitignore_path.exists():
                    with open(gitignore_path, 'r') as f:
                        gitignore_content = f.read()
                    
                    for match in matches:
                        relative_path = match.relative_to(self.project_root)
                        if str(relative_path) not in gitignore_content:
                            issues.append(f"Sensitive file '{relative_path}' may not be in .gitignore")
        
        return issues[:5]  # Limit to 5 issues
    
    def _parse_yaml_security_analysis(self, yaml_report_path: Path) -> List[str]:
        """Parse YAML security analysis with robust error handling."""
        issues = []
        
        # Try to import yaml module
        try:
            import yaml
        except ImportError:
            logger.debug("YAML module not available, using fallback security analysis")
            return self._fallback_security_analysis()
        
        # Parse YAML file with comprehensive error handling
        try:
            with open(yaml_report_path, 'r') as f:
                analysis_data = yaml.safe_load(f)
                
            # Validate data structure
            if not isinstance(analysis_data, dict):
                logger.warning("Invalid YAML structure in analysis file")
                return self._fallback_security_analysis()
                
            # Extract critical security issues from YAML structure
            security_summary = analysis_data.get('security_summary', {})
            if not isinstance(security_summary, dict):
                logger.debug("Security summary section missing or invalid in YAML")
                return self._fallback_security_analysis()
                
            severity_dist = security_summary.get('severity_distribution', {})
            
            if severity_dist.get('critical', 0) > 0:
                critical_count = severity_dist['critical']
                issues.append(f"🔒 CRITICAL: {critical_count} critical security issues found")
            
            if severity_dist.get('high', 0) > 0:
                high_count = severity_dist['high']
                issues.append(f"⚠️ HIGH: {high_count} high-severity security issues")
            
            # Extract top categories if available
            top_categories = security_summary.get('top_categories', [])
            if isinstance(top_categories, list):
                for category in top_categories[:3]:
                    if isinstance(category, dict):
                        cat_name = category.get('category', 'Unknown')
                        cat_count = category.get('count', 0)
                        if cat_count > 0:
                            issues.append(f"🔍 {cat_name}: {cat_count} instances")
            
            if issues:
                return issues[:5]  # Limit to 5 most important issues
                
        except yaml.YAMLError as e:
            logger.warning(f"YAML parsing error in security analysis: {e}")
            return self._fallback_security_analysis()
        except (FileNotFoundError, PermissionError) as e:
            logger.debug(f"Cannot access YAML analysis file: {e}")
            return self._fallback_security_analysis()
        except Exception as e:
            logger.error(f"Unexpected error parsing YAML security analysis: {e}")
            return self._fallback_security_analysis()
            
        return self._fallback_security_analysis()
    
    def _fallback_security_analysis(self) -> List[str]:
        """Fallback security analysis when YAML parsing fails."""
    
    def _analyze_performance_patterns(self) -> List[str]:
        """Analyze for potential performance improvements."""
        suggestions = []
        
        # Check for large files (with safety limits)
        large_files = []
        files_checked = 0
        max_files_check = 5000  # Limit file checks for performance
        
        try:
            for file_path in self.project_root.rglob('*'):
                if files_checked >= max_files_check:
                    logger.debug(f"Large file check limit reached ({max_files_check}), analysis may be incomplete")
                    break
                    
                try:
                    if file_path.is_file() and file_path.stat().st_size > 1_000_000:  # 1MB
                        large_files.append(file_path)
                except (PermissionError, OSError):
                    # Skip files we can't access
                    pass
                    
                files_checked += 1
        except Exception as e:
            logger.warning(f"Error during large file analysis: {e}")
        
        if large_files:
            suggestions.append(f"Found {len(large_files)} files over 1MB - consider optimization")
        
        # Check for common performance patterns in Python files (with optimization)
        found_import_star = False
        files_checked = 0
        max_py_files_check = 20  # Increased slightly but still bounded
        
        try:
            for py_file in self.project_root.rglob('*.py'):
                if files_checked >= max_py_files_check or found_import_star:
                    break
                    
                try:
                    with open(py_file, 'r') as f:
                        # Read only first 2KB to check for import patterns efficiently
                        chunk = f.read(2048)
                        if 'import *' in chunk:
                            suggestions.append("Avoid 'import *' for better performance")
                            found_import_star = True
                            break
                except (PermissionError, OSError):
                    # Skip files we can't access
                    pass
                except UnicodeDecodeError as e:
                    logger.debug(f"Encoding error in file {py_file}: {e}")
                    pass
                except Exception as e:
                    logger.debug(f"Unexpected error reading file {py_file}: {type(e).__name__}: {e}")
                    pass
                    
                files_checked += 1
        except Exception as e:
            logger.debug(f"Error during Python file analysis: {e}")
        
        return suggestions[:5]  # Limit suggestions