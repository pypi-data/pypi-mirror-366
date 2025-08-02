"""
Unit tests for cycle detection module.

Tests all public methods and edge cases for the pure Python cycle detection
implementation that replaces NetworkX dependency.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from coppersun_brass.agents.planner.cycle_detection import (
    PurePythonCycleDetector,
    find_simple_cycles,
    convert_tasks_to_graph,
    detect_task_dependency_cycles
)


class TestPurePythonCycleDetector(unittest.TestCase):
    """Test the core PurePythonCycleDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = PurePythonCycleDetector()
    
    def test_simple_cycle_detection(self):
        """Test detection of a simple 3-node cycle."""
        graph = {'A': ['B'], 'B': ['C'], 'C': ['A']}
        cycles = self.detector.simple_cycles(graph)
        
        self.assertEqual(len(cycles), 1)
        self.assertEqual(len(cycles[0]), 3)
        self.assertIn('A', cycles[0])
        self.assertIn('B', cycles[0])
        self.assertIn('C', cycles[0])
    
    def test_no_cycles_dag(self):
        """Test that DAG (Directed Acyclic Graph) returns no cycles."""
        graph = {'A': ['B'], 'B': ['C'], 'C': []}
        cycles = self.detector.simple_cycles(graph)
        
        self.assertEqual(cycles, [])
    
    def test_multiple_cycles(self):
        """Test detection of multiple independent cycles."""
        graph = {
            'A': ['B'], 'B': ['A'],  # Cycle 1: A-B
            'C': ['D'], 'D': ['C']   # Cycle 2: C-D
        }
        cycles = self.detector.simple_cycles(graph)
        
        self.assertEqual(len(cycles), 2)
    
    def test_empty_graph(self):
        """Test empty graph returns no cycles."""
        cycles = self.detector.simple_cycles({})
        self.assertEqual(cycles, [])
    
    def test_single_node_no_edges(self):
        """Test single node with no edges."""
        cycles = self.detector.simple_cycles({'A': []})
        self.assertEqual(cycles, [])
    
    def test_self_loop_filtering(self):
        """Test that self-loops are properly filtered out."""
        graph = {'A': ['A']}
        cycles = self.detector.simple_cycles(graph)
        self.assertEqual(cycles, [])
    
    def test_complex_graph_structure(self):
        """Test complex graph with multiple paths to same nodes."""
        graph = {
            'A': ['B', 'C'],
            'B': ['D'],
            'C': ['D'], 
            'D': ['E'],
            'E': ['A']
        }
        cycles = self.detector.simple_cycles(graph)
        
        self.assertEqual(len(cycles), 1)
        self.assertIn('A', cycles[0])
        self.assertIn('E', cycles[0])
    
    def test_cycle_uniqueness(self):
        """Test that duplicate cycles (different rotations) are handled correctly."""
        # This graph could produce the same cycle from different starting points
        graph = {'A': ['B'], 'B': ['C'], 'C': ['A', 'D'], 'D': ['B']}
        cycles = self.detector.simple_cycles(graph)
        
        # Should not have duplicate cycles with different rotations
        normalized_cycles = []
        for cycle in cycles:
            min_idx = cycle.index(min(cycle))
            normalized = cycle[min_idx:] + cycle[:min_idx]
            self.assertNotIn(normalized, normalized_cycles)
            normalized_cycles.append(normalized)


class TestConvenienceFunctions(unittest.TestCase):
    """Test the convenience functions for cycle detection."""
    
    def test_find_simple_cycles_wrapper(self):
        """Test the find_simple_cycles convenience function."""
        graph = {'A': ['B'], 'B': ['C'], 'C': ['A']}
        cycles = find_simple_cycles(graph)
        
        self.assertEqual(len(cycles), 1)
        self.assertEqual(len(cycles[0]), 3)
    
    def test_convert_tasks_to_graph_basic(self):
        """Test basic task to graph conversion."""
        tasks = [
            {'id': 'task1', 'dependencies': ['task2']},
            {'id': 'task2', 'dependencies': ['task3']},
            {'id': 'task3', 'dependencies': []}
        ]
        graph = convert_tasks_to_graph(tasks)
        
        expected_nodes = {'task1', 'task2', 'task3'}
        self.assertEqual(set(graph.keys()), expected_nodes)
        
        # task2 should point to task1 (task1 depends on task2)
        self.assertIn('task1', graph['task2'])
        self.assertIn('task2', graph['task3'])
        self.assertEqual(graph['task1'], [])
    
    def test_convert_tasks_missing_dependencies(self):
        """Test task conversion with missing dependencies field."""
        tasks = [
            {'id': 'task1'},  # No dependencies field
            {'id': 'task2', 'dependencies': ['task1']}
        ]
        graph = convert_tasks_to_graph(tasks)
        
        self.assertIn('task1', graph)
        self.assertIn('task2', graph)
        self.assertIn('task2', graph['task1'])
    
    def test_convert_tasks_self_dependency(self):
        """Test that self-dependencies are filtered out."""
        tasks = [
            {'id': 'task1', 'dependencies': ['task1', 'task2']},
            {'id': 'task2', 'dependencies': []}
        ]
        graph = convert_tasks_to_graph(tasks)
        
        # task1 should not depend on itself
        self.assertNotIn('task1', graph['task1'])
        # But should depend on task2
        self.assertIn('task1', graph['task2'])
    
    def test_convert_tasks_invalid_data(self):
        """Test task conversion with invalid task data."""
        tasks = [
            {'id': None},  # Invalid ID
            {'dependencies': ['task1']},  # Missing ID
            {'id': 'task1', 'dependencies': ['nonexistent']}  # Invalid dependency
        ]
        graph = convert_tasks_to_graph(tasks)
        
        # Should handle gracefully
        self.assertIn('task1', graph)
        # Nonexistent dependency should be ignored
        self.assertEqual(graph['task1'], [])
    
    def test_detect_task_dependency_cycles_integration(self):
        """Test the main interface function with real task data."""
        tasks = [
            {'id': 'impl', 'dependencies': ['test']},
            {'id': 'test', 'dependencies': ['docs']},
            {'id': 'docs', 'dependencies': ['impl']}
        ]
        cycles = detect_task_dependency_cycles(tasks)
        
        self.assertEqual(len(cycles), 1)
        cycle_nodes = set(cycles[0])
        expected_nodes = {'impl', 'test', 'docs'}
        self.assertEqual(cycle_nodes, expected_nodes)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_none_input_handling(self):
        """Test handling of None input."""
        cycles = detect_task_dependency_cycles(None)
        self.assertEqual(cycles, [])
    
    def test_empty_task_list(self):
        """Test handling of empty task list."""
        cycles = detect_task_dependency_cycles([])
        self.assertEqual(cycles, [])
    
    def test_malformed_task_structure(self):
        """Test handling of malformed task structures."""
        malformed_tasks = [
            "not_a_dict",
            {'wrong': 'structure'},
            {'id': 123, 'dependencies': 'not_a_list'}
        ]
        
        # Should not crash, should return empty list
        cycles = detect_task_dependency_cycles(malformed_tasks)
        self.assertEqual(cycles, [])
    
    def test_very_large_graph_performance(self):
        """Test performance with larger graphs."""
        import time
        
        # Create a large cycle (100 nodes)
        large_graph = {f'node{i}': [f'node{(i+1)%100}'] for i in range(100)}
        
        start_time = time.time()
        cycles = find_simple_cycles(large_graph)
        end_time = time.time()
        
        # Should complete quickly (under 0.1 seconds)
        self.assertLess(end_time - start_time, 0.1)
        self.assertEqual(len(cycles), 1)
        self.assertEqual(len(cycles[0]), 100)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)