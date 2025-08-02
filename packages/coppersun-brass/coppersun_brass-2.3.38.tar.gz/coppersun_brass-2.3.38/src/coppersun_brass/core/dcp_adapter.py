"""
DCP Adapter - Makes existing agents work with new SQLite storage

This adapter provides a DCPManager-compatible interface while using the
new SQLite storage backend. This allows us to fix the agents with minimal changes.
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import logging
import threading
import time
import heapq
from datetime import datetime
from contextlib import contextmanager

from .storage import BrassStorage

logger = logging.getLogger(__name__)


class DCPAdapter:
    """Adapter that mimics DCPManager interface but uses SQLite storage.
    
    This allows existing agents to work with minimal changes - just replace
    DCPManager with DCPAdapter in their __init__ methods.
    """
    
    def __init__(self, storage: Optional[BrassStorage] = None, 
                 dcp_path: Optional[str] = None):
        """Initialize adapter with storage backend.
        
        Supports both old DCPManager and new DCPAdapter calling conventions:
        
        Old style (DCPManager compatibility):
            DCPAdapter("/path/to/dcp")  # First arg is string path
            DCPAdapter(dcp_path="/path/to/dcp")  # Named path argument
            
        New style (DCPAdapter preferred):
            DCPAdapter(storage=brass_storage)  # BrassStorage object
            DCPAdapter()  # Use default storage
        
        Args:
            storage: BrassStorage instance (preferred) OR legacy path string
            dcp_path: Legacy parameter for compatibility
        """
        # Handle backward compatibility with old DCPManager calling convention
        if isinstance(storage, str):
            # Old style: DCPAdapter("/path/to/dcp") - first arg is path string
            logger.debug(f"DCPAdapter called with legacy path string: {storage}")
            dcp_path = storage
            storage = None
        elif storage is not None and not hasattr(storage, 'add_observation'):
            # Safety check: if storage doesn't look like BrassStorage, treat as path
            logger.info(f"DCPAdapter backward compatibility: Converting Path object to string for legacy DCPManager calling convention. Path: {storage}. This is normal behavior for Strategist components using 'DCPAdapter as DCPManager' import pattern. No action required.")
            dcp_path = str(storage)
            storage = None
            
        if storage is None:
            # Create default storage if not provided
            from ..config import BrassConfig
            config = BrassConfig()
            
            # Always use BrassConfig for unified storage - ignore dcp_path for database location
            # dcp_path is only used for project context, not database storage
            db_path = config.db_path
                
            storage = BrassStorage(db_path)
            logger.debug(f"Created BrassStorage at: {db_path}")
            
        self.storage = storage
        self._context_cache = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        
        # Cache management settings
        self._cache_max_size = 1000
        self._cache_cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()
        
        # Log that we're using the adapter
        logger.info("Using DCPAdapter for SQLite-based storage")
    
    def add_observation(self, *args, **kwargs):
        """Add observation to storage with backward compatibility.
        
        Supports both DCPManager and DCPAdapter API styles:
        
        DCPManager style (old):
            add_observation({'type': 'startup_time', 'data': {...}}, source_agent='agent')
            add_observation({'type': 'startup_time', 'data': {...}}, 'agent')
            
        DCPAdapter style (new):
            add_observation(obs_type='startup_time', data={...}, source_agent='agent', priority=50)
            
        Returns:
            String observation ID for compatibility (converts from int)
        """
        try:
            # Detect calling style by examining first argument
            if len(args) >= 1 and isinstance(args[0], dict):
                # Old DCPManager style: first arg is observation dictionary
                obs_dict = args[0]
                
                # Extract source_agent from args or kwargs
                if len(args) >= 2:
                    source_agent = args[1]
                else:
                    source_agent = kwargs.get('source_agent', 'unknown')
                
                # Extract observation details from dict
                obs_type = obs_dict.get('type', obs_dict.get('observation_type', 'unknown'))
                priority = obs_dict.get('priority', 50)
                
                # For old style, the entire dict becomes the data
                data = obs_dict
                
                logger.debug(f"DCPManager-style add_observation call: type={obs_type}, agent={source_agent}")
                
            else:
                # New DCPAdapter style: use individual parameters
                if len(args) >= 3:
                    obs_type, data, source_agent = args[0], args[1], args[2]
                    priority = args[3] if len(args) >= 4 else kwargs.get('priority', 50)
                else:
                    obs_type = args[0] if len(args) >= 1 else kwargs.get('obs_type', kwargs.get('observation_type', 'unknown'))
                    data = args[1] if len(args) >= 2 else kwargs.get('data', {})
                    source_agent = kwargs.get('source_agent', 'unknown')
                    priority = kwargs.get('priority', 50)
                
                logger.debug(f"DCPAdapter-style add_observation call: type={obs_type}, agent={source_agent}")
            
            # Call the underlying storage with the new API
            obs_id = self.storage.add_observation(
                obs_type=obs_type,
                data=data,
                source_agent=source_agent,
                priority=priority
            )
            
            logger.debug(f"Added observation {obs_id}: {obs_type} from {source_agent}")
            
            # Convert int ID to string for DCPManager compatibility
            return str(obs_id) if obs_id is not None else None
            
        except (TypeError, KeyError, ValueError) as e:
            # Expected errors from data validation or API compatibility issues
            logger.error(f"Data validation error in add_observation: {e}")
            return None
        except Exception as e:
            # Unexpected errors should be visible to callers
            logger.error(f"Unexpected error in add_observation: {e}")
            raise
    
    def update_metadata(self, updates: Dict[str, Any]) -> None:
        """Update context metadata (compatibility method).
        
        Args:
            updates: Metadata updates to apply
        """
        try:
            # Store as context snapshot
            current = self.storage.get_latest_context_snapshot('metadata') or {}
            current.update(updates)
            current['last_updated'] = datetime.utcnow().isoformat()
            
            self.storage.save_context_snapshot('metadata', current)
            
            # Update cache with atomic operations and rollback capability
            with self._lock:
                # Create backup for rollback in case of partial failure
                cache_backup = {key: self._context_cache.get(key) for key in updates.keys() if key in self._context_cache}
                
                try:
                    # Atomic cache update with consistent timestamps
                    current_time = time.time()
                    for key, value in updates.items():
                        # Ensure atomic update with access time tracking
                        if isinstance(value, dict):
                            value['_last_access'] = current_time
                        self._context_cache[key] = value  # Single atomic assignment
                    
                    # Periodic cleanup check (internal method that doesn't re-acquire lock)
                    self._maybe_cleanup_cache_internal()
                    
                except Exception as cache_error:
                    # Defensive rollback with verification
                    try:
                        for key in updates.keys():
                            if key in cache_backup:
                                self._context_cache[key] = cache_backup[key]
                            elif key in self._context_cache:
                                del self._context_cache[key]
                        
                        # Verify rollback succeeded for critical keys
                        for key, expected_value in cache_backup.items():
                            if key in self._context_cache:
                                if self._context_cache[key] != expected_value:
                                    logger.error(f"Rollback verification failed for key {key}")
                                    
                    except Exception as rollback_error:
                        logger.critical(f"Cache rollback failed: {rollback_error}. Cache may be in inconsistent state.")
                        # Consider clearing affected keys or marking cache as corrupted
                        
                    logger.error(f"Cache update failed, rolled back changes: {cache_error}")
                    raise  # Re-raise to trigger outer exception handler
            
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
            # Note: Storage operations may have partially succeeded, but cache is consistent
    
    def _maybe_cleanup_cache(self):
        """Check if cache cleanup is needed and perform it."""
        current_time = time.time()
        if (current_time - self._last_cleanup) > self._cache_cleanup_interval:
            self._cleanup_cache()
            self._last_cleanup = current_time
    
    def _maybe_cleanup_cache_internal(self):
        """Internal cleanup check that assumes lock is already held."""
        current_time = time.time()
        if (current_time - self._last_cleanup) > self._cache_cleanup_interval:
            self._cleanup_cache_internal()
            self._last_cleanup = current_time
    
    def _cleanup_cache_internal(self):
        """Internal cache cleanup that assumes lock is already held."""
        if len(self._context_cache) <= self._cache_max_size:
            return
            
        logger.info(f"Cleaning up cache: {len(self._context_cache)} items -> {self._cache_max_size}")
        self._perform_lru_cleanup()
    
    def _cleanup_cache(self):
        """Clean up cache using LRU strategy."""
        if len(self._context_cache) <= self._cache_max_size:
            return
            
        logger.info(f"Cleaning up cache: {len(self._context_cache)} items -> {self._cache_max_size}")
        self._perform_lru_cleanup()
    
    def _perform_lru_cleanup(self):
        """Shared LRU cleanup implementation with memory efficiency.
        
        Uses direct iterator to avoid unnecessary memory allocation from list conversion.
        Assumes caller holds the appropriate lock.
        """
        current_time = time.time()
        items_to_remove = len(self._context_cache) - self._cache_max_size
        
        # Helper function to get access time for heapq
        def get_access_time(item):
            key, value = item
            if isinstance(value, dict) and '_last_access' in value:
                return value['_last_access']
            else:
                return current_time - 3600  # Assume 1 hour old if no timestamp
        
        # Memory-efficient: Use direct iterator instead of list conversion
        # heapq.nsmallest can work directly with dict.items() iterator
        oldest_items = heapq.nsmallest(
            items_to_remove,
            self._context_cache.items(),  # Direct iterator - no list conversion needed
            key=get_access_time
        )
        
        # Remove oldest items from cache with existence check for thread safety
        for key, _ in oldest_items:
            if key in self._context_cache:
                del self._context_cache[key]
        
        logger.debug(f"Cache cleanup complete: {len(self._context_cache)} items remaining")
    
    def _parse_timestamp_safely(self, timestamp: str) -> datetime:
        """Safely parse various timestamp formats with fallback handling.
        
        Args:
            timestamp: String timestamp in various possible formats
            
        Returns:
            datetime object, using current time as fallback for unparseable timestamps
        """
        if not timestamp:
            logger.warning("Empty timestamp provided, using current time")
            return datetime.utcnow()
            
        # Try multiple common timestamp formats
        formats_to_try = [
            '%Y-%m-%dT%H:%M:%S.%fZ',           # ISO format with microseconds and Z
            '%Y-%m-%dT%H:%M:%SZ',              # ISO format without microseconds and Z
            '%Y-%m-%dT%H:%M:%S.%f%z',          # ISO format with microseconds and timezone
            '%Y-%m-%dT%H:%M:%S%z',             # ISO format with timezone
            '%Y-%m-%d %H:%M:%S.%f',            # Space-separated with microseconds
            '%Y-%m-%d %H:%M:%S',               # Space-separated without microseconds
        ]
        
        # First try the formats that don't require string manipulation
        for fmt in formats_to_try:
            try:
                return datetime.strptime(timestamp, fmt)
            except ValueError:
                continue
        
        # Try fromisoformat with safer string replacement
        try:
            # Handle common timezone suffixes
            clean_timestamp = timestamp
            if timestamp.endswith('Z'):
                clean_timestamp = timestamp[:-1] + '+00:00'
            elif '+' not in timestamp and '-' not in timestamp[-6:]:
                # Add UTC timezone if missing
                clean_timestamp = timestamp + '+00:00'
                
            return datetime.fromisoformat(clean_timestamp)
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse timestamp '{timestamp}': {e}. Using current time as fallback.")
            return datetime.utcnow()
    
    def get_observations(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """Get observations with filters and backward compatibility.
        
        Supports both DCPManager and DCPAdapter API styles:
        
        DCPManager style (old):
            get_observations()  # No filters
            get_observations({'type': 'feedback_entry', 'since': cutoff, 'limit': 100})
            get_observations(filters={'type': 'feedback_entry'})
            
        DCPAdapter style (new):
            get_observations(source_agent='agent', obs_type='type', since=datetime)
            
        Returns:
            List of observation dictionaries
        """
        try:
            # Detect calling style
            if len(args) == 0 and len(kwargs) == 0:
                # No arguments - return all observations (DCPManager style)
                logger.debug("DCPManager-style get_observations call: no filters")
                # Still apply compatibility conversion
                source_agent = None
                obs_type = None
                since = None
                limit = 1000
                
            elif len(args) == 1 and isinstance(args[0], dict):
                # Old DCPManager style: filters dictionary
                filters = args[0]
                logger.debug(f"DCPManager-style get_observations call: filters={filters}")
                
                # Extract common filter fields
                source_agent = filters.get('agent', filters.get('source_agent'))
                obs_type = filters.get('type', filters.get('obs_type', filters.get('observation_type')))
                since = filters.get('since')
                limit = filters.get('limit', 1000)  # Default limit if not specified
                
            elif 'filters' in kwargs:
                # DCPManager style with filters kwarg
                filters = kwargs['filters']
                logger.debug(f"DCPManager-style get_observations call: filters kwarg={filters}")
                
                source_agent = filters.get('agent', filters.get('source_agent'))
                obs_type = filters.get('type', filters.get('obs_type', filters.get('observation_type')))
                since = filters.get('since')
                limit = filters.get('limit', 1000)  # Default limit if not specified
                
            else:
                # New DCPAdapter style: individual parameters
                logger.debug("DCPAdapter-style get_observations call")
                source_agent = args[0] if len(args) >= 1 else kwargs.get('source_agent')
                obs_type = args[1] if len(args) >= 2 else kwargs.get('obs_type', kwargs.get('observation_type'))
                since = args[2] if len(args) >= 3 else kwargs.get('since')
                limit = kwargs.get('limit', 1000)  # Default limit if not specified
            
            
            # Call the underlying storage
            result = self.storage.get_observations(
                source_agent=source_agent,
                obs_type=obs_type,
                since=since,
                limit=limit,
                processed=False  # Only unprocessed by default
            )
            
            # Convert field names for compatibility and flatten data fields
            compatible_result = []
            for obs in result:
                compatible_obs = obs.copy()
                
                # Add obs_type field for DCPManager compatibility
                if 'type' in compatible_obs:
                    compatible_obs['obs_type'] = compatible_obs['type']
                
                # Flatten important data fields to top level for backward compatibility
                if 'data' in compatible_obs and isinstance(compatible_obs['data'], dict):
                    data = compatible_obs['data']
                    logger.debug(f"Flattening data fields: {list(data.keys())}")
                    # Add common fields to top level if they exist in data
                    for field in ['description', 'metadata', 'file_path', 'content']:
                        if field in data:
                            compatible_obs[field] = data[field]
                            logger.debug(f"Flattened field '{field}' to top level")
                
                # Ensure timestamp field exists at top level
                if 'created_at' in compatible_obs and 'timestamp' not in compatible_obs:
                    compatible_obs['timestamp'] = compatible_obs['created_at']
                
                compatible_result.append(compatible_obs)
            
            logger.debug(f"Retrieved {len(compatible_result)} observations")
            return compatible_result
            
        except (TypeError, KeyError, AttributeError) as e:
            # Expected errors from data parsing or compatibility issues
            logger.error(f"Data parsing error in get_observations: {e}")
            return []
        except Exception as e:
            # Unexpected errors should be visible to callers
            logger.error(f"Unexpected error in get_observations: {e}")
            raise
    
    def read_dcp(self, validate: bool = True) -> Dict[str, Any]:
        """Read DCP context (compatibility method).
        
        This method provides compatibility with DCPManager interface by calling
        the existing load_context() method. The validate parameter is accepted
        for compatibility but ignored since DCPAdapter uses SQLite storage.
        
        Args:
            validate: Validation flag (ignored for compatibility)
            
        Returns:
            Context dictionary with observations and metadata
        """
        try:
            logger.debug(f"read_dcp() called with validate={validate} (parameter ignored)")
            return self.load_context()
        except Exception as e:
            logger.error(f"Failed to read DCP context: {e}")
            return {'observations': [], 'metadata': {}, 'version': '2.0'}
    
    def load_context(self) -> Dict[str, Any]:
        """Load context (compatibility method).
        
        Returns:
            Context dictionary with observations and metadata
        """
        with self._lock:  # Ensure thread safety for context loading
            try:
                # Get recent observations
                observations = self.storage.get_observations(limit=100)
                
                # Get latest metadata
                metadata = self.storage.get_latest_context_snapshot('metadata') or {}
                
                # Get project info
                project_info = self.storage.get_latest_context_snapshot('project_info') or {}
                
                context = {
                    'observations': observations,
                    'metadata': metadata,
                    'project_info': project_info,
                    'version': '2.0'  # Indicate new storage version
                }
                
                return context
            except Exception as e:
                logger.error(f"Failed to load context: {e}")
                return {'observations': [], 'metadata': {}, 'version': '2.0'}
    
    def get_section(self, section: str, default: Any = None) -> Any:
        """Get a specific section from context (compatibility method).
        
        Args:
            section: Section name (e.g., 'metadata', 'project_info')
            default: Default value if section not found
            
        Returns:
            Section data or default
        """
        try:
            if section == 'observations':
                return self.storage.get_observations(limit=100)
            elif section == 'metadata':
                return self.storage.get_latest_context_snapshot('metadata') or default
            elif section == 'project_info':
                return self.storage.get_latest_context_snapshot('project_info') or default
            else:
                # Check if it's a nested path (e.g., 'metadata.version')
                parts = section.split('.')
                data = self.load_context()
                
                for part in parts:
                    if isinstance(data, dict) and part in data:
                        data = data[part]
                    else:
                        return default
                        
                return data
                
        except Exception as e:
            logger.error(f"Failed to get section {section}: {e}")
            return default
    
    def update_section(self, section: str, data: Any) -> None:
        """Update a specific section (compatibility method).
        
        Args:
            section: Section name to update
            data: New data for the section
        """
        with self._lock:  # Ensure thread safety for section updates
            try:
                # Handle different section types
                if section.startswith('observations'):
                    # Can't directly update observations - log warning
                    logger.warning("Cannot update observations section directly")
                    
                elif section in ['metadata', 'project_info']:
                    # Save as context snapshot
                    self.storage.save_context_snapshot(section, data)
                    
                else:
                    # Handle nested paths
                    if '.' in section:
                        # For nested updates, load current context, update, and save
                        parts = section.split('.')
                        root_section = parts[0]
                        
                        if root_section in ['metadata', 'project_info']:
                            current = self.storage.get_latest_context_snapshot(root_section) or {}
                            
                            # Navigate to nested location
                            target = current
                            for part in parts[1:-1]:
                                if part not in target:
                                    target[part] = {}
                                target = target[part]
                                
                            # Set the value
                            target[parts[-1]] = data
                            
                            # Save updated snapshot
                            self.storage.save_context_snapshot(root_section, current)
                            
            except Exception as e:
                logger.error(f"Failed to update section {section}: {e}")
    
    def get_project_type(self) -> str:
        """Get detected project type (compatibility method).
        
        Returns:
            Project type string
        """
        project_info = self.get_section('project_info', {})
        return project_info.get('project_type', 'unknown')
    
    def get_recent_changes(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent file changes (compatibility method).
        
        Args:
            limit: Maximum number of changes to return
            
        Returns:
            List of file change observations
        """
        return self.storage.get_observations(
            obs_type='file_modified',
            limit=limit
        )
    
    def get_current_sprint(self) -> str:
        """Get current sprint identifier (compatibility method).
        
        Returns:
            Sprint identifier or 'unknown'
        """
        metadata = self.get_section('metadata', {})
        return metadata.get('current_sprint', 'unknown')
    
    def get_patterns_for_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Get patterns detected in a specific file.
        
        Args:
            file_path: File to get patterns for
            
        Returns:
            List of patterns
        """
        try:
            all_patterns = self.storage.get_patterns()
            return [
                p for p in all_patterns 
                if p.get('file_path') == str(file_path)
            ]
        except Exception as e:
            logger.error(f"Failed to get patterns for {file_path}: {e}")
            return []
    
    def get_complexity_history(self, file_path: Path) -> List[int]:
        """Get complexity history for a file.
        
        Args:
            file_path: File to get history for
            
        Returns:
            List of complexity values (most recent last)
        """
        try:
            # For now, return current complexity as single-item list
            # Could be enhanced to track history over time
            metrics = self.storage.get_file_metrics()
            for metric in metrics:
                if metric['file_path'] == str(file_path):
                    return [metric.get('complexity', 0)]
            return []
            
        except Exception as e:
            logger.error(f"Failed to get complexity history: {e}")
            return []
    
    def get_file_change_patterns(self) -> List[Dict[str, Any]]:
        """Get patterns of files that change together.
        
        Returns:
            List of file change correlation patterns
        """
        try:
            # Get file change observations
            changes = self.storage.get_observations(
                obs_type='file_modified',
                limit=1000
            )
            
            # Group by timestamp proximity (simplified)
            # In production, would use more sophisticated correlation
            patterns = []
            
            # Group changes within 5-minute windows
            from collections import defaultdict
            time_groups = defaultdict(list)
            
            for change in changes:
                # Round to 5-minute window
                timestamp = change['created_at']
                if isinstance(timestamp, str):
                    # Robust timestamp parsing with multiple format support
                    dt = self._parse_timestamp_safely(timestamp)
                else:
                    dt = timestamp
                    
                window = dt.replace(minute=(dt.minute // 5) * 5, second=0, microsecond=0)
                time_groups[window].append(change['data'].get('file', ''))
            
            # Find files that frequently change together
            for window, files in time_groups.items():
                if len(files) > 1:
                    patterns.append({
                        'files': list(set(files)),
                        'correlation': 0.8,  # Simplified
                        'occurrences': 1
                    })
                    
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to get file change patterns: {e}")
            return []
    
    def cleanup(self):
        """Cleanup old data (maintenance method)."""
        try:
            self.storage.cleanup_old_data(days=30)
            logger.info("Cleaned up old data")
        except Exception as e:
            logger.error(f"Failed to cleanup: {e}")
    
    @contextmanager
    def lock(self):
        """Provide thread-safe lock context (mimics DCPManager.lock()).
        
        Usage:
            with dcp_adapter.lock():
                # Thread-safe operations here
                pass
        """
        with self._lock:
            yield
    
    def add_observations(self, observations: List[Dict[str, Any]], 
                        source_agent: str = "unknown") -> Dict[str, int]:
        """Add multiple observations in batch (mimics DCPManager.add_observations()).
        
        Args:
            observations: List of observation dictionaries
            source_agent: Agent creating the observations
            
        Returns:
            Dictionary with 'succeeded' and 'failed' counts
        """
        with self._lock:  # Ensure thread safety for batch operations
            succeeded = 0
            failed = 0
            
            for obs in observations:
                try:
                    # Extract observation data from the expected format
                    obs_type = obs.get('type', obs.get('observation_type', 'unknown'))
                    if obs_type == 'unknown':
                        logger.warning(f"Observation with unknown type: keys={list(obs.keys())}, obs={obs}")
                    data = obs.get('data', obs)  # Use 'data' field or entire obs
                    priority = obs.get('priority', 50)
                    
                    # Add the observation
                    obs_id = self.add_observation(
                        obs_type=obs_type,
                        data=data,
                        source_agent=source_agent,
                        priority=priority
                    )
                    
                    if obs_id is not None:
                        succeeded += 1
                    else:
                        failed += 1
                        
                except Exception as e:
                    logger.error(f"Failed to add observation: {e}")
                    failed += 1
            
            logger.info(f"Batch observation storage: {succeeded} succeeded, {failed} failed")
            return {
                'succeeded': succeeded,
                'failed': failed
            }
    
    def get_observation(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a single observation by key using context snapshots.
        
        Maps to storage.get_latest_context_snapshot() for single-observation access pattern.
        Used by components like FileScheduler that need key-based observation retrieval.
        
        Args:
            key: Unique identifier for the observation
            
        Returns:
            Observation data dictionary or None if not found
        """
        try:
            return self.storage.get_latest_context_snapshot(key)
        except Exception as e:
            logger.error(f"Failed to get observation {key}: {e}")
            return None
    
    def store_observation(self, key: str, data: Dict[str, Any]) -> None:
        """
        Store a single observation by key using context snapshots.
        
        Maps to storage.save_context_snapshot() for single-observation access pattern.
        Used by components like FileScheduler that need key-based observation storage.
        
        Args:
            key: Unique identifier for the observation
            data: Observation data to store
        """
        try:
            self.storage.save_context_snapshot(key, data)
            logger.debug(f"Stored observation {key}")
        except Exception as e:
            logger.error(f"Failed to store observation {key}: {e}")
    
    # Convenience properties for backward compatibility
    def get_dcp_info(self) -> Dict[str, Any]:
        """Get DCP adapter status information (compatibility method).
        
        Returns:
            Dictionary with DCP status information
        """
        try:
            # Get basic storage information - use most efficient counting method available
            try:
                # Priority order: exact count methods first, then fallback to estimation
                if hasattr(self.storage, 'get_observation_count'):
                    observations_count = self.storage.get_observation_count()
                elif hasattr(self.storage, 'count_observations'):
                    observations_count = self.storage.count_observations()
                else:
                    # Fallback: minimal query for estimation only
                    sample_observations = self.storage.get_observations(limit=100)
                    observations_count = len(sample_observations)
                    logger.debug("Using sample count for observation count (not exact total)")
            except Exception as count_error:
                logger.warning(f"Could not get observation count: {count_error}")
                observations_count = 0
            db_size = 0
            if hasattr(self.storage, 'db_path') and self.storage.db_path.exists():
                db_size = self.storage.db_path.stat().st_size
                
            return {
                'adapter_type': 'DCPAdapter',
                'storage_type': 'SQLite',
                'storage_path': str(self.storage.db_path),
                'storage_size_bytes': db_size,
                'observations_count': observations_count,
                'status': 'active'
            }
        except Exception as e:
            logger.error(f"Failed to get DCP info: {e}")
            return {
                'adapter_type': 'DCPAdapter',
                'status': 'error',
                'error': str(e)
            }
    
    def store_context(self, context_id: str, context_data: Dict[str, Any]) -> str:
        """Store context data by ID (compatibility method).
        
        Args:
            context_id: Unique identifier for context
            context_data: Context data to store
            
        Returns:
            Context ID for compatibility
        """
        try:
            self.storage.save_context_snapshot(context_id, context_data)
            logger.debug(f"Stored context {context_id}")
            return context_id
        except Exception as e:
            logger.error(f"Failed to store context {context_id}: {e}")
            return context_id  # Return ID even on failure for compatibility
    
    def get_latest_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Get latest context data by ID (compatibility method).
        
        Args:
            context_id: Context identifier to retrieve
            
        Returns:
            Context data or None if not found
        """
        try:
            return self.storage.get_latest_context_snapshot(context_id)
        except Exception as e:
            logger.error(f"Failed to get context {context_id}: {e}")
            return None
    
    @property
    def dcp_path(self) -> str:
        """Legacy property for compatibility."""
        return str(self.storage.db_path)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"DCPAdapter(storage={self.storage.db_path})"