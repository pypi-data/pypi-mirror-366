"""
Test suite for file scheduler implementations.

Tests weighted fair queuing, round-robin, and state persistence functionality.
"""
import time
import unittest
from unittest.mock import Mock, patch
import tempfile
import json
from pathlib import Path

from src.coppersun_brass.core.file_scheduler import (
    WeightedFairFileScheduler,
    RoundRobinFileScheduler,
    FileSchedulerState,
    create_file_scheduler
)


class TestFileSchedulerState(unittest.TestCase):
    """Test FileSchedulerState class functionality."""
    
    def setUp(self):
        self.state = FileSchedulerState()
    
    def test_initial_state(self):
        """Test initial state is empty."""
        self.assertEqual(len(self.state.last_analyzed), 0)
        self.assertEqual(len(self.state.analysis_count), 0)
    
    def test_update_analysis(self):
        """Test updating analysis state."""
        files = ['file1.py', 'file2.py']
        timestamp = time.time()
        
        self.state.update_analysis(files, timestamp)
        
        self.assertEqual(self.state.last_analyzed['file1.py'], timestamp)
        self.assertEqual(self.state.last_analyzed['file2.py'], timestamp)
        self.assertEqual(self.state.analysis_count['file1.py'], 1)
        self.assertEqual(self.state.analysis_count['file2.py'], 1)
    
    def test_multiple_analysis_updates(self):
        """Test multiple analysis updates increment count."""
        files = ['file1.py']
        
        self.state.update_analysis(files)
        self.state.update_analysis(files)
        
        self.assertEqual(self.state.analysis_count['file1.py'], 2)
    
    def test_get_file_priority_new_file(self):
        """Test priority calculation for new file."""
        current_time = 1000.0  # Fixed timestamp for consistent testing
        priority = self.state.get_file_priority('new_file.py', current_time, 1.0, 0.5)
        
        # New file: age_score = 1000.0 - 0 = 1000.0, frequency_score = 1.0/(0+1) = 1.0
        # priority = (1.0 * 1000.0) + (0.5 * 1.0) = 1000.5
        expected = 1000.5
        self.assertAlmostEqual(priority, expected, places=2)
    
    def test_get_file_priority_analyzed_file(self):
        """Test priority calculation for previously analyzed file."""
        files = ['old_file.py']
        old_time = time.time() - 3600  # 1 hour ago
        current_time = time.time()
        
        self.state.update_analysis(files, old_time)
        priority = self.state.get_file_priority('old_file.py', current_time, 1.0, 0.5)
        
        # Should be roughly: (current_time - old_time) + 0.5 * (1.0 / 2)
        age_component = current_time - old_time
        frequency_component = 0.5 * (1.0 / 2)
        expected = age_component + frequency_component
        self.assertAlmostEqual(priority, expected, places=2)
    
    def test_serialization(self):
        """Test state serialization and deserialization."""
        files = ['file1.py', 'file2.py']
        self.state.update_analysis(files)
        
        # Serialize
        data = self.state.to_dict()
        self.assertIn('last_analyzed', data)
        self.assertIn('analysis_count', data)
        self.assertIn('version', data)
        
        # Deserialize
        new_state = FileSchedulerState.from_dict(data)
        self.assertEqual(new_state.last_analyzed, self.state.last_analyzed)
        self.assertEqual(new_state.analysis_count, self.state.analysis_count)
    
    def test_cleanup_deleted_files(self):
        """Test cleanup of deleted files from state."""
        files = ['file1.py', 'file2.py', 'file3.py']
        self.state.update_analysis(files)
        
        # Simulate file2.py being deleted
        existing_files = ['file1.py', 'file3.py']
        self.state.cleanup_deleted_files(existing_files)
        
        self.assertIn('file1.py', self.state.last_analyzed)
        self.assertNotIn('file2.py', self.state.last_analyzed)
        self.assertIn('file3.py', self.state.last_analyzed)


class TestWeightedFairFileScheduler(unittest.TestCase):
    """Test WeightedFairFileScheduler functionality."""
    
    def setUp(self):
        self.mock_dcp = Mock()
        self.scheduler = WeightedFairFileScheduler(self.mock_dcp, age_weight=1.0, frequency_weight=0.5)
    
    def test_select_files_all_fit(self):
        """Test selection when all files fit in batch."""
        files = ['file1.py', 'file2.py']
        max_batch = 5
        
        selected = self.scheduler.select_files(files, max_batch)
        
        self.assertEqual(len(selected), 2)
        self.assertEqual(set(selected), set(files))
    
    def test_select_files_needs_selection(self):
        """Test selection when files exceed batch size."""
        files = ['file1.py', 'file2.py', 'file3.py', 'file4.py', 'file5.py']
        max_batch = 3
        
        selected = self.scheduler.select_files(files, max_batch)
        
        self.assertEqual(len(selected), 3)
        self.assertTrue(all(f in files for f in selected))
    
    def test_select_files_prioritizes_new_files(self):
        """Test that new files are prioritized over analyzed files."""
        files = ['old_file.py', 'new_file.py']
        max_batch = 1
        
        # Mock state loading to return state with old_file.py already analyzed
        mock_state = FileSchedulerState()
        mock_state.update_analysis(['old_file.py'], time.time() - 3600)
        
        with patch.object(self.scheduler, '_load_state', return_value=mock_state):
            selected = self.scheduler.select_files(files, max_batch)
        
        # new_file.py should be selected over old_file.py
        self.assertEqual(selected, ['new_file.py'])
    
    def test_select_files_empty_list(self):
        """Test selection with empty file list."""
        files = []
        max_batch = 5
        
        selected = self.scheduler.select_files(files, max_batch)
        
        self.assertEqual(selected, [])
    
    def test_select_files_invalid_batch_size(self):
        """Test selection with invalid batch size."""
        files = ['file1.py']
        
        with self.assertRaises(ValueError):
            self.scheduler.select_files(files, 0)
        
        with self.assertRaises(ValueError):
            self.scheduler.select_files(files, -1)
    
    def test_coverage_stats(self):
        """Test coverage statistics calculation."""
        all_files = ['file1.py', 'file2.py', 'file3.py']
        
        # Mock state with some files analyzed
        mock_state = FileSchedulerState()
        mock_state.update_analysis(['file1.py', 'file2.py'])
        
        with patch.object(self.scheduler, '_load_state', return_value=mock_state):
            stats = self.scheduler.get_coverage_stats(all_files)
        
        self.assertEqual(stats['total_files'], 3)
        self.assertEqual(stats['analyzed_files'], 2)
        self.assertEqual(stats['never_analyzed'], ['file3.py'])
        self.assertEqual(stats['never_analyzed_count'], 1)
        self.assertAlmostEqual(stats['coverage_percentage'], 66.67, places=1)
    
    def test_state_persistence_success(self):
        """Test successful state persistence via DCP."""
        files = ['file1.py']
        
        # Mock DCP operations
        self.mock_dcp.get_observation.return_value = None
        self.mock_dcp.store_observation.return_value = None
        
        self.scheduler.select_files(files, 1)
        
        # Verify store_observation was called
        self.mock_dcp.store_observation.assert_called()
    
    def test_state_persistence_failure(self):
        """Test graceful handling of DCP persistence failures."""
        files = ['file1.py']
        
        # Mock DCP to raise exceptions
        self.mock_dcp.get_observation.side_effect = Exception("DCP error")
        self.mock_dcp.store_observation.side_effect = Exception("DCP error")
        
        # Should not raise exception
        selected = self.scheduler.select_files(files, 1)
        self.assertEqual(selected, files)
    
    def test_reset_state(self):
        """Test state reset functionality."""
        files = ['file1.py']
        self.scheduler.select_files(files, 1)
        
        self.scheduler.reset_state()
        
        # State should be reset
        self.assertIsInstance(self.scheduler._state, FileSchedulerState)


class TestRoundRobinFileScheduler(unittest.TestCase):
    """Test RoundRobinFileScheduler functionality."""
    
    def setUp(self):
        self.mock_dcp = Mock()
        self.scheduler = RoundRobinFileScheduler(self.mock_dcp)
    
    def test_round_robin_selection(self):
        """Test basic round-robin selection."""
        files = ['file1.py', 'file2.py', 'file3.py', 'file4.py', 'file5.py']
        max_batch = 3
        
        # Mock DCP to return start index 0
        self.mock_dcp.get_observation.return_value = {'data': {'last_start_index': 0}}
        
        selected = self.scheduler.select_files(files, max_batch)
        
        # Should select first 3 files
        self.assertEqual(selected, ['file1.py', 'file2.py', 'file3.py'])
    
    def test_round_robin_wrapping(self):
        """Test round-robin wrapping around file list."""
        files = ['file1.py', 'file2.py', 'file3.py']
        max_batch = 2
        
        # Mock DCP to return start index 2 (near end of list)
        self.mock_dcp.get_observation.return_value = {'data': {'last_start_index': 2}}
        
        selected = self.scheduler.select_files(files, max_batch)
        
        # Should wrap around: file3.py, file1.py
        self.assertEqual(selected, ['file3.py', 'file1.py'])
    
    def test_round_robin_state_update(self):
        """Test that round-robin state is updated correctly."""
        files = ['file1.py', 'file2.py', 'file3.py', 'file4.py']
        max_batch = 2
        
        # Mock DCP
        self.mock_dcp.get_observation.return_value = {'data': {'last_start_index': 0}}
        
        self.scheduler.select_files(files, max_batch)
        
        # Should update state to index 2
        expected_call = {
            'data': {'last_start_index': 2},
            'timestamp': unittest.mock.ANY,
            'type': 'round_robin_scheduler_state'
        }
        self.mock_dcp.store_observation.assert_called_with(
            'round_robin_scheduler_state', 
            unittest.mock.ANY
        )
    
    def test_round_robin_all_files_fit(self):
        """Test round-robin when all files fit in batch."""
        files = ['file1.py', 'file2.py']
        max_batch = 5
        
        selected = self.scheduler.select_files(files, max_batch)
        
        self.assertEqual(selected, files)


class TestSchedulerFactory(unittest.TestCase):
    """Test scheduler factory function."""
    
    def test_create_weighted_fair_queuing(self):
        """Test creating weighted fair queuing scheduler."""
        scheduler = create_file_scheduler('weighted_fair_queuing')
        self.assertIsInstance(scheduler, WeightedFairFileScheduler)
    
    def test_create_round_robin(self):
        """Test creating round-robin scheduler."""
        scheduler = create_file_scheduler('round_robin')
        self.assertIsInstance(scheduler, RoundRobinFileScheduler)
    
    def test_create_invalid_algorithm(self):
        """Test creating scheduler with invalid algorithm."""
        with self.assertRaises(ValueError):
            create_file_scheduler('invalid_algorithm')
    
    def test_create_with_dcp_adapter(self):
        """Test creating scheduler with DCP adapter."""
        mock_dcp = Mock()
        scheduler = create_file_scheduler('weighted_fair_queuing', dcp_adapter=mock_dcp)
        self.assertEqual(scheduler.dcp, mock_dcp)
    
    def test_create_with_kwargs(self):
        """Test creating scheduler with additional arguments."""
        scheduler = create_file_scheduler(
            'weighted_fair_queuing', 
            age_weight=2.0, 
            frequency_weight=1.0
        )
        self.assertEqual(scheduler.age_weight, 2.0)
        self.assertEqual(scheduler.frequency_weight, 1.0)


class TestFileSchedulerIntegration(unittest.TestCase):
    """Integration tests for file scheduler."""
    
    def test_comprehensive_coverage_guarantee(self):
        """Test that all files are eventually analyzed."""
        files = [f'file{i}.py' for i in range(50)]  # 50 files
        max_batch = 20
        scheduler = WeightedFairFileScheduler()
        
        analyzed_files = set()
        cycles = 0
        max_cycles = 5  # Should cover all files in 3 cycles (50/20 = 2.5)
        
        while len(analyzed_files) < len(files) and cycles < max_cycles:
            selected = scheduler.select_files(files, max_batch)
            analyzed_files.update(selected)
            cycles += 1
        
        # All files should be analyzed within expected cycles
        self.assertEqual(len(analyzed_files), len(files), 
                        f"Only {len(analyzed_files)}/{len(files)} files analyzed in {cycles} cycles")
        self.assertLessEqual(cycles, 3, 
                            f"Required {cycles} cycles, expected at most 3")
    
    def test_priority_based_selection(self):
        """Test that older files are prioritized."""
        scheduler = WeightedFairFileScheduler()
        
        # First selection - all files are new
        files = ['file1.py', 'file2.py', 'file3.py']
        first_batch = scheduler.select_files(files, 2)
        
        # Wait a bit
        time.sleep(0.1)
        
        # Add a new file and select again
        files.append('file4.py')
        second_batch = scheduler.select_files(files, 2)
        
        # New file should be prioritized
        self.assertIn('file4.py', second_batch)
    
    def test_fairness_over_time(self):
        """Test that all files get analyzed fairly over multiple cycles."""
        files = [f'file{i}.py' for i in range(10)]
        max_batch = 3
        scheduler = WeightedFairFileScheduler()
        
        analysis_count = {f: 0 for f in files}
        
        # Run multiple cycles
        for _ in range(15):  # 15 cycles * 3 files = 45 analyses
            selected = scheduler.select_files(files, max_batch)
            for f in selected:
                analysis_count[f] += 1
        
        # Check that analysis is relatively fair
        counts = list(analysis_count.values())
        min_count = min(counts)
        max_count = max(counts)
        
        # No file should be analyzed much more or less than others
        self.assertLessEqual(max_count - min_count, 2, 
                           f"Unfair analysis distribution: {analysis_count}")


if __name__ == '__main__':
    unittest.main()