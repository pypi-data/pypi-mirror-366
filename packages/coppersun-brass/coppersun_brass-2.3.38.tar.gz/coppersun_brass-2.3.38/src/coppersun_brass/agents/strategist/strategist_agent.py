# coppersun_brass/agents/strategist/strategist_agent.py
"""
Copper Sun Brass Strategist Agent - Central DCP Orchestration Hub
Coordinates all agent activities and maintains project intelligence
"""

import asyncio
import logging
import time
from collections import deque
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

# Event Bus removed - using DCP coordination
from coppersun_brass.core.dcp_adapter import DCPAdapter as DCPManager
from coppersun_brass.agents.strategist.priority_engine import PriorityEngine
from coppersun_brass.agents.strategist.duplicate_detector import DuplicateDetector
from coppersun_brass.agents.strategist.orchestration_engine import OrchestrationEngine
from coppersun_brass.agents.strategist.meta_reasoning.historical_analyzer import HistoricalAnalyzer
from coppersun_brass.agents.strategist.meta_reasoning.dcp_snapshot_manager import DCPSnapshotManager
from coppersun_brass.agents.strategist.meta_reasoning.diff_engine import DiffEngine
from coppersun_brass.agents.strategist.predictive.prediction_engine import PredictionEngine
from coppersun_brass.agents.strategist.predictive.prediction_config import PredictionConfig
from coppersun_brass.agents.strategist.planning.intelligence_coordinator import IntelligenceCoordinator
# BestPracticesEngine removed - replaced with evidence-based system in OutputGenerator
from coppersun_brass.agents.strategist.autonomous.gap_detector import GapDetector
from coppersun_brass.agents.base_agent import DCPAwareAgent
from coppersun_brass.core.context.dcp_coordination import DCPCoordinator, CoordinationMessage
from coppersun_brass.core.constants import AgentNames, TimeWindows, ObservationTypes

logger = logging.getLogger(__name__)

class StrategistAgent(DCPAwareAgent):
    """
    Central coordination agent for Copper Sun Brass ecosystem.
    Orchestrates DCP updates, prioritizes observations, and routes tasks.
    """
    
    def __init__(self, project_path: str, config: Optional[Dict] = None, dcp_path: Optional[str] = None, dcp_adapter: Optional[Any] = None):
        # Initialize DCP-aware base class
        super().__init__(
            project_path=project_path,
            dcp_path=dcp_path,
            dcp_adapter=dcp_adapter,
            context_window_hours=(config or {}).get('context_window_hours', TimeWindows.STRATEGIST_CONTEXT)
        )
        
        self.config = config or {}
        self.agent_id = AgentNames.STRATEGIST
        self._previous_boot = None  # Track hot vs cold starts
        
        # Core components
        self.priority_engine = PriorityEngine(self.config.get('priority', {}))
        self.duplicate_detector = DuplicateDetector(self.config.get('duplicates', {}))
        
        # Meta-reasoning components (defer snapshot manager to avoid concurrent DB access during init)
        # TODO FUTURE FEATURE: Re-enable when implementing historical analysis snapshots
        # snapshot_dir = self.project_path / ".brass" / "snapshots"
        # snapshot_dir.mkdir(parents=True, exist_ok=True)
        # self.snapshot_dir = snapshot_dir
        self.snapshot_dir = None  # Disabled: Feature not implemented yet
        self.snapshot_manager = None  # Lazy-loaded to prevent database conflicts during init
        self.diff_engine = DiffEngine()
        self.historical_analyzer = None  # Lazy-loaded since it depends on snapshot_manager
        
        # Predictive analytics components (defer to avoid DB conflicts)
        self.prediction_config = PredictionConfig()
        self.prediction_engine = None  # Lazy-loaded since it depends on historical_analyzer
        
        # Planning intelligence components
        self.intelligence_coordinator = IntelligenceCoordinator()
        # Integrations will be set lazily when components are initialized
        
        # Autonomous analysis components
        # BestPracticesEngine removed - replaced with evidence-based system in OutputGenerator
        self.best_practices_engine = None  # Set to None to avoid AttributeError in orchestration
        # Initialize GapDetector with the shared DCP adapter instead of creating its own
        self.gap_detector = GapDetector(
            project_root=self.project_path
        )
        # Pass shared DCP manager to prevent database conflicts
        if hasattr(self.gap_detector, 'dcp_manager') and self.dcp_manager:
            self.gap_detector.dcp_manager = self.dcp_manager
        
        # Initialize sophisticated AI analysis modules with lazy loading for better concurrency
        # These will be initialized on first access to avoid constructor complexity
        self.capability_assessor = None
        self.context_analyzer = None
        self.framework_detector = None
        self.dependency_analyzer = None
        self._sophisticated_modules_initialized = False
        
        # Initialize orchestration engine - sophisticated modules will be lazy-loaded
        # Pass None for sophisticated modules initially, they'll be initialized on first use
        self.orchestration_engine = OrchestrationEngine(
            self.dcp_manager, 
            self.priority_engine,
            self.duplicate_detector,
            self.best_practices_engine,
            self.gap_detector,
            None,  # capability_assessor - lazy loaded
            None,  # context_analyzer - lazy loaded
            None,  # framework_detector - lazy loaded
            None   # dependency_analyzer - lazy loaded
        )
        
        # State tracking
        self.last_orchestration = None
        self.orchestration_metrics = {
            'total_cycles': 0,
            'observations_processed': 0,
            'duplicates_detected': 0,
            'priorities_assigned': 0,
            'average_cycle_time': 0.0
        }
        
        # Context already loaded by base class
    
    def _ensure_components_initialized(self):
        """Lazy initialization of database-dependent components with performance tracking."""
        initialization_start = time.time()
        components_initialized = []
        
        if self.snapshot_manager is None:
            component_start = time.time()
            
            # Skip snapshot manager initialization if snapshot_dir is None (future feature)
            if self.snapshot_dir is None:
                logger.debug("Snapshot manager disabled - feature not implemented yet")
                # Create a dummy snapshot manager to avoid None checks elsewhere
                class DummySnapshotManager:
                    def capture_snapshot(self, *args, **kwargs): return "disabled"
                self.snapshot_manager = DummySnapshotManager()
            else:
                self.snapshot_manager = DCPSnapshotManager(
                    db_path=str(self.snapshot_dir / "snapshots.db"),
                    storage_path=str(self.snapshot_dir)
                )
            init_time = time.time() - component_start
            components_initialized.append(('snapshot_manager', init_time))
            logger.debug(f"Snapshot manager initialized in {init_time:.3f}s")
        
        if self.historical_analyzer is None:
            component_start = time.time()
            self.historical_analyzer = HistoricalAnalyzer(
                self.dcp_manager,
                self.snapshot_manager,
                self.diff_engine
            )
            init_time = time.time() - component_start
            components_initialized.append(('historical_analyzer', init_time))
            logger.debug(f"Historical analyzer initialized in {init_time:.3f}s")
        
        if self.prediction_engine is None:
            component_start = time.time()
            self.prediction_engine = PredictionEngine(
                self.historical_analyzer,
                self.dcp_manager,
                None,  # Event bus being phased out
                self.prediction_config
            )
            init_time = time.time() - component_start
            components_initialized.append(('prediction_engine', init_time))
            logger.debug(f"Prediction engine initialized in {init_time:.3f}s")
            
            # Set integrations now that components are ready
            integration_start = time.time()
            self.intelligence_coordinator.set_historical_analyzer(self.historical_analyzer)
            self.intelligence_coordinator.set_prediction_engine(self.prediction_engine)
            integration_time = time.time() - integration_start
            logger.debug(f"Intelligence coordinator integrations set in {integration_time:.3f}s")
        
        # Track total initialization time and component metrics
        total_time = time.time() - initialization_start
        if components_initialized:
            logger.info(f"AI components lazy loading: {len(components_initialized)} components initialized in {total_time:.3f}s")
            
            # Store initialization metrics for monitoring
            if not hasattr(self, '_initialization_metrics'):
                self._initialization_metrics = {
                    'total_initializations': 0,
                    'component_init_times': {},
                    'last_initialization': None,
                    'lazy_loading_triggers': {}
                }
            
            self._initialization_metrics['total_initializations'] += 1
            self._initialization_metrics['last_initialization'] = datetime.now(timezone.utc).isoformat()
            
            for component_name, init_time in components_initialized:
                if component_name not in self._initialization_metrics['component_init_times']:
                    # Use deque with maxlen for automatic bounds management
                    self._initialization_metrics['component_init_times'][component_name] = deque(maxlen=10)
                self._initialization_metrics['component_init_times'][component_name].append(init_time)
                # No manual bounds checking needed - deque handles it automatically
    
    def _track_lazy_loading_trigger(self, method_name: str):
        """Track which methods trigger lazy loading for monitoring purposes."""
        if not hasattr(self, '_initialization_metrics'):
            self._initialization_metrics = {
                'total_initializations': 0,
                'component_init_times': {},
                'last_initialization': None,
                'lazy_loading_triggers': {}
            }
        
        if method_name not in self._initialization_metrics['lazy_loading_triggers']:
            self._initialization_metrics['lazy_loading_triggers'][method_name] = 0
        
        self._initialization_metrics['lazy_loading_triggers'][method_name] += 1
        logger.debug(f"Lazy loading triggered by {method_name} (total: {self._initialization_metrics['lazy_loading_triggers'][method_name]})")
    
    def get_initialization_metrics(self) -> Dict[str, Any]:
        """Get AI component initialization metrics for monitoring."""
        if not hasattr(self, '_initialization_metrics'):
            return {
                'total_initializations': 0,
                'component_init_times': {},
                'last_initialization': None,
                'lazy_loading_triggers': {},
                'average_init_times': {}
            }
        
        metrics = self._initialization_metrics.copy()
        
        # Calculate average initialization times
        metrics['average_init_times'] = {}
        for component, times in metrics['component_init_times'].items():
            if times:
                metrics['average_init_times'][component] = sum(times) / len(times)
        
        return metrics
    
    def _ensure_sophisticated_modules_initialized(self):
        """Lazy initialization of sophisticated AI analysis modules for better concurrency."""
        if self._sophisticated_modules_initialized:
            return
            
        initialization_start = time.time()
        
        try:
            from coppersun_brass.agents.strategist.autonomous.capability_assessor import CapabilityAssessor
            from coppersun_brass.agents.strategist.autonomous.context_analyzer import ProjectContextAnalyzer
            from coppersun_brass.agents.strategist.autonomous.framework_detector import FrameworkDetector
            from coppersun_brass.agents.strategist.autonomous.dependency_analyzer import DependencyAnalyzer
            
            # Initialize all sophisticated analysis modules
            self.capability_assessor = CapabilityAssessor(project_root=self.project_path)
            self.context_analyzer = ProjectContextAnalyzer()
            self.framework_detector = FrameworkDetector()
            self.dependency_analyzer = DependencyAnalyzer()
            
            # Share DCP manager with modules that support it
            if hasattr(self.capability_assessor, 'dcp_manager') and self.dcp_manager:
                self.capability_assessor.dcp_manager = self.dcp_manager
            
            self._sophisticated_modules_initialized = True
            init_time = time.time() - initialization_start
            logger.info(f"Sophisticated AI analysis modules lazily initialized in {init_time:.3f}s")
            
        except ImportError as e:
            logger.warning(f"Sophisticated analysis modules not available: {e}")
            self.capability_assessor = None
            self.context_analyzer = None
            self.framework_detector = None
            self.dependency_analyzer = None
            self._sophisticated_modules_initialized = True  # Mark as "initialized" to avoid retries
    
    def _get_capability_assessor(self):
        """Get capability assessor with lazy initialization."""
        self._ensure_sophisticated_modules_initialized()
        return self.capability_assessor
    
    def _get_context_analyzer(self):
        """Get context analyzer with lazy initialization."""
        self._ensure_sophisticated_modules_initialized()
        return self.context_analyzer
    
    def _get_framework_detector(self):
        """Get framework detector with lazy initialization."""
        self._ensure_sophisticated_modules_initialized()
        return self.framework_detector
    
    def _get_dependency_analyzer(self):
        """Get dependency analyzer with lazy initialization."""
        self._ensure_sophisticated_modules_initialized()
        return self.dependency_analyzer
    
    @property
    def agent_name(self) -> str:
        """Return the agent's identifier."""
        return AgentNames.STRATEGIST
    
    @property
    def relevant_observation_types(self) -> List[str]:
        """Define which observation types this agent needs on startup."""
        return [
            'capability_assessment', 'strategic_recommendation',
            'orchestration_complete', 'priority_assignment',
            'duplicate_detection', 'gap_detection', 'best_practice'
        ]
        
        logger.info(f"Strategist Agent initialized for project: {project_path}")
    
    
    def _process_startup_context(self, context: Dict[str, List[Dict[str, Any]]]) -> None:
        """Process loaded context from base class.
        
        Args:
            context: Dict mapping observation types to lists of observations
        """
        # Track startup timing for metrics
        start_time = time.time()
        
        # Extract observations by type
        capability_assessments = context.get('capability_assessment', [])
        strategic_recommendations = context.get('strategic_recommendation', [])
        orchestration_history = context.get('orchestration_complete', [])
        priority_history = context.get('priority_assignment', [])
        duplicate_history = context.get('duplicate_detection', [])
        
        # Initialize decision state from context
        self._initialize_strategy(
            capability_assessments,
            strategic_recommendations,
            orchestration_history,
            priority_history,
            duplicate_history
        )
        
        # Log what was loaded
        total_observations = sum(len(obs_list) for obs_list in context.values())
        is_cold_start = total_observations == 0
        logger.info(f"Strategist processed {total_observations} observations from startup context")
        self._previous_boot = 'hot' if total_observations > 0 else 'cold'
        
        if self.dcp_manager:
            self.dcp_manager.add_observation({
                'type': 'startup_time',
                'agent': 'strategist',
                'duration_ms': (time.time() - start_time) * 1000,
                'is_cold_start': is_cold_start,
                'observations_loaded': total_observations,
                'context_categories': ['capability_assessment', 'strategic_recommendation', 
                                     'orchestration_complete', 'priority_assignment', 'duplicate_detection'],
                'components_initialized': self._get_component_count()
            }, source_agent='strategist')
                
        logger.info(f"Strategist agent loaded context: {len(capability_assessments)} assessments, "
                   f"{len(strategic_recommendations)} recommendations, {len(orchestration_history)} orchestrations")
    
    def _initialize_strategy(self, capability_assessments, strategic_recommendations, 
                           orchestration_history, priority_history, duplicate_history):
        """Initialize decision state from loaded DCP context."""
        
        # Configure priority engine based on historical assignments
        if priority_history:
            # Extract priority patterns from history
            priority_scores = []
            for obs in priority_history[-20:]:  # Last 20 priority assignments
                if 'details' in obs and 'calculated_priority' in obs['details']:
                    priority_scores.append(obs['details']['calculated_priority'])
            
            if priority_scores:
                avg_priority = sum(priority_scores) / len(priority_scores)
                # Adjust priority thresholds based on historical patterns
                if hasattr(self.priority_engine, 'adjust_thresholds'):
                    self.priority_engine.adjust_thresholds(baseline=avg_priority)
                logger.debug(f"Adjusted priority thresholds based on avg priority: {avg_priority:.1f}")
        
        # Configure duplicate detector based on detection history
        if duplicate_history:
            # Extract duplicate patterns
            duplicate_patterns = set()
            for obs in duplicate_history[-10:]:  # Last 10 duplicate detections
                if 'details' in obs and 'duplicate_type' in obs['details']:
                    duplicate_patterns.add(obs['details']['duplicate_type'])
            
            # Update duplicate detector sensitivity
            if duplicate_patterns and hasattr(self.duplicate_detector, 'update_patterns'):
                self.duplicate_detector.update_patterns(list(duplicate_patterns))
                logger.debug(f"Updated duplicate patterns: {duplicate_patterns}")
        
        # Set orchestration timing based on history
        if orchestration_history:
            # Calculate average orchestration cycle time
            cycle_times = []
            for obs in orchestration_history[-5:]:  # Last 5 orchestrations
                if 'details' in obs and 'cycle_time' in obs['details']:
                    cycle_times.append(obs['details']['cycle_time'])
            
            if cycle_times:
                avg_cycle_time = sum(cycle_times) / len(cycle_times)
                self.orchestration_metrics['average_cycle_time'] = avg_cycle_time
                logger.debug(f"Set expected cycle time based on history: {avg_cycle_time:.2f}s")
        
        # Initialize prediction engine with historical data
        if strategic_recommendations and self.prediction_engine and hasattr(self.prediction_engine, 'initialize_from_recommendations'):
            self.prediction_engine.initialize_from_recommendations(strategic_recommendations)
        
        # _previous_boot is already set by base class based on startup observations
        # Don't override it here
    
    def _cold_boot_initialization(self):
        """Initialize agent without DCP context (fallback mode)."""
        logger.info("Strategist agent starting in cold boot mode")
        # Set conservative defaults
        self.orchestration_metrics['average_cycle_time'] = 5.0  # Conservative 5s estimate
        self._previous_boot = None
        
        # Initialize components with default settings
        if hasattr(self.priority_engine, 'reset_to_defaults'):
            self.priority_engine.reset_to_defaults()
        if hasattr(self.duplicate_detector, 'reset_to_defaults'):
            self.duplicate_detector.reset_to_defaults()
    
    def _get_component_count(self) -> int:
        """Get count of initialized components."""
        components = [
            self.priority_engine, self.duplicate_detector, self.orchestration_engine,
            self.snapshot_manager, self.diff_engine, self.historical_analyzer,
            self.prediction_engine, self.intelligence_coordinator,
            self.best_practices_engine, self.gap_detector
        ]
        return len([c for c in components if c is not None])
    
    async def orchestrate_dcp_updates(self, force: bool = False) -> Dict[str, Any]:
        """
        Main orchestration cycle - coordinates all DCP updates
        
        Args:
            force: Force orchestration even if no changes detected
            
        Returns:
            Dict with orchestration results and metrics
        """
        # Ensure components are initialized before use
        self._ensure_components_initialized()
        
        start_time = time.time()
        
        try:
            logger.info("Starting DCP orchestration cycle")
            
            # Load current DCP state
            current_dcp = self.dcp_manager.read_dcp()
            
            # Check if orchestration needed
            if not force and not self._needs_orchestration(current_dcp):
                logger.debug("No orchestration needed")
                return {'status': 'skipped', 'reason': 'no_changes'}
            
            # Run orchestration
            result = await self.orchestration_engine.orchestrate(current_dcp)
            
            # Update metrics
            cycle_time = time.time() - start_time
            self._update_metrics(result, cycle_time)
            
            # Dual publish during migration
            orchestration_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'result': result,
                'cycle_time': cycle_time
            }
            
            # Publish via DCP coordination
            if hasattr(self, 'dcp_coordinator') and self.dcp_coordinator:
                self.dcp_coordinator.publish(CoordinationMessage(
                    observation_type=ObservationTypes.ORCHESTRATION_COMPLETE,
                    source_agent=self.agent_name,
                    data=orchestration_data,
                    metadata={'cycle_time': cycle_time},
                    broadcast=True
                ))
            
            self.last_orchestration = datetime.now(timezone.utc)
            
            logger.info(f"Orchestration cycle complete in {cycle_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Orchestration cycle failed: {e}", exc_info=True)
            return {'status': 'error', 'error': str(e)}
    
    def analyze_patterns(self, observations: List[Dict]) -> List[Dict]:
        """
        Analyze patterns in observations using basic pattern detection.
        
        Args:
            observations: List of observation dictionaries
            
        Returns:
            List of pattern analysis results
        """
        # Track lazy loading trigger and ensure components are initialized
        self._track_lazy_loading_trigger('analyze_patterns')
        self._ensure_components_initialized()
        
        try:
            patterns = []
            
            # Basic pattern analysis - group by type and detect frequencies
            type_counts = {}
            priority_patterns = {}
            source_patterns = {}
            
            for obs in observations:
                obs_type = obs.get('type', 'unknown')
                priority = obs.get('priority', 50)
                source = obs.get('source_agent', 'unknown')
                
                # Count observation types
                type_counts[obs_type] = type_counts.get(obs_type, 0) + 1
                
                # Track priority patterns by type
                if obs_type not in priority_patterns:
                    priority_patterns[obs_type] = []
                priority_patterns[obs_type].append(priority)
                
                # Track source patterns
                source_patterns[source] = source_patterns.get(source, 0) + 1
            
            # Generate pattern insights
            for obs_type, count in type_counts.items():
                if count > 1:  # Only analyze types with multiple instances
                    avg_priority = sum(priority_patterns[obs_type]) / len(priority_patterns[obs_type])
                    
                    pattern = {
                        'type': 'pattern_analysis',
                        'pattern_type': 'observation_frequency',
                        'observation_type': obs_type,
                        'frequency': count,
                        'average_priority': avg_priority,
                        'confidence': min(0.9, count / 10.0),  # Higher confidence with more samples
                        'recommendation': f"Observed {count} instances of {obs_type} with avg priority {avg_priority:.1f}"
                    }
                    patterns.append(pattern)
                    
                    # Store pattern in DCP for other agents
                    if self.dcp_manager:
                        self.dcp_manager.add_observation(
                            obs_type='pattern_analysis',
                            data=pattern,
                            source_agent=self.agent_name,
                            priority=int(avg_priority)
                        )
            
            logger.info(f"Pattern analysis completed: {len(patterns)} patterns identified")
            return patterns
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return []
    
    def prioritize_observations(self, observations: List[Dict]) -> List[Dict]:
        """
        Score and rank observations by priority
        
        Args:
            observations: List of observation dictionaries
            
        Returns:
            Observations sorted by priority (highest first)
        """
        logger.debug(f"Prioritizing {len(observations)} observations")
        
        # Score each observation
        scored_observations = []
        for obs in observations:
            try:
                priority_score = self.priority_engine.calculate_priority(obs)
                obs_with_score = obs.copy()
                obs_with_score['calculated_priority'] = priority_score
                obs_with_score['priority_rationale'] = self.priority_engine.get_rationale(obs)
                scored_observations.append(obs_with_score)
            except Exception as e:
                logger.warning(f"Failed to score observation {obs.get('id', 'unknown')}: {e}")
                # Keep original priority or assign default
                obs_with_score = obs.copy()
                obs_with_score['calculated_priority'] = obs.get('priority', 50)
                scored_observations.append(obs_with_score)
        
        # Sort by calculated priority (descending)
        prioritized = sorted(
            scored_observations, 
            key=lambda x: x['calculated_priority'], 
            reverse=True
        )
        
        logger.info(f"Prioritized observations: {len(prioritized)} total")
        return prioritized
    
    def detect_duplicates(self, observations: List[Dict]) -> Dict[str, List[str]]:
        """
        Identify duplicate observations across agents
        
        Args:
            observations: List of observations to check
            
        Returns:
            Dict mapping canonical observation IDs to lists of duplicate IDs
        """
        return self.duplicate_detector.find_duplicates(observations)
    
    def route_tasks_to_agents(self, observations: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Route observations to appropriate agents for action
        
        Args:
            observations: Prioritized observations
            
        Returns:
            Dict mapping agent names to their assigned tasks
        """
        routing = {
            'watch': [],
            'scout': [],
            'claude': [],
            'human': []
        }
        
        for obs in observations:
            obs_type = obs.get('type', 'unknown')
            priority = obs.get('calculated_priority', obs.get('priority', 50))
            
            # Routing logic based on observation type and priority
            if obs_type in ['todo_item', 'fixme_item', 'research_needed']:
                # High priority TODOs go to Claude, others to Scout
                if priority >= 80:
                    routing['claude'].append(obs)
                else:
                    routing['scout'].append(obs)
            
            elif obs_type in ['security', 'critical_bug']:
                # Security issues always go to human review
                routing['human'].append(obs)
            
            elif obs_type in ['file_change', 'code_analysis']:
                # File changes handled by Watch agent
                routing['watch'].append(obs)
            
            elif obs_type in ['performance', 'optimization']:
                # Performance issues can be handled by Claude
                routing['claude'].append(obs)
            
            else:
                # Default routing based on priority
                if priority >= 90:
                    routing['human'].append(obs)
                elif priority >= 70:
                    routing['claude'].append(obs)
                else:
                    routing['scout'].append(obs)
        
        # Log routing decisions
        for agent, tasks in routing.items():
            if tasks:
                logger.info(f"Routed {len(tasks)} tasks to {agent}")
        
        return routing
    
    def _handle_agent_status_observation(self, observation: Dict[str, Any]):
        """Handle agent status observations from DCP."""
        metadata = observation.get('metadata', {})
        data = observation.get('data', {})
        source = metadata.get('source_agent', 'unknown')
        status = metadata.get('status', 'unknown')
        
        logger.info(f"Agent {source} status: {status}")
        
        # Could trigger orchestration if key agent comes online
        if status == 'started' and source in ['watch', 'scout']:
            self._schedule_orchestration()
    
    def _handle_analysis_result_observation(self, observation: Dict[str, Any]):
        """Handle analysis result observations from DCP."""
        # Trigger orchestration to process new analysis results
        self._schedule_orchestration()
    
    def _handle_todo_observation(self, observation: Dict[str, Any]):
        """Handle TODO observations from DCP."""
        # High priority TODOs might trigger immediate orchestration
        metadata = observation.get('metadata', {})
        priority = metadata.get('priority', 50)
        
        if priority >= 80:
            logger.info(f"High priority TODO detected, scheduling orchestration")
            self._schedule_orchestration()
    
    def _schedule_orchestration(self):
        """Schedule an orchestration cycle with robust event loop handling."""
        # This could be enhanced with debouncing/throttling
        try:
            import asyncio
            
            # Check if event loop is running before creating task
            try:
                loop = asyncio.get_running_loop()
                # Event loop is running, safe to create task
                asyncio.create_task(self.orchestrate_dcp_updates())
                logger.debug("Orchestration task scheduled in running event loop")
            except RuntimeError:
                # No event loop running, defer orchestration
                logger.info("No event loop running, orchestration deferred until agent start")
                # Store flag to trigger orchestration when event loop becomes available
                self._pending_orchestration = True
                
        except Exception as e:
            logger.error(f"Failed to schedule orchestration: {e}")
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current strategist status and metrics"""
        return {
            'agent_id': self.agent_id,
            'last_orchestration': self.last_orchestration.isoformat() if self.last_orchestration else None,
            'metrics': self.orchestration_metrics.copy(),
            'dcp_coordinator_active': hasattr(self, 'dcp_coordinator') and self.dcp_coordinator is not None,
            'dcp_status': self.dcp_manager.get_dcp_info(),
            'components': {
                'priority_engine': self.priority_engine.get_status(),
                'duplicate_detector': self.duplicate_detector.get_status(),
                'orchestration_engine': self.orchestration_engine.get_status(),
                'sophisticated_modules': {
                    'capability_assessor': 'available' if self._get_capability_assessor() else 'unavailable',
                    'context_analyzer': 'available' if self._get_context_analyzer() else 'unavailable', 
                    'framework_detector': 'available' if self._get_framework_detector() else 'unavailable',
                    'dependency_analyzer': 'available' if self._get_dependency_analyzer() else 'unavailable'
                }
            }
        }
    
    def _needs_orchestration(self, current_dcp: Dict) -> bool:
        """Determine if orchestration cycle is needed"""
        # Check for new observations since last orchestration
        if not self.last_orchestration:
            return True
        
        # Check for recent DCP modifications
        try:
            dcp_path = self.dcp_manager.dcp_file_path
            if dcp_path.exists():
                dcp_modified = datetime.fromtimestamp(dcp_path.stat().st_mtime, tz=timezone.utc)
                if dcp_modified > self.last_orchestration:
                    return True
        except (OSError, PermissionError, AttributeError) as e:
            logger.warning(f"Could not check DCP file modification time: {e}")
        except Exception as e:
            logger.error(f"Unexpected error checking DCP modifications: {e}")
        
        # Check for unprocessed observations
        observations = current_dcp.get('current_observations', [])
        unprocessed = [obs for obs in observations if not obs.get('strategist_processed')]
        
        return len(unprocessed) > 0
    
    def _update_metrics(self, result: Dict, cycle_time: float):
        """Update orchestration metrics"""
        self.orchestration_metrics['total_cycles'] += 1
        self.orchestration_metrics['observations_processed'] += result.get('observations_processed', 0)
        self.orchestration_metrics['duplicates_detected'] += result.get('duplicates_found', 0)
        self.orchestration_metrics['priorities_assigned'] += result.get('priorities_updated', 0)
        
        # Update average cycle time
        total_cycles = self.orchestration_metrics['total_cycles']
        current_avg = self.orchestration_metrics['average_cycle_time']
        self.orchestration_metrics['average_cycle_time'] = (
            (current_avg * (total_cycles - 1) + cycle_time) / total_cycles
        )
    
    # Historical Analysis Methods
    async def capture_snapshot(self, tags: Optional[List[str]] = None) -> str:
        """Capture a DCP snapshot for historical analysis"""
        try:
            current_dcp = self.dcp_manager.read_dcp()
            snapshot_id = await self.snapshot_manager.capture_snapshot(
                project_id=str(self.project_path.name),
                dcp_data=current_dcp,
                tags=tags or []
            )
            logger.info(f"Captured DCP snapshot: {snapshot_id}")
            return snapshot_id
        except Exception as e:
            logger.error(f"Failed to capture snapshot: {e}")
            raise
    
    async def analyze_trends(self, timeframe_days: int = 30) -> Dict:
        """
        Analyze DCP trends over specified timeframe with integrated storage.
        
        Args:
            timeframe_days: Number of days to analyze (default 30)
            
        Returns:
            Dictionary containing trend analysis results
        """
        # Track lazy loading trigger and ensure components are initialized
        self._track_lazy_loading_trigger('analyze_trends')
        self._ensure_components_initialized()
        
        try:
            # Get trend analysis from historical analyzer if available
            trends = {}
            if self.historical_analyzer:
                trends = await self.historical_analyzer.analyze_trends(
                    project_id=str(self.project_path.name),
                    timeframe_days=timeframe_days
                )
            else:
                # Basic trend analysis if historical analyzer not available
                logger.info("Historical analyzer not available, performing basic trend analysis")
                current_observations = self.dcp_manager.get_observations() if self.dcp_manager else []
                
                # Analyze observation trends over time
                trends = {
                    'timeframe_days': timeframe_days,
                    'total_observations': len(current_observations),
                    'observation_types': {},
                    'priority_distribution': {'high': 0, 'medium': 0, 'low': 0},
                    'trend_summary': 'Basic trend analysis - historical analyzer not available'
                }
                
                for obs in current_observations:
                    obs_type = obs.get('type', 'unknown')
                    priority = obs.get('priority', 50)
                    
                    trends['observation_types'][obs_type] = trends['observation_types'].get(obs_type, 0) + 1
                    
                    if priority >= 80:
                        trends['priority_distribution']['high'] += 1
                    elif priority >= 50:
                        trends['priority_distribution']['medium'] += 1
                    else:
                        trends['priority_distribution']['low'] += 1
            
            # Store trend analysis results in DCP for other agents and output generation
            if self.dcp_manager and trends:
                self.dcp_manager.add_observation(
                    obs_type='trend_analysis',
                    data={
                        'type': 'trend_analysis',
                        'timeframe_days': timeframe_days,
                        'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                        'trends': trends,
                        'source': 'strategist_agent'
                    },
                    source_agent=self.agent_name,
                    priority=70  # Medium-high priority for strategic information
                )
                logger.info(f"Trend analysis stored in DCP for output generation")
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")
            return {}
    
    async def generate_health_score(self) -> Dict:
        """
        Generate project health score based on historical data with robust error handling.
        
        Returns:
            Dictionary containing health score metrics and analysis
        """
        # Track lazy loading trigger and ensure components are initialized
        self._track_lazy_loading_trigger('generate_health_score')
        self._ensure_components_initialized()
        
        try:
            health_score = {}
            
            if self.historical_analyzer:
                # Try to call the historical analyzer with proper error handling
                try:
                    health = await self.historical_analyzer.generate_health_score(
                        project_id=str(self.project_path.name)
                    )
                    health_score = health.__dict__ if hasattr(health, '__dict__') else health or {}
                except TypeError as e:
                    # Handle method signature mismatch
                    logger.warning(f"Historical analyzer method signature issue: {e}")
                    # Try alternative method signature
                    try:
                        health = await self.historical_analyzer.generate_health_score()
                        health_score = health.__dict__ if hasattr(health, '__dict__') else health or {}
                    except Exception as fallback_e:
                        logger.warning(f"Fallback health score generation failed: {fallback_e}")
                        health_score = {}
            
            # Generate basic health score if historical analyzer not available or failed
            if not health_score:
                logger.info("Generating basic health score using current observations")
                current_observations = self.dcp_manager.get_observations() if self.dcp_manager else []
                
                # Basic health metrics
                total_obs = len(current_observations)
                high_priority = len([obs for obs in current_observations if obs.get('priority', 50) >= 80])
                error_obs = len([obs for obs in current_observations if 'error' in obs.get('type', '').lower()])
                
                health_score = {
                    'overall_score': max(0, min(100, 80 - (high_priority * 2) - (error_obs * 5))),
                    'total_observations': total_obs,
                    'high_priority_issues': high_priority,
                    'error_observations': error_obs,
                    'health_status': 'basic_analysis',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # Store health score results in DCP for output generation
            if self.dcp_manager and health_score:
                self.dcp_manager.add_observation(
                    obs_type='health_score',
                    data={
                        'type': 'health_score',
                        'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                        'health_metrics': health_score,
                        'source': 'strategist_agent'
                    },
                    source_agent=self.agent_name,
                    priority=75  # High priority for health monitoring
                )
                logger.info(f"Health score stored in DCP for output generation")
            
            return health_score
            
        except Exception as e:
            logger.error(f"Failed to generate health score: {e}")
            return {
                'error': str(e),
                'health_status': 'analysis_failed',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def detect_drift(self, baseline_id: Optional[str] = None) -> Dict:
        """Detect architectural drift from baseline"""
        try:
            drift = await self.historical_analyzer.detect_drift(
                project_id=str(self.project_path.name),
                baseline_snapshot_id=baseline_id
            )
            return drift.__dict__ if drift else {}
        except Exception as e:
            logger.error(f"Failed to detect drift: {e}")
            return {}
    
    # Predictive Analytics Methods
    async def generate_predictions(self, prediction_types: Optional[List[str]] = None) -> Dict:
        """Generate predictions for the project"""
        try:
            self._track_lazy_loading_trigger('generate_predictions')
            self._ensure_components_initialized()
            predictions = await self.prediction_engine.generate_predictions(
                project_id=str(self.project_path.name),
                prediction_types=prediction_types
            )
            return predictions
        except Exception as e:
            logger.error(f"Failed to generate predictions: {e}")
            return {}
    
    async def predict_timeline(self, current_velocity: Optional[float] = None) -> Dict:
        """Generate timeline predictions"""
        try:
            self._track_lazy_loading_trigger('predict_timeline')
            self._ensure_components_initialized()
            timeline = await self.prediction_engine.predict_timeline(
                project_id=str(self.project_path.name),
                current_velocity=current_velocity
            )
            return timeline
        except Exception as e:
            logger.error(f"Failed to predict timeline: {e}")
            return {}
    
    async def get_prediction_recommendations(self) -> List[Dict]:
        """Get recommendations based on predictions"""
        try:
            self._track_lazy_loading_trigger('get_prediction_recommendations')
            self._ensure_components_initialized()
            recommendations = await self.prediction_engine.get_recommendations(
                project_id=str(self.project_path.name)
            )
            return recommendations
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return []
    
    # Planning Intelligence Methods
    async def generate_intelligent_plan(
        self, 
        goals: List[str], 
        constraints: Optional[Dict] = None,
        use_learning: bool = True
    ) -> Dict:
        """Generate intelligent plan with goal decomposition and constraint solving"""
        # Track lazy loading trigger and ensure components are initialized
        self._track_lazy_loading_trigger('generate_intelligent_plan')
        self._ensure_components_initialized()
        
        try:
            # Create planning context
            from coppersun_brass.agents.strategist.planning.intelligence_coordinator import PlanningContext
            from coppersun_brass.agents.strategist.planning.constraint_solver import Agent
            
            # Convert constraints to planning context
            available_agents = [
                Agent(
                    id="scout", 
                    name="Scout",
                    skills=["research", "analysis", "todo_detection"],
                    max_concurrent_tasks=5,
                    hourly_capacity=8.0,
                    efficiency_rating=0.9,
                    specializations=["code_analysis", "documentation"]
                ),
                Agent(
                    id="watch",
                    name="Watch",
                    skills=["monitoring", "tracking", "file_analysis"],
                    max_concurrent_tasks=10,
                    hourly_capacity=24.0,  # Continuous monitoring
                    efficiency_rating=0.95,
                    specializations=["real_time_monitoring", "change_detection"]
                ),
                Agent(
                    id="claude",
                    name="Claude",
                    skills=["implementation", "review", "planning"],
                    max_concurrent_tasks=3,
                    hourly_capacity=6.0,
                    efficiency_rating=0.85,
                    specializations=["ai_planning", "code_generation"]
                )
            ]
            
            context = PlanningContext(
                goals=goals,
                constraints=constraints or {},
                available_agents=available_agents,
                existing_observations=self.dcp_manager.read_dcp().get('current_observations', []) if self.dcp_manager else [],
                timeline_constraints={},
                resource_constraints={},
                priority_weights={}
            )
            
            # Generate comprehensive plan
            result = await self.intelligence_coordinator.generate_comprehensive_plan(
                goals=goals,
                context=context
            )
            
            # Convert result to dictionary
            return result.__dict__ if result else {}
        except Exception as e:
            logger.error(f"Failed to generate intelligent plan: {e}")
            return {}
    
    async def adapt_plan(
        self,
        plan_id: str,
        trigger_event: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """Adapt existing plan based on new conditions"""
        try:
            adapted_plan = await self.intelligence_coordinator.adapt_plan(
                plan_id=plan_id,
                trigger_event=trigger_event,
                context=context or {}
            )
            return adapted_plan
        except Exception as e:
            logger.error(f"Failed to adapt plan: {e}")
            return {}
    
    async def get_planning_insights(self) -> Dict:
        """Get insights from planning intelligence"""
        try:
            insights = await self.intelligence_coordinator.get_planning_insights()
            return insights
        except Exception as e:
            logger.error(f"Failed to get planning insights: {e}")
            return {}
    
    # Event handlers
    async def _handle_watch_analysis(self, event_data: Dict):
        """Handle Watch agent analysis completion"""
        logger.debug("Received watch analysis event")
        await self.orchestrate_dcp_updates()
    
    async def _handle_scout_research(self, event_data: Dict):
        """Handle Scout agent research completion"""
        logger.debug("Received scout research event")
        await self.orchestrate_dcp_updates()
    
    # Best Practices and Gap Detection Methods
    async def analyze_best_practices(self, observations: Optional[List[Dict]] = None) -> List[Dict]:
        """Analyze project against best practices"""
        try:
            if observations is None:
                # Get recent observations from DCP
                observations = self.dcp_manager.get_observations()
            
            # Extract project info for best practices analysis
            project_type = self.dcp_manager.get_project_type()
            
            # Create capabilities dict from observations
            capabilities = {}
            for obs in observations:
                if obs.get('type') == 'capability_assessment':
                    details = obs.get('details', {})
                    for cap_name, score in details.items():
                        if isinstance(score, (int, float)):
                            capabilities[cap_name] = score / 100.0  # Normalize to 0-1
            
            # Best practices now handled by evidence-based system in OutputGenerator
            # Return empty list since recommendations are generated in OutputGenerator
            logger.info("Best practices analysis skipped - now handled by evidence-based system in OutputGenerator")
            return []
            
        except Exception as e:
            logger.error(f"Best practices analysis failed: {e}")
            return []
    
    async def detect_project_gaps(self, context: Optional[Dict] = None) -> List[Dict]:
        """Detect gaps in project capabilities and coverage"""
        try:
            # For gap detection, we need ProjectCapabilities object
            # Create a mock one from available data
            from coppersun_brass.agents.strategist.autonomous.capability_assessor import ProjectCapabilities, CapabilityScore
            from datetime import datetime
            
            # Get observations to build capabilities
            observations = self.dcp_manager.get_observations()
            project_type = self.dcp_manager.get_project_type()
            
            # Build capabilities from observations
            capabilities_dict = {}
            for obs in observations:
                if obs.get('type') == 'capability_assessment':
                    details = obs.get('details', {})
                    for cap_name, score in details.items():
                        if isinstance(score, (int, float)):
                            capabilities_dict[cap_name] = CapabilityScore(
                                name=cap_name,
                                category='general',
                                score=float(score),
                                confidence=0.7,
                                details={},
                                missing_components=[],
                                recommendations=[]
                            )
            
            # Create ProjectCapabilities object
            project_capabilities = ProjectCapabilities(
                project_type=project_type,
                assessment_time=datetime.now(),
                overall_score=70.0,  # Default
                overall_confidence=0.7,
                capabilities=capabilities_dict,
                strengths=[],
                weaknesses=[],
                critical_gaps=[]
            )
            
            # Run gap detection
            gap_analysis = await self.gap_detector.find_gaps(project_capabilities)
            
            # Convert gaps to dict format and store in DCP
            gap_dicts = []
            all_gaps = (gap_analysis.critical_gaps + gap_analysis.important_gaps + 
                       gap_analysis.recommended_gaps + gap_analysis.nice_to_have_gaps)
            
            for gap in all_gaps:
                gap_dict = {
                    'type': 'gap_detection',
                    'category': gap.category,
                    'capability_name': gap.capability_name,
                    'description': f"Gap in {gap.capability_name}: current score {gap.current_score:.1f}, target {gap.target_score:.1f}",
                    'gap_size': gap.gap_size,
                    'confidence': gap.confidence,
                    'priority': gap.risk_score,  # Use risk score as priority
                    'risk_level': 'high' if gap.risk_score >= 70 else 'medium' if gap.risk_score >= 50 else 'low',
                    'estimated_effort': gap.estimated_effort,
                    'dependencies': gap.dependencies,
                    'recommended_actions': gap.recommendations,
                    'security_related': gap.security_related,
                    'compliance_related': gap.compliance_related
                }
                
                # Store in DCP
                self.dcp_manager.add_observation(
                    obs_type='gap_detection',
                    data=gap_dict,
                    source_agent=self.agent_name,
                    priority=gap.priority
                )
                
                gap_dicts.append(gap_dict)
            
            return gap_dicts
            
        except Exception as e:
            logger.error(f"Gap detection failed: {e}")
            return []
    
    def _get_observation_type_distribution(self, observations: List[Dict]) -> Dict[str, int]:
        """Get distribution of observation types"""
        distribution = {}
        for obs in observations:
            obs_type = obs.get('type', 'unknown')
            distribution[obs_type] = distribution.get(obs_type, 0) + 1
        return distribution
    
    def _get_priority_distribution(self, observations: List[Dict]) -> Dict[str, int]:
        """Get distribution of priorities"""
        distribution = {'high': 0, 'medium': 0, 'low': 0}
        for obs in observations:
            priority = obs.get('priority', 50)
            if priority >= 80:
                distribution['high'] += 1
            elif priority >= 50:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        return distribution
    
    # Event handlers removed - using DCP observation handlers instead
    
    async def start(self):
        """Start the strategist agent"""
        logger.info("Starting Strategist Agent")
        
        # Start DCP coordinator polling
        if hasattr(self, 'dcp_coordinator') and self.dcp_coordinator:
            self.dcp_coordinator.start_polling()
        
        # Initial orchestration
        await self.orchestrate_dcp_updates(force=True)
        
        # Handle any pending orchestration requests that were deferred
        if hasattr(self, '_pending_orchestration') and self._pending_orchestration:
            logger.info("Processing pending orchestration request from earlier scheduling")
            await self.orchestrate_dcp_updates()
            self._pending_orchestration = False
        
        # Best practices analysis - Generate sophisticated OWASP/NIST recommendations
        try:
            logger.info("Starting best practices analysis for sophisticated recommendations")
            recommendations = await self.analyze_best_practices()
            logger.info(f"Best practices analysis completed: {len(recommendations)} sophisticated recommendations generated")
        except Exception as e:
            logger.error(f"Best practices analysis failed: {e}")
            # Continue with fallback behavior - don't break agent startup
        
        # Event loop removed - using DCP coordination
    
    async def stop(self):
        """Stop the strategist agent"""
        logger.info("Stopping Strategist Agent")
        
        # Stop DCP coordinator polling
        if hasattr(self, 'dcp_coordinator') and self.dcp_coordinator:
            self.dcp_coordinator.stop_polling()
        
        # Event loop removed - using DCP coordination
    
    def generate_recommendations(self, observations: List[Dict]) -> List[Dict]:
        """Generate strategic recommendations based on observations (compatibility method).
        
        Args:
            observations: List of observation dictionaries
            
        Returns:
            List of recommendation dictionaries
        """
        try:
            recommendations = []
            
            # Group observations by type for strategic analysis
            obs_by_type = {}
            for obs in observations:
                obs_type = obs.get('type', 'unknown')
                if obs_type not in obs_by_type:
                    obs_by_type[obs_type] = []
                obs_by_type[obs_type].append(obs)
            
            # Generate recommendations based on observation patterns
            for obs_type, obs_list in obs_by_type.items():
                if obs_type == 'todo':
                    # TODO-based recommendations
                    high_priority_todos = [o for o in obs_list if o.get('priority', 50) >= 80]
                    if len(high_priority_todos) > 5:
                        recommendations.append({
                            'type': 'strategic_recommendation',
                            'category': 'todo_management',
                            'title': 'High Priority TODO Backlog',
                            'description': f'Found {len(high_priority_todos)} high-priority TODOs requiring attention',
                            'priority': 85,
                            'action': 'review_todos',
                            'impact': 'high',
                            'effort': 'medium'
                        })
                
                elif obs_type == 'security':
                    # Security-based recommendations
                    if len(obs_list) > 0:
                        recommendations.append({
                            'type': 'strategic_recommendation',
                            'category': 'security',
                            'title': 'Security Review Required',
                            'description': f'Found {len(obs_list)} security-related observations',
                            'priority': 95,
                            'action': 'security_audit',
                            'impact': 'critical',
                            'effort': 'high'
                        })
                
                elif obs_type == 'capability_assessment':
                    # Capability-based recommendations
                    low_scores = []
                    for obs in obs_list:
                        data = obs.get('data', {})
                        if isinstance(data, dict):
                            for cap, score in data.items():
                                if isinstance(score, (int, float)) and score < 50:
                                    low_scores.append(cap)
                    
                    if low_scores:
                        recommendations.append({
                            'type': 'strategic_recommendation',
                            'category': 'capability_improvement',
                            'title': 'Capability Gaps Identified',
                            'description': f'Low capability scores in: {", ".join(low_scores[:3])}',
                            'priority': 70,
                            'action': 'improve_capabilities',
                            'impact': 'medium',
                            'effort': 'high'
                        })
            
            # Add general strategic recommendations
            if len(observations) > 100:
                recommendations.append({
                    'type': 'strategic_recommendation',
                    'category': 'data_management',
                    'title': 'High Observation Volume',
                    'description': f'Processing {len(observations)} observations - consider archiving older data',
                    'priority': 60,
                    'action': 'archive_old_data',
                    'impact': 'low',
                    'effort': 'low'
                })
            
            logger.info(f"Generated {len(recommendations)} strategic recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    def _cleanup(self) -> None:
        """Clean up agent resources."""
        # Stop DCP coordinator if running
        if hasattr(self, 'dcp_coordinator') and self.dcp_coordinator:
            self.dcp_coordinator.stop_polling()
        
        # Clean up any other resources
        logger.debug("Strategist agent cleanup complete")
