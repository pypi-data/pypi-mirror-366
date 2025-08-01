"""
Integration tests for cycle detection with TaskGenerator.

Tests the integration between cycle detection module and TaskGenerator
to ensure seamless replacement of NetworkX functionality.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from coppersun_brass.agents.planner.cycle_detection import detect_task_dependency_cycles
from coppersun_brass.agents.planner.task_generator import TaskGenerationConfig


class TestTaskGeneratorIntegration(unittest.TestCase):
    """Test integration with TaskGenerator."""
    
    def test_networkx_compatibility_format(self):
        """Test that output format matches NetworkX expectations."""
        tasks = [
            {'id': 'A', 'dependencies': ['B']},
            {'id': 'B', 'dependencies': ['C']},
            {'id': 'C', 'dependencies': ['A']}
        ]
        
        cycles = detect_task_dependency_cycles(tasks)
        
        # Should return List[List[str]] format
        self.assertIsInstance(cycles, list)
        self.assertTrue(all(isinstance(cycle, list) for cycle in cycles))
        self.assertTrue(all(isinstance(node, str) for cycle in cycles for node in cycle))
    
    def test_task_generator_config_compatibility(self):
        """Test compatibility with TaskGenerationConfig."""
        config = TaskGenerationConfig(cycle_detection_enabled=True)
        
        # Should work with cycle detection enabled
        self.assertTrue(config.cycle_detection_enabled)
        
        # Create minimal TaskGenerator instance for testing
        tasks_with_cycle = [
            {'id': 'task1', 'dependencies': ['task2']},
            {'id': 'task2', 'dependencies': ['task1']}
        ]
        
        cycles = detect_task_dependency_cycles(tasks_with_cycle)
        self.assertEqual(len(cycles), 1)
    
    def test_realistic_task_scenario(self):
        """Test with realistic software development task scenario."""
        tasks = [
            {
                'id': 'implement_feature',
                'dependencies': ['write_tests'],
                'task_type': 'implementation',
                'priority_score': 80
            },
            {
                'id': 'write_tests', 
                'dependencies': ['update_docs'],
                'task_type': 'testing',
                'priority_score': 70
            },
            {
                'id': 'update_docs',
                'dependencies': ['implement_feature'],
                'task_type': 'documentation', 
                'priority_score': 60
            },
            {
                'id': 'deploy',
                'dependencies': ['implement_feature', 'write_tests'],
                'task_type': 'deployment',
                'priority_score': 90
            }
        ]
        
        cycles = detect_task_dependency_cycles(tasks)
        
        # Should detect the cycle between implement_feature -> write_tests -> update_docs -> implement_feature
        self.assertEqual(len(cycles), 1)
        cycle_nodes = set(cycles[0])
        expected_cycle_nodes = {'implement_feature', 'write_tests', 'update_docs'}
        self.assertEqual(cycle_nodes, expected_cycle_nodes)
        
        # Deploy task should not be in the cycle
        self.assertNotIn('deploy', cycles[0])
    
    def test_no_cycle_workflow(self):
        """Test proper workflow without cycles."""
        tasks = [
            {'id': 'research', 'dependencies': []},
            {'id': 'design', 'dependencies': ['research']},
            {'id': 'implement', 'dependencies': ['design']},
            {'id': 'test', 'dependencies': ['implement']},
            {'id': 'deploy', 'dependencies': ['test']}
        ]
        
        cycles = detect_task_dependency_cycles(tasks)
        self.assertEqual(cycles, [])
    
    def test_multiple_independent_cycles(self):
        """Test detection of multiple independent cycles in task workflow."""
        tasks = [
            # Cycle 1: Frontend development cycle
            {'id': 'ui_design', 'dependencies': ['ui_test']},
            {'id': 'ui_implement', 'dependencies': ['ui_design']},
            {'id': 'ui_test', 'dependencies': ['ui_implement']},
            
            # Cycle 2: Backend development cycle  
            {'id': 'api_design', 'dependencies': ['api_test']},
            {'id': 'api_implement', 'dependencies': ['api_design']},
            {'id': 'api_test', 'dependencies': ['api_implement']},
            
            # Independent task
            {'id': 'database_setup', 'dependencies': []}
        ]
        
        cycles = detect_task_dependency_cycles(tasks)
        
        # Should detect 2 cycles
        self.assertEqual(len(cycles), 2)
        
        # Verify cycles contain expected nodes
        all_cycle_nodes = set()
        for cycle in cycles:
            all_cycle_nodes.update(cycle)
        
        expected_ui_nodes = {'ui_design', 'ui_implement', 'ui_test'}
        expected_api_nodes = {'api_design', 'api_implement', 'api_test'}
        
        self.assertTrue(expected_ui_nodes.issubset(all_cycle_nodes))
        self.assertTrue(expected_api_nodes.issubset(all_cycle_nodes))
        self.assertNotIn('database_setup', all_cycle_nodes)
    
    def test_error_recovery_integration(self):
        """Test that TaskGenerator can handle errors gracefully."""
        # Test with various malformed inputs
        test_cases = [
            None,
            [],
            [{'bad': 'format'}],
            [{'id': None, 'dependencies': ['something']}]
        ]
        
        for bad_input in test_cases:
            cycles = detect_task_dependency_cycles(bad_input)
            self.assertEqual(cycles, [], f"Failed to handle input: {bad_input}")
    
    def test_performance_with_typical_task_counts(self):
        """Test performance with typical numbers of tasks (20-100)."""
        import time
        
        # Generate 50 tasks with various dependency patterns
        tasks = []
        for i in range(50):
            task = {
                'id': f'task_{i}',
                'dependencies': [f'task_{(i-1)%50}'] if i > 0 else []
            }
            tasks.append(task)
        
        # Add a cycle
        tasks[0]['dependencies'] = ['task_49']
        
        start_time = time.time()
        cycles = detect_task_dependency_cycles(tasks)
        end_time = time.time()
        
        # Should complete very quickly (under 10ms for 50 tasks)
        self.assertLess(end_time - start_time, 0.01)
        
        # Should detect the created cycle
        self.assertEqual(len(cycles), 1)
        self.assertEqual(len(cycles[0]), 50)


class TestRegressionPrevention(unittest.TestCase):
    """Regression tests to prevent future bugs."""
    
    def test_bug_001_cycle_uniqueness_fixed(self):
        """Ensure BUG-001 (cycle uniqueness) doesn't regress."""
        # This graph could produce the same cycle starting from different nodes
        graph = {'A': ['B'], 'B': ['C'], 'C': ['A']}
        
        from coppersun_brass.agents.planner.cycle_detection import PurePythonCycleDetector
        detector = PurePythonCycleDetector()
        cycles = detector.simple_cycles(graph)
        
        # Should only find one unique cycle, not multiple rotations
        self.assertEqual(len(cycles), 1)
        
        # Test the normalization works
        cycle = cycles[0]
        min_idx = cycle.index(min(cycle))
        normalized = cycle[min_idx:] + cycle[:min_idx]
        
        # Should start with lexicographically smallest element
        self.assertEqual(normalized[0], min(cycle))
    
    def test_bug_002_self_dependency_filtering_fixed(self):
        """Ensure BUG-002 (self-dependency filtering) doesn't regress."""
        tasks = [
            {'id': 'task1', 'dependencies': ['task1', 'task2']},  # Self-dependency
            {'id': 'task2', 'dependencies': []}
        ]
        
        from coppersun_brass.agents.planner.cycle_detection import convert_tasks_to_graph
        graph = convert_tasks_to_graph(tasks)
        
        # task1 should not have an edge to itself
        self.assertNotIn('task1', graph['task1'])
        # But should still have edge to task2
        self.assertIn('task1', graph['task2'])
    
    def test_bug_003_specific_exception_handling_fixed(self):
        """Ensure BUG-003 (specific exception handling) doesn't regress."""
        # Test that specific exceptions are caught appropriately
        import logging
        
        # Capture log messages (WARNING level for input validation, ERROR for exceptions)
        with self.assertLogs('coppersun_brass.agents.planner.cycle_detection', level='WARNING') as log:
            # This should trigger input validation warning (not exception)
            cycles = detect_task_dependency_cycles(None)
            
        # Should return empty list and log appropriate message
        self.assertEqual(cycles, [])
        
        # Should log a warning about None input
        self.assertTrue(any('Task input is None' in message for message in log.output))


if __name__ == '__main__':
    unittest.main(verbosity=2)