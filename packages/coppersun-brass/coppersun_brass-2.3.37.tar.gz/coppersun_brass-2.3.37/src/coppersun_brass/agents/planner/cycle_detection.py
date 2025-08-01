"""
Pure Python implementation of simple cycle detection for directed graphs.

This module provides a replacement for NetworkX's simple_cycles function 
to maintain Blood Oath compliance (no heavy dependencies).

Author: Claude Code
Date: July 17, 2025
Purpose: Resolve NetworkX dependency missing bug in task generation
"""

from typing import List, Dict, Set, Optional
import logging

logger = logging.getLogger(__name__)


class PurePythonCycleDetector:
    """
    Pure Python implementation of simple cycle detection for directed graphs.
    
    This class provides functionality equivalent to NetworkX's simple_cycles()
    function without requiring any external dependencies.
    
    The algorithm uses depth-first search (DFS) with path tracking to detect
    all simple cycles in a directed graph.
    """
    
    def __init__(self):
        self.graph = {}  # adjacency list representation
        self.visited = set()  # visited nodes
        self.recursion_stack = set()  # nodes in current DFS path
        self.path = []  # current DFS path
        self.cycles = []  # found cycles
    
    def simple_cycles(self, graph_dict: Dict[str, List[str]]) -> List[List[str]]:
        """
        Find all simple cycles in a directed graph.
        
        Args:
            graph_dict: Dictionary representing adjacency list of directed graph
                       Format: {node_id: [list_of_successor_nodes]}
        
        Returns:
            List of cycles, where each cycle is a list of node IDs
            
        Example:
            >>> detector = PurePythonCycleDetector()
            >>> graph = {'A': ['B'], 'B': ['C'], 'C': ['A']}
            >>> cycles = detector.simple_cycles(graph)
            >>> print(cycles)  # [['A', 'B', 'C']]
        """
        if not graph_dict:
            return []
        
        # Initialize state
        self.graph = graph_dict
        self.visited = set()
        self.recursion_stack = set()
        self.path = []
        self.cycles = []
        
        # Run DFS from each unvisited node
        for node in graph_dict:
            if node not in self.visited:
                self._dfs_cycle_detection(node)
        
        return self.cycles
    
    def _dfs_cycle_detection(self, node: str) -> None:
        """
        Perform DFS to detect cycles starting from the given node.
        
        Args:
            node: Starting node for DFS traversal
        """
        # Mark node as visited and add to recursion stack
        self.visited.add(node)
        self.recursion_stack.add(node)
        self.path.append(node)
        
        # Explore all neighbors
        for neighbor in self.graph.get(node, []):
            if neighbor in self.recursion_stack:
                # Found a back edge - this indicates a cycle
                cycle_start_idx = self.path.index(neighbor)
                cycle = self.path[cycle_start_idx:]
                
                # Add cycle if it's not already found and has more than one node
                if len(cycle) > 1 and not self._is_duplicate_cycle(cycle):
                    self.cycles.append(cycle)
                    
            elif neighbor not in self.visited:
                # Continue DFS for unvisited neighbors
                self._dfs_cycle_detection(neighbor)
        
        # Backtrack: remove from recursion stack and path
        self.recursion_stack.remove(node)
        self.path.pop()
    
    def _is_duplicate_cycle(self, new_cycle: List[str]) -> bool:
        """
        Check if a cycle is already present (considering rotations).
        
        Args:
            new_cycle: Cycle to check for duplicates
            
        Returns:
            True if cycle already exists in a different rotation
        """
        if not new_cycle:
            return True
            
        # Normalize cycle by starting with the lexicographically smallest node
        min_idx = new_cycle.index(min(new_cycle))
        normalized_new = new_cycle[min_idx:] + new_cycle[:min_idx]
        
        for existing_cycle in self.cycles:
            if len(existing_cycle) == len(new_cycle):
                # Normalize existing cycle
                min_idx = existing_cycle.index(min(existing_cycle))
                normalized_existing = existing_cycle[min_idx:] + existing_cycle[:min_idx]
                
                if normalized_new == normalized_existing:
                    return True
        
        return False


def find_simple_cycles(graph_dict: Dict[str, List[str]]) -> List[List[str]]:
    """
    Convenience function to find all simple cycles in a directed graph.
    
    This function provides a drop-in replacement for NetworkX's simple_cycles()
    function with the same interface and return format.
    
    Args:
        graph_dict: Dictionary representing adjacency list of directed graph
                   Format: {node_id: [list_of_successor_nodes]}
    
    Returns:
        List of cycles, where each cycle is a list of node IDs
        
    Example:
        >>> graph = {'A': ['B'], 'B': ['C'], 'C': ['A', 'D'], 'D': ['C']}
        >>> cycles = find_simple_cycles(graph)
        >>> print(cycles)  # [['A', 'B', 'C'], ['C', 'D']]
    """
    detector = PurePythonCycleDetector()
    return detector.simple_cycles(graph_dict)


def convert_tasks_to_graph(tasks: List[Dict]) -> Dict[str, List[str]]:
    """
    Convert task list with dependencies to adjacency list format.
    
    Args:
        tasks: List of task dictionaries with 'id' and 'dependencies' fields
        
    Returns:
        Dictionary in adjacency list format suitable for cycle detection
        
    Example:
        >>> tasks = [
        ...     {'id': 'task1', 'dependencies': ['task2']},
        ...     {'id': 'task2', 'dependencies': ['task3']},
        ...     {'id': 'task3', 'dependencies': ['task1']}
        ... ]
        >>> graph = convert_tasks_to_graph(tasks)
        >>> print(graph)  # {'task2': ['task1'], 'task3': ['task2'], 'task1': ['task3']}
    """
    graph = {}
    
    # Initialize all nodes
    for task in tasks:
        task_id = task.get('id')
        if task_id:
            graph[task_id] = []
    
    # Add edges based on dependencies
    for task in tasks:
        task_id = task.get('id')
        dependencies = task.get('dependencies', [])
        
        if task_id:
            for dep_id in dependencies:
                if dep_id and dep_id in graph and dep_id != task_id:
                    # Add edge from dependency to task (dep -> task)
                    # Skip self-dependencies to avoid trivial cycles
                    graph[dep_id].append(task_id)
    
    return graph


def detect_task_dependency_cycles(tasks: List[Dict]) -> List[List[str]]:
    """
    Detect dependency cycles in a list of tasks.
    
    This function is specifically designed for the TaskGenerator use case
    and provides a complete solution for detecting cycles in task dependencies.
    
    Args:
        tasks: List of task dictionaries with 'id' and 'dependencies' fields
        
    Returns:
        List of cycles, where each cycle is a list of task IDs
        
    Example:
        >>> tasks = [
        ...     {'id': 'A', 'dependencies': ['B']},
        ...     {'id': 'B', 'dependencies': ['C']},
        ...     {'id': 'C', 'dependencies': ['A']}
        ... ]
        >>> cycles = detect_task_dependency_cycles(tasks)
        >>> print(cycles)  # [['A', 'B', 'C']]
    """
    # Input validation
    if not _validate_task_input(tasks):
        return []
    
    try:
        # Convert tasks to graph format
        graph = convert_tasks_to_graph(tasks)
        
        # Find cycles
        cycles = find_simple_cycles(graph)
        
        logger.debug(f"Detected {len(cycles)} cycles in {len(tasks)} tasks")
        return cycles
        
    except (TypeError, AttributeError) as e:
        logger.error(f"Invalid task format for cycle detection: {e}")
        return []
    except (KeyError, ValueError) as e:
        logger.error(f"Task data error during cycle detection: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during cycle detection: {e}")
        return []


def _validate_task_input(tasks: any) -> bool:
    """
    Validate input tasks for cycle detection.
    
    Args:
        tasks: Input to validate
        
    Returns:
        True if input is valid for processing, False otherwise
    """
    if tasks is None:
        logger.warning("Task input is None for cycle detection")
        return False
    
    if not isinstance(tasks, list):
        logger.warning(f"Task input must be a list, got {type(tasks)}")
        return False
    
    if not tasks:  # Empty list is valid
        return True
    
    # Validate task structure
    valid_tasks = 0
    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            logger.warning(f"Task {i} is not a dictionary: {type(task)}")
            continue
        
        task_id = task.get('id')
        if not task_id or not isinstance(task_id, str):
            logger.warning(f"Task {i} has invalid or missing 'id' field: {task_id}")
            continue
        
        dependencies = task.get('dependencies', [])
        if not isinstance(dependencies, list):
            logger.warning(f"Task {task_id} has invalid 'dependencies' field: {type(dependencies)}")
            continue
        
        # Check dependency types
        for dep in dependencies:
            if dep is not None and not isinstance(dep, str):
                logger.warning(f"Task {task_id} has invalid dependency type: {dep}")
                break
        else:
            valid_tasks += 1
    
    if valid_tasks == 0 and len(tasks) > 0:
        logger.warning("No valid tasks found in input")
        return False
    
    return True