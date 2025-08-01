# coppersun_brass/agents/strategist/orchestration_engine.py
"""
DCP Orchestration Engine for Copper Alloy Brass Strategist
Coordinates DCP updates, observation processing, and agent task routing
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

# Import for sophisticated AI analysis integration
try:
    from .autonomous.capability_assessor import CapabilityAssessor
    from .autonomous.context_analyzer import ProjectContext, ProjectContextAnalyzer
    from .autonomous.framework_detector import FrameworkDetector
    from .autonomous.dependency_analyzer import DependencyAnalyzer
    SOPHISTICATED_ANALYSIS_AVAILABLE = True
except ImportError:
    SOPHISTICATED_ANALYSIS_AVAILABLE = False
    CapabilityAssessor = None
    ProjectContext = None
    ProjectContextAnalyzer = None
    FrameworkDetector = None
    DependencyAnalyzer = None

logger = logging.getLogger(__name__)

class OrchestrationEngine:
    """
    Central orchestration engine that coordinates all DCP operations
    """
    
    def __init__(self, dcp_manager, priority_engine, duplicate_detector, 
                 best_practices_engine=None, gap_detector=None, capability_assessor=None,
                 context_analyzer=None, framework_detector=None, dependency_analyzer=None):
        self.dcp_manager = dcp_manager
        self.priority_engine = priority_engine
        self.duplicate_detector = duplicate_detector
        self.best_practices_engine = best_practices_engine
        self.gap_detector = gap_detector
        self.capability_assessor = capability_assessor
        self.context_analyzer = context_analyzer
        self.framework_detector = framework_detector
        self.dependency_analyzer = dependency_analyzer
        
        # Orchestration state
        self.last_orchestration_result = None
        self.orchestration_count = 0
        
        logger.debug("Orchestration engine initialized")
    
    async def orchestrate(self, current_dcp: Dict) -> Dict[str, Any]:
        """
        Main orchestration method - coordinates all DCP operations
        
        Args:
            current_dcp: Current DCP state
            
        Returns:
            Orchestration result with metrics and actions taken
        """
        self.orchestration_count += 1
        
        logger.info(f"Starting orchestration cycle #{self.orchestration_count}")
        
        try:
            result = {
                'cycle_id': self.orchestration_count,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'success',
                'actions_taken': [],
                'observations_processed': 0,
                'priorities_updated': 0,
                'duplicates_found': 0,
                'tasks_routed': 0,
                'dcp_updated': False,
                'errors': []
            }
            
            # Phase 1: Load and validate current observations
            observations = current_dcp.get('observations', [])
            logger.debug(f"Processing {len(observations)} observations")
            
            if not observations:
                result['status'] = 'no_observations'
                return result
            
            # Phase 2: Detect and handle duplicates
            duplicate_groups = self.duplicate_detector.find_duplicates(observations)
            if duplicate_groups:
                observations = self._handle_duplicates(observations, duplicate_groups, result)
                result['duplicates_found'] = sum(len(dups) for dups in duplicate_groups.values())
                result['actions_taken'].append('duplicate_detection')
            
            # Phase 3: Calculate priorities
            prioritized_observations = self._prioritize_all_observations(observations, result)
            result['observations_processed'] = len(prioritized_observations)
            result['actions_taken'].append('priority_calculation')
            
            # Phase 4: Update strategist metadata
            strategist_metadata = self._generate_strategist_metadata(prioritized_observations, duplicate_groups)
            
            # Phase 5: Route tasks to agents
            task_routing = self._route_tasks(prioritized_observations, result)
            result['tasks_routed'] = sum(len(tasks) for tasks in task_routing.values())
            if result['tasks_routed'] > 0:
                result['actions_taken'].append('task_routing')
            
            # Phase 6: Update DCP with orchestrated data
            if self._should_update_dcp(current_dcp, prioritized_observations, strategist_metadata):
                updated_dcp = self._build_updated_dcp(
                    current_dcp, 
                    prioritized_observations, 
                    strategist_metadata,
                    task_routing
                )
                
                self._save_updated_dcp(updated_dcp, result)
                result['dcp_updated'] = True
                result['actions_taken'].append('dcp_update')
            
            # Phase 7: Generate recommendations
            recommendations = await self._generate_recommendations(prioritized_observations, task_routing)
            if recommendations:
                result['recommendations'] = recommendations
                result['actions_taken'].append('recommendation_generation')
            
            self.last_orchestration_result = result
            
            logger.info(f"Orchestration cycle #{self.orchestration_count} completed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Orchestration cycle #{self.orchestration_count} failed: {e}"
            logger.error(error_msg, exc_info=True)
            
            return {
                'cycle_id': self.orchestration_count,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'error',
                'error': str(e),
                'actions_taken': [],
                'observations_processed': 0
            }
    
    def _handle_duplicates(self, observations: List[Dict], duplicate_groups: Dict[str, List[str]], result: Dict) -> List[Dict]:
        """Handle duplicate observations by merging or removing"""
        duplicate_ids = set()
        for canonical_id, dups in duplicate_groups.items():
            duplicate_ids.update(dups)
        
        # Remove duplicates, keep canonical observations
        filtered_observations = []
        for obs in observations:
            obs_id = obs.get('id', '')
            
            if obs_id not in duplicate_ids:
                # Mark if this is a canonical observation
                if obs_id in duplicate_groups:
                    obs['duplicate_count'] = len(duplicate_groups[obs_id])
                    obs['is_canonical'] = True
                
                filtered_observations.append(obs)
        
        removed_count = len(observations) - len(filtered_observations)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate observations")
        
        return filtered_observations
    
    def _prioritize_all_observations(self, observations: List[Dict], result: Dict) -> List[Dict]:
        """Calculate priorities for all observations"""
        prioritized = []
        priority_updates = 0
        
        for obs in observations:
            try:
                # Calculate new priority
                calculated_priority = self.priority_engine.calculate_priority(obs)
                original_priority = obs.get('priority', 50)
                
                # Update if significantly different
                if abs(calculated_priority - original_priority) >= 5:
                    obs['priority'] = calculated_priority
                    obs['priority_updated_by'] = 'strategist'
                    obs['priority_updated_at'] = datetime.now(timezone.utc).isoformat()
                    priority_updates += 1
                
                # Add priority rationale
                obs['priority_rationale'] = self.priority_engine.get_rationale(obs)
                
                # Mark as processed by strategist
                obs['strategist_processed'] = True
                obs['strategist_processed_at'] = datetime.now(timezone.utc).isoformat()
                
                prioritized.append(obs)
                
            except Exception as e:
                logger.warning(f"Failed to prioritize observation {obs.get('id', 'unknown')}: {e}")
                # Keep original observation
                prioritized.append(obs)
        
        # Sort by priority (highest first)
        prioritized.sort(key=lambda x: x.get('priority', 50), reverse=True)
        
        result['priorities_updated'] = priority_updates
        logger.debug(f"Updated priorities for {priority_updates} observations")
        
        return prioritized
    
    def _generate_strategist_metadata(self, observations: List[Dict], duplicate_groups: Dict) -> Dict:
        """Generate metadata about strategist analysis"""
        priority_dist = self.priority_engine.get_priority_distribution(observations)
        duplicate_stats = self.duplicate_detector.get_duplicate_stats(duplicate_groups)
        
        # Analyze observation types
        type_counts = {}
        for obs in observations:
            obs_type = obs.get('type', 'unknown')
            type_counts[obs_type] = type_counts.get(obs_type, 0) + 1
        
        # Identify top priorities
        top_priorities = [
            {
                'id': obs.get('id'),
                'type': obs.get('type'),
                'priority': obs.get('priority'),
                'summary': obs.get('summary', '')[:100] + ('...' if len(obs.get('summary', '')) > 100 else '')
            }
            for obs in observations[:5]  # Top 5
        ]
        
        return {
            'orchestration_timestamp': datetime.now(timezone.utc).isoformat(),
            'total_observations': len(observations),
            'priority_distribution': priority_dist,
            'duplicate_statistics': duplicate_stats,
            'type_distribution': type_counts,
            'top_priorities': top_priorities,
            'orchestration_cycle': self.orchestration_count
        }
    
    def _route_tasks(self, observations: List[Dict], result: Dict) -> Dict[str, List[Dict]]:
        """Route high-priority observations to appropriate agents"""
        routing = {
            'claude': [],
            'scout': [],
            'watch': [],
            'human': []
        }
        
        # Only route high-priority items to avoid spam
        high_priority_obs = [obs for obs in observations if obs.get('priority', 0) >= 70]
        
        for obs in high_priority_obs:
            obs_type = obs.get('type', 'unknown')
            priority = obs.get('priority', 50)
            
            # Enhanced routing logic
            if obs_type in ['security', 'critical_bug'] or priority >= 95:
                # Critical issues go to human
                routing['human'].append(self._create_task(obs, 'critical_review'))
            
            elif obs_type in ['todo_item', 'fixme_item'] and priority >= 80:
                # High-priority TODOs go to Claude
                routing['claude'].append(self._create_task(obs, 'implement_fix'))
            
            elif obs_type in ['research_needed', 'implementation_gap'] and priority >= 75:
                # Research tasks go to Scout
                routing['scout'].append(self._create_task(obs, 'research_solution'))
            
            elif obs_type in ['performance', 'optimization'] and priority >= 80:
                # Performance issues go to Claude
                routing['claude'].append(self._create_task(obs, 'optimize_code'))
            
            elif obs_type == 'test_coverage' and priority >= 75:
                # Test coverage issues go to Claude
                routing['claude'].append(self._create_task(obs, 'write_tests'))
        
        # Log routing decisions
        for agent, tasks in routing.items():
            if tasks:
                logger.info(f"Routed {len(tasks)} tasks to {agent}")
        
        return routing
    
    def _create_task(self, observation: Dict, task_type: str) -> Dict:
        """Create a task from an observation"""
        return {
            'observation_id': observation.get('id'),
            'task_type': task_type,
            'priority': observation.get('priority', 50),
            'summary': observation.get('summary'),
            'context': {
                'type': observation.get('type'),
                'location': self._extract_location_from_summary(observation.get('summary', '')),
                'created_at': observation.get('created_at')
            },
            'assigned_at': datetime.now(timezone.utc).isoformat(),
            'assigned_by': 'strategist'
        }
    
    def _extract_location_from_summary(self, summary: str) -> Optional[str]:
        """Extract location information from observation summary"""
        import re
        
        patterns = [
            r'\[Location: ([^\]]+)\]',
            r'Location: ([^\,\|]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, summary)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _should_update_dcp(self, current_dcp: Dict, prioritized_observations: List[Dict], metadata: Dict) -> bool:
        """Determine if DCP should be updated"""
        # Always update if we have new prioritized observations
        if any(obs.get('priority_updated_by') == 'strategist' for obs in prioritized_observations):
            return True
        
        # Update if we processed new observations
        unprocessed_count = len([obs for obs in prioritized_observations if not obs.get('strategist_processed')])
        if unprocessed_count > 0:
            return True
        
        # Update if metadata is significantly different
        current_metadata = current_dcp.get('strategist_metadata', {})
        if current_metadata.get('total_observations', 0) != metadata['total_observations']:
            return True
        
        return False
    
    def _build_updated_dcp(self, current_dcp: Dict, observations: List[Dict], metadata: Dict, task_routing: Dict) -> Dict:
        """Build updated DCP with orchestrated data"""
        updated_dcp = current_dcp.copy()
        
        # Update observations
        updated_dcp['current_observations'] = observations
        
        # Add strategist metadata
        updated_dcp['strategist_metadata'] = metadata
        
        # Add task routing information
        if any(tasks for tasks in task_routing.values()):
            updated_dcp['task_routing'] = {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'routing': task_routing
            }
        
        # Update meta information
        meta = updated_dcp.get('meta', {})
        meta['last_orchestration'] = datetime.now(timezone.utc).isoformat()
        meta['orchestration_cycle'] = self.orchestration_count
        updated_dcp['meta'] = meta
        
        return updated_dcp
    
    def _save_updated_dcp(self, updated_dcp: Dict, result: Dict):
        """Save updated DCP with error handling"""
        try:
            # Use DCPAdapter's update_section method instead of write_dcp
            for section, data in updated_dcp.items():
                # DCP STRATEGIST OBSERVATIONS WARNING FIX: Skip observations sections
                if section.startswith('observations'):
                    logger.debug(f"Skipping observations section '{section}' - not directly updatable")
                    continue
                    
                self.dcp_manager.update_section(section, data)
            logger.debug("DCP updated successfully")
        except Exception as e:
            error_msg = f"Failed to save updated DCP: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            raise
    
    async def _generate_recommendations(self, observations: List[Dict], task_routing: Dict) -> List[Dict]:
        """Generate strategic recommendations based on analysis"""
        recommendations = []
        
        # High-priority issues recommendation
        critical_obs = [obs for obs in observations if obs.get('priority', 0) >= 90]
        if critical_obs:
            recommendations.append({
                'type': 'immediate_attention',
                'priority': 95,
                'summary': f"{len(critical_obs)} critical issues require immediate attention",
                'details': [obs.get('summary', '')[:100] for obs in critical_obs[:3]],
                'recommended_action': 'Review and address critical observations'
            })
        
        # Test coverage recommendation
        test_obs = [obs for obs in observations if obs.get('type') == 'test_coverage']
        if len(test_obs) >= 3:
            recommendations.append({
                'type': 'test_coverage',
                'priority': 70,
                'summary': f"Multiple test coverage gaps detected ({len(test_obs)} issues)",
                'recommended_action': 'Implement comprehensive test suite'
            })
        
        # Security recommendation
        security_obs = [obs for obs in observations if obs.get('type') == 'security']
        if security_obs:
            recommendations.append({
                'type': 'security_review',
                'priority': 85,
                'summary': f"{len(security_obs)} security issues identified",
                'recommended_action': 'Conduct security audit and remediation'
            })
        
        # Sophisticated AI Analysis: Complete Pipeline Integration
        if self.capability_assessor and SOPHISTICATED_ANALYSIS_AVAILABLE:
            try:
                # Phase 1: Create rich project context using ContextAnalyzer (571 lines of analysis)
                if self.context_analyzer:
                    logger.info("Performing comprehensive project context analysis...")
                    project_context = await self.context_analyzer.analyze_project(self._get_project_path())
                else:
                    # Fallback: Enhanced manual context creation with direct framework/dependency analysis
                    logger.info("Creating enhanced project context with direct framework/dependency analysis...")
                    project_path = self._get_project_path()
                    
                    # Use FrameworkDetector for sophisticated framework analysis
                    framework_analysis = {}
                    if self.framework_detector:
                        framework_data = await self.framework_detector.detect_frameworks(project_path)
                        project_type_data = await self.framework_detector.detect_project_type(project_path)
                        framework_analysis = {
                            'detected_frameworks': framework_data,
                            'project_type': project_type_data['type'],
                            'confidence': project_type_data['confidence']
                        }
                    
                    # Use DependencyAnalyzer for sophisticated dependency analysis
                    dependency_analysis = {}
                    if self.dependency_analyzer:
                        dependency_analysis = await self.dependency_analyzer.analyze(project_path)
                    
                    project_context = ProjectContext(
                        project_type=framework_analysis.get('project_type', self._detect_project_type(observations)),
                        confidence_score=framework_analysis.get('confidence', 0.8),
                        framework_stack=framework_analysis.get('detected_frameworks', self._analyze_framework_stack(observations)),
                        file_structure=self._analyze_file_structure(observations),
                        dependencies=dependency_analysis,
                        code_patterns={},  # Will be enhanced
                        existing_capabilities={},  # Will be filled by capability assessor
                        quality_metrics={},  # Will be enhanced
                        security_posture={},  # Will be enhanced
                        scalability_readiness={},  # Will be enhanced
                        project_size=self._assess_project_size(observations),
                        project_maturity=self._assess_project_maturity(observations)
                    )
                
                # Phase 2: Perform sophisticated capability assessment (15+ categories)
                logger.info("Performing sophisticated capability assessment...")
                capabilities = await self.capability_assessor.assess(project_context)
                
                # Add capability assessment to recommendations
                if capabilities.overall_score < 75:
                    recommendations.append({
                        'type': 'capability_assessment',
                        'priority': max(60, 100 - int(capabilities.overall_score)),
                        'summary': f"Project capabilities: {capabilities.overall_score:.0f}% ({len(capabilities.capabilities)} categories assessed)",
                        'details': {
                            'strengths': capabilities.strengths[:3],
                            'weaknesses': capabilities.weaknesses[:3],
                            'critical_gaps': capabilities.critical_gaps
                        },
                        'recommended_action': 'Review capability assessment for improvement opportunities'
                    })
                
                # Phase 3: Perform sophisticated gap analysis using capability results
                if self.gap_detector:
                    logger.info("Performing sophisticated gap analysis...")
                    gap_analysis = await self.gap_detector.find_gaps(capabilities)
                    
                    # Convert high-priority gaps to recommendations
                    all_gaps = (gap_analysis.critical_gaps + gap_analysis.important_gaps + 
                               gap_analysis.recommended_gaps + gap_analysis.nice_to_have_gaps)
                    
                    for gap in all_gaps:
                        if gap.confidence > 0.7 and gap.risk_score >= 70:
                            recommendations.append({
                                'type': 'gap_analysis',
                                'priority': gap.risk_score,
                                'summary': f"{gap.capability_name}: {gap.gap_size:.0f}pt gap ({gap.category})",
                                'category': gap.category,
                                'confidence': gap.confidence,
                                'risk_score': gap.risk_score,
                                'recommended_action': gap.recommendations[0] if gap.recommendations else 'Address identified gap',
                                'estimated_effort': gap.estimated_effort
                            })
                
                # Phase 4: Add framework-specific recommendations
                if self.framework_detector and project_context.framework_stack:
                    logger.info("Generating framework-specific strategic recommendations...")
                    framework_recommendations = await self._generate_framework_recommendations(
                        project_context.framework_stack, observations
                    )
                    recommendations.extend(framework_recommendations)
                
                # Phase 5: Add dependency-specific recommendations
                if self.dependency_analyzer and project_context.dependencies:
                    logger.info("Generating dependency-specific strategic recommendations...")
                    dependency_recommendations = await self._generate_dependency_recommendations(
                        project_context.dependencies, observations
                    )
                    recommendations.extend(dependency_recommendations)
                
                logger.info(f"Sophisticated analysis completed: {len(capabilities.capabilities)} capabilities, {len(all_gaps) if 'all_gaps' in locals() else 0} gaps identified, framework analysis: {bool(self.framework_detector)}, dependency analysis: {bool(self.dependency_analyzer)}")
                        
            except Exception as e:
                logger.warning(f"Sophisticated analysis failed: {e}")
                # Fall back to basic gap detection if sophisticated analysis fails
                if self.gap_detector:
                    try:
                        # Fallback: basic project context
                        basic_context = {
                            'observations': observations,
                            'type_distribution': self._get_type_distribution(observations),
                            'priority_distribution': self._get_priority_distribution(observations)
                        }
                        logger.info("Falling back to basic gap analysis...")
                    except Exception as fallback_error:
                        logger.error(f"Fallback gap detection also failed: {fallback_error}")
        
        # Best Practices Engine replaced with evidence-based system in OutputGenerator
        # This check will be False since best_practices_engine is now None
        if self.best_practices_engine:
            try:
                # Get relevant observations for best practices analysis
                code_obs = [obs for obs in observations if obs.get('type') in ['code_issue', 'code_entity', 'code_metrics', 'todo', 'security_issue']]
                
                if code_obs:
                    # Generate best practices recommendations
                    bp_recommendations = self.best_practices_engine.generate_recommendations(
                        observations=code_obs,
                        limit=5  # Top 5 recommendations
                    )
                    
                    # Convert to orchestration recommendations
                    for bp_rec in bp_recommendations:
                        recommendations.append({
                            'type': 'best_practice',
                            'priority': bp_rec.get('priority', 60),
                            'summary': bp_rec.get('title', 'Best practice recommendation'),
                            'description': bp_rec.get('description', ''),
                            'category': bp_rec.get('category', 'general'),
                            'recommended_action': bp_rec.get('recommendation', ''),
                            'references': bp_rec.get('references', [])
                        })
                        
            except Exception as e:
                logger.warning(f"Best practices analysis failed: {e}")
        
        return recommendations
    
    def _get_type_distribution(self, observations: List[Dict]) -> Dict[str, int]:
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
    
    def _detect_project_type(self, observations: List[Dict]) -> str:
        """Detect project type from observations"""
        # Simple heuristics based on observation patterns
        types = {'web_app': 0, 'api_service': 0, 'cli_tool': 0, 'library': 0}
        
        for obs in observations:
            summary = obs.get('summary', '').lower()
            if any(keyword in summary for keyword in ['web', 'html', 'css', 'frontend', 'react', 'vue']):
                types['web_app'] += 1
            elif any(keyword in summary for keyword in ['api', 'endpoint', 'service', 'server', 'backend']):
                types['api_service'] += 1
            elif any(keyword in summary for keyword in ['cli', 'command', 'arg', 'main.py', '__main__']):
                types['cli_tool'] += 1
            elif any(keyword in summary for keyword in ['library', 'package', 'module', 'import']):
                types['library'] += 1
        
        # Return most likely type or default
        return max(types, key=types.get) if any(types.values()) else 'library'
    
    def _analyze_framework_stack(self, observations: List[Dict]) -> Dict[str, Any]:
        """Analyze framework stack from observations"""
        detected_frameworks = []
        primary_languages = []
        
        for obs in observations:
            summary = obs.get('summary', '').lower()
            # Framework detection patterns
            if 'react' in summary:
                if 'react' not in detected_frameworks:
                    detected_frameworks.append('react')
                if 'javascript' not in primary_languages:
                    primary_languages.append('javascript')
            elif 'django' in summary:
                if 'django' not in detected_frameworks:
                    detected_frameworks.append('django')
                if 'python' not in primary_languages:
                    primary_languages.append('python')
            elif 'flask' in summary:
                if 'flask' not in detected_frameworks:
                    detected_frameworks.append('flask')
                if 'python' not in primary_languages:
                    primary_languages.append('python')
            elif 'express' in summary or 'node' in summary:
                if 'express' not in detected_frameworks:
                    detected_frameworks.append('express')
                if 'javascript' not in primary_languages:
                    primary_languages.append('javascript')
            elif '.py' in summary:
                if 'python' not in primary_languages:
                    primary_languages.append('python')
            elif '.js' in summary or '.ts' in summary:
                if 'javascript' not in primary_languages:
                    primary_languages.append('javascript')
        
        return {
            'primary': detected_frameworks,  # List of detected frameworks
            'secondary': [],  # Could be enhanced with secondary frameworks
            'languages': primary_languages  # List of detected languages
        }
    
    def _analyze_file_structure(self, observations: List[Dict]) -> Dict[str, Any]:
        """Analyze file structure from observations"""
        files_by_type = {}
        patterns = {}
        
        for obs in observations:
            summary = obs.get('summary', '')
            # Extract file patterns
            if '.py' in summary:
                files_by_type.setdefault('python', []).append(summary)
            elif '.js' in summary or '.ts' in summary:
                files_by_type.setdefault('javascript', []).append(summary)
            elif '.html' in summary or '.css' in summary:
                files_by_type.setdefault('web', []).append(summary)
            
            # Directory patterns
            if 'test' in summary.lower():
                patterns.setdefault('testing', []).append(summary)
            elif 'config' in summary.lower():
                patterns.setdefault('configuration', []).append(summary)
        
        return {'files_by_type': files_by_type, 'patterns': patterns}
    
    def _extract_file_paths(self, observations: List[Dict]) -> List[str]:
        """Extract file paths from observations"""
        files = []
        for obs in observations:
            summary = obs.get('summary', '')
            # Simple extraction - look for file-like patterns
            import re
            file_matches = re.findall(r'[^\s]+\.[a-z]{2,4}', summary)
            files.extend(file_matches)
        return list(set(files))  # Remove duplicates
    
    def _get_project_path(self) -> Path:
        """Get project path for sophisticated analysis"""
        # Try to extract project path from DCP manager or use current directory
        if hasattr(self.dcp_manager, 'project_path'):
            return Path(self.dcp_manager.project_path)
        elif hasattr(self.dcp_manager, 'dcp_dir'):
            return Path(self.dcp_manager.dcp_dir).parent
        else:
            return Path.cwd()
    
    async def _generate_framework_recommendations(self, framework_stack: Dict[str, Any], observations: List[Dict]) -> List[Dict]:
        """Generate framework-specific strategic recommendations"""
        recommendations = []
        
        try:
            primary_frameworks = framework_stack.get('primary', [])
            secondary_frameworks = framework_stack.get('secondary', [])
            
            # Framework-specific best practices
            framework_best_practices = {
                'react': [
                    {'type': 'react_optimization', 'summary': 'Consider React performance optimization patterns'},
                    {'type': 'react_testing', 'summary': 'Implement React Testing Library for component testing'}
                ],
                'django': [
                    {'type': 'django_security', 'summary': 'Review Django security middleware configuration'},
                    {'type': 'django_performance', 'summary': 'Consider Django ORM optimization and caching strategies'}
                ],
                'express': [
                    {'type': 'express_security', 'summary': 'Implement Express security middleware (helmet, cors)'},
                    {'type': 'express_async', 'summary': 'Consider async/await patterns for Express route handlers'}
                ],
                'flask': [
                    {'type': 'flask_security', 'summary': 'Review Flask security configurations and CSRF protection'},
                    {'type': 'flask_structure', 'summary': 'Consider Flask Blueprint organization for larger applications'}
                ]
            }
            
            for framework in primary_frameworks:
                if framework in framework_best_practices:
                    for practice in framework_best_practices[framework]:
                        recommendations.append({
                            'type': practice['type'],
                            'priority': 70,
                            'summary': practice['summary'],
                            'category': 'framework_optimization',
                            'framework': framework,
                            'recommended_action': f'Review {framework} best practices for project optimization'
                        })
            
            # Multi-framework complexity warning
            if len(primary_frameworks) > 2:
                recommendations.append({
                    'type': 'framework_complexity',
                    'priority': 75,
                    'summary': f'Multiple primary frameworks detected: {primary_frameworks}',
                    'category': 'architecture_review',
                    'recommended_action': 'Consider consolidating frameworks to reduce complexity'
                })
            
        except Exception as e:
            logger.warning(f"Framework recommendation generation failed: {e}")
        
        return recommendations
    
    async def _generate_dependency_recommendations(self, dependencies: Dict[str, Any], observations: List[Dict]) -> List[Dict]:
        """Generate dependency-specific strategic recommendations"""
        recommendations = []
        
        try:
            total_deps = dependencies.get('total_count', 0)
            security_analysis = dependencies.get('security_analysis', {})
            conflicts = dependencies.get('conflicts', {})
            health_score = dependencies.get('dependency_health_score', 100)
            
            # High dependency count warning
            if total_deps > 50:
                recommendations.append({
                    'type': 'dependency_count',
                    'priority': 60,
                    'summary': f'{total_deps} dependencies detected - consider dependency audit',
                    'category': 'dependency_management',
                    'recommended_action': 'Review and consolidate dependencies to reduce complexity'
                })
            
            # Security risk recommendations
            risky_packages = security_analysis.get('risky_packages', [])
            if risky_packages:
                for package in risky_packages[:3]:  # Top 3 risky packages
                    recommendations.append({
                        'type': 'dependency_security',
                        'priority': 85 if package['risk_level'] == 'critical' else 70,
                        'summary': f"Security risk: {package['name']} ({package['risk_level']} risk)",
                        'category': 'security_review',
                        'package': package['name'],
                        'risk_level': package['risk_level'],
                        'recommended_action': f"Review and update {package['name']} for security vulnerabilities"
                    })
            
            # Dependency conflicts
            version_conflicts = conflicts.get('version_conflicts', [])
            if version_conflicts:
                recommendations.append({
                    'type': 'dependency_conflicts',
                    'priority': 80,
                    'summary': f'{len(version_conflicts)} dependency version conflicts detected',
                    'category': 'dependency_management',
                    'conflicts': version_conflicts[:3],
                    'recommended_action': 'Resolve dependency version conflicts to prevent runtime issues'
                })
            
            # Overall dependency health
            if health_score < 70:
                recommendations.append({
                    'type': 'dependency_health',
                    'priority': 65,
                    'summary': f'Dependency health score: {health_score:.0f}% - needs improvement',
                    'category': 'dependency_management',
                    'health_score': health_score,
                    'recommended_action': 'Implement dependency monitoring and update strategy'
                })
            
        except Exception as e:
            logger.warning(f"Dependency recommendation generation failed: {e}")
        
        return recommendations
    
    def _assess_project_size(self, observations: List[Dict]) -> str:
        """Assess project size based on observations"""
        file_count = 0
        code_complexity_indicators = 0
        
        for obs in observations:
            summary = obs.get('summary', '').lower()
            # Count file references
            if any(ext in summary for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']):
                file_count += 1
            
            # Look for complexity indicators
            if any(indicator in summary for indicator in ['class', 'function', 'method', 'import', 'module']):
                code_complexity_indicators += 1
        
        # Assess size based on file count and complexity
        if file_count < 10 and code_complexity_indicators < 20:
            return 'small'
        elif file_count < 50 and code_complexity_indicators < 100:
            return 'medium'
        elif file_count < 200 and code_complexity_indicators < 500:
            return 'large'
        else:
            return 'enterprise'
    
    def _assess_project_maturity(self, observations: List[Dict]) -> str:
        """Assess project maturity based on observations"""
        maturity_indicators = {
            'early': 0,
            'developing': 0,
            'mature': 0,
            'maintenance': 0
        }
        
        for obs in observations:
            summary = obs.get('summary', '').lower()
            obs_type = obs.get('type', '')
            
            # Early stage indicators
            if any(indicator in summary for indicator in ['todo', 'fixme', 'placeholder', 'stub']):
                maturity_indicators['early'] += 1
            
            # Developing stage indicators
            if any(indicator in summary for indicator in ['implementation', 'feature', 'enhancement']):
                maturity_indicators['developing'] += 1
            
            # Mature stage indicators
            if any(indicator in summary for indicator in ['test', 'documentation', 'optimization', 'refactor']):
                maturity_indicators['mature'] += 1
            
            # Maintenance stage indicators
            if any(indicator in summary for indicator in ['bug', 'fix', 'patch', 'security', 'maintenance']):
                maturity_indicators['maintenance'] += 1
        
        # Return the stage with the highest score
        dominant_stage = max(maturity_indicators, key=maturity_indicators.get)
        
        # Default to developing if no clear indicators
        if all(score == 0 for score in maturity_indicators.values()):
            return 'developing'
        
        return dominant_stage
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestration engine status"""
        return {
            'orchestration_count': self.orchestration_count,
            'last_result': self.last_orchestration_result,
            'components': {
                'dcp_manager': 'connected',
                'priority_engine': 'connected',
                'duplicate_detector': 'connected',
                'best_practices_engine': 'connected' if self.best_practices_engine else 'not_configured',
                'gap_detector': 'connected' if self.gap_detector else 'not_configured',
                'capability_assessor': 'connected' if self.capability_assessor else 'not_configured',
                'context_analyzer': 'connected' if self.context_analyzer else 'not_configured',
                'framework_detector': 'connected' if self.framework_detector else 'not_configured',
                'dependency_analyzer': 'connected' if self.dependency_analyzer else 'not_configured'
            }
        }