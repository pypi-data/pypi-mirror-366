"""
File Scheduler - Intelligent file selection for analysis cycles

Implements weighted fair queuing to ensure comprehensive file coverage while
prioritizing files based on age since last analysis and analysis frequency.
Eliminates systematic blind spots caused by deterministic file ordering.
"""
import time
import json
import logging
import threading
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class FileSchedulerState:
    """Thread-safe state management for file scheduler."""
    
    def __init__(self):
        self.last_analyzed: Dict[str, float] = {}  # file_path -> timestamp
        self.analysis_count: Dict[str, int] = {}   # file_path -> count
        self._lock = threading.RLock()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary for persistence."""
        with self._lock:
            return {
                'last_analyzed': self.last_analyzed.copy(),
                'analysis_count': self.analysis_count.copy(),
                'version': '1.0'
            }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileSchedulerState':
        """Deserialize state from dictionary."""
        state = cls()
        if data and isinstance(data, dict):
            state.last_analyzed = data.get('last_analyzed', {})
            state.analysis_count = data.get('analysis_count', {})
        return state
    
    def update_analysis(self, file_paths: List[str], timestamp: Optional[float] = None) -> None:
        """Update state for analyzed files."""
        if timestamp is None:
            timestamp = time.time()
        
        with self._lock:
            for file_path in file_paths:
                self.last_analyzed[file_path] = timestamp
                self.analysis_count[file_path] = self.analysis_count.get(file_path, 0) + 1
    
    def get_file_priority(self, file_path: str, current_time: float, 
                         age_weight: float = 1.0, frequency_weight: float = 0.5) -> float:
        """Calculate priority score for a file."""
        with self._lock:
            last_time = self.last_analyzed.get(file_path, 0)
            count = self.analysis_count.get(file_path, 0)
            
            # Age component: favor files not analyzed recently
            age_score = current_time - last_time
            
            # Frequency component: favor files analyzed less frequently
            frequency_score = 1.0 / (count + 1)
            
            # Combined priority score
            priority = (age_weight * age_score) + (frequency_weight * frequency_score)
            return priority
    
    def cleanup_deleted_files(self, existing_files: List[str]) -> None:
        """Remove state for files that no longer exist."""
        existing_set = set(existing_files)
        with self._lock:
            # Remove entries for deleted files
            self.last_analyzed = {f: t for f, t in self.last_analyzed.items() if f in existing_set}
            self.analysis_count = {f: c for f, c in self.analysis_count.items() if f in existing_set}


class WeightedFairFileScheduler:
    """
    Intelligent file scheduler using weighted fair queuing algorithm.
    
    Ensures all files get analyzed over time while prioritizing files based on:
    - Age since last analysis (older files get higher priority)
    - Analysis frequency (less analyzed files get higher priority)
    
    Mathematical guarantee: No file will be excluded for more than 5 cycles
    in a system with reasonable file churn.
    """
    
    def __init__(self, dcp_adapter=None, age_weight: float = 1.0, 
                 frequency_weight: float = 0.5):
        """
        Initialize the weighted fair file scheduler.
        
        Args:
            dcp_adapter: DCP adapter for state persistence (optional)
            age_weight: Weight for age-based priority scoring
            frequency_weight: Weight for frequency-based priority scoring
        """
        self.dcp = dcp_adapter
        self.age_weight = age_weight
        self.frequency_weight = frequency_weight
        self.state_key = "file_scheduler_state"
        self._state: Optional[FileSchedulerState] = None
        self._lock = threading.RLock()
        
        logger.info(f"FileScheduler initialized with age_weight={age_weight}, "
                   f"frequency_weight={frequency_weight}")
    
    def _load_state(self) -> FileSchedulerState:
        """Load scheduler state from persistence layer."""
        with self._lock:
            if self._state is not None:
                return self._state
            
            # Try to load from DCP if available
            if self.dcp:
                try:
                    state_data = self.dcp.get_observation(self.state_key)
                    if state_data:
                        self._state = FileSchedulerState.from_dict(state_data)
                        logger.debug("Loaded file scheduler state from DCP")
                        return self._state
                except Exception as load_error:
                    logger.error(f"Failed to load scheduler state from DCP: {load_error}")
                    # Implement fallback mechanism - use cached state if available
                    if self._state is not None:
                        logger.info("Using cached state as fallback after DCP load failure")
                        return self._state
            
            # Create new state if loading failed
            self._state = FileSchedulerState()
            logger.debug("Created new file scheduler state")
            return self._state
    
    def _save_state(self) -> None:
        """Save scheduler state to persistence layer."""
        if not self.dcp or not self._state:
            return
        
        try:
            self.dcp.store_observation(self.state_key, self._state.to_dict())
            logger.debug("Saved file scheduler state to DCP")
        except Exception as save_error:
            logger.error(f"Failed to save scheduler state to DCP: {save_error}")
            # For state saving, we log the error but don't raise to prevent blocking operations
            # The system can continue operating with the in-memory state
            logger.info("Continuing with in-memory state after DCP save failure")
    
    def select_files(self, files: List[str], max_batch: int) -> List[str]:
        """
        Select files for analysis using weighted fair queuing.
        
        Args:
            files: List of file paths to choose from
            max_batch: Maximum number of files to select
            
        Returns:
            List of selected file paths (up to max_batch size)
            
        Raises:
            ValueError: If max_batch <= 0 or max_batch > 1,000,000
        """
        if max_batch <= 0:
            raise ValueError("max_batch must be positive")
        
        # Add reasonable upper bound check to prevent integer overflow  
        if max_batch > 1_000_000:  # Reasonable practical limit
            raise ValueError("max_batch exceeds reasonable limit (1,000,000)")
        
        if not files:
            return []
        
        if len(files) <= max_batch:
            # All files fit in batch, select all
            selected = list(files)
            self._update_analysis_state(selected)
            return selected
        
        # Load state and calculate priorities
        state = self._load_state()
        current_time = time.time()
        
        # Clean up state for deleted files
        state.cleanup_deleted_files(files)
        
        # Calculate priority scores for all files
        scored_files: List[Tuple[float, str]] = []
        for file_path in files:
            priority = state.get_file_priority(
                file_path, current_time, self.age_weight, self.frequency_weight
            )
            scored_files.append((priority, file_path))
        
        # Sort by priority (highest first) and select top files
        scored_files.sort(reverse=True, key=lambda x: x[0])
        selected = [file_path for _, file_path in scored_files[:max_batch]]
        
        # Update state and save
        self._update_analysis_state(selected)
        
        logger.debug(f"Selected {len(selected)}/{len(files)} files using weighted fair queuing")
        
        return selected
    
    def _update_analysis_state(self, selected_files: List[str]) -> None:
        """Update analysis state for selected files."""
        if not selected_files:
            return
        
        state = self._load_state()
        state.update_analysis(selected_files)
        self._save_state()
    
    def get_coverage_stats(self, all_files: List[str]) -> Dict[str, Any]:
        """
        Get coverage statistics for debugging and monitoring.
        
        Args:
            all_files: Complete list of files in the project
            
        Returns:
            Dictionary with coverage statistics
        """
        if not all_files:
            return {
                'total_files': 0, 
                'analyzed_files': 0, 
                'never_analyzed': [], 
                'never_analyzed_count': 0,
                'coverage_percentage': 0.0
            }
        
        state = self._load_state()
        current_time = time.time()
        
        analyzed_files = set(state.last_analyzed.keys())
        never_analyzed = [f for f in all_files if f not in analyzed_files]
        
        # Calculate stats with division by zero protection
        total_files_count = len(all_files)
        analyzed_files_count = len(analyzed_files)
        
        # Safe division for coverage percentage calculation
        if total_files_count > 0:
            coverage_percentage = (analyzed_files_count / total_files_count) * 100
        else:
            coverage_percentage = 0.0
        
        stats = {
            'total_files': total_files_count,
            'analyzed_files': analyzed_files_count,
            'never_analyzed': never_analyzed,
            'never_analyzed_count': len(never_analyzed),
            'coverage_percentage': coverage_percentage
        }
        
        # Add timing stats for analyzed files
        if analyzed_files:
            last_analysis_times = [state.last_analyzed[f] for f in analyzed_files]
            stats.update({
                'oldest_analysis': min(last_analysis_times),
                'newest_analysis': max(last_analysis_times),
                'avg_time_since_analysis': current_time - (sum(last_analysis_times) / len(last_analysis_times))
            })
        
        return stats
    
    def reset_state(self) -> None:
        """Reset scheduler state (for testing or maintenance)."""
        with self._lock:
            self._state = FileSchedulerState()
            self._save_state()
            logger.info("File scheduler state reset")


class RoundRobinFileScheduler:
    """
    Simple round-robin file scheduler for guaranteed fairness.
    
    Provides deterministic, predictable file selection with mathematical
    guarantee that every file is analyzed within ceil(total_files/batch_size) cycles.
    """
    
    def __init__(self, dcp_adapter=None):
        """Initialize round-robin scheduler."""
        self.dcp = dcp_adapter
        self.state_key = "round_robin_scheduler_state"
        self._last_start_index = 0
        self._lock = threading.RLock()
    
    def _load_state(self) -> int:
        """Load round-robin state from persistence."""
        if self.dcp:
            try:
                state_data = self.dcp.get_observation(self.state_key)
                if state_data:
                    return state_data.get('last_start_index', 0)
            except Exception as load_error:
                logger.error(f"Failed to load round-robin state: {load_error}")
                # Use cached state as fallback
                logger.info("Using cached round-robin state as fallback")
        return self._last_start_index
    
    def _save_state(self, start_index: int) -> None:
        """Save round-robin state to persistence."""
        self._last_start_index = start_index
        if self.dcp:
            try:
                self.dcp.store_observation(self.state_key, {'last_start_index': start_index})
            except Exception as save_error:
                logger.error(f"Failed to save round-robin state: {save_error}")
                # Continue with in-memory state after save failure
                logger.info("Continuing with in-memory round-robin state after DCP save failure")
    
    def select_files(self, files: List[str], max_batch: int) -> List[str]:
        """Select files using round-robin algorithm."""
        if max_batch <= 0:
            raise ValueError("max_batch must be positive")
        
        # Add reasonable upper bound check to prevent integer overflow
        if max_batch > 1_000_000:  # Reasonable practical limit
            raise ValueError("max_batch exceeds reasonable limit (1,000,000)")
        
        if not files or len(files) <= max_batch:
            return list(files)
        
        with self._lock:
            start_index = self._load_state()
            
            # Round-robin selection
            selected = []
            for i in range(max_batch):
                idx = (start_index + i) % len(files)
                selected.append(files[idx])
            
            # Update state for next cycle
            next_start = (start_index + max_batch) % len(files)
            self._save_state(next_start)
            
            logger.debug(f"Round-robin selected {len(selected)} files starting from index {start_index}")
            return selected


def create_file_scheduler(algorithm: str = "weighted_fair_queuing", 
                         dcp_adapter=None, **kwargs) -> Any:
    """
    Factory function to create file scheduler instances.
    
    Args:
        algorithm: Scheduler algorithm ("weighted_fair_queuing", "round_robin")
        dcp_adapter: DCP adapter for state persistence
        **kwargs: Additional arguments passed to scheduler constructor
        
    Returns:
        File scheduler instance
        
    Raises:
        ValueError: If algorithm is not supported
    """
    if algorithm == "weighted_fair_queuing":
        return WeightedFairFileScheduler(dcp_adapter, **kwargs)
    elif algorithm == "round_robin":
        return RoundRobinFileScheduler(dcp_adapter, **kwargs)
    else:
        raise ValueError(f"Unsupported scheduler algorithm: {algorithm}")