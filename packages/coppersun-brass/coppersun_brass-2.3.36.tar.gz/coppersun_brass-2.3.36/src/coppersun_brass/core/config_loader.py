"""Production configuration loader for Copper Alloy Brass.

This module handles loading and validating configuration from YAML files
and environment variables, with support for environment-specific overrides.
"""

import os
import yaml
import logging
import threading
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass, field
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class StorageConfig:
    """Storage configuration."""
    type: str = "sqlite"
    path: str = None  # Use BrassConfig.db_path for consistent path resolution
    backup_enabled: bool = True
    backup_interval: int = 3600
    backup_retention_days: int = 30
    backup_path: str = ".brass/backups"
    max_backups: int = 168
    connection_pool_size: int = 10
    connection_pool_overflow: int = 20
    connection_timeout: int = 30


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    enabled: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 60
    memory_alert_mb: int = 1024
    disk_alert_percent: int = 90
    error_rate_alert_percent: int = 5
    response_time_alert_ms: int = 1000
    metrics_retention_days: int = 7


@dataclass
class SecurityConfig:
    """Security configuration."""
    api_authentication: bool = True
    api_key_header: str = "X-Copper Alloy Brass-API-Key"
    rate_limiting_enabled: bool = True
    rate_limit_rpm: int = 60
    rate_limit_burst: int = 10
    max_path_length: int = 4096
    max_file_size_mb: int = 50


@dataclass
class BrassConfig:
    """Main Copper Alloy Brass configuration."""
    version: str = "1.0.0"
    environment: str = "development"
    project_root: str = "."
    log_level: str = "INFO"
    max_workers: int = 4
    thread_pool_size: int = 8
    
    # Sub-configurations
    storage: StorageConfig = field(default_factory=StorageConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Feature flags
    features: Dict[str, bool] = field(default_factory=lambda: {
        "experimental_semantic_analysis": False,
        "advanced_pattern_detection": True,
        "real_time_collaboration": False,
        "distributed_processing": False
    })


class ConfigLoader:
    """Loads and manages Copper Alloy Brass configuration."""
    
    def __init__(self, config_path: Optional[str] = None, env_file: Optional[str] = None):
        """Initialize configuration loader.
        
        Args:
            config_path: Path to YAML configuration file
            env_file: Path to environment file (defaults to .env)
        """
        self.config_path = config_path
        self.env_file = env_file or ".env"
        self._config: Optional[BrassConfig] = None
        self._config_file_mtime: Optional[float] = None
        
    def load(self) -> BrassConfig:
        """Load configuration from all sources.
        
        Order of precedence (highest to lowest):
        1. Environment variables
        2. Environment-specific YAML config
        3. Main YAML config
        4. Defaults
        """
        # CONFIG RELOAD RACE CONDITION FIX: Thread-safe config reload check
        with self._lock:
            # Check if config file has changed since last load
            if self._config is not None and self._should_reload_config():
                logger.info("Configuration file changed, reloading...")
                self._config = None
                
            if self._config is not None:
                return self._config
            
        # Load environment variables
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
            
        # Start with defaults
        config = BrassConfig()
        
        # Load YAML config if provided
        if self.config_path and os.path.exists(self.config_path):
            yaml_config = self._load_yaml(self.config_path)
            config = self._merge_config(config, yaml_config)
            
        # Apply environment variable overrides
        config = self._apply_env_overrides(config)
        
        # File modification time is now stored during YAML loading to reduce race conditions
        
        # Validate configuration
        self._validate_config(config)
        
        self._config = config
        logger.info(f"Loaded configuration for environment: {config.environment}")
        
        return config
        
    def _load_yaml(self, path: str) -> Dict[str, Any]:
        """Load YAML configuration file."""
        yaml_data, mtime = self._load_yaml_with_mtime(path)
        self._config_file_mtime = mtime
        return yaml_data
    
    def _load_yaml_with_mtime(self, path: str) -> Tuple[Dict[str, Any], float]:
        """Load YAML configuration file and return data with modification time.
        
        Returns:
            Tuple of (config_data, modification_time)
        """        
        try:
            # Get file info atomically to reduce race window
            stat_info = os.stat(path)
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                
            # Get base config
            base_config = data.get('coppersun_brass', {}) if data else {}
            
            # Apply environment-specific overrides
            env = os.getenv('BRASS_ENV', 'development')
            env_overrides = data.get('environments', {}).get(env, {}) if data else {}
            
            # Merge environment overrides
            if env_overrides:
                override_config = env_overrides.get('coppersun_brass', {})
                if override_config:
                    logger.info(f"Applying environment-specific overrides for '{env}': {list(override_config.keys())}")
                base_config = self._deep_merge(base_config, override_config)
                
            return base_config, stat_info.st_mtime
            
        except FileNotFoundError:
            logger.warning(f"Config file not found: {path}")
            return {}, 0.0
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in {path}: {e}")
            return {}, 0.0
        except PermissionError:
            logger.error(f"Permission denied reading {path}")
            raise  # Re-raise critical errors
        except Exception as e:
            logger.error(f"Unexpected error loading {path}: {e}")
            return {}, 0.0
            
    def _merge_config(self, config: BrassConfig, yaml_data: Dict[str, Any]) -> BrassConfig:
        """Merge YAML data into configuration object."""
        # Core settings
        config.version = yaml_data.get('version', config.version)
        config.environment = yaml_data.get('environment', config.environment)
        
        core = yaml_data.get('core', {})
        config.project_root = core.get('project_root', config.project_root)
        config.log_level = core.get('log_level', config.log_level)
        config.max_workers = self._safe_int_yaml(core.get('max_workers', config.max_workers), config.max_workers)
        config.thread_pool_size = self._safe_int_yaml(core.get('thread_pool_size', config.thread_pool_size), config.thread_pool_size)
        
        # Storage settings
        storage = yaml_data.get('storage', {})
        if storage:
            backup = storage.get('backup', {})
            pool = storage.get('connection_pool', {})
            
            config.storage.type = storage.get('type', config.storage.type)
            config.storage.path = storage.get('path', config.storage.path)
            config.storage.backup_enabled = backup.get('enabled', config.storage.backup_enabled)
            config.storage.backup_interval = self._safe_int_yaml(backup.get('interval', config.storage.backup_interval), config.storage.backup_interval)
            config.storage.backup_retention_days = self._safe_int_yaml(backup.get('retention_days', config.storage.backup_retention_days), config.storage.backup_retention_days)
            config.storage.backup_path = backup.get('backup_path', config.storage.backup_path)
            config.storage.max_backups = self._safe_int_yaml(backup.get('max_backups', config.storage.max_backups), config.storage.max_backups)
            config.storage.connection_pool_size = self._safe_int_yaml(pool.get('size', config.storage.connection_pool_size), config.storage.connection_pool_size)
            config.storage.connection_pool_overflow = self._safe_int_yaml(pool.get('max_overflow', config.storage.connection_pool_overflow), config.storage.connection_pool_overflow)
            config.storage.connection_timeout = self._safe_int_yaml(pool.get('timeout', config.storage.connection_timeout), config.storage.connection_timeout)
            
        # Monitoring settings
        monitoring = yaml_data.get('monitoring', {})
        if monitoring:
            alerts = monitoring.get('alerts', {})
            metrics = monitoring.get('metrics', {})
            
            config.monitoring.enabled = monitoring.get('enabled', config.monitoring.enabled)
            config.monitoring.metrics_port = self._safe_int_yaml(monitoring.get('metrics_port', config.monitoring.metrics_port), config.monitoring.metrics_port)
            config.monitoring.health_check_interval = self._safe_int_yaml(monitoring.get('health_check_interval', config.monitoring.health_check_interval), config.monitoring.health_check_interval)
            config.monitoring.memory_alert_mb = self._safe_int_yaml(alerts.get('memory_usage_mb', config.monitoring.memory_alert_mb), config.monitoring.memory_alert_mb)
            config.monitoring.disk_alert_percent = self._safe_int_yaml(alerts.get('disk_usage_percent', config.monitoring.disk_alert_percent), config.monitoring.disk_alert_percent)
            config.monitoring.error_rate_alert_percent = self._safe_int_yaml(alerts.get('error_rate_percent', config.monitoring.error_rate_alert_percent), config.monitoring.error_rate_alert_percent)
            config.monitoring.response_time_alert_ms = self._safe_int_yaml(alerts.get('response_time_ms', config.monitoring.response_time_alert_ms), config.monitoring.response_time_alert_ms)
            config.monitoring.metrics_retention_days = self._safe_int_yaml(metrics.get('retention_days', config.monitoring.metrics_retention_days), config.monitoring.metrics_retention_days)
            
        # Security settings
        security = yaml_data.get('security', {})
        if security:
            rate_limiting = security.get('rate_limiting', {})
            validation = security.get('validation', {})
            
            config.security.api_authentication = security.get('api_authentication', config.security.api_authentication)
            config.security.api_key_header = security.get('api_key_header', config.security.api_key_header)
            config.security.rate_limiting_enabled = rate_limiting.get('enabled', config.security.rate_limiting_enabled)
            config.security.rate_limit_rpm = self._safe_int_yaml(rate_limiting.get('requests_per_minute', config.security.rate_limit_rpm), config.security.rate_limit_rpm)
            config.security.rate_limit_burst = self._safe_int_yaml(rate_limiting.get('burst_size', config.security.rate_limit_burst), config.security.rate_limit_burst)
            config.security.max_path_length = self._safe_int_yaml(validation.get('max_path_length', config.security.max_path_length), config.security.max_path_length)
            config.security.max_file_size_mb = self._safe_int_yaml(validation.get('max_file_size_mb', config.security.max_file_size_mb), config.security.max_file_size_mb)
            
        # Feature flags
        features = yaml_data.get('features', {})
        if features:
            self._safe_dict_update(config.features, features, max_size=1000)
            
        return config
        
    def _safe_int_yaml(self, value: Any, default: int) -> int:
        """Safely convert YAML value to integer with type validation.
        
        Args:
            value: YAML value that should be converted to integer
            default: Default value if conversion fails
            
        Returns:
            Integer value or default if conversion fails
        """
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                logger.warning(f"Invalid YAML integer value: {value}, using default: {default}")
                return default
        logger.warning(f"Non-numeric YAML value: {value}, using default: {default}")
        return default
    
    def _safe_dict_update(self, target_dict: Dict[str, Any], source_dict: Dict[str, Any], max_size: int = 1000) -> None:
        """Safely update dictionary with size limits to prevent memory exhaustion.
        
        Args:
            target_dict: Dictionary to update
            source_dict: Dictionary with new values
            max_size: Maximum allowed size for target dictionary
        """
        if len(target_dict) + len(source_dict) > max_size:
            logger.warning(f"Dictionary size limit exceeded ({max_size}), partial update applied")
            for key, value in source_dict.items():
                if len(target_dict) >= max_size:
                    break
                target_dict[key] = value
        else:
            target_dict.update(source_dict)
        
    def _safe_int_env(self, key: str, default: int) -> int:
        """Safely convert environment variable to integer with fallback.
        
        Args:
            key: Environment variable name
            default: Default value if conversion fails
            
        Returns:
            Integer value or default if conversion fails
        """
        try:
            value = os.getenv(key)
            if value is None:
                return default
            return int(value)
        except (ValueError, TypeError):
            # ENVIRONMENT VARIABLE TYPE COERCION FIX: Use cached value, don't re-fetch for security
            logger.warning(f"Invalid integer value for {key}: {value}, using default: {default}")
            return default
    
    def _apply_env_overrides(self, config: BrassConfig) -> BrassConfig:
        """Apply environment variable overrides to configuration."""
        # Core settings
        config.environment = os.getenv('BRASS_ENV', config.environment)
        config.log_level = os.getenv('BRASS_LOG_LEVEL', config.log_level)
        config.max_workers = self._safe_int_env('BRASS_MAX_WORKERS', config.max_workers)
        config.thread_pool_size = self._safe_int_env('BRASS_THREAD_POOL_SIZE', config.thread_pool_size)
        
        # Storage settings
        config.storage.path = os.getenv('BRASS_DB_PATH', config.storage.path)
        config.storage.backup_path = os.getenv('BRASS_BACKUP_PATH', config.storage.backup_path)
        config.storage.backup_retention_days = self._safe_int_env('BRASS_DCP_BACKUP_RETENTION', config.storage.backup_retention_days)
        
        # Monitoring settings
        config.monitoring.enabled = os.getenv('BRASS_MONITORING_ENABLED', 'true').lower() == 'true'
        config.monitoring.metrics_port = self._safe_int_env('BRASS_METRICS_PORT', config.monitoring.metrics_port)
        config.monitoring.health_check_interval = self._safe_int_env('BRASS_HEALTH_CHECK_INTERVAL', config.monitoring.health_check_interval)
        
        # Security settings
        config.security.api_authentication = os.getenv('BRASS_API_AUTH_ENABLED', 'true').lower() == 'true'
        config.security.rate_limiting_enabled = os.getenv('BRASS_CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true'
        config.security.rate_limit_rpm = self._safe_int_env('BRASS_RATE_LIMIT_RPM', config.security.rate_limit_rpm)
        
        return config
        
    def _validate_config(self, config: BrassConfig) -> None:
        """Validate configuration values."""
        # Validate paths exist or can be created
        project_root = Path(config.project_root).resolve()
        if not project_root.exists():
            raise ValueError(f"Project root does not exist: {project_root}")
        if not project_root.is_dir():
            raise ValueError(f"Project root is not a directory: {project_root}")
            
        # Validate numeric ranges
        if config.max_workers < 1:
            raise ValueError("max_workers must be at least 1")
            
        if config.thread_pool_size < 1:
            raise ValueError("thread_pool_size must be at least 1")
            
        if config.monitoring.metrics_port < 1024 or config.monitoring.metrics_port > 65535:
            raise ValueError("metrics_port must be between 1024 and 65535")
            
        if config.security.rate_limit_rpm < 1:
            raise ValueError("rate_limit_rpm must be at least 1")
            
        # Log validation success
        logger.info("Configuration validation successful")
        
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def _should_reload_config(self) -> bool:
        """Check if configuration file has changed since last load.
        
        Returns:
            True if config should be reloaded, False otherwise
        """
        if not self.config_path or not os.path.exists(self.config_path):
            return False
            
        if self._config_file_mtime is None:
            return True
            
        current_mtime = os.path.getmtime(self.config_path)
        return current_mtime > self._config_file_mtime
        
    def get_config(self) -> BrassConfig:
        """Get loaded configuration, loading if necessary."""
        if self._config is None:
            self.load()
        return self._config
        
    def reload(self) -> BrassConfig:
        """Reload configuration from sources."""
        self._config = None
        return self.load()


# Global configuration instance with thread safety
_config_loader: Optional[ConfigLoader] = None
_config_lock = threading.Lock()


def get_config() -> BrassConfig:
    """Get global configuration instance with thread safety."""
    global _config_loader
    
    with _config_lock:
        if _config_loader is None:
            # Check for config path in environment
            config_path = os.getenv('BRASS_CONFIG_PATH')
            env_file = os.getenv('BRASS_ENV_FILE', '.env')
            
            _config_loader = ConfigLoader(config_path=config_path, env_file=env_file)
            
        return _config_loader.get_config()


def init_config(config_path: Optional[str] = None, env_file: Optional[str] = None) -> BrassConfig:
    """Initialize global configuration with specific paths and thread safety."""
    global _config_loader
    
    with _config_lock:
        _config_loader = ConfigLoader(config_path=config_path, env_file=env_file)
        return _config_loader.load()