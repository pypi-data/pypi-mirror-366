"""
TODO YAML Generator

YAML variant of TODO JSON generator that creates .brass/todos.yaml
with structured data optimized for AI consumption while preserving all TODO intelligence.

Key Features:
- Structured YAML format for direct programmatic access
- Location-based consolidation to prevent duplicate entries
- Type-safe data (native integers, floats, booleans, arrays)  
- AI-optimized schema with consistent data access patterns
- Inherits data collection logic from existing TODO system

Follows the exact same proven pattern as PrivacyYamlGenerator.
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class TodoYamlGenerator:
    """
    YAML variant of TODO generator for AI consumption.
    
    Creates structured YAML format optimized for programmatic access by AI agents.
    
    Follows evidence-based consolidation patterns from OutputGenerator
    to prevent duplicate entries and group similar issues by location.
    """
    
    def __init__(self, project_path: str, storage):
        """
        Initialize YAML TODO generator.
        
        Args:
            project_path: Root path of project to analyze
            storage: BrassStorage instance for data access
        """
        self.project_path = Path(project_path)
        self.storage = storage
        self.brass_dir = self.project_path / '.brass'
        self.yaml_output_path = self.brass_dir / 'todos.yaml'
        self.json_fallback_path = self.brass_dir / 'todos.json'
        
        # Pre-compile pattern sets for optimized category detection
        self._init_pattern_sets()
        
        logger.info(f"YAML TODO generator initialized for project: {self.project_path}")
    
    def _init_pattern_sets(self):
        """
        Initialize optimized pattern sets for fast category detection.
        
        Converts pattern lists to sets for O(1) average case lookup performance
        instead of O(n) linear search through patterns.
        """
        # Security-related keywords
        self.security_patterns_set = {
            'password', 'credential', 'auth', 'encrypt', 'decrypt', 'hash', 'salt',
            'security', 'vulnerable', 'vulnerability', 'xss', 'sql injection', 
            'sanitiz', 'validat', 'permission', 'access control'
        }
        
        # Performance-related keywords  
        self.performance_patterns_set = {
            'performance', 'slow', 'optimize', 'cache', 'memory', 'speed', 'efficient',
            'oom', 'timeout', 'bottleneck', 'scale', 'load', 'concurrent', 'async',
            'batch', 'pagina', 'index', 'query optimization'
        }
        
        # Bug/Error handling keywords
        self.bug_patterns_set = {
            'crash', 'error', 'exception', 'fail', 'bug', 'fix', 'broken', 'issue',
            'null', 'none', 'keyerror', 'indexerror', 'typeerror', 'handling',
            'validate', 'check', 'guard', 'defensive'
        }
        
        # Documentation keywords
        self.documentation_patterns_set = {
            'document', 'documentation', 'comment', 'explain', 'clarify', 'readme', 'guide', 'help',
            'example', 'tutorial', 'api doc', 'javadoc', 'docstring', 'specification'
        }
        
        # Refactoring/Code quality keywords
        self.refactoring_patterns_set = {
            'refactor', 'cleanup', 'reorganize', 'simplify', 'extract', 'rename',
            'duplicate', 'dead code', 'legacy', 'deprecated', 'migrate', 'upgrade',
            'modernize', 'consolidate', 'technical debt', 'maintenance'
        }
    
    def generate_yaml_report(self) -> str:
        """
        Generate structured YAML TODO report for AI consumption with comprehensive fallback.
        
        Implements multi-level fallback strategy:
        1. Primary: Generate structured YAML report
        2. Fallback 1: Generate simplified YAML on structure errors
        3. Fallback 2: Generate JSON report for compatibility
        4. Fallback 3: Generate minimal emergency file
        
        Returns:
            Path to generated file (YAML preferred, JSON fallback, or emergency file)
        """
        start_time = datetime.now()
        
        logger.info("Starting TODO report generation with fallback strategy")
        
        # Ensure .brass directory exists
        try:
            self.brass_dir.mkdir(exist_ok=True)
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create .brass directory: {e}")
            return self._generate_emergency_fallback([])
        
        # Phase 1: Collect TODO data with fallback protection
        logger.info("Phase 1: Collecting TODO data")
        try:
            todo_data = self._collect_todo_data()
        except (RuntimeError, OSError, IOError) as e:
            logger.error(f"Phase 1 failed - TODO data collection error: {e}")
            return self._generate_emergency_fallback([])
        
        # Phase 2: Try primary YAML generation
        try:
            return self._generate_primary_yaml(todo_data, start_time)
        except (yaml.YAMLError, IOError, OSError, RuntimeError) as e:
            logger.warning(f"Primary YAML generation failed: {e}")
            
            # Fallback 1: Try simplified YAML generation
            try:
                return self._generate_simplified_yaml(todo_data, start_time)
            except (yaml.YAMLError, IOError, OSError) as e2:
                logger.warning(f"Simplified YAML generation failed: {e2}")
                
                # Fallback 2: Try JSON generation
                try:
                    return self._generate_json_fallback(todo_data, start_time)
                except (json.JSONEncodeError, IOError, OSError) as e3:
                    logger.error(f"JSON fallback generation failed: {e3}")
                    
                    # Fallback 3: Emergency minimal file
                    return self._generate_emergency_fallback(todo_data)
    
    def _collect_todo_data(self) -> List[Dict[str, Any]]:
        """
        Collect TODO data using existing logic from OutputGenerator.
        
        Replicates the 24-hour window filtering and deduplication logic.
        
        Returns:
            List of processed TODO data
        """
        try:
            # Get TODO observations (mimicking OutputGenerator logic)
            all_todos = self.storage.get_observations_by_type('todo')
            
            # Apply 24-hour window filtering (from OutputGenerator.generate_todo_list)
            from datetime import timezone
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
            recent_todos = []
            
            for todo in all_todos:
                try:
                    created_at_str = todo['created_at']
                    # Handle both timezone-aware and naive datetime strings
                    if 'Z' in created_at_str or '+' in created_at_str:
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    else:
                        # Make naive datetime timezone-aware (assume UTC)
                        created_at = datetime.fromisoformat(created_at_str).replace(tzinfo=timezone.utc)
                    
                    if created_at >= cutoff_time:
                        recent_todos.append(todo)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Failed to parse TODO created_at: {e}")
                    # Include TODO even if timestamp parsing fails
                    recent_todos.append(todo)
            
            # Deduplicate by file path, line number, and content (from OutputGenerator logic)
            seen_combinations = set()
            deduplicated_todos = []
            
            for todo in recent_todos:
                try:
                    data = todo.get('data', {})
                    if isinstance(data, str):
                        import json
                        data = json.loads(data)
                    
                    file_path = data.get('file_path', '')
                    line_number = data.get('line_number', 0)
                    content = data.get('content', '')
                    
                    # Create deduplication key
                    dedup_key = (file_path, line_number, content.strip())
                    
                    if dedup_key not in seen_combinations:
                        seen_combinations.add(dedup_key)
                        deduplicated_todos.append({
                            'id': todo.get('id'),
                            'content': content,
                            'file_path': file_path,
                            'line_number': line_number,
                            'priority': todo.get('priority', 0),
                            'category': data.get('category', 'general'),
                            'created_at': todo.get('created_at', ''),
                            'metadata': data.get('metadata', {})
                        })
                        
                except (KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
                    logger.warning(f"Failed to process TODO data: {e}")
                    continue
            
            logger.info(f"Collected {len(deduplicated_todos)} TODOs from {len(all_todos)} total observations")
            return deduplicated_todos
            
        except (AttributeError, KeyError, ValueError, TypeError, OSError, IOError) as e:
            logger.error(f"Failed to collect TODO data: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            # Re-raise to trigger fallback mechanisms
            raise RuntimeError(f"TODO data collection failed: {e}") from e
    
    def _structure_todo_data(self, todos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Structure TODO data for YAML output with location-based grouping.
        
        Args:
            todos: Raw TODO data
            
        Returns:
            Structured TODO data organized by priority, location, and category
            
        Raises:
            RuntimeError: If structuring fails due to data format issues
        """
        try:
            return self._structure_todo_data_impl(todos)
        except (KeyError, ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to structure TODO data: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            raise RuntimeError(f"TODO data structuring failed: {e}") from e
    
    def _structure_todo_data_impl(self, todos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Implementation of TODO data structuring.
        
        Args:
            todos: Raw TODO data
            
        Returns:
            Structured TODO data organized by priority, location, and category
        """
        # Priority-based grouping
        priority_groups = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        # Location-based grouping (following PrivacyYamlGenerator pattern)
        location_groups = defaultdict(list)
        
        # Category-based grouping
        category_groups = defaultdict(list)
        
        # Priority mapping
        def get_priority_level(priority_score):
            if priority_score >= 80:
                return 'critical'
            elif priority_score >= 60:
                return 'high'
            elif priority_score >= 40:
                return 'medium'
            else:
                return 'low'
        
        for todo in todos:
            priority_level = get_priority_level(todo.get('priority', 0))
            
            # Enhanced category detection based on content analysis
            intelligent_category = self._detect_todo_category(todo.get('content', ''))
            
            # Format for YAML output
            yaml_todo = {
                'content': todo['content'],
                'location': f"{todo['file_path']}:{todo['line_number']}",
                'priority_score': int(todo.get('priority', 0)),
                'priority_level': priority_level,
                'category': intelligent_category,
                'created_at': todo.get('created_at', ''),
                'id': todo.get('id')
            }
            
            # Add metadata if available
            if todo.get('metadata'):
                yaml_todo['metadata'] = todo['metadata']
            
            # Group by priority
            priority_groups[priority_level].append(yaml_todo)
            
            # Group by location
            location_key = yaml_todo['location']
            location_groups[location_key].append({
                'content': yaml_todo['content'],
                'priority_level': priority_level,
                'priority_score': yaml_todo['priority_score'],
                'category': yaml_todo['category'],
                'id': yaml_todo['id']
            })
            
            # Group by category
            category_groups[yaml_todo['category']].append(yaml_todo)
        
        # Sort within each priority group by priority score (descending)
        for priority_level in priority_groups:
            priority_groups[priority_level].sort(key=lambda x: x['priority_score'], reverse=True)
        
        return {
            'todos': todos,
            'priority_groups': priority_groups,
            'location_groups': dict(location_groups),
            'category_groups': dict(category_groups)
        }
    
    def _detect_todo_category(self, content: str) -> str:
        """
        Detect TODO category based on content analysis using optimized pattern matching.
        
        Uses set intersection for O(1) average case pattern lookup performance
        instead of O(n*m) linear search through pattern lists.
        
        Args:
            content: TODO content text
            
        Returns:
            Category string (bug_fixes, performance, security, documentation, refactoring, general)
        """
        # Convert content to word set for efficient intersection matching
        content_words = set(content.lower().split())
        
        # Check patterns in order of specificity using set intersection
        if content_words & self.security_patterns_set:
            return 'security'
        elif content_words & self.performance_patterns_set:
            return 'performance'  
        elif content_words & self.bug_patterns_set:
            return 'bug_fixes'
        elif content_words & self.documentation_patterns_set:
            return 'documentation'
        elif content_words & self.refactoring_patterns_set:
            return 'refactoring'
        else:
            return 'general'
    
    def _build_yaml_structure(
        self, 
        structured_data: Dict[str, Any], 
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Build comprehensive YAML structure with error handling.
        
        Args:
            structured_data: Structured TODO data
            start_time: Generation start time
            
        Returns:
            Complete YAML data structure
            
        Raises:
            RuntimeError: If YAML structure building fails
        """
        try:
            return self._build_yaml_structure_impl(structured_data, start_time)
        except (KeyError, ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to build YAML structure: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            raise RuntimeError(f"YAML structure building failed: {e}") from e
    
    def _build_yaml_structure_impl(
        self, 
        structured_data: Dict[str, Any], 
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Build structured YAML data optimized for AI consumption.
        
        Args:
            structured_data: Structured TODO data
            start_time: Report generation start time
            
        Returns:
            Complete YAML data structure
        """
        # Validate required keys in structured_data
        required_keys = ['todos', 'priority_groups', 'location_groups', 'category_groups']
        for key in required_keys:
            if key not in structured_data:
                raise ValueError(f"Missing required key in structured_data: {key}")
        
        todos = structured_data['todos']
        priority_groups = structured_data['priority_groups']
        location_groups = structured_data['location_groups']
        category_groups = structured_data['category_groups']
        
        # Calculate summary statistics
        total_todos = len(todos)
        priority_counts = {
            level: len(group) for level, group in priority_groups.items()
        }
        
        # Calculate location statistics
        location_stats = {}
        for location, location_todos in location_groups.items():
            priorities = [t['priority_level'] for t in location_todos]
            location_stats[location] = {
                'todo_count': len(location_todos),
                'primary_priority': max(priorities, key=['critical', 'high', 'medium', 'low'].index) if priorities else 'low',
                'todos': location_todos,
                'categories_present': list(set(t['category'] for t in location_todos))
            }
        
        return {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'generator_version': '2.3.30',
                'format_version': '1.0',
                'schema_description': 'TODO analysis data optimized for AI consumption',
                'project_name': self.project_path.name,
                'window_hours': 24,
                'deduplication_applied': True
            },
            
            'todo_summary': {
                'total_todos': total_todos,
                'active_todos': total_todos,  # All collected TODOs are active (resolution detection already applied)
                'window_description': 'TODOs from last 24 hours with deduplication',
                'priority_breakdown': priority_counts,
                'locations_with_todos': len(location_groups),
                'categories_detected': len(category_groups)
            },
            
            'todos_by_priority': {
                'critical': self._format_todos_for_yaml(priority_groups['critical']),
                'high': self._format_todos_for_yaml(priority_groups['high']),
                'medium': self._format_todos_for_yaml(priority_groups['medium']),
                'low': self._format_todos_for_yaml(priority_groups['low'])
            },
            
            'todos_by_location': location_stats,
            
            'todos_by_category': {
                category: self._format_todos_for_yaml(category_todos)
                for category, category_todos in category_groups.items()
            },
            
            'priority_analysis': {
                'critical_ratio': priority_counts['critical'] / total_todos if total_todos > 0 else 0.0,
                'high_priority_ratio': (priority_counts['critical'] + priority_counts['high']) / total_todos if total_todos > 0 else 0.0,
                'most_common_priority': max(priority_counts.items(), key=lambda x: x[1])[0] if priority_counts else 'low',
                'average_priority_score': sum(t.get('priority', 0) for t in todos) / len(todos) if todos else 0.0
            },
            
            'performance_metrics': {
                'generation_time_seconds': (datetime.now() - start_time).total_seconds(),
                'total_todos_processed': total_todos,
                'deduplication_applied': True,
                'time_window_hours': 24
            },
            
            'ai_consumption_metadata': {
                'parsing_instruction': 'Use yaml.safe_load() for secure parsing',
                'data_access_examples': {
                    'total_todos': "data['todo_summary']['total_todos']",
                    'critical_count': "len(data['todos_by_priority']['critical'])",
                    'todos_at_location': "data['todos_by_location']['file.py:line']['todos']",
                    'category_todos': "data['todos_by_category']['bug_fixes']"
                },
                'recommended_libraries': ['PyYAML', 'ruamel.yaml'],
                'schema_stability': 'format_version tracks breaking changes',
                'integration_note': 'Replaces todos.json with enhanced AI-optimized structure'
            }
        }
    
    def _format_todos_for_yaml(self, todos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format TODOs list for YAML output with type-safe data.
        
        Args:
            todos: TODOs to format
            
        Returns:
            List of TODO dictionaries optimized for YAML
        """
        yaml_todos = []
        
        for todo in todos:
            yaml_todo = {
                'content': todo['content'],
                'location': todo['location'],
                'priority_score': int(todo['priority_score']),  # Ensure numeric type
                'priority_level': todo['priority_level'],
                'category': todo['category'],
                'created_at': todo['created_at']
            }
            
            # Add metadata if available
            if todo.get('metadata'):
                yaml_todo['metadata'] = todo['metadata']
            
            # Add ID for tracking
            if todo.get('id'):
                yaml_todo['id'] = todo['id']
            
            yaml_todos.append(yaml_todo)
        
        return yaml_todos


    def _generate_primary_yaml(self, todo_data: List[Dict[str, Any]], start_time: datetime) -> str:
        """
        Generate primary structured YAML report.
        
        Args:
            todo_data: Collected TODO data
            start_time: Generation start time
            
        Returns:
            Path to generated YAML file
        """
        logger.info("Generating primary structured YAML report")
        
        # Phase 2: Process and structure TODO data
        structured_todos = self._structure_todo_data(todo_data)
        
        # Phase 3: Generate YAML structure
        yaml_data = self._build_yaml_structure(structured_todos, start_time)
        
        # Phase 4: Write YAML file
        with open(self.yaml_output_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        generation_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Primary YAML report generated successfully in {generation_time:.2f}s: {self.yaml_output_path}")
        
        return str(self.yaml_output_path)
    
    def _generate_simplified_yaml(self, todo_data: List[Dict[str, Any]], start_time: datetime) -> str:
        """
        Generate simplified YAML report as first fallback.
        
        Uses basic structure without complex groupings to avoid structure errors.
        
        Args:
            todo_data: Collected TODO data
            start_time: Generation start time
            
        Returns:
            Path to generated simplified YAML file
        """
        logger.info("Generating simplified YAML report (Fallback 1)")
        
        # Simple structure without complex processing
        simplified_data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'generator_version': '2.3.32',
                'format_version': '1.0-simplified',
                'fallback_reason': 'Primary generation failed - using simplified structure',
                'project_name': self.project_path.name,
                'total_todos': len(todo_data)
            },
            'todos': [
                {
                    'content': todo.get('content', ''),
                    'file_path': todo.get('file_path', ''),
                    'line_number': todo.get('line_number', 0),
                    'priority': todo.get('priority', 0),
                    'category': todo.get('category', 'general'),
                    'created_at': todo.get('created_at', '')
                }
                for todo in todo_data
            ]
        }
        
        # Write simplified YAML
        with open(self.yaml_output_path, 'w', encoding='utf-8') as f:
            yaml.dump(simplified_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        generation_time = (datetime.now() - start_time).total_seconds()
        logger.warning(f"Simplified YAML report generated in {generation_time:.2f}s: {self.yaml_output_path}")
        
        return str(self.yaml_output_path)
    
    def _generate_json_fallback(self, todo_data: List[Dict[str, Any]], start_time: datetime) -> str:
        """
        Generate JSON fallback report for maximum compatibility.
        
        Uses JSON format based on OutputGenerator._generate_fallback_todo_json()
        
        Args:
            todo_data: Collected TODO data
            start_time: Generation start time
            
        Returns:
            Path to generated JSON fallback file
        """
        logger.info("Generating JSON fallback report (Fallback 2)")
        
        # Create JSON structure compatible with existing system expectations
        json_data = {
            'generated_at': datetime.now().isoformat(),
            'generator': 'TodoYamlGenerator-JSONFallback',
            'version': '2.3.32',
            'fallback_reason': 'YAML generation failed - using JSON compatibility mode',
            'total_todos': len(todo_data),
            'todos': [
                {
                    'file': todo.get('file_path', 'unknown'),
                    'line': todo.get('line_number', 0),
                    'content': todo.get('content', ''),
                    'priority': todo.get('priority', 50),
                    'classification': todo.get('category', 'unclassified'),
                    'created_at': todo.get('created_at', '')
                }
                for todo in todo_data
            ]
        }
        
        # Write JSON fallback file
        with open(self.json_fallback_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        generation_time = (datetime.now() - start_time).total_seconds()
        logger.warning(f"JSON fallback report generated in {generation_time:.2f}s: {self.json_fallback_path}")
        
        return str(self.json_fallback_path)
    
    def _generate_emergency_fallback(self, todo_data: List[Dict[str, Any]]) -> str:
        """
        Generate emergency minimal file as last resort.
        
        Creates basic text file when all other methods fail.
        
        Args:
            todo_data: TODO data (may be empty if collection failed)
            
        Returns:
            Path to generated emergency file
        """
        logger.error("Generating emergency fallback file (Fallback 3)")
        
        emergency_path = self.brass_dir / 'todos_emergency.txt'
        
        try:
            with open(emergency_path, 'w', encoding='utf-8') as f:
                f.write(f"EMERGENCY TODO REPORT - {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n")
                f.write("WARNING: Normal TODO generation failed. This is a minimal emergency report.\n\n")
                
                if todo_data:
                    f.write(f"Found {len(todo_data)} TODOs:\n\n")
                    for i, todo in enumerate(todo_data, 1):
                        f.write(f"{i}. {todo.get('content', 'No content')}\n")
                        f.write(f"   File: {todo.get('file_path', 'Unknown')}\n")
                        f.write(f"   Line: {todo.get('line_number', 'Unknown')}\n\n")
                else:
                    f.write("No TODO data available (data collection may have failed).\n")
                
                f.write("\nPlease check logs for error details and retry TODO generation.\n")
        
            logger.error(f"Emergency fallback file created: {emergency_path}")
            return str(emergency_path)
            
        except (IOError, OSError, PermissionError) as e:
            # Absolute last resort - return error message
            logger.critical(f"Emergency fallback creation failed: {e}")
            return f"CRITICAL_ERROR: All TODO generation methods failed. Check logs and system permissions."

# Standalone execution capability (matching PrivacyYamlGenerator pattern)
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python todo_yaml_generator.py <project_path>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    
    # Mock storage for standalone testing
    class MockStorage:
        def get_observations_by_type(self, obs_type):
            return []
    
    storage = MockStorage()
    generator = TodoYamlGenerator(project_path, storage)
    report_path = generator.generate_yaml_report()
    print(f"TODO YAML report generated: {report_path}")